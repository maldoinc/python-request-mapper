from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable, Mapping, TypeVar

from pydantic import BaseModel, ValidationError
from typing_extensions import Annotated

from request_mapper.integration.integration import (
    AsyncRequestMapperIntegration,
    RequestMapperIntegration,
    RequestMapperIntegrationType,
)
from request_mapper.types import (
    AnnotatedParameter,
    FormDataMapping,
    FunctionCall,
    QueryStringMapping,
    RequestBodyMapping,
    RequestDataMapping,
    RequestValidationError,
)

_integration: RequestMapperIntegrationType | None = None
_response_converter: Callable[[BaseModel], Any] | None = None
__T = TypeVar("__T")

FromRequestBody = Annotated[__T, RequestBodyMapping]
FromFormData = Annotated[__T, FormDataMapping]
FromQueryString = Annotated[__T, QueryStringMapping]


def _validate_input(val: AnnotatedParameter, data: Mapping[Any, Any]) -> BaseModel:
    try:
        return val.cls(**data)
    except ValidationError as e:
        raise RequestValidationError(
            location=val.annotation.location,
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

        if param and issubclass(param.annotation, RequestDataMapping):
            mapped_params[param_name] = param

    return mapped_params


async def _async_get_bound_args(
    mapped_params: Mapping[str, Any], fn_call: FunctionCall
) -> Mapping[str, Any]:
    if not isinstance(_integration, AsyncRequestMapperIntegration):
        msg = (
            "Integration is not set. Please call setup_mapper with an async integration "
            "before starting your application"
        )
        raise TypeError(msg)

    bound_args = {}
    for name, param in mapped_params.items():
        data = None
        if param.annotation == QueryStringMapping:
            data = await _integration.get_query_as_dict(fn_call)
        elif param.annotation == RequestBodyMapping:
            data = await _integration.get_request_body_as_dict(fn_call)
        elif param.annotation == FormDataMapping:
            data = await _integration.get_form_data_as_dict(fn_call)

        if data is not None:
            bound_args[name] = _validate_input(param, data)

    return bound_args


def _sync_get_bound_args(
    mapped_params: Mapping[str, Any], fn_call: FunctionCall
) -> Mapping[str, Any]:
    if not isinstance(_integration, RequestMapperIntegration):
        msg = "Integration is not set. Please call setup_mapper before starting your application."
        raise TypeError(msg)

    bound_args = {}
    for name, param in mapped_params.items():
        data = None
        if param.annotation == QueryStringMapping:
            data = _integration.get_query_as_dict(fn_call)
        elif param.annotation == RequestBodyMapping:
            data = _integration.get_request_body_as_dict(fn_call)
        elif param.annotation == FormDataMapping:
            data = _integration.get_form_data_as_dict(fn_call)

        if data is not None:
            bound_args[name] = _validate_input(param, data)

    return bound_args


def map_request(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Map annotated arguments from the function this decorates to strongly typed models."""
    mapped_params = _get_mapped_params(fn)

    # If this particular function did not request any mappings
    # return immediately to avoid any performance overhead.
    if not mapped_params:
        return fn

    if asyncio.iscoroutinefunction(fn):

        @functools.wraps(fn)
        async def async_inner(*args: Any, **kwargs: Any) -> Any:
            bound_args = await _async_get_bound_args(mapped_params, FunctionCall(fn, args, kwargs))

            return await fn(*args, **kwargs, **bound_args)

        return async_inner

    @functools.wraps(fn)
    def sync_inner(*args: Any, **kwargs: Any) -> Any:
        bound_args = _sync_get_bound_args(mapped_params, FunctionCall(fn, args, kwargs))

        return fn(*args, **kwargs, **bound_args)

    return sync_inner


def setup_mapper(
    integration: RequestMapperIntegrationType,
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
    "AsyncRequestMapperIntegration",
    "RequestMapperIntegrationType",
    "RequestValidationError",
]
