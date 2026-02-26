"""CI pipeline for the Python FastAPI project.

This module defines a Dagger CI pipeline for the project.
"""

import tomllib
from typing import Annotated

import dagger
from dagger import DefaultPath, Doc, Ignore, dag, function, object_type


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

    @function
    async def test_unit(self, source: TestSourceDir) -> str:
        """Runs the unit tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the pytest command.
        """
        test_container = Utils.with_env_variables(
            self.build_env(source, development=True), DEFAULT_ENV_VARS
        ).with_exec(["pytest", "tests/unit_tests"])
        return await test_container.stdout()

    @function
    async def test_integration(self, source: TestSourceDir) -> str:
        """Runs the integration tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the pytest command.
        """
        test_container = Utils.with_env_variables(
            self.build_env(source, development=True), DEFAULT_ENV_VARS
        ).with_exec(["pytest", "tests/integration_tests"])
        return await test_container.stdout()

    @function
    async def test_acceptance(self, source: TestSourceDir) -> str:
        """Runs the acceptance tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the pytest command.
        """
        main_db_container = (
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

        api_container = (
            Utils.with_env_variables(
                self.build_env(source),
                {
                    "DATABASE__MAIN_CONNECTION__DBMS": "postgresql",
                    "DATABASE__MAIN_CONNECTION__DRIVER": "asyncpg",
                    "DATABASE__MAIN_CONNECTION__HOST": "main_db",
                    "DATABASE__MAIN_CONNECTION__PORT": "5432",
                    "DATABASE__MAIN_CONNECTION__USER": "admin",
                    "DATABASE__MAIN_CONNECTION__PASSWORD": "admin",
                    "DATABASE__MAIN_CONNECTION__NAME": "python_fastapi_v01",
                },
            )
            .with_service_binding("main_db", main_db_container)
            .with_exposed_port(8000)
            .with_entrypoint(["fastapi", "run", "/project/src/main.py"])
            .as_service()
        )

        test_container = (
            Utils.with_env_variables(
                self.build_env(source, development=True),
                {
                    "TEST_API_BASE_URL": "http://api:8000",
                    "DATABASE__MAIN_CONNECTION__DBMS": "postgresql",
                    "DATABASE__MAIN_CONNECTION__DRIVER": "asyncpg",
                    "DATABASE__MAIN_CONNECTION__HOST": "main_db",
                    "DATABASE__MAIN_CONNECTION__PORT": "5432",
                    "DATABASE__MAIN_CONNECTION__USER": "admin",
                    "DATABASE__MAIN_CONNECTION__PASSWORD": "admin",
                    "DATABASE__MAIN_CONNECTION__NAME": "python_fastapi_v01",
                },
            )
            .with_service_binding("main_db", main_db_container)
            .with_service_binding("api", api_container)
            .with_exec(["alembic", "--name", "main", "upgrade", "head"])
            .with_exec(["pytest", "-v", "tests/acceptance_tests"])
        )

        return await test_container.stdout()

    @function
    async def test(self, source: TestSourceDir) -> str:
        """Runs all levels tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the three pytest commands.
        """
        unit_tests_output = await self.test_unit(source)
        integration_tests_output = await self.test_integration(source)
        acceptance_tests_output = await self.test_acceptance(source)

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
        container = self.build_env(source).with_registry_auth(registry, username, token)

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
