from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass
from typing import Any, Protocol

from typesafe_sdk import Choice, Noul, NoulCriteria, TypeSafeClient

from app.transcripts import TranscriptChunk

RISK_DEFINITIONS = {
    "demand_weakness": (
        "Does the transcript contain direct evidence that customer demand is weakening?",
        "Concrete reports of lower demand, delayed purchases, reduced spending, or weaker bookings",
        "No direct demand weakness; exclude generic caution and legal boilerplate",
    ),
    "competitive_pressure": (
        "Does the transcript contain direct evidence that competitive pressure is increasing?",
        "Concrete pricing pressure, lost share, displacement, or stronger competitor activity",
        "No direct increase in competitive pressure; exclude generic mentions of competitors",
    ),
    "management_evasiveness": (
        "Does management evade or redirect a material analyst question in the transcript?",
        "A material question is not addressed, is redirected, or receives a nonresponsive answer",
        "Management directly addresses material questions, even when the answer is uncertain",
    ),
    "guidance_uncertainty": (
        "Does the transcript contain direct evidence of uncertainty, reduction, or withdrawal around forward guidance?",
        "Guidance is reduced, withdrawn, qualified, or described with material uncertainty",
        "Guidance is maintained or clear; exclude standard forward-looking-statement boilerplate",
    ),
}


@dataclass(frozen=True, slots=True)
class FactorAnalysis:
    probability: float
    evidence_chunk_id: str | None


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    model: str
    factors: dict[str, FactorAnalysis]


class RiskAnalyzer(Protocol):
    def analyze(self, chunks: tuple[TranscriptChunk, ...]) -> AnalysisResult: ...


class TypeSafeRiskAnalyzer:
    def __init__(
        self,
        api_key: str,
        model: str,
        evidence_threshold: float,
        client_factory: Callable[[], AbstractContextManager[Any]] | None = None,
    ) -> None:
        self._model = model
        self._evidence_threshold = evidence_threshold
        self._client_factory = client_factory or (
            lambda: TypeSafeClient(api_key=api_key, model=model)
        )

    def analyze(self, chunks: tuple[TranscriptChunk, ...]) -> AnalysisResult:
        criteria = {chunk.chunk_id: None for chunk in chunks}
        questions: dict[str, Noul | Choice] = {}
        for factor, (instruction, true_criteria, false_criteria) in RISK_DEFINITIONS.items():
            questions[factor] = Noul(
                instructions=instruction,
                criteria=NoulCriteria(true=true_criteria, false=false_criteria),
            )
            questions[f"{factor}_evidence"] = Choice(
                instructions=(
                    f"Which transcript chunk provides the strongest direct evidence for this proposition: {instruction} "
                    "Select its chunk ID."
                ),
                criteria=criteria,
            )

        state = {
            "transcript": [
                {
                    "chunk_id": chunk.chunk_id,
                    "speaker": chunk.speaker,
                    "title": chunk.title,
                    "content": chunk.content,
                }
                for chunk in chunks
            ]
        }
        with self._client_factory() as client:
            response = client.system_one(
                state=state,
                questions=questions,
                model=self._model,
            )

        factors = {}
        for factor in RISK_DEFINITIONS:
            probability = response.nouls[factor].noul
            evidence_id = response.choices[f"{factor}_evidence"].choice
            factors[factor] = FactorAnalysis(
                probability=probability,
                evidence_chunk_id=(
                    evidence_id if probability >= self._evidence_threshold else None
                ),
            )
        return AnalysisResult(model=response.model, factors=factors)