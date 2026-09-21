from collections.abc import Mapping
from typing import Any

import httpx

from app.providers.base import (
    Transcript,
    TranscriptNotFoundError,
    TranscriptRateLimitError,
    TranscriptTurn,
    TranscriptUnavailableError,
)


class AlphaVantageTranscriptProvider:
    def __init__(self, client: httpx.Client, api_key: str) -> None:
        self._client = client
        self._api_key = api_key

    def fetch(self, symbol: str, quarter: str) -> Transcript:
        try:
            response = self._client.get(
                "",
                params={
                    "function": "EARNINGS_CALL_TRANSCRIPT",
                    "symbol": symbol,
                    "quarter": quarter,
                    "apikey": self._api_key,
                },
            )
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise TranscriptUnavailableError(
                "Alpha Vantage is unavailable"
            ) from exc

        if not isinstance(payload, Mapping):
            raise TranscriptUnavailableError("Alpha Vantage returned malformed data")
        if "Note" in payload or "Information" in payload:
            raise TranscriptRateLimitError("Alpha Vantage request limit reached")
        if "Error Message" in payload:
            raise TranscriptNotFoundError("Transcript not found")

        turns = self._parse_turns(payload.get("transcript"))
        if not turns:
            raise TranscriptNotFoundError("Transcript not found")

        return Transcript(
            symbol=str(payload.get("symbol", symbol)).upper(),
            quarter=str(payload.get("quarter", quarter)).upper(),
            turns=turns,
            source="alpha_vantage",
        )

    @staticmethod
    def _parse_turns(value: Any) -> tuple[TranscriptTurn, ...]:
        if not isinstance(value, list):
            return ()

        turns: list[TranscriptTurn] = []
        for item in value:
            if not isinstance(item, Mapping):
                continue
            speaker = item.get("speaker")
            content = item.get("content")
            title = item.get("title")
            if not isinstance(speaker, str) or not isinstance(content, str):
                continue
            if not content.strip():
                continue
            turns.append(
                TranscriptTurn(
                    speaker=speaker.strip() or "Unknown speaker",
                    title=title.strip() if isinstance(title, str) and title.strip() else None,
                    content=content.strip(),
                )
            )
        return tuple(turns)