from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError # Для обработки ошибок валидации Pydantic
import traceback # Для логирования полных трассировок стека

from .models import ErrorResponse, UserAlreadyExistsError

def register_exception_handlers(app: FastAPI):
    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        print(f"HTTPException: {exc.status_code} - {exc.detail} for URL: {request.url}")

        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                code=f"HTTP_{exc.status_code}",
                message=exc.detail,
                details={"path":
                             str(request.url.path), "method":
                             request.method}
            ).model_dump()
        )

    @app.exception_handler(status.HTTP_404_NOT_FOUND)
    async def custom_404_handler(request: Request, exc: HTTPException):
        print(f"Custom 404 handler for: {request.url}")

        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=ErrorResponse(
                code="RESOURCE_NOT_FOUND",
                message="The requested resource could not be found. Please Check URL.",
                details={"requested path":
                             str(request.url.path)}
            ).model_dump()
        )

    @app.exception_handler(UserAlreadyExistsError)
    async def user_already_exist_exception_handler(request: Request, exc: UserAlreadyExistsError):
        print(f"User already existsError caught for user: {exc.username}")

        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=ErrorResponse(
                code="DUPLICATE_USER",
                message=exc.message,
                details={"username": exc.username,
                         "path": str(request.url.path)}
            ).model_dump()
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        print(f"RequestValidationError caught for url: {request.url}")

        errors_list = []

        for error in exc.errors():
            errors_list.append({
                "loc": [str(loc) for loc in error['loc']],
                "msg": error['msg'],
                "type": error['type']
            })

        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=ErrorResponse(
                code="VALIDATION_ERROR",
                message="One or more validation errors occurred in the request body/parameters.",
                details={"errors": errors_list,
                         "path": str(request.url.path)}
            ).model_dump()
        )

    @app.exception_handler(Exception)
    async def generic_http_exception_handler(request: Request, exc: Exception):
        print(f"Unhandled exception caught for URL: {request.url}")
        print(f"Exception type: {type(exc).__name__}")
        traceback.print_exc()

        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=ErrorResponse(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected error occured. Please try again later.",
                details={"request_id": str(request.url)}
            ).model_dump()
        )


