from __future__ import annotations

import abc
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable, Mapping, Optional

from pydantic import BaseModel

if TYPE_CHECKING:
    from request_mapper import RequestMapperIntegration

AnyCallable = Callable[..., Optional[Any]]
IncomingMappedData = Mapping[str, Any]
RequestMapperDecorator = Callable[[AnyCallable], AnyCallable]
ResponseConverter = Callable[[BaseModel], Any]


class IntegrationDoesNotExistError(Exception):
    """Raised when the required dependency for an integration is not installed."""

    def __init__(self, name: str) -> None:
        super().__init__(f"{name} is not installed")


class RequestValidationError(Exception):
    """Raised when pydantic fails to validate a model."""

    def __init__(self, location: str, source_errors: Any) -> None:
        self.source_errors = source_errors
        self.location = location

        super().__init__("Request data validation failed")


class RequestDataMapping(abc.ABC):
    """Base class to represent request data."""

    location: str

    @abc.abstractmethod
    def get_data(
        self, integration: RequestMapperIntegration, call: FunctionCall
    ) -> IncomingMappedData:
        """Return mapped data."""


class RequestBodyMapping(RequestDataMapping):
    """Retrieve incoming data from the request body."""

    location = "request-body"

    def get_data(
        self, integration: RequestMapperIntegration, call: FunctionCall
    ) -> IncomingMappedData:
        return integration.get_request_body_as_dict(call)


class QueryStringMapping(RequestDataMapping):
    """Retrieve incoming data from the query string."""

    location = "query-string"

    def get_data(
        self, integration: RequestMapperIntegration, call: FunctionCall
    ) -> IncomingMappedData:
        return integration.get_query_as_dict(call)


@dataclass(frozen=True)
class AnnotatedParameter:
    """Model containing information about the class type and source of data to map."""

    cls: type[BaseModel]
    annotation: type[RequestDataMapping]


@dataclass(frozen=True)
class FunctionCall:
    """Model representing a function call."""

    fn: AnyCallable
    args: tuple[Any, ...]
    kwargs: dict[str, Any]
