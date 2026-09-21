from app.analyzer import RiskAnalyzer
from app.models import (
    EarningsCallRiskResponse,
    EvidenceExcerpt,
    RiskFactorResult,
)
from app.providers.base import TranscriptProvider
from app.scoring import FACTOR_WEIGHTS, calculate_risk
from app.transcripts import prepare_transcript


class EarningsCallRiskService:
    def __init__(self, provider: TranscriptProvider, analyzer: RiskAnalyzer) -> None:
        self._provider = provider
        self._analyzer = analyzer

    def analyze(self, symbol: str, quarter: str) -> EarningsCallRiskResponse:
        transcript = self._provider.fetch(symbol, quarter)
        chunks = prepare_transcript(transcript)
        chunks_by_id = {chunk.chunk_id: chunk for chunk in chunks}
        analysis = self._analyzer.analyze(chunks)
        probabilities = {
            factor: result.probability for factor, result in analysis.factors.items()
        }
        overall_risk, risk_band = calculate_risk(probabilities)

        factors = []
        for factor, weight in FACTOR_WEIGHTS.items():
            result = analysis.factors[factor]
            chunk = (
                chunks_by_id.get(result.evidence_chunk_id)
                if result.evidence_chunk_id
                else None
            )
            evidence = (
                EvidenceExcerpt(
                    chunk_id=chunk.chunk_id,
                    speaker=chunk.speaker,
                    title=chunk.title,
                    content=chunk.content,
                )
                if chunk
                else None
            )
            factors.append(
                RiskFactorResult(
                    factor=factor,
                    probability=result.probability,
                    weight=weight,
                    flagged=evidence is not None,
                    evidence=evidence,
                )
            )

        return EarningsCallRiskResponse(
            symbol=transcript.symbol,
            quarter=transcript.quarter,
            source=transcript.source,
            model=analysis.model,
            overall_risk=overall_risk,
            risk_band=risk_band,
            factors=factors,
        )