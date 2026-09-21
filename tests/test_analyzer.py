from types import SimpleNamespace
from typing import Any, Self

from app.analyzer import RISK_DEFINITIONS, TypeSafeRiskAnalyzer
from app.transcripts import TranscriptChunk


class FakeClient:
    def __init__(self) -> None:
        self.questions: dict[str, Any] = {}

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *_args: object) -> None:
        pass

    def system_one(self, **kwargs: Any) -> SimpleNamespace:
        self.questions = kwargs["questions"]
        return SimpleNamespace(
            model="jev-test",
            nouls={
                factor: SimpleNamespace(noul=0.75 if index == 0 else 0.25)
                for index, factor in enumerate(RISK_DEFINITIONS)
            },
            choices={
                f"{factor}_evidence": SimpleNamespace(choice="turn_0001")
                for factor in RISK_DEFINITIONS
            },
        )


def test_analyzer_asks_all_questions_and_thresholds_evidence() -> None:
    client = FakeClient()
    analyzer = TypeSafeRiskAnalyzer(
        api_key="test",
        model="jev-test",
        evidence_threshold=0.5,
        client_factory=lambda: client,
    )

    result = analyzer.analyze(
        (
            TranscriptChunk(
                chunk_id="turn_0001",
                speaker="CEO",
                title=None,
                content="Demand softened.",
            ),
        )
    )

    assert len(client.questions) == 8
    assert result.factors["demand_weakness"].evidence_chunk_id == "turn_0001"
    assert result.factors["competitive_pressure"].evidence_chunk_id is None