import math
from collections.abc import Mapping

from app.models import RiskBand

FACTOR_WEIGHTS = {
    "demand_weakness": 0.25,
    "competitive_pressure": 0.25,
    "management_evasiveness": 0.25,
    "guidance_uncertainty": 0.25,
}


def calculate_risk(
    probabilities: Mapping[str, float],
    weights: Mapping[str, float] = FACTOR_WEIGHTS,
) -> tuple[float, RiskBand]:
    if probabilities.keys() != weights.keys():
        raise ValueError("probabilities and weights must contain the same factors")
    if not math.isclose(sum(weights.values()), 1.0, abs_tol=1e-9):
        raise ValueError("weights must sum to 1")
    if any(not math.isfinite(value) or not 0 <= value <= 1 for value in probabilities.values()):
        raise ValueError("probabilities must be finite values from 0 to 1")
    if any(not math.isfinite(value) or value < 0 for value in weights.values()):
        raise ValueError("weights must be finite non-negative values")

    score = sum(probabilities[factor] * weight for factor, weight in weights.items())
    if score < 0.33:
        band = RiskBand.LOW
    elif score < 0.67:
        band = RiskBand.MEDIUM
    else:
        band = RiskBand.HIGH
    return score, band