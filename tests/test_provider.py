import httpx
import pytest

from app.providers.alpha_vantage import AlphaVantageTranscriptProvider
from app.providers.base import TranscriptNotFoundError, TranscriptRateLimitError


def build_provider(payload: dict[str, object]) -> AlphaVantageTranscriptProvider:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["apikey"] == "test-key"
        return httpx.Response(200, json=payload)

    client = httpx.Client(
        base_url="https://example.test/query",
        transport=httpx.MockTransport(handler),
    )
    return AlphaVantageTranscriptProvider(client=client, api_key="test-key")


def test_provider_normalizes_transcript_and_ignores_sentiment() -> None:
    provider = build_provider(
        {
            "symbol": "acme",
            "quarter": "2025q1",
            "transcript": [
                {
                    "speaker": " CEO ",
                    "title": " Chief Executive Officer ",
                    "content": " Demand softened. ",
                    "sentiment": "Bearish",
                }
            ],
        }
    )

    transcript = provider.fetch("ACME", "2025Q1")

    assert transcript.symbol == "ACME"
    assert transcript.turns[0].content == "Demand softened."
    assert not hasattr(transcript.turns[0], "sentiment")


@pytest.mark.parametrize(
    ("payload", "error_type"),
    [
        ({"Note": "limit"}, TranscriptRateLimitError),
        ({"transcript": []}, TranscriptNotFoundError),
    ],
)
def test_provider_maps_upstream_responses(
    payload: dict[str, object], error_type: type[Exception]
) -> None:
    with pytest.raises(error_type):
        build_provider(payload).fetch("ACME", "2025Q1")