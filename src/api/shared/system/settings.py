from anyio.functools import lru_cache
from pydantic import BaseModel, SecretStr
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)


class DatabaseConnection(BaseModel):
    """Database connection settings."""

    dbms: str
    driver: str
    host: str
    port: int
    user: str
    password: SecretStr
    name: str

    pool_pre_ping: bool = True
    pool_size: int = 20
    max_overflow: int = -1

    @property
    def url(self) -> str:
        """The database connection string."""
        return (
            f"{self.dbms}"
            f"+{self.driver}"
            f"://{self.user}"
            f":{self.password.get_secret_value()}"
            f"@{self.host}"
            f":{self.port}"
            f"/{self.name}"
        )


class DatabaseSettings(BaseModel):
    """Database settings."""

    main_connection: DatabaseConnection | None = None


class ProjectSettings(BaseModel):
    """
    Project settings.

    This is intended to be loaded from the pyproject.toml file.
    """

    name: str
    title: str
    version: str
    description: str


class Settings(BaseSettings):
    """Application settings."""

    project: ProjectSettings
    database: DatabaseSettings
    timezone: str = "Europe/Rome"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        toml_file="pyproject.toml",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
            TomlConfigSettingsSource(settings_cls),
        )


@lru_cache
def get_settings() -> Settings:
    """Get the application settings."""
    # Pydantic's BaseSettings does not support type hints for the constructor,
    # but it is valid to call it without arguments.
    # noinspection PyArgumentList
    return Settings()
