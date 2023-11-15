# Python request mapper

* Map and validate incoming request data to Pydantic (v1 and v2) models. 
* framework-agnostic and comes with first-party support for Flask and AioHttp.
* Async ready.

![Build](https://img.shields.io/github/actions/workflow/status/maldoinc/python-request-mapper/run_all.yml)
![PyPI version](https://img.shields.io/pypi/v/request-mapper)
![Python versions](https://img.shields.io/pypi/pyversions/request-mapper)

## Examples

```python
# Add this in your app initialization code.
setup_mapper(
    integration=FlaskIntegration(
        # Automatically decorate views to avoid adding @map_request to every view.
        # Will not incur any performance overhead for views that don't use request-mapper.

        # If map_views is enabled, setup_mapper must be called after 
        # all views have been registered!
        map_views=True,
        # Register an error handler that returns 422 alongside pydantic validation errors
        # when the request cannot be mapped.
        add_error_handler=True,
    )
)


# Define models using Pydantic v1 or v2.
class PostCreateRequest(BaseModel):
    title: str
    content: str


class PostFilterQuery(BaseModel):
    status: PostStatus | None = None


@app.get("/posts")
# Map data from the current request.
def post_list_all(query: FromQuery[PostFilterQuery]) -> PaginatedResponse[Post]:
    # "query" is a valid pydantic model at this point.
    return PaginatedResponse(...)


@app.post("/posts")
def post_create(body: FromBody[PostCreateRequest]) -> PostCreateResponse:
    # "body" is a valid pydantic model at this point.
    return PostCreateResponse(...)

```

## Quickstart

* `pip install request-mapper`.
* In your application setup, call `mapper.setup_mapper` with the integration of your choice.
* Decorate targets with `@map_request` (Optional when using flask integration).
* Map request data using one of the provided annotated types.
    * `FromQuery[T]` or `Annotated[T, QueryStringMapping]`
    * `FromBody[T]` or  `Annotated[T, RequestBodyMapping]`
* Response is converted back to dict using Pydantic.
  * Override behavior by passing a custom response converter.

## Integrations

### Flask

* Pull data from flask's request args, json and form data.
* Optional: Automatically map views without having to decorate them.
    * Views which do not use request mapper will not incur any performance penalty.
    * When using this feature the call to `setup_mapper` must be AFTER all views are registered.
* Optional: Set up an error handler for validation errors which makes the api respond with a 422.

### Aiohttp

* Async integration.
* Pull data from the current request.
* Note: even when using `map_request`, `request` must still be present as the first argument as required by aio.

### Custom integrations

You can create your own integration by inheriting `BaseIntegration` and supplying an instance of that
to the `setup_mapper` call.

Note that you must decorate your views with `@map_request`

## Demo application

A demo flask application is available at [maldoinc/wireup-demo](https://github.com/maldoinc/wireup-demo)

## Related projects

Check out [Wireup](https://github.com/maldoinc/wireup), a Dependency Injection library with
a focus on developer experience, type safety and ease of use.
