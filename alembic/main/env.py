from sqlalchemy import create_engine

from alembic import context
from src.api.shared.system.settings import get_settings

settings = get_settings()

# Alembic requires a synchronous driver, but the application uses an asynchronous one
settings.database.main_connection.driver = "psycopg"

connectable = create_engine(url=settings.database.main_connection.url)

with connectable.connect() as connection:
    context.configure(connection=connection)

    with context.begin_transaction():
        context.run_migrations()
