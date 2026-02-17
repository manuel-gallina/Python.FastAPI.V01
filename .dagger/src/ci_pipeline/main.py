import tomllib
from typing import Annotated

import dagger
from dagger import DefaultPath, Doc, Ignore, dag, function, object_type


@object_type
class PythonFastapiV01:
    PROJECT_PATH = "/project"
    BASE_IGNORES = [
        "**/.venv",
        "**/__pycache__",
        ".git",
        "**/.gitignore",
        ".idea",
        ".ruff_cache",
        ".env",
    ]

    SourceDir = Annotated[
        dagger.Directory,
        DefaultPath("."),
        Doc("The project source directory"),
        Ignore(BASE_IGNORES + ["tests/", ".pytest_cache"]),
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
        development: Annotated[bool, Doc("install development dependencies")] = False,
    ) -> dagger.Container:
        """
        Builds the container environment for the application.

        The build process is split into two stages: a builder stage where the dependencies are installed
        and a runner stage where the application code and the installed dependencies are combined
        to create the final container.

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
            .with_directory(self.PROJECT_PATH, source)
            .with_workdir(self.PROJECT_PATH)
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
            .with_directory(self.PROJECT_PATH, source)
            .with_workdir(self.PROJECT_PATH)
            .with_directory(venv_path, builder.directory(venv_path))
            .with_env_variable(
                "PATH", ":".join([f"{venv_path}/bin", "$PATH"]), expand=True
            )
            .with_env_variable(
                "PYTHONPATH",
                ":".join(
                    [self.PROJECT_PATH, f"{self.PROJECT_PATH}/src", "$PYTHONPATH"]
                ),
                expand=True,
            )
            .with_env_variable("VIRTUAL_ENV", venv_path)
        )
        if not development:
            runner = runner.with_env_variable("PYTHONOPTIMIZE", "1")

        return runner

    @function
    async def test_unit(self, source: TestSourceDir) -> str:
        """
        Runs the unit tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the pytest command.
        """
        return (
            await self.build_env(source, development=True)
            .with_exec(["pytest", "tests/unit_tests"])
            .stdout()
        )

    @function
    async def test_integration(self, source: TestSourceDir) -> str:
        """
        Runs the integration tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the pytest command.
        """
        return (
            await self.build_env(source, development=True)
            .with_exec(["pytest", "tests/integration_tests"])
            .stdout()
        )

    @function
    async def test_acceptance(self, source: TestSourceDir) -> str:
        """
        Runs the acceptance tests using pytest.

        Args:
            source (TestSourceDir): The project source directory.

        Returns:
            str: The output of the pytest command.
        """
        postgres_container = (
            dag.container()
            .from_("postgres:18")
            .with_env_variable("POSTGRES_USER", "admin")
            .with_env_variable("POSTGRES_PASSWORD", "admin")
            .with_env_variable("POSTGRES_DB", "python_fastapi_v01")
            .with_exposed_port(5432)
            .as_service()
        )

        async def build_api_container() -> dagger.Service:
            env = {"DATABASE__MAIN_CONNECTION__HOST": "db"}

            api_container_ = (
                await self.build_env(source)
                .with_service_binding("db", postgres_container)
                .with_exposed_port(8000)
            )

            for key, value in env.items():
                api_container_ = api_container_.with_env_variable(key, value)

            api_container_ = api_container_.with_entrypoint(
                ["fastapi", "run", "/project/src/main.py"]
            ).as_service()

            return api_container_

        api_container = await build_api_container()

        return (
            await self.build_env(source, development=True)
            .with_service_binding("db", postgres_container)
            .with_env_variable("DATABASE__MAIN_CONNECTION__HOST", "db")
            .with_service_binding("api", api_container)
            .with_env_variable("TEST_API_BASE_URL", "http://api:8000")
            .with_exec(["alembic", "--name", "main", "upgrade", "head"])
            .with_exec(["pytest", "-v", "tests/acceptance_tests"])
            .stdout()
        )

    @function
    async def test(self, source: TestSourceDir) -> str:
        """
        Runs all levels tests using pytest.

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
        """
        Exports the OpenAPI schema to a file.

        When calling this Dagger function ensure to specify the -o, --output option, otherwise the output will
        be lost as the directory is created inside the container.

        E.g. dagger call export-openapi-schema -o .

        Args:
            source (SourceDir): The project source directory.

        Returns:
            dagger.Directory: A directory containing the exported OpenAPI schema file.
        """
        openapi_schema_path = "./docs/openapi.yaml"
        openapi_schema_file = (
            await self.build_env(source, development=True)
            .with_workdir(self.PROJECT_PATH)
            .with_exec(
                [
                    "python",
                    "-c",
                    f"from utils.openapi import export_schema; export_schema('{openapi_schema_path}')",
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
    ) -> list[str]:
        """
        Publish the Docker image to the specified registry.

        Args:
            source (SourceDir): The project source directory.
            token (dagger.Secret): The registry token for authentication.
            registry (str): The registry URL where the image will be published.
            username (str): The registry username for authentication.

        Returns:
            list[str]: A list of published image tags.
        """
        # TODO: username is used both for authentication and as part of the image path
        #   we should separate these two concepts and allow for a different image path
        #   or derive the image path from the username.
        pyproject_toml = await source.file("pyproject.toml").contents()
        project_version = tomllib.loads(pyproject_toml)["project"]["version"]

        container_name = "python-fastapi-v01"
        container = self.build_env(source).with_registry_auth(registry, username, token)

        published_tags = []
        for tag in ["latest", project_version]:
            published_tags.append(
                await container.publish(f"{registry}/{username}/{container_name}:{tag}")
            )

        return published_tags
