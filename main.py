from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

import httpx
from fastapi import Depends, FastAPI, Request
from fastapi.responses import JSONResponse
from typesafe_sdk import TypeSafeError, TypeSafeRateLimitError

from app.analyzer import TypeSafeRiskAnalyzer
from app.config import get_settings
from app.models import (
    EarningsCallRiskRequest,
    EarningsCallRiskResponse,
    ErrorResponse,
)
from app.providers.alpha_vantage import AlphaVantageTranscriptProvider
from app.providers.base import (
    TranscriptNotFoundError,
    TranscriptRateLimitError,
    TranscriptUnavailableError,
)
from app.service import EarningsCallRiskService


def create_app(service: EarningsCallRiskService | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        if service is not None:
            app.state.risk_service = service
            yield
            return

        settings = get_settings()
        with httpx.Client(
            base_url=settings.alpha_vantage_base_url,
            timeout=settings.request_timeout_seconds,
        ) as http_client:
            app.state.risk_service = EarningsCallRiskService(
                provider=AlphaVantageTranscriptProvider(
                    client=http_client,
                    api_key=settings.alpha_vantage_api_key.get_secret_value(),
                ),
                analyzer=TypeSafeRiskAnalyzer(
                    api_key=settings.typesafe_api_key.get_secret_value(),
                    model=settings.typesafe_model,
                    evidence_threshold=settings.evidence_threshold,
                ),
            )
            yield

    application = FastAPI(
        title="Earnings Call Risk API",
        version="0.1.0",
        lifespan=lifespan,
    )

    def get_service(request: Request) -> EarningsCallRiskService:
        return request.app.state.risk_service

    @application.get("/healthz")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @application.post(
        "/v1/earnings-call-risk",
        response_model=EarningsCallRiskResponse,
        responses={
            404: {"model": ErrorResponse},
            429: {"model": ErrorResponse},
            502: {"model": ErrorResponse},
        },
    )
    def analyze_earnings_call(
        request: EarningsCallRiskRequest,
        risk_service: Annotated[EarningsCallRiskService, Depends(get_service)],
    ) -> EarningsCallRiskResponse:
        return risk_service.analyze(request.symbol, request.quarter)

    @application.exception_handler(TranscriptNotFoundError)
    async def transcript_not_found(
        _request: Request, exc: TranscriptNotFoundError
    ) -> JSONResponse:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @application.exception_handler(TranscriptRateLimitError)
    async def transcript_rate_limited(
        _request: Request, exc: TranscriptRateLimitError
    ) -> JSONResponse:
        return JSONResponse(status_code=429, content={"detail": str(exc)})

    @application.exception_handler(TypeSafeRateLimitError)
    async def typesafe_rate_limited(
        _request: Request, _exc: TypeSafeRateLimitError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=429, content={"detail": "TypeSafe request limit reached"}
        )

    @application.exception_handler(TranscriptUnavailableError)
    async def transcript_unavailable(
        _request: Request, exc: TranscriptUnavailableError
    ) -> JSONResponse:
        return JSONResponse(status_code=502, content={"detail": str(exc)})

    @application.exception_handler(TypeSafeError)
    async def typesafe_unavailable(
        _request: Request, _exc: TypeSafeError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=502, content={"detail": "TypeSafe analysis is unavailable"}
        )

    return application


app = create_app()
