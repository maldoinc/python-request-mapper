from __future__ import annotations

from request_mapper.types import (
    IncomingMappedData,
    IntegrationDoesNotExistError,
    RequestMapperDecorator,
)

try:
    import flask  # type: ignore[import-not-found]
except ImportError as e:
    msg = "Flask"
    raise IntegrationDoesNotExistError(msg) from e

from request_mapper import RequestValidationError
from request_mapper.integration.integration import RequestMapperIntegration


def _handle_request_validation_error(err: RequestValidationError) -> flask.Response:
    return flask.jsonify({"location": err.location, "errors": err.source_errors}), 422


class FlaskIntegration(RequestMapperIntegration):
    """Enables integration with Flask.

    Automatically decorates views which use request mappers
    and registers an error handler for validation errors.
    """

    def __init__(
        self, app: flask.Flask, *, decorate_views: bool = True, register_error_handler: bool = True
    ) -> None:
        """Initialize a new Flask Integration. Flask must be installed for this to work.

        @param app: An instance of your flask application.
        @param decorate_views: If true, all views will be decorated with map_request.
        @param register_error_handler: If true, an error handler will be added to convert
        RequestValidationError to 422.
        """
        self.add_error_handler = register_error_handler
        self.map_views = decorate_views
        self.__app = app

    def set_up(self, request_mapper_decorator: RequestMapperDecorator) -> None:
        """Register error handler and map views.

        This must be called after all views have been registered!
        """
        if self.add_error_handler:
            self.__app.register_error_handler(
                RequestValidationError, _handle_request_validation_error
            )

        if self.map_views:
            self.__app.view_functions = {
                name: request_mapper_decorator(fn) for name, fn in self.__app.view_functions.items()
            }

    def get_request_body_as_dict(self) -> IncomingMappedData:
        """Return the current request body using request.json."""
        return flask.request.json

    def get_query_as_dict(self) -> IncomingMappedData:
        """Return the query data as a dict using request.args."""
        return flask.request.args.to_dict()

    def get_form_data_as_dict(self) -> IncomingMappedData:
        """Return form data as a dict using request.form."""
        return flask.request.form.to_dict()
