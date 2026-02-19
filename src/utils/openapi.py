"""Utility functions for handling OpenAPI schema generation and export."""

from pathlib import Path

import yaml

from main import app


def export_schema(dst: str | Path) -> None:
    """Export the OpenAPI schema of the FastAPI application to a YAML file.

    Args:
        dst (str | Path): The destination file path where
            the OpenAPI schema will be saved.
    """
    openapi_schema = app.openapi()
    openapi_schema["info"]["x-logo"] = {"url": "./logo/logo.png", "altText": "Logo"}
    openapi_schema_file = Path(dst)
    openapi_schema_file.write_text(
        yaml.dump(openapi_schema, None, sort_keys=False),
        encoding="utf-8",
        newline="\r\n",
    )
