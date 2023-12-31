import importlib
import unittest
from test.fixtures import (
    DummyIntegration,
    QueryDummyModel,
    RequestBodyDummyModel,
)
from typing import Optional

import request_mapper
from request_mapper import FromQuery, FromBody, RequestValidationError


class TestMapper(unittest.TestCase):
    def setUp(self):
        importlib.reload(request_mapper)

    def test_mapper_does_setup_sets_integration_converter(self):
        integration = DummyIntegration()

        request_mapper.setup_mapper(integration)

        self.assertEqual(request_mapper._integration, integration)
        self.assertTrue(integration.set_up_called)

    def test_mapper_maps_data_after_setup(self):
        @request_mapper.map_request
        def target(
            query: FromQuery[QueryDummyModel],
            body: FromBody[RequestBodyDummyModel],
        ):
            self.assertEqual(query, QueryDummyModel(query=True))
            self.assertEqual(body, RequestBodyDummyModel(body=True))

        request_mapper.setup_mapper(DummyIntegration())
        target()

    def test_mapper_raises_on_validation_error(self):
        @request_mapper.map_request
        def target(
            _query: FromQuery[QueryDummyModel],
        ):
            pass

        request_mapper.setup_mapper(DummyIntegration(query={}))
        with self.assertRaises(RequestValidationError) as e:
            target()
        self.assertEqual(str(e.exception), "Request data validation failed")
        self.assertEqual(e.exception.location, "query-string")
        self.assertEqual(
            e.exception.source_errors,
            [
                {
                    "input": {},
                    "loc": ("query",),
                    "msg": "Field required",
                    "type": "missing",
                    "url": "https://errors.pydantic.dev/2.5/v/missing",
                }
            ],
        )

    def test_mapper_converts_response(self):
        @request_mapper.map_request
        def target(query: FromQuery[QueryDummyModel]):
            self.assertEqual(query, QueryDummyModel(query=True))

            return query

        request_mapper.setup_mapper(DummyIntegration())
        self.assertEqual(target(), {"query": True})

    def test_mapper_raises_when_not_set_up(self):
        @request_mapper.map_request
        def _dummy(_foo: FromQuery[unittest.TestCase]):
            pass

        with self.assertRaises(TypeError) as e:
            _dummy()

        self.assertEqual(
            str(e.exception),
            "Integration is not set. Please call setup_mapper before starting your application.",
        )

    def test_mapper_does_not_have_mappings_causes_no_side_effects(self):
        @request_mapper.map_request
        def _dummy(_foo: Optional[unittest.TestCase] = None, _some_int: int = 5):
            pass

        _dummy()
