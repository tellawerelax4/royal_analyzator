"""First-order Markov predictor."""
from __future__ import annotations

from collections import defaultdict

from RoyalAnalyzer.app.core.models import Roll
from RoyalAnalyzer.app.predictors.base import BasePredictor, Prediction


class MarkovPredictor(BasePredictor):
    """Models transitions between selected dice values."""

    name = "markov"

    def __init__(self) -> None:
        self.transitions: dict[int, dict[int, int]] = defaultdict(lambda: {v: 1 for v in range(1, 7)})

    def fit(self, rolls: list[Roll]) -> None:
        self.transitions = defaultdict(lambda: {v: 1 for v in range(1, 7)})
        values = [roll.chosen_dice or roll.dice[0] for roll in rolls]
        for previous, current in zip(values, values[1:], strict=False):
            self.transitions[previous][current] += 1

    def predict(self, history: list[Roll]) -> Prediction:
        if not history:
            return {value: 1 / 6 for value in range(1, 7)}
        current = history[-1].chosen_dice or history[-1].dice[0]
        row = self.transitions[current]
        total = sum(row.values())
        return {value: row[value] / total for value in range(1, 7)}
