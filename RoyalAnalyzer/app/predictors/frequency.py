"""Frequency based Royal predictor."""
from __future__ import annotations

from collections import Counter

from RoyalAnalyzer.app.core.models import Roll
from RoyalAnalyzer.app.predictors.base import BasePredictor, Prediction


class FrequencyPredictor(BasePredictor):
    """Predicts the next selected value from empirical frequencies."""

    name = "frequency"

    def __init__(self) -> None:
        self.counts: Counter[int] = Counter({value: 1 for value in range(1, 7)})

    def fit(self, rolls: list[Roll]) -> None:
        self.counts = Counter({value: 1 for value in range(1, 7)})
        for roll in rolls:
            self.counts.update([roll.chosen_dice or roll.dice[0]])

    def predict(self, history: list[Roll]) -> Prediction:
        total = sum(self.counts.values())
        return {value: self.counts[value] / total for value in range(1, 7)}
