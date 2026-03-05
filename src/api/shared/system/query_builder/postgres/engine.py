"""Query builder engine for PostgreSQL."""

from abc import ABC
from typing import Any, override

from api.shared.system.query_builder.shared.engine import (
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


class Equal(Operator):
    """Equality operator for query building."""

    @staticmethod
    def validate_value(value: Value) -> None:
        """Validates the value for the equality operator.

        Args:
            value (Value): The value to validate.
        """
        if isinstance(value, list):
            detail = f"Expected a non-list value, got {type(value).__name__}."
            raise ValueError(detail)

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        self.validate_value(value)
        return f"{field.definition} = {self.param(field, params, value)}"


class IEqual(Operator):
    """Case-insensitive equality operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Equal.validate_value(value)
        return f"lower({field.definition}) = lower({self.param(field, params, value)})"


class NotEqual(Operator):
    """Inequality operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Equal.validate_value(value)
        return f"{field.definition} is distinct from {self.param(field, params, value)}"


class INotEqual(Operator):
    """Case-insensitive inequality operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Equal.validate_value(value)
        return (
            f"lower({field.definition}) "
            f"is distinct from "
            f"lower({self.param(field, params, value)})"
        )


class Like(Operator):
    """LIKE operator for query building."""

    @staticmethod
    def validate_value(value: Value) -> None:
        """Validates the value for the LIKE operator.

        Args:
            value (Value): The value to validate.
        """
        if not isinstance(value, str):
            detail = f"Expected a string value, got {type(value).__name__}."
            raise ValueError(detail)

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        self.validate_value(value)
        return f"{field.definition} like {self.param(field, params, value)}"


class ILike(Operator):
    """Case-insensitive LIKE operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Like.validate_value(value)
        return f"{field.definition} ilike {self.param(field, params, value)}"


class StartsWith(Operator):
    """Starts with operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        return Like().compile(field, f"{value}%", params)


class IStartsWith(Operator):
    """Case-insensitive starts with operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        return ILike().compile(field, f"{value}%", params)


class EndsWith(Operator):
    """Ends with operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        return Like().compile(field, f"%{value}", params)


class IEndsWith(Operator):
    """Case-insensitive ends with operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        return ILike().compile(field, f"%{value}", params)


class Contains(Operator):
    """Containment operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        return Like().compile(field, f"%{value}%", params)


class IContains(Operator):
    """Case-insensitive containment operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        return ILike().compile(field, f"%{value}%", params)


class GreaterThan(Operator):
    """Greater than operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Equal.validate_value(value)
        return f"{field.definition} > {self.param(field, params, value)}"


class GreaterThanOrEqual(Operator):
    """Greater than or equal operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Equal.validate_value(value)
        return f"{field.definition} >= {self.param(field, params, value)}"


class LessThan(Operator):
    """Less than operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Equal.validate_value(value)
        return f"{field.definition} < {self.param(field, params, value)}"


class LessThanOrEqual(Operator):
    """Less than or equal operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        Equal.validate_value(value)
        return f"{field.definition} <= {self.param(field, params, value)}"


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
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        self.validate_value(value)
        return f"{field.definition} is null"


class IsNotNull(Operator):
    """IS NOT NULL operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        IsNull.validate_value(value)
        return f"{field.definition} is not null"


class IsEmpty(Operator):
    """IS EMPTY operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        IsNull.validate_value(value)
        return Equal().compile(field, "", params)


class IsNotEmpty(Operator):
    """IS NOT EMPTY operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        IsNull.validate_value(value)
        return NotEqual().compile(field, "", params)


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
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        self.validate_value(value)
        param_names = [self.param(field, params, v) for v in value]
        return f"{field.definition} in ({', '.join(param_names)})"


class NotIn(Operator):
    """NOT IN operator for query building."""

    @override
    def compile(self, field: Field, value: Value, params: dict[str, Any]) -> str:
        In.validate_value(value)
        param_names = [self.param(field, params, v) for v in value]
        return f"{field.definition} not in ({', '.join(param_names)})"


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
            },
            pagination_limit_config,
        )
