"""CI pipeline for the Python FastAPI project.

This module defines a Dagger CI pipeline for the project.
"""

import tomllib
from pathlib import Path
from typing import Annotated

import dagger
from dagger import DefaultPath, Doc, Ignore, dag, function, object_type

from .utils.coverage import CoverageFormats, format_coverage
from .utils.locust import OutputFormats, format_comparison

_DEFAULT_BASELINE_IMAGE = "ghcr.io/manuel-gallina/python-fastapi-v01:latest"
_LOCUSTFILES_PATH = "/project/tests/acceptance_tests/non_functional/locustfiles"
_DB_ENV_VARS = {
    "DATABASE__MAIN_CONNECTION__DBMS": "postgresql",
    "DATABASE__MAIN_CONNECTION__DRIVER": "asyncpg",
    "DATABASE__MAIN_CONNECTION__HOST": "main_db",
    "DATABASE__MAIN_CONNECTION__PORT": "5432",
    "DATABASE__MAIN_CONNECTION__USER": "admin",
    "DATABASE__MAIN_CONNECTION__PASSWORD": "admin",
    "DATABASE__MAIN_CONNECTION__NAME": "python_fastapi_v01",
}


class Utils:
    """Utility functions for the CI pipeline."""

    @staticmethod
    def with_env_variables(
        container: dagger.Container, env_vars: dict[str, str]
    ) -> dagger.Container:
        """Writes the provided environment variables into the container.

        Args:
            container (dagger.Container): The container to which the environment
                variables will be added.
            env_vars (dict[str, str]): A dictionary of environment variable names
                and their corresponding values.

        Returns:
            dagger.Container: The container with the added environment variables.
        """
        for key, value in env_vars.items():
            container = container.with_env_variable(key, value)
        return container


PROJECT_PATH = "/project"
DEFAULT_ENV_VARS = {
    "DATABASE__MAIN_CONNECTION__DBMS": "postgresql",
    "DATABASE__MAIN_CONNECTION__DRIVER": "asyncpg",
    "DATABASE__MAIN_CONNECTION__HOST": "UNSET",
    "DATABASE__MAIN_CONNECTION__PORT": "0",
    "DATABASE__MAIN_CONNECTION__USER": "UNSET",
    "DATABASE__MAIN_CONNECTION__PASSWORD": "UNSET",
    "DATABASE__MAIN_CONNECTION__NAME": "UNSET",
}
BASE_IGNORES = [
    "**/.venv",
    "**/__pycache__",
    ".git",
    "**/.gitignore",
    ".idea",
    ".ruff_cache",
    ".env",
]


@object_type
class PythonFastapiV01:
    """Dagger CI pipeline for the Python FastAPI project."""

    SourceDir = Annotated[
        dagger.Directory,
        DefaultPath("."),
        Doc("The project source directory"),
        Ignore([*BASE_IGNORES, "tests/", ".pytest_cache"]),
    ]

    TestSourceDir = Annotated[
        dagger.Directory,
        DefaultPath("."),
        Doc("The project source directory"),
        Ignore(BASE_IGNORES),
    ]

    @function
    def build_env(
        self,
        source: SourceDir,
        *,
        development: Annotated[bool, Doc("install development dependencies")] = False,
    ) -> dagger.Container:
        """Builds the container environment for the application.

        The build process is split into two stages: a builder stage where
        the dependencies are installed and a runner stage where the application
        code and the installed dependencies are combined to create the final container.

        Args:
            source (SourceDir): The project source directory.
            development (bool): Whether to install development dependencies.

        Returns:
            dagger.Container: The container with the built environment.
        """
        base_image = "python:3.13-slim"
        venv_path = "/venv"
        uv_bin = dag.container().from_("ghcr.io/astral-sh/uv:0.10.0").file("/uv")
        uv_path = "/usr/local/bin/uv"

        # Builder container
        builder = (
            dag.container()
            .from_(base_image)
            .with_exec(
                [
                    "sh",
                    "-c",
                    """apt-get update && apt-get install -y --no-install-recommends \
                        build-essential \
                        gcc \
                        pkg-config \
                        && rm -rf /var/lib/apt/lists/*""",
                ]
            )
            .with_file(uv_path, uv_bin)
            .with_env_variable("UV_PROJECT_ENVIRONMENT", venv_path)
            .with_directory(PROJECT_PATH, source)
            .with_workdir(PROJECT_PATH)
            .with_mounted_cache("/root/.cache/uv", dag.cache_volume("uv-cache"))
        )
        sync_cmd = ["uv", "sync", "--locked"]
        if not development:
            sync_cmd.append("--no-dev")
        builder = builder.with_exec(sync_cmd)

        # Final container
        runner = (
            dag.container()
            .from_(base_image)
            .with_directory(PROJECT_PATH, source)
            .with_workdir(PROJECT_PATH)
            .with_directory(venv_path, builder.directory(venv_path))
            .with_env_variable(
                "PATH", ":".join([f"{venv_path}/bin", "$PATH"]), expand=True
            )
            .with_env_variable(
                "PYTHONPATH",
                ":".join([PROJECT_PATH, f"{PROJECT_PATH}/src", "$PYTHONPATH"]),
                expand=True,
            )
            .with_env_variable("VIRTUAL_ENV", venv_path)
        )
        if not development:
            runner = runner.with_env_variable("PYTHONOPTIMIZE", "1")

        return runner

    @staticmethod
    def _live_environment(
        api_app: dagger.Container,
    ) -> tuple[dagger.Service, dagger.Service]:
        """Creates a live database and API service pair for testing.

        Args:
            api_app (dagger.Container): The API application container, without
                database environment variables or service bindings applied.

        Returns:
            tuple[dagger.Service, dagger.Service]: A (db_service, api_service) pair
                where the API service is bound to the database service.
        """
        db_service = (
            Utils.with_env_variables(
                dag.container().from_("postgres:18"),
                {
                    "POSTGRES_USER": "admin",
                    "POSTGRES_PASSWORD": "admin",
                    "POSTGRES_DB": "python_fastapi_v01",
                },
            )
            .with_exposed_port(5432)
            .as_service()
        )

        api_service = (
            Utils.with_env_variables(api_app, _DB_ENV_VARS)
            .with_service_binding("main_db", db_service)
            .with_exposed_port(8000)
            .with_entrypoint(["fastapi", "run", "/project/src/main.py"])
            .as_service()
        )

        return db_service, api_service

    @function
    async def test_unit(
        self,
        source: TestSourceDir,
        *,
        pytest_quiet: bool = False,
        pytest_randomly_seed: str | None = None,
    ) -> str:
        """Runs the unit tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.
            pytest_quiet (bool): Run tests with quiet output.
            pytest_randomly_seed (str | None): The seed for random test case ordering

        Returns:
            str: The output of the pytest command.
        """
        pytest_args = []
        if pytest_quiet:
            pytest_args.append("-q")
        if pytest_randomly_seed:
            pytest_args.append(f"--randomly-seed={pytest_randomly_seed}")

        test_container = Utils.with_env_variables(
            self.build_env(source, development=True), DEFAULT_ENV_VARS
        ).with_exec(["pytest", *pytest_args, "tests/unit_tests"])
        return await test_container.stdout()

    @function
    async def test_integration(
        self,
        source: TestSourceDir,
        *,
        pytest_quiet: bool = False,
        pytest_randomly_seed: str | None = None,
    ) -> str:
        """Runs the integration tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.
            pytest_quiet (bool): Run tests with quiet output.
            pytest_randomly_seed (str | None): The seed for random test case ordering

        Returns:
            str: The output of the pytest command.
        """
        pytest_args = []
        if pytest_quiet:
            pytest_args.append("-q")
        if pytest_randomly_seed:
            pytest_args.append(f"--randomly-seed={pytest_randomly_seed}")

        test_container = Utils.with_env_variables(
            self.build_env(source, development=True), DEFAULT_ENV_VARS
        ).with_exec(["pytest", *pytest_args, "tests/integration_tests"])
        return await test_container.stdout()

    @function
    async def test_coverage(
        self,
        source: TestSourceDir,
        *,
        pytest_quiet: bool = False,
        pytest_randomly_seed: str | None = None,
        output_format: Annotated[
            str, Doc("output format for the coverage report ('terminal' or 'markdown')")
        ] = CoverageFormats.TERMINAL,
    ) -> str:
        """Runs unit and integration tests with coverage and returns a report.

        Args:
            source (TestSourceDir): The project source directory.
            pytest_quiet (bool): Run tests with quiet output.
            pytest_randomly_seed (str | None): The seed for random test case ordering.
            output_format (str): Output format for the coverage report.

        Returns:
            str: A formatted coverage report.
        """
        pytest_args = []
        if pytest_quiet:
            pytest_args.append("-q")
        if pytest_randomly_seed:
            pytest_args.append(f"--randomly-seed={pytest_randomly_seed}")

        test_container = Utils.with_env_variables(
            self.build_env(source, development=True), DEFAULT_ENV_VARS
        ).with_exec(
            [
                "pytest",
                *pytest_args,
                "--cov=src",
                "--cov-report=term-missing",
                "tests/unit_tests",
                "tests/integration_tests",
            ]
        )
        raw_output = await test_container.stdout()
        return format_coverage(raw_output, CoverageFormats(output_format))

    @function
    async def test_acceptance(
        self,
        source: TestSourceDir,
        *,
        pytest_quiet: bool = False,
        pytest_randomly_seed: str | None = None,
    ) -> str:
        """Runs the acceptance tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.
            pytest_quiet (bool): Run tests with quiet output.
            pytest_randomly_seed (str | None): The seed for random test case ordering

        Returns:
            str: The output of the pytest command.
        """
        pytest_args = []
        if pytest_quiet:
            pytest_args.append("-q")
        if pytest_randomly_seed:
            pytest_args.append(f"--randomly-seed={pytest_randomly_seed}")

        db_service, api_service = self._live_environment(self.build_env(source))

        test_container = (
            Utils.with_env_variables(
                self.build_env(source, development=True),
                {"TEST_API_BASE_URL": "http://api:8000", **_DB_ENV_VARS},
            )
            .with_service_binding("main_db", db_service)
            .with_service_binding("api", api_service)
            .with_exec(["alembic", "--name", "main", "upgrade", "head"])
            .with_exec(
                [
                    "pytest",
                    *pytest_args,
                    "tests/acceptance_tests/functional",
                    "tests/acceptance_tests/non_functional",
                    "--ignore=tests/acceptance_tests/non_functional/locustfiles",
                ]
            )
        )

        return await test_container.stdout()

    @function
    async def test_performance(  # noqa: PLR0913
        self,
        source: TestSourceDir,
        *,
        baseline_image: Annotated[
            str,
            Doc(
                "Docker image to use as the performance baseline. "
                "Defaults to the latest published image."
            ),
        ] = _DEFAULT_BASELINE_IMAGE,
        users: Annotated[int, Doc("number of concurrent locust users")] = 10,
        spawn_rate: Annotated[
            int, Doc("rate at which locust users are spawned per second")
        ] = 2,
        run_time: Annotated[
            str, Doc("duration of each locust run (e.g. '30s', '1m')")
        ] = "30s",
        output_format: Annotated[
            str,
            Doc("output format for the comparison report ('terminal' or 'markdown')"),
        ] = OutputFormats.TERMINAL,
    ) -> str:
        """Runs comparative load tests between the current branch and a baseline image.

        Spins up two live environments: one built from the current source and one
        from the baseline Docker image. Runs the same locust scenario against both
        and returns a human-readable comparison of p50, p95, p99 latency and RPS.

        Args:
            source (TestSourceDir): The project source directory.
            baseline_image (str): Docker image to use as the performance baseline.
            users (int): Number of concurrent locust users.
            spawn_rate (int): Rate at which locust users are spawned (per second).
            run_time (str): Duration of each locust run (e.g. '30s', '1m').
            output_format (str): Output format for the comparison report.

        Returns:
            str: A human-readable comparison report of latency and RPS metrics.
        """
        current_db, current_api = self._live_environment(self.build_env(source))
        baseline_db, baseline_api = self._live_environment(
            dag.container().from_(baseline_image)
        )

        dev_env = self.build_env(source, development=True)

        locustfiles_path = Path(_LOCUSTFILES_PATH)
        stats_dir = f"{PROJECT_PATH}/locust_output"
        stats_file = f"{stats_dir}/stats_stats.csv"

        async def _run_locustfile(
            container: dagger.Container,
            db_service: dagger.Service,
            api_service: dagger.Service,
            locust_cmd_: list[str],
        ) -> str:
            return await (
                Utils.with_env_variables(
                    container, {"TEST_API_BASE_URL": "http://api:8000", **_DB_ENV_VARS}
                )
                .with_service_binding("main_db", db_service)
                .with_service_binding("api", api_service)
                .with_exec(["alembic", "--name", "main", "upgrade", "head"])
                .with_exec(["mkdir", "-p", stats_dir])
                .with_exec([*locust_cmd_, "--host=http://api:8000"])
                .file(stats_file)
                .contents()
            )

        results = []
        for scenario in ["normal_load.py", "heavy_load.py"]:
            locust_cmd = [
                "locust",
                "-f",
                str(locustfiles_path / scenario),
                "--headless",
                f"--users={users}",
                f"--spawn-rate={spawn_rate}",
                f"--run-time={run_time}",
                f"--csv={stats_dir}/stats",
            ]

            current_stats_csv = await _run_locustfile(
                dev_env, current_db, current_api, locust_cmd
            )
            baseline_stats_csv = await _run_locustfile(
                dev_env, baseline_db, baseline_api, locust_cmd
            )

            results.append(
                format_comparison(
                    current_stats_csv,
                    baseline_stats_csv,
                    baseline_image,
                    scenario,
                    OutputFormats(output_format),
                )
            )

        return "# Performance test results\n\n" + "\n\n".join(results)

    @function
    async def test(
        self,
        source: TestSourceDir,
        *,
        pytest_quiet: bool = False,
        pytest_randomly_seed: str | None = None,
    ) -> str:
        """Runs all levels tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.
            pytest_quiet (bool): Run tests with quiet output.
            pytest_randomly_seed (str | None): The seed for random test case ordering

        Returns:
            str: The output of the three pytest commands.
        """
        unit_tests_output = await self.test_unit(
            source, pytest_quiet=pytest_quiet, pytest_randomly_seed=pytest_randomly_seed
        )
        integration_tests_output = await self.test_integration(
            source, pytest_quiet=pytest_quiet, pytest_randomly_seed=pytest_randomly_seed
        )
        acceptance_tests_output = await self.test_acceptance(
            source, pytest_quiet=pytest_quiet, pytest_randomly_seed=pytest_randomly_seed
        )

        return "\n".join(
            [
                "Unit Tests Output:",
                unit_tests_output,
                "Integration Tests Output:",
                integration_tests_output,
                "Acceptance Tests Output:",
                acceptance_tests_output,
            ]
        )

    @function
    async def export_openapi_schema(self, source: SourceDir) -> dagger.Directory:
        """Exports the OpenAPI schema to a file.

        When calling this Dagger function ensure to specify the -o, --output option,
        otherwise the output will be lost as the directory is created
        inside the container.

        E.g. dagger call export-openapi-schema -o .

        Args:
            source (SourceDir): The project source directory.

        Returns:
            dagger.Directory: A directory containing the exported OpenAPI schema file.
        """
        openapi_schema_path = "./docs/openapi.yaml"
        openapi_schema_file = (
            await Utils.with_env_variables(
                self.build_env(source, development=True), DEFAULT_ENV_VARS
            )
            .with_workdir(PROJECT_PATH)
            .with_exec(
                [
                    "python",
                    "-c",
                    "from utils.openapi import export_schema; "
                    f"export_schema('{openapi_schema_path}')",
                ]
            )
            .file(openapi_schema_path)
        )
        return dag.directory().with_file(openapi_schema_path, openapi_schema_file)

    @function
    async def publish_docker_image(
        self,
        source: SourceDir,
        token: Annotated[dagger.Secret, Doc("registry token")],
        registry: Annotated[str, Doc("registry url")] = "ghcr.io",
        username: Annotated[str, Doc("registry username")] = "manuel-gallina",
        version: Annotated[
            str | None,
            Doc(
                "explicit version tag to publish (e.g. '1.2.0', no 'v' prefix); "
                "when omitted the version is read from pyproject.toml"
            ),
        ] = None,
    ) -> list[str]:
        """Publish the Docker image to the specified registry.

        Args:
            source (SourceDir): The project source directory.
            token (dagger.Secret): The registry token for authentication.
            registry (str): The registry URL where the image will be published.
            username (str): The registry username for authentication.
            version (str | None): Explicit version tag (no 'v' prefix). When
                provided it overrides the version read from pyproject.toml,
                decoupling the published tag from the file's static content.
                Defaults to None (read from pyproject.toml).

        Returns:
            list[str]: A list of published image tags.
        """
        # TODO(@manuel-gallina): username is used both for authentication
        #   and as part of the image path we should separate these two concepts
        #   and allow for a different image path or derive
        #   the image path from the username.
        #   https://github.com/manuel-gallina/Python.FastAPI.V01/issues/7
        if version is None:
            pyproject_toml = await source.file("pyproject.toml").contents()
            version = tomllib.loads(pyproject_toml)["project"]["version"]

        container_name = "python-fastapi-v01"
        container = (
            self.build_env(source)
            .with_env_variable("PROJECT__VERSION", version)
            .with_registry_auth(registry, username, token)
        )

        published_tags = []
        for tag in ["latest", version]:
            published_tags.append(
                await container.publish(f"{registry}/{username}/{container_name}:{tag}")
            )

        return published_tags

    @function
    async def lint(self, source: TestSourceDir) -> str:
        """Checks the code style using ruff.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the ruff command.
        """
        style_container = Utils.with_env_variables(
            self.build_env(source, development=True), DEFAULT_ENV_VARS
        ).with_exec(["ruff", "check", ".", "--exit-zero"])
        return await style_container.stdout()
