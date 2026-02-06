from typing import Annotated

import dagger
from dagger import DefaultPath, Doc, dag, function, object_type


@object_type
class PythonFastapiV01:
    @function
    async def test(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("source directory")],
    ) -> str:
        return await self.build_env(source).with_exec(["uv", "run", "pytest"]).stdout()

    @function
    def build_env(
        self,
        source: Annotated[dagger.Directory, DefaultPath("/"), Doc("source directory")],
    ) -> dagger.Container:
        uv_bin = dag.container().from_("ghcr.io/astral-sh/uv:0.10.0").file("/uv")
        return (
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
            .with_file("/usr/local/bin/uv", uv_bin)
            .with_directory("/project", source)
            .with_workdir("/project")
            .with_exec(["uv", "sync"])
        )
