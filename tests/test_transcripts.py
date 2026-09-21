from app.providers.base import Transcript, TranscriptTurn
from app.transcripts import MAX_CHOICE_OPTIONS, prepare_transcript


def test_prepare_transcript_coalesces_to_choice_limit() -> None:
    transcript = Transcript(
        symbol="ACME",
        quarter="2025Q1",
        turns=tuple(
            TranscriptTurn(speaker=f"Speaker {index}", title=None, content=f"Text {index}")
            for index in range(300)
        ),
        source="test",
    )

    chunks = prepare_transcript(transcript)

    assert len(chunks) <= MAX_CHOICE_OPTIONS
    assert chunks[0].chunk_id == "turn_0001"
    assert "Text 0" in chunks[0].content
    assert "Text 1" in chunks[0].content