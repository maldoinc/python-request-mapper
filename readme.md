# Python request mapper

Map and validate incoming request data to Pydantic models.

## Examples

```python
class PostCreateRequest(BaseModel):
    title: str
    content: str


class PostFilterQuery(BaseModel):
    status: PostStatus | None = None
    

@app.get("/posts")
@map_request
def post_list_all(query: FromQueryString[PostFilterQuery]) -> PaginatedResponse[Post]:
    # "query" is a valid pydantic model at this point.
    return PaginatedResponse(...)
    

@app.post("/posts")
@map_request
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

