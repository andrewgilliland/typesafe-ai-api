import pytest

from app.models import RiskBand
from app.scoring import FACTOR_WEIGHTS, calculate_risk


def probabilities(value: float) -> dict[str, float]:
    return dict.fromkeys(FACTOR_WEIGHTS, value)


@pytest.mark.parametrize(
    ("value", "expected_band"),
    [
        (0.329, RiskBand.LOW),
        (0.33, RiskBand.MEDIUM),
        (0.669, RiskBand.MEDIUM),
        (0.67, RiskBand.HIGH),
    ],
)
def test_calculate_risk_band_boundaries(
    value: float, expected_band: RiskBand
) -> None:
    score, band = calculate_risk(probabilities(value))

    assert score == pytest.approx(value)
    assert band is expected_band


def test_calculate_risk_rejects_missing_factor() -> None:
    with pytest.raises(ValueError, match="same factors"):
        calculate_risk({"demand_weakness": 0.5})