from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def execute_queries(db_engine: AsyncEngine, queries: list[str]) -> None:
    """
    Executes the given list of queries using the provided database engine
    and commits the transaction after all queries have been executed.

    Args:
        db_engine (AsyncEngine): The asynchronous database engine to use for executing the queries.
        queries (list[str]): A list of SQL query strings to be executed.
    """
    async with db_engine.connect() as connection:
        async with connection.begin() as transaction:
            for query in queries:
                await connection.execute(text(query))
            await transaction.commit()
