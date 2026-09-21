from enum import StrEnum

from pydantic import BaseModel, Field, field_validator


class RiskBand(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class EarningsCallRiskRequest(BaseModel):
    symbol: str = Field(min_length=1, max_length=20, pattern=r"^[A-Z0-9.-]+$")
    quarter: str = Field(pattern=r"^\d{4}Q[1-4]$")

    @field_validator("symbol", "quarter", mode="before")
    @classmethod
    def normalize_identifier(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value

    @field_validator("quarter")
    @classmethod
    def validate_supported_quarter(cls, value: str) -> str:
        if int(value[:4]) < 2010:
            raise ValueError("quarter must be 2010Q1 or later")
        return value


class EvidenceExcerpt(BaseModel):
    chunk_id: str
    speaker: str
    title: str | None = None
    content: str


class RiskFactorResult(BaseModel):
    factor: str
    probability: float = Field(ge=0, le=1)
    weight: float = Field(ge=0, le=1)
    flagged: bool
    evidence: EvidenceExcerpt | None


class EarningsCallRiskResponse(BaseModel):
    symbol: str
    quarter: str
    source: str
    model: str
    overall_risk: float = Field(ge=0, le=1)
    risk_band: RiskBand
    factors: list[RiskFactorResult]


class ErrorResponse(BaseModel):
    detail: str