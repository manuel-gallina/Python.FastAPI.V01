"""Query builder engine for PostgreSQL."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from datetime import datetime
from typing import Any, Self, override
from uuid import uuid4

from sqlalchemy import UUID, Column, DateTime, MetaData, String, Table, select, text
from sqlalchemy.orm import DeclarativeBase

WhereClause = str
OrderByClause = str


class Field:
    """A field that can be used in query building."""

    name: str
    definition: str
    transform: Callable[[Any], Any] | None
    cast: str | None

    def __init__(
        self,
        name: str,
        db_definition: str,
        transform: Callable[[Any], Any] | None = None,
        cast: str | None = None,
    ) -> None:
        """Initializes a Field instance.

        Args:
            name (str): The name of the field.
            db_definition (str): The database definition
                of the field (e.g., "users.name").
            transform (Callable[[Any], Any] | None): An optional function to transform
                the value before it's used in the query.
            cast (str | None): An optional SQL type to cast the value to in the query.
        """
        self.name = name
        self.definition = db_definition
        self.transform = transform
        self.cast = cast or ""


ScalarValue = str | int | float | bool | None
Value = ScalarValue | list[ScalarValue]


class Operator(ABC):
    """Represents a query operator that can be used in where clauses."""

    symbol: str

    def __init__(self, symbol: str) -> None:
        """Creates a new Operator instance.

        Args:
            symbol (str): The symbol representing the operator
                (e.g., "equal", "contains").
        """
        self.symbol = symbol

    @staticmethod
    def param(field: Field, params: dict[str, Any], value: Value) -> str:
        """Registers a parameter for the given value and returns its placeholder.

        Args:
            field (Field): The field for which the parameter is being registered.
            params (dict[str, Any]): The dictionary where the parameter
                will be registered.
            value (Value): The value of the parameter to be registered.

        Returns:
            str: The parameter placeholder to be used in the query.
        """
        param_name = f"{field.name}_{uuid4()}"

        if field.transform:
            params[param_name] = field.transform(value)
        else:
            params[param_name] = value

        if field.cast:
            return f"cast(:{param_name} as {field.cast})"
        return f":{param_name}"

    @abstractmethod
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        """Compiles the operator into a SQL expression for the given field and value.

        Args:
            field (Field): The field to which the operator is being applied.
            value (Value): The value to which the operator is being applied.
            params (dict[str, Any]): The dictionary where any parameters
                needed for the operator will be registered.

        Returns:
            str: The SQL expression representing the operator
                applied to the field and value.
        """
        raise NotImplementedError


class QueryBuilder:
    """A class for building SQL queries in a structured way."""

    with_: str | None
    select_: str
    from_: str
    where_: str | None
    group_by_: str | None
    order_by_: str | None

    fields_map: dict[str, Field]
    params: dict[str, Any]

    def __init__(
        self,
        select_: str,
        from_: str,
        with_: str | None = None,
        where_: str | None = None,
        group_by_: str | None = None,
        order_by_: str | None = None,
        fields_map: dict[str, Field] | None = None,
        params: dict[str, Any] | None = None,
    ) -> None:
        self.with_ = with_
        self.select_ = select_
        self.from_ = from_
        self.where_ = where_
        self.group_by_ = group_by_
        self.order_by_ = order_by_
        self.fields_map = fields_map or {}
        self.params = params or {}

    def build(self) -> str:
        raise NotImplementedError

    def count(self) -> Self:
        return QueryBuilder(
            select_="select count(*)",
            from_=self.from_,
            with_=self.with_,
            where_=self.where_,
            group_by_=self.group_by_,
            order_by_=None,
            fields_map=self.fields_map,
            params=self.params,
        )

    def where(self, where_: WhereClause | None) -> Self:
        raise NotImplementedError

    def order_by(self, order_by_: OrderByClause | None) -> Self:
        raise NotImplementedError

    def skip(self, skip: int | None) -> Self:
        raise NotImplementedError

    def limit(self, limit: int | None) -> Self:
        raise NotImplementedError

    def param(self, value: Any) -> str:
        raise NotImplementedError

    @staticmethod
    def build_where(where_: str) -> WhereClause:
        raise NotImplementedError

    @staticmethod
    def build_order_by(order_by_: str) -> OrderByClause:
        raise NotImplementedError


class Equal(Operator):
    def __init__(self) -> None:
        super().__init__("equal")

    @override
    def compile(self, field: Field, value: Any, params: dict[str, Any]) -> str:
        return f"{field.definition} = {self.param(field, params, value)}"


class BaseDbEntity(DeclarativeBase):
    __abstract__ = True

    id = Column(UUID, primary_key=True)


class User(BaseDbEntity):
    __tablename__ = "users"

    name = Column(String, nullable=False)


if __name__ == "__main__":
    print(
        select(User).where(
            User.name == "Alice", User.id == uuid4(), text("user.prova") == "test"
        )
    )
