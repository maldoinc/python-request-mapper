# Python request mapper

Map and validate incoming request data to Pydantic models. Request-mapper is framework agnostic with first-party
support for Flask.

## Examples

```python
# Add this in your app initialization code.

# Optionally will decorate views so there's no need to 
# add @map_request to every view.

# This has no performance overhead for views that don't use request-mapper.
# This must be called after all views have been registered!
setup_mapper(integration=FlaskIntegration(app))


# Define the models using Pydantic v1 or v2.
class PostCreateRequest(BaseModel):
    title: str
    content: str


class PostFilterQuery(BaseModel):
    status: PostStatus | None = None
    

@app.get("/posts")
# Request data from the current request. 
def post_list_all(query: FromQueryString[PostFilterQuery]) -> PaginatedResponse[Post]:
    # "query" is a valid pydantic model at this point.
    return PaginatedResponse(...)
    

@app.post("/posts")
def post_create(body: FromRequestBody[PostCreateRequest]) -> PostCreateResponse:
    # "body" is a valid pydantic model at this point.
    return PostCreateResponse(...)
```

## Quickstart

* `pip install request-mapper`.
* In your application setup, call `mapper.setup_mapper` with the integration of your choice.

## Integrations

Request mapper provides its own interface for integrations, so it can be added to any application. The following
integrations are available.

### Flask

* Pull data from flask's request args, json and form data.
* Optional: Automatically map views without having to decorate them.
  * Views which do not use request mapper will not incur any performance penalty.
  * When using this feature the call to `setup_mapper` must be AFTER all views are registered.
* Optional: Set up an error handler for validation errors which makes the api respond with a 422.

### Custom integrations

You can create your own integration by inheriting `BaseIntegration` and supplying an instance of that
to the `setup_mapper` call.

Note that you must decorate your views with `@map_request`
