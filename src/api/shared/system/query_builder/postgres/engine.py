"""Query builder engine for PostgreSQL."""

from abc import ABC
from typing import Any, override

from api.shared.system.query_builder.shared.engine import (
    SUBQUERY_WHERE,
    Field,
    IOperator,
    IQueryBuilder,
    Operators,
    PaginationLimitConfig,
    Value,
)


class Operator(IOperator, ABC):
    """A PostgreSQL query operator that can be used in where clauses."""

    @override
    @staticmethod
    def cast(param_name: str, cast_type: str) -> str:
        return f"cast(:{param_name} as {cast_type})"


class ScalarComparisonOperator(Operator, ABC):
    """A base class for scalar comparison operators in PostgreSQL query building."""

    _symbol: str

    @staticmethod
    def validate_value(value: Value) -> None:
        """Validates the value for the equality operator.

        Args:
            value (Value): The value to validate.
        """
        if isinstance(value, (list, dict)):
            detail = f"Expected a scalar value, got {type(value).__name__}."
            raise ValueError(detail)

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        self.validate_value(value)
        return (
            f"{field.definition}"
            f" {self._symbol} "
            f"{self.sql_param(field, sql_params, value)}"
        )


class Equal(ScalarComparisonOperator):
    """Equality operator for query building."""

    _symbol = "="


class NotEqual(ScalarComparisonOperator):
    """Inequality operator for query building."""

    _symbol = "is distinct from"


class GreaterThan(ScalarComparisonOperator):
    """Greater than operator for query building."""

    _symbol = ">"


class GreaterThanOrEqual(ScalarComparisonOperator):
    """Greater than or equal operator for query building."""

    _symbol = ">="


class LessThan(ScalarComparisonOperator):
    """Less than operator for query building."""

    _symbol = "<"


class LessThanOrEqual(ScalarComparisonOperator):
    """Less than or equal operator for query building."""

    _symbol = "<="


class IEqual(Operator):
    """Case-insensitive equality operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        ScalarComparisonOperator.validate_value(value)
        return (
            f"lower({field.definition})"
            f" = "
            f"lower({self.sql_param(field, sql_params, value)})"
        )


class INotEqual(Operator):
    """Case-insensitive inequality operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        ScalarComparisonOperator.validate_value(value)
        return (
            f"lower({field.definition}) "
            f"is distinct from "
            f"lower({self.sql_param(field, sql_params, value)})"
        )


class Like(Operator):
    """LIKE operator for query building."""

    @staticmethod
    def validate_value(value: Value) -> None:
        """Validates the value for the LIKE operator.

        Args:
            value (Value): The value to validate.
        """
        if value is not None and not isinstance(value, str):
            detail = f"Expected a string value, got {type(value).__name__}."
            raise ValueError(detail)

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        self.validate_value(value)
        return f"{field.definition} like {self.sql_param(field, sql_params, value)}"


class ILike(Operator):
    """Case-insensitive LIKE operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        Like.validate_value(value)
        return f"{field.definition} ilike {self.sql_param(field, sql_params, value)}"


class StartsWith(Operator):
    """Starts with operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        return Like().compile(
            field, f"{value}%" if value is not None else None, sql_params, query_builder
        )


class IStartsWith(Operator):
    """Case-insensitive starts with operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        return ILike().compile(
            field, f"{value}%" if value is not None else None, sql_params, query_builder
        )


class EndsWith(Operator):
    """Ends with operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        return Like().compile(
            field, f"%{value}" if value is not None else None, sql_params, query_builder
        )


class IEndsWith(Operator):
    """Case-insensitive ends with operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        return ILike().compile(
            field, f"%{value}" if value is not None else None, sql_params, query_builder
        )


class Contains(Operator):
    """Containment operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        return Like().compile(
            field,
            f"%{value}%" if value is not None else None,
            sql_params,
            query_builder,
        )


class IContains(Operator):
    """Case-insensitive containment operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        return ILike().compile(
            field,
            f"%{value}%" if value is not None else None,
            sql_params,
            query_builder,
        )


class IsNull(Operator):
    """IS NULL operator for query building."""

    @staticmethod
    def validate_value(value: Value) -> None:
        """Validates the value for the IS NULL operator.

        Args:
            value (Value): The value to validate.
        """
        if value is not None:
            detail = f"Expected value to be null, got {type(value).__name__}."
            raise ValueError(detail)

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        self.validate_value(value)
        return f"{field.definition} is null"


class IsNotNull(Operator):
    """IS NOT NULL operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        IsNull.validate_value(value)
        return f"{field.definition} is not null"


class IsEmpty(Operator):
    """IS EMPTY operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        IsNull.validate_value(value)
        return Equal().compile(field, "", sql_params, query_builder)


class IsNotEmpty(Operator):
    """IS NOT EMPTY operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        IsNull.validate_value(value)
        return NotEqual().compile(field, "", sql_params, query_builder)


class In(Operator):
    """IN operator for query building."""

    @staticmethod
    def validate_value(value: Value) -> None:
        """Validates the value for the IN operator.

        Args:
            value (Value): The value to validate.
        """
        if not isinstance(value, list):
            detail = f"Expected a list of values, got {type(value).__name__}."
            raise ValueError(detail)

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        self.validate_value(value)
        param_names = [self.sql_param(field, sql_params, v) for v in value]
        return f"{field.definition} in ({', '.join(param_names)})"


class NotIn(Operator):
    """NOT IN operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        In.validate_value(value)
        param_names = [self.sql_param(field, sql_params, v) for v in value]
        return f"{field.definition} not in ({', '.join(param_names)})"


class Any_(Operator):  # noqa: N801
    """ANY operator for query building."""

    @staticmethod
    def validate_value(value: Value) -> None:
        """Validates the value for the ANY operator.

        Args:
            value (Value): The value to validate.
        """
        if not isinstance(value, dict):
            detail = f"Expected a subquery (dict) value, got {type(value).__name__}."
            raise ValueError(detail)

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        self.validate_value(value)
        subquery_where, subquery_sql_params = query_builder.build_where(
            value, request_id
        )
        sql_params.update(subquery_sql_params)
        subquery = field.definition.replace(
            SUBQUERY_WHERE, subquery_where
        )
        return f"exists ({subquery})"


class All_(Operator):  # noqa: N801
    """ALL operator for query building."""

    @override
    def compile(
        self,
        field: Field,
        value: Value,
        sql_params: dict[str, Any],
        query_builder: IQueryBuilder,
        request_id: str = "N/A",
    ) -> str:
        Any_.validate_value(value)
        subquery_where, subquery_sql_params = query_builder.build_where(
            value, request_id
        )
        sql_params.update(subquery_sql_params)
        subquery = field.definition.replace(
            SUBQUERY_WHERE, f"not ({subquery_where})"
        )
        return f"not exists ({subquery})"


class QueryBuilder(IQueryBuilder):
    """Utilities for building PostgreSQL queries."""

    def __init__(
        self,
        fields: list[Field],
        pagination_limit_config: PaginationLimitConfig | None = None,
    ) -> None:
        """Initializes a QueryBuilder instance.

        Args:
            fields (list[Field]): A list of Field instances that
                can be used in the query builder.
            pagination_limit_config (PaginationLimitConfig | None): The configuration
                for the pagination limit query parameter.
        """
        super().__init__(
            fields,
            {
                Operators.EQUAL: Equal(),
                Operators.I_EQUAL: IEqual(),
                Operators.NOT_EQUAL: NotEqual(),
                Operators.I_NOT_EQUAL: INotEqual(),
                Operators.LIKE: Like(),
                Operators.I_LIKE: ILike(),
                Operators.STARTS_WITH: StartsWith(),
                Operators.I_STARTS_WITH: IStartsWith(),
                Operators.ENDS_WITH: EndsWith(),
                Operators.I_ENDS_WITH: IEndsWith(),
                Operators.CONTAINS: Contains(),
                Operators.I_CONTAINS: IContains(),
                Operators.GREATER_THAN: GreaterThan(),
                Operators.GREATER_THAN_OR_EQUAL: GreaterThanOrEqual(),
                Operators.LESS_THAN: LessThan(),
                Operators.LESS_THAN_OR_EQUAL: LessThanOrEqual(),
                Operators.IS_NULL: IsNull(),
                Operators.IS_NOT_NULL: IsNotNull(),
                Operators.IS_EMPTY: IsEmpty(),
                Operators.IS_NOT_EMPTY: IsNotEmpty(),
                Operators.IN: In(),
                Operators.NOT_IN: NotIn(),
                Operators.ANY: Any_(),
                Operators.ALL: All_(),
            },
            pagination_limit_config,
        )
