"""
Custom application exceptions and FastAPI exception handlers.
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse


class HCPFillerError(Exception):
    """Base application error."""
    def __init__(self, message: str, status_code: int = 500) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class AIServiceError(HCPFillerError):
    """Raised when the LangGraph / Groq service fails."""
    def __init__(self, message: str = "AI service error") -> None:
        super().__init__(message, status_code=status.HTTP_502_BAD_GATEWAY)


class ValidationError(HCPFillerError):
    """Raised on invalid input that passes Pydantic but fails business rules."""
    def __init__(self, message: str) -> None:
        super().__init__(message, status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers on the FastAPI app."""

    @app.exception_handler(HCPFillerError)
    async def hcpfiller_error_handler(
        request: Request, exc: HCPFillerError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.message, "type": type(exc).__name__},
        )

    @app.exception_handler(Exception)
    async def unhandled_error_handler(
        request: Request, exc: Exception
    ) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "An unexpected error occurred.", "type": "InternalServerError"},
        )
