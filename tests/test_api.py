from fastapi.testclient import TestClient

from app.providers.base import TranscriptNotFoundError
from main import create_app


class FailingService:
    def analyze(self, _symbol: str, _quarter: str) -> None:
        raise TranscriptNotFoundError("Transcript not found")


def test_health() -> None:
    with TestClient(create_app(FailingService())) as client:
        assert client.get("/healthz").json() == {"status": "ok"}


def test_request_is_normalized_and_not_found_is_mapped() -> None:
    with TestClient(create_app(FailingService())) as client:
        response = client.post(
            "/v1/earnings-call-risk",
            json={"symbol": " acme ", "quarter": "2025q1"},
        )

    assert response.status_code == 404
    assert response.json() == {"detail": "Transcript not found"}


def test_invalid_request_returns_validation_error() -> None:
    with TestClient(create_app(FailingService())) as client:
        response = client.post(
            "/v1/earnings-call-risk",
            json={"symbol": "ACME", "quarter": "2009Q4"},
        )

    assert response.status_code == 422