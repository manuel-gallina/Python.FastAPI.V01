import yaml

from main import app


def export_schema(dst: str) -> None:
    """
    Export the OpenAPI schema of the FastAPI application to a YAML file.

    Args:
        dst (str): The destination file path where the OpenAPI schema will be saved.

    Returns:

    """
    openapi_schema = app.openapi()
    openapi_schema["info"]["x-logo"] = {"url": "./logo/logo.png", "altText": "Logo"}
    with open(dst, "w") as f:
        yaml.dump(openapi_schema, f, sort_keys=False)
