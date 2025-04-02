import logging
from enum import StrEnum

from fastapi import Request, status
from fastapi.responses import JSONResponse

from doxer.domain.exceptions import (
    AuthenticationError,
    ConflictError,
    DomainException,
    NotFoundError,
    ValidationError,
)

logger = logging.getLogger(__name__)

class ErrorCode(StrEnum):
    VALIDATION_ERROR = "VALIDATION_ERROR"
    NOT_FOUND = "NOT_FOUND"
    CONFLICT_ERROR = "CONFLICT_ERROR"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    AUTHORIZATION_ERROR = "AUTHORIZATION_ERROR"
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"


async def domain_exception_handler(request: Request, exc: DomainException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = ErrorCode.INTERNAL_SERVER_ERROR

    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
        error_code = ErrorCode.NOT_FOUND
    elif isinstance(exc, ConflictError):
        status_code = status.HTTP_409_CONFLICT
        error_code = ErrorCode.CONFLICT_ERROR
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        error_code = ErrorCode.VALIDATION_ERROR
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
        error_code = ErrorCode.AUTHENTICATION_ERROR

    logger.warning(
        f"Domain Exception Handled: {exc.__class__.__name__} - {exc.message}. "
        f"URL: {request.url.path}, Method: {request.method}, Status Code: {status_code}",
        exc_info=False
    )

    return JSONResponse(
        status_code=status_code, content={"message": exc.message, "code": error_code}
    )


async def global_exception_handler(request: Request, exc: Exception):
    logger.error(
        f"Unhandled Exception: {exc.__class__.__name__} - {str(exc)}. "
        f"URL: {request.url.path}, Method: {request.method}",
        exc_info=True
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "message": "An unexpected error occurred",
            "code": ErrorCode.INTERNAL_SERVER_ERROR,
        },
    )


def register_exception_handlers(app):
    app.add_exception_handler(DomainException, domain_exception_handler)
    app.add_exception_handler(Exception, global_exception_handler)
    logger.info("Registered custom exception handlers.")