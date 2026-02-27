"""Query builder engine for PostgreSQL."""

from abc import ABC
from typing import Any, override

from api.shared.system.query_builder.shared.engine import (
    Field,
    IOperator,
    IQueryBuilder,
    Operators,
)


class Operator(IOperator, ABC):
    """A PostgreSQL query operator that can be used in where clauses."""

    @override
    @staticmethod
    def cast(param_name: str, cast_type: str) -> str:
        return f"cast(:{param_name} as {cast_type})"


class Equal(Operator):
    """Equality operator for query building."""

    @override
    def compile(self, field: Field, value: Any, params: dict[str, Any]) -> str:
        return f"{field.definition} = {self.param(field, params, value)}"


class QueryBuilder(IQueryBuilder):
    """Utilities for building PostgreSQL queries."""

    def __init__(self, fields: list[Field]) -> None:
        """Initializes a QueryBuilder instance.

        Args:
            fields (list[Field]): A list of Field instances that
                can be used in the query builder.
        """
        super().__init__(fields, {Operators.EQUAL: Equal()})
