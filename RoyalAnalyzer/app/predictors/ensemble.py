"""Voting ensemble for Royal predictors."""
from __future__ import annotations

from RoyalAnalyzer.app.core.models import Roll
from RoyalAnalyzer.app.predictors.base import BasePredictor, Prediction
from RoyalAnalyzer.app.predictors.frequency import FrequencyPredictor
from RoyalAnalyzer.app.predictors.markov import MarkovPredictor


class VotingEnsemble(BasePredictor):
    """Averages probabilities from enabled predictors."""

    name = "voting_ensemble"

    def __init__(self, predictors: list[BasePredictor] | None = None) -> None:
        self.predictors = predictors or [FrequencyPredictor(), MarkovPredictor()]

    def fit(self, rolls: list[Roll]) -> None:
        for predictor in self.predictors:
            predictor.fit(rolls)

    def predict(self, history: list[Roll]) -> Prediction:
        if not self.predictors:
            return {value: 1 / 6 for value in range(1, 7)}
        result = {value: 0.0 for value in range(1, 7)}
        for predictor in self.predictors:
            prediction = predictor.predict(history)
            for value, probability in prediction.items():
                result[value] += probability / len(self.predictors)
        return result
