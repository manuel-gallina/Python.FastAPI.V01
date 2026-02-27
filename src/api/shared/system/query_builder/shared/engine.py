"""Query builder engine for PostgreSQL."""

from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import StrEnum, auto
from typing import Any, Self
from uuid import uuid4

from pydantic import BaseModel

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
        self.cast = cast


ScalarValue = str | int | float | bool | None
Value = ScalarValue | list[ScalarValue]


class IOperator(ABC):
    """Represents a query operator that can be used in where clauses."""

    @staticmethod
    @abstractmethod
    def cast(param_name: str, cast_type: str) -> str:
        """Applies a cast to a parameter in the SQL query.

        Args:
            param_name (str): The name of the parameter to be cast.
            cast_type (str): The SQL type to cast the parameter to.

        Returns:
            str: The SQL expression representing the cast parameter.
        """
        raise NotImplementedError

    @classmethod
    def param(cls, field: Field, params: dict[str, Any], value: Value) -> str:
        """Registers a parameter for the given value and returns its placeholder.

        Args:
            field (Field): The field for which the parameter is being registered.
            params (dict[str, Any]): The dictionary where the parameter
                will be registered.
            value (Value): The value of the parameter to be registered.

        Returns:
            str: The parameter placeholder to be used in the query.
        """
        param_name = f"{field.name}_{uuid4().hex}"

        if field.transform:
            params[param_name] = field.transform(value)
        else:
            params[param_name] = value

        if field.cast:
            return cls.cast(param_name, field.cast)
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


class Operators(StrEnum):
    """Supported query operators."""

    EQUAL = auto()


class Conditions(StrEnum):
    """Supported query conditions."""

    AND = auto()
    OR = auto()


class Directions(StrEnum):
    """Supported order by directions."""

    ASC = auto()
    DESC = auto()


class SimpleWhereRule(BaseModel):
    """Represents a simple where rule in the query builder."""

    field: str
    operator: str
    value: Value


class ComplexWhereRule(BaseModel):
    """Represents a complex where rule with conditions in the query builder."""

    condition: str = Conditions.AND
    rules: "list[SimpleWhereRule | ComplexWhereRule]"


class OrderByRule(BaseModel):
    """Represents an order by rule in the query builder."""

    field: str
    direction: str = Directions.ASC


class IQueryBuilder:
    """Utilities for building SQL queries."""

    fields: dict[str, Field]
    operators: dict[str, IOperator]

    def __init__(
        self, fields: dict[str, Field], operators: dict[str, IOperator]
    ) -> None:
        """Initializes a QueryBuilder instance.

        Args:
            fields (dict[str, Field]): A dictionary mapping field names
                to Field instances.
            operators (dict[str, IOperator]): A dictionary mapping operator
                names to Operator instances.
        """
        self.fields = {name.lower(): field for name, field in fields.items()}
        self.operators = {
            name.lower(): operator for name, operator in operators.items()
        }

    def __call__(self) -> Self:
        """Get a new instance with predefined fields.

        Returns:
            Self: A new instance of QueryBuilder with the same fields.
        """
        return self

    def build_where(
        self, where_: dict[str, Any] | None, params: dict[str, Any] | None = None
    ) -> tuple[WhereClause, dict[str, Any]]:
        """Builds a WHERE clause from the given where structure and parameters.

        Args:
            where_ (dict[str, Any] | None): The structure representing the where clause.
            params (dict[str, Any] | None): The dictionary where any parameters needed
                for the where clause will be registered.

        Returns:
            tuple[WhereClause, dict[str, Any]]: A tuple containing the compiled
                WHERE clause and the dictionary of parameters.
        """
        params = params or {}

        if not where_:
            return "1=1", params

        if "field" in where_:
            rule = SimpleWhereRule(**where_)

            if rule.operator.lower() not in self.operators:
                error = f"Unsupported operator: {rule.operator}."
                raise ValueError(error)
            operator = self.operators[rule.operator.lower()]

            if rule.field.lower() not in self.fields:
                error = f"Unknown field: {rule.field}."
                raise ValueError(error)
            field = self.fields[rule.field.lower()]

            compiled_rule = operator.compile(field, rule.value, params)
            return compiled_rule, params

        if "condition" in where_:
            rule = ComplexWhereRule(**where_)

            if rule.condition.lower() not in Conditions:
                error = f"Unsupported condition: {rule.condition}."
                raise ValueError(error)

            compiled_rules = []
            for sub_rule in rule.rules:
                compiled_sub_rule, params = self.build_where(
                    sub_rule.model_dump(), params
                )
                compiled_rules.append(f"({compiled_sub_rule})")

            condition_str = f" {rule.condition.lower()} ".join(compiled_rules)
            return condition_str, params

        error = (
            "Invalid where clause structure: expected either a simple "
            "rule with 'field' or a condition with 'condition'."
        )
        raise ValueError(error)

    def build_order_by(self, order_by_: list[dict[str, str]]) -> OrderByClause:
        """Builds an ORDER BY clause from the given order by structure.

        Args:
            order_by_ (list[dict[str, str]]): The structure representing
                the order by clause.

        Returns:
            OrderByClause: The compiled ORDER BY clause.
        """
        order_by_clauses = []
        for order in order_by_:
            rule = OrderByRule(**order)

            if rule.direction.lower() not in Directions:
                error = f"Unsupported order by direction: {rule.direction}."
                raise ValueError(error)

            if rule.field.lower() not in self.fields:
                error = f"Unknown field: {rule.field}."
                raise ValueError(error)
            field = self.fields[rule.field.lower()]

            order_by_clauses.append(f"{field.definition} {rule.direction.lower()}")

        return ", ".join(order_by_clauses)
