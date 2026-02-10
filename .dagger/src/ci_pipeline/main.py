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
        venv_path = "/venv"
        uv_bin = dag.container().from_("ghcr.io/astral-sh/uv:0.10.0").file("/uv")
        uv_path = "/usr/local/bin/uv"

        # Builder container
        builder = (
            dag.container()
            .from_("python:3.13-slim")
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
        sync_cmd = ["uv", "sync"]
        if not development:
            sync_cmd.append("--no-dev")
        builder = builder.with_exec(sync_cmd)

        # Final container
        runner = (
            dag.container()
            .from_("python:3.13-slim")
            .with_directory(self.PROJECT_PATH, source)
            .with_workdir(self.PROJECT_PATH)
            .with_directory(venv_path, builder.directory(venv_path))
            .with_env_variable(
                "PATH", ":".join([f"{venv_path}/bin", "$PATH"]), expand=True
            )
            .with_env_variable("VIRTUAL_ENV", venv_path)
        )
        if not development:
            runner = runner.with_env_variable("PYTHONOPTIMIZE", "1")

        return runner

    @function
    async def test(self, source: TestSourceDir) -> str:
        return (
            await self.build_env(source, development=True)
            .with_exec(["pytest"])
            .stdout()
        )

    @function
    async def export_openapi_schema(self, source: SourceDir) -> dagger.File:
        openapi_schema_file = (
            await self.build_env(source, development=True)
            .with_workdir(f"{self.PROJECT_PATH}/src")
            .with_exec(
                [
                    "python",
                    "-c",
                    "from utils.openapi import export_schema; export_schema('../docs/openapi.yaml')",
                ]
            )
            .with_workdir(self.PROJECT_PATH)
            .file("docs/openapi.yaml")
        )

        await openapi_schema_file.export("docs/openapi.yaml")

        return openapi_schema_file

    @function
    async def publish(
        self,
        source: SourceDir,
        token: Annotated[dagger.Secret, Doc("registry token")],
        registry: Annotated[str, Doc("registry url")] = "ghcr.io",
        username: Annotated[str, Doc("registry username")] = "manuel-gallina",
    ) -> list[str]:
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
