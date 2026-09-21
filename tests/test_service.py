import pytest

from app.analyzer import AnalysisResult, FactorAnalysis
from app.providers.base import Transcript, TranscriptTurn
from app.scoring import FACTOR_WEIGHTS
from app.service import EarningsCallRiskService


class FakeProvider:
    def fetch(self, symbol: str, quarter: str) -> Transcript:
        return Transcript(
            symbol=symbol,
            quarter=quarter,
            turns=(
                TranscriptTurn(
                    speaker="CEO",
                    title="Chief Executive Officer",
                    content="Demand softened in the quarter.",
                ),
            ),
            source="test",
        )


class FakeAnalyzer:
    def analyze(self, _chunks: object) -> AnalysisResult:
        return AnalysisResult(
            model="jev-test",
            factors={
                factor: FactorAnalysis(
                    probability=0.8 if factor == "demand_weakness" else 0.2,
                    evidence_chunk_id=(
                        "turn_0001" if factor == "demand_weakness" else None
                    ),
                )
                for factor in FACTOR_WEIGHTS
            },
        )


def test_service_returns_verbatim_evidence() -> None:
    result = EarningsCallRiskService(FakeProvider(), FakeAnalyzer()).analyze(
        "ACME", "2025Q1"
    )

    assert result.overall_risk == pytest.approx(0.35)
    assert result.factors[0].evidence is not None
    assert result.factors[0].evidence.content == "Demand softened in the quarter."
    assert result.factors[1].evidence is None