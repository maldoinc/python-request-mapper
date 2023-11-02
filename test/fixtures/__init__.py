from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel
from request_mapper import RequestMapperIntegration

if TYPE_CHECKING:
    from request_mapper.types import IncomingMappedData, RequestMapperDecorator


class QueryDummyModel(BaseModel):
    query: bool


class RequestBodyDummyModel(BaseModel):
    body: bool


class FormDataDummyModel(BaseModel):
    form: bool


class DummyIntegration(RequestMapperIntegration):
    def __init__(
        self,
        query: IncomingMappedData | None = None,
        body: IncomingMappedData | None = None,
        form: IncomingMappedData | None = None,
    ) -> None:
        self.set_up_called = False
        self.query = {"query": True} if query is None else query
        self.body = {"body": True} if body is None else body
        self.form = {"form": True} if form is None else form

    def set_up(self, request_mapper_decorator: RequestMapperDecorator) -> None:
        self.set_up_called = True

    def get_query_as_dict(self) -> IncomingMappedData:
        return self.query

    def get_request_body_as_dict(self) -> IncomingMappedData:
        return self.body

    def get_form_data_as_dict(self) -> IncomingMappedData:
        return self.form
