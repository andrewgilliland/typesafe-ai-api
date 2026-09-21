from dataclasses import dataclass
from math import ceil

from app.providers.base import Transcript, TranscriptTurn

MAX_CHOICE_OPTIONS = 255


@dataclass(frozen=True, slots=True)
class TranscriptChunk:
    chunk_id: str
    speaker: str
    title: str | None
    content: str


def prepare_transcript(transcript: Transcript) -> tuple[TranscriptChunk, ...]:
    turns = tuple(turn for turn in transcript.turns if turn.content.strip())
    if not turns:
        raise ValueError("transcript contains no usable turns")

    group_size = max(1, ceil(len(turns) / MAX_CHOICE_OPTIONS))
    chunks = [
        _build_chunk(index + 1, turns[index : index + group_size])
        for index in range(0, len(turns), group_size)
    ]
    return tuple(chunks)


def _build_chunk(number: int, turns: tuple[TranscriptTurn, ...]) -> TranscriptChunk:
    speakers = list(dict.fromkeys(turn.speaker for turn in turns))
    titles = list(dict.fromkeys(turn.title for turn in turns if turn.title))
    content = "\n\n".join(
        f"{turn.speaker}: {turn.content}" if len(turns) > 1 else turn.content
        for turn in turns
    )
    return TranscriptChunk(
        chunk_id=f"turn_{number:04d}",
        speaker=" / ".join(speakers),
        title=" / ".join(titles) or None,
        content=content,
    )