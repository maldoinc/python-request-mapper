import unittest

from flask import Flask
from pydantic import BaseModel

from request_mapper import FromBody, FromQuery, setup_mapper
from request_mapper.integration.flask_integration import FlaskIntegration
from test.fixtures import QueryDummyModel, RequestBodyDummyModel


class FlaskIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update({"TESTING": True})
        self.client = self.app.test_client()

    def test_maps_query_json_models_converts_response_successfully(self):
        class TestResponse(BaseModel):
            content: str

        @self.app.route("/", methods=["POST"])
        def flask_view(query: FromBody[QueryDummyModel], body: FromQuery[RequestBodyDummyModel]):
            self.assertEqual(query, QueryDummyModel(query=True))
            self.assertEqual(body, RequestBodyDummyModel(body=True))

            return TestResponse(content="response body")

        setup_mapper(integration=FlaskIntegration(app=self.app))
        res = self.client.post("/", query_string={"query": True}, json={"body": True})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json, {"content": "response body"})
