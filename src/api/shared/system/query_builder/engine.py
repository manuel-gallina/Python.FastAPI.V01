from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any, Self, override

WhereClause = str
OrderByClause = str


class Field:
    name: str
    db_definition: str
    transform: Callable[[Any], Any] | None

    def __init__(
        self,
        name: str,
        db_definition: str,
        transform: Callable[[Any], Any] | None = None,
    ) -> None:
        self.name = name
        self.db_definition = db_definition
        self.transform = transform


class QueryBuilder:
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

    class Operator(ABC):
        symbol: str

        def __init__(self, symbol: str) -> None:
            self.symbol = symbol

        @abstractmethod
        def compile(self, field: Field, value: Any) -> str:
            raise NotImplementedError

    class Equal(Operator):
        def __init__(self) -> None:
            super().__init__("equal")

        @override
        def compile(self, field: Field, value: Any) -> str:
            return f"{field.db_definition} = {selfvalue}"
