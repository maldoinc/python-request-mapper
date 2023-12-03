import unittest
from test.fixtures import QueryDummyModel, RequestBodyDummyModel

from flask import Flask
from request_mapper import FromBody, FromQuery, setup_mapper
from request_mapper.integration.flask_integration import FlaskIntegration


class FlaskIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update({"TESTING": True})
        self.client = self.app.test_client()

    def test_maps_query_json_models(self):
        @self.app.route("/", methods=["POST"])
        def flask_view(query: FromQuery[QueryDummyModel], body: FromBody[RequestBodyDummyModel]):
            self.assertEqual(query, QueryDummyModel(query=True))
            self.assertEqual(body, RequestBodyDummyModel(body=True))

            return "ok"

        setup_mapper(integration=FlaskIntegration(app=self.app))
        res = self.client.post("/", query_string={"query": True}, json={"body": True})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.data, b"ok")
