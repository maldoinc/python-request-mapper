from test.fixtures import QueryDummyModel, RequestBodyDummyModel

import pytest
from aiohttp import web
from aiohttp.pytest_plugin import aiohttp_client
from request_mapper import FromQuery, FromBody, map_request, setup_mapper
from request_mapper.integration.aiohttp_integration import AioHttpIntegration


@pytest.mark.asyncio()
async def test_maps_query_json_models_successfully(aiohttp_client):
    @map_request
    async def view(
        _request: web.Request,
        query: FromQuery[QueryDummyModel],
        body: FromBody[RequestBodyDummyModel],
    ):
        assert query == QueryDummyModel(query=True)
        assert body == RequestBodyDummyModel(body=True)

        return web.Response(text="Hello world")

    app = web.Application()
    app.router.add_post("/", view)
    setup_mapper(integration=AioHttpIntegration(app))

    client = await aiohttp_client(app)
    resp = await client.post("/?query=true", json={"body": True})
    assert await resp.text() == "Hello world"
