from dataclasses import dataclass
from typing import Protocol


class TranscriptProviderError(Exception):
    """Base error for transcript provider failures."""


class TranscriptNotFoundError(TranscriptProviderError):
    pass


class TranscriptRateLimitError(TranscriptProviderError):
    pass


class TranscriptUnavailableError(TranscriptProviderError):
    pass


@dataclass(frozen=True, slots=True)
class TranscriptTurn:
    speaker: str
    title: str | None
    content: str


@dataclass(frozen=True, slots=True)
class Transcript:
    symbol: str
    quarter: str
    turns: tuple[TranscriptTurn, ...]
    source: str


class TranscriptProvider(Protocol):
    def fetch(self, symbol: str, quarter: str) -> Transcript: ...