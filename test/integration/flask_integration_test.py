import unittest
from test.fixtures import QueryDummyModel, RequestBodyDummyModel

from flask import Flask
from request_mapper import FromQueryString, FromRequestBody, setup_mapper
from request_mapper.integration.flask_integration import FlaskIntegration


class FlaskIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update({"TESTING": True})
        self.client = self.app.test_client()

    def test_maps_query_json_models_successfully(self):
        @self.app.route("/", methods=["POST"])
        def flask_view(
            query: FromQueryString[QueryDummyModel], body: FromRequestBody[RequestBodyDummyModel]
        ):
            self.assertEqual(query, QueryDummyModel(query=True))
            self.assertEqual(body, RequestBodyDummyModel(body=True))

            return "response body"

        setup_mapper(integration=FlaskIntegration(app=self.app))
        res = self.client.post("/", query_string={"query": True}, json={"body": True})
        self.assertEqual(res.status_code, 200)

    # def test_maps_form_data(self):
    #     @self.app.route("/", methods=["POST"])
    #     def flask_view(form: FromRequestBody[FormDataDummyModel]):
    #         self.assertEqual(form, FormDataDummyModel(form=True))
    #
    #         return {}
    #
    #     setup_mapper(integration=FlaskIntegration(app=self.app))
    #     res = self.client.post("/form", data={"form": True})
    #     self.assertEqual(res.status_code, 200)
