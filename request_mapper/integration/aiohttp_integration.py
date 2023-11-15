from typing import Awaitable, Callable

from request_mapper import AsyncRequestMapperIntegration, RequestValidationError
from request_mapper.types import (
    FunctionCall,
    IncomingMappedData,
    IntegrationDoesNotExistError,
    RequestMapperDecorator,
)

try:
    from aiohttp import web
except ImportError as e:
    msg = "aiohttp"
    raise IntegrationDoesNotExistError(msg) from e


@web.middleware
async def _aio_error_middleware(
    request: web.Request,
    handler: Callable[[web.Request], Awaitable[web.StreamResponse]],
) -> web.StreamResponse:
    try:
        return await handler(request)
    except RequestValidationError as e:
        return web.json_response(e.source_errors, status=422)


def _get_request(call: FunctionCall) -> web.Request:
    for arg in call.args:
        if isinstance(arg, web.Request):
            return arg

    msg = "Function call does not contain request information"
    raise ValueError(msg)


class AioHttpIntegration(AsyncRequestMapperIntegration):
    """Async integration for aiohttp framework v3.x."""

    def __init__(self, app: web.Application, *, add_error_handling_middleware: bool = True) -> None:
        self.app = app
        if add_error_handling_middleware:
            self.app.middlewares.append(_aio_error_middleware)

    def set_up(self, request_mapper_decorator: RequestMapperDecorator) -> None:
        pass

    async def get_query_as_dict(self, call: FunctionCall) -> IncomingMappedData:
        return _get_request(call).query

    async def get_request_body_as_dict(self, call: FunctionCall) -> IncomingMappedData:
        return await _get_request(call).json()  # type: ignore[no-any-return]
