"""Query builder engine for PostgreSQL."""

import json
from abc import ABC, abstractmethod
from collections.abc import Callable
from enum import StrEnum, auto
from typing import Annotated, Any
from uuid import uuid4

import pydantic
from fastapi import Depends, Query, status
from pydantic import AliasChoices, BaseModel

from api.shared.schemas.errors import ApiError, UnprocessableContentErrorSchema
from api.shared.system.request_tracing import get_request_id

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


class QueryBuilderCompiledParams(BaseModel):
    """The result of compiling query builder parameters."""

    where: WhereClause
    order_by: OrderByClause
    skip: int
    limit: int
    sql_params: dict[str, Any]


class QueryBuilderParams(BaseModel):
    """The parameters for building a query."""

    filters: Annotated[
        str | None, pydantic.Field(validation_alias=AliasChoices("filters", "where"))
    ] = None
    sort: Annotated[
        str | None, pydantic.Field(validation_alias=AliasChoices("sort", "orderBy"))
    ] = None
    skip: int | None = None
    limit: int | None = None


class PaginationLimitConfig(BaseModel):
    """Configuration for pagination limit query parameter."""

    default: int
    max: int


QUERY_BUILDER_ERROR_MESSAGE = "Query builder error."


class IQueryBuilder:
    """Utilities for building SQL queries."""

    fields: dict[str, Field]
    operators: dict[str, IOperator]
    pagination_limit_config: PaginationLimitConfig

    def __init__(
        self,
        fields: list[Field],
        operators: dict[str, IOperator],
        pagination_limit_config: PaginationLimitConfig | None = None,
    ) -> None:
        """Initializes a QueryBuilder instance.

        Args:
            fields (list[Field]): A list of Field instances that
                can be used in the query builder.
            operators (dict[str, IOperator]): A dictionary mapping operator
                names to Operator instances.
            pagination_limit_config (PaginationLimitConfig | None): The configuration
                for the pagination limit query parameter.
        """
        self.fields = {field.name.lower(): field for field in fields}
        self.operators = {
            name.lower(): operator for name, operator in operators.items()
        }
        self.pagination_limit_config = pagination_limit_config or PaginationLimitConfig(
            default=100, max=500
        )

    def get_compiled_params(
        self,
        request_params: Annotated[QueryBuilderParams, Query()],
        request_id: Annotated[str, Depends(get_request_id)],
    ) -> QueryBuilderCompiledParams:
        """Compiles the query builder parameters into SQL clauses and parameters.

        Args:
            request_params (QueryBuilderParams): The query builder parameters
                extracted from the request.
            request_id (str): The unique ID of the request
                for tracing purposes.

        Returns:
            QueryBuilderCompiledParams: The compiled query parameters including
                the WHERE clause, ORDER BY clause, skip, limit,
                and the dictionary of SQL parameters.

        Raises:
            ApiError: If any of the query parameters are invalid,
                such as unknown fields, unsupported operators,
                or if the limit exceeds the maximum allowed.
        """
        raw_where: dict[str, Any] | None = None
        if request_params.filters is not None:
            try:
                raw_where = json.loads(request_params.filters)
            except json.JSONDecodeError as e:
                detail = (
                    "Invalid 'filters' query parameter. Must be a valid JSON string."
                )
                raise ApiError(
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                    UnprocessableContentErrorSchema(
                        request_id=request_id,
                        message=QUERY_BUILDER_ERROR_MESSAGE,
                        detail=detail,
                    ),
                ) from e
        where, params = self.build_where(raw_where, request_id)

        raw_order_by: list[dict[str, str]] | None = None
        if request_params.sort is not None:
            try:
                raw_order_by = json.loads(request_params.sort)
            except json.JSONDecodeError as e:
                detail = "Invalid 'sort' query parameter. Must be a valid JSON string."
                raise ApiError(
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                    UnprocessableContentErrorSchema(
                        request_id=request_id,
                        message=QUERY_BUILDER_ERROR_MESSAGE,
                        detail=detail,
                    ),
                ) from e
        order_by = self.build_order_by(raw_order_by, request_id)

        skip = request_params.skip or 0

        limit = request_params.limit or self.pagination_limit_config.default
        if limit > self.pagination_limit_config.max:
            detail = (
                f"Limit cannot exceed {self.pagination_limit_config.max}. "
                f"Received: {limit}."
            )
            raise ApiError(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                UnprocessableContentErrorSchema(
                    request_id=request_id,
                    message=QUERY_BUILDER_ERROR_MESSAGE,
                    detail=detail,
                ),
            )
        return QueryBuilderCompiledParams(
            where=where, order_by=order_by, skip=skip, limit=limit, sql_params=params
        )

    def build_where(
        self, where: dict[str, Any] | None, request_id: str = "N/A"
    ) -> tuple[WhereClause, dict[str, Any]]:
        """Builds a WHERE clause from the given where structure and parameters.

        The default filter is "1=1" if no where clause is provided,
        which effectively means no filtering.

        Args:
            where (dict[str, Any] | None): The structure representing the where clause.
            request_id (str): The unique ID of the request for tracing purposes.

        Returns:
            tuple[WhereClause, dict[str, Any]]: A tuple containing the compiled
                WHERE clause and the dictionary of parameters.

        Raises:
            ApiError: If the where clause structure or syntax are invalid,
                or it contains unknown fields or unsupported operators/conditions.
        """

        def _build_where(
            where_: dict[str, Any] | None, params: dict[str, Any] | None = None
        ) -> tuple[WhereClause, dict[str, Any]]:
            try:
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
                        compiled_sub_rule, params = _build_where(
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
            except ValueError as e:
                detail = str(e)
                raise ApiError(
                    status.HTTP_422_UNPROCESSABLE_CONTENT,
                    UnprocessableContentErrorSchema(
                        request_id=request_id,
                        message=QUERY_BUILDER_ERROR_MESSAGE,
                        detail=detail,
                    ),
                ) from e

        return _build_where(where)

    def build_order_by(
        self, order_by_: list[dict[str, str]] | None, request_id: str = "N/A"
    ) -> OrderByClause:
        """Builds an ORDER BY clause from the given order by structure.

        The default order by clause is "1=1" if no order by rules are provided,
        which effectively means no ordering.

        Args:
            order_by_ (list[dict[str, str]] | None): The structure representing
                the order by clause.
            request_id (str): The unique ID of the request for tracing purposes.

        Returns:
            OrderByClause: The compiled ORDER BY clause.

        Raises:
            ApiError: If the order by structure is invalid, or it contains
                unknown fields or unsupported directions.
        """
        try:
            if not order_by_:
                return "1=1"

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
        except ValueError as e:
            detail = str(e)
            raise ApiError(
                status.HTTP_422_UNPROCESSABLE_CONTENT,
                UnprocessableContentErrorSchema(
                    request_id=request_id,
                    message=QUERY_BUILDER_ERROR_MESSAGE,
                    detail=detail,
                ),
            ) from e
