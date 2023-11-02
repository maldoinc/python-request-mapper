from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Mapping, TypeVar

from pydantic import BaseModel, ValidationError
from typing_extensions import Annotated

from request_mapper.integration.integration import RequestMapperIntegration
from request_mapper.types import (
    AnnotatedParameter,
    MappingFormRequest,
    QueryStringMapping,
    RequestBodyMapping,
    RequestDataMapping,
    RequestValidationError,
)

_integration: RequestMapperIntegration | None = None
_response_converter: Callable[[BaseModel], Any] | None = None
__T = TypeVar("__T")

FromRequestBody = Annotated[__T, RequestBodyMapping()]
FromFormData = Annotated[__T, MappingFormRequest()]
FromQueryString = Annotated[__T, QueryStringMapping()]


def _validate_input(val: AnnotatedParameter) -> BaseModel:
    try:
        return val.cls(**val.annotation.get_data(_integration))
    except ValidationError as e:
        raise RequestValidationError(
            location=val.annotation.get_location(),
            source_errors=e.errors(),
        ) from e


def _parameter_get_type_and_annotation(
    parameter: inspect.Parameter,
) -> AnnotatedParameter | None:
    """Get the annotation injection type from a signature's Parameter.

    Returns either the first annotation for an Annotated type or the default value.
    """
    if hasattr(parameter.annotation, "__metadata__") and hasattr(parameter.annotation, "__args__"):
        klass = parameter.annotation.__args__[0]
        annotation = parameter.annotation.__metadata__[0]

        return AnnotatedParameter(cls=klass, annotation=annotation)

    return None


def _get_mapped_params(fn: Callable[..., Any]) -> Mapping[str, AnnotatedParameter]:
    mapped_params = {}

    for param_name, param_type in inspect.signature(fn).parameters.items():
        param = _parameter_get_type_and_annotation(param_type)

        if param and isinstance(param.annotation, RequestDataMapping):
            mapped_params[param_name] = param

    return mapped_params


def map_request(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Map annotated arguments from the function this decorates to strongly typed models."""
    mapped_params = _get_mapped_params(fn)

    # If this particular function did not request any mappings
    # return immediately to avoid any performance overhead.
    if not mapped_params:
        return fn

    @functools.wraps(fn)
    def inner(*args: Any, **kwargs: Any) -> Any:
        if not _integration:
            msg = (
                "Integration is not set. Please call setup_mapper before starting your application."
            )
            raise ValueError(msg)

        bound_args = {name: _validate_input(val) for name, val in mapped_params.items()}

        return fn(*args, **kwargs, **bound_args)

    return inner


def setup_mapper(
    integration: RequestMapperIntegration,
) -> None:
    """Initialize request mapper using a given integration.

    If one of the existing ones does not fit for the project,
    subclass `RequestMapperIntegration` to provide your own.
    """
    global _integration  # noqa: PLW0603
    _integration = integration

    _integration.set_up(request_mapper_decorator=map_request)


__all__ = [
    "FromRequestBody",
    "FromFormData",
    "FromQueryString",
    "setup_mapper",
    "map_request",
    "RequestMapperIntegration",
    "RequestValidationError",
]
