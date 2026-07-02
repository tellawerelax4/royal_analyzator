"""Predictor protocol and serialisation helpers."""
from __future__ import annotations

import pickle
from abc import ABC, abstractmethod
from pathlib import Path

from RoyalAnalyzer.app.core.models import Roll

Prediction = dict[int, float]


class BasePredictor(ABC):
    """Common interface implemented by every forecasting algorithm."""

    name = "base"

    @abstractmethod
    def fit(self, rolls: list[Roll]) -> None: ...

    @abstractmethod
    def predict(self, history: list[Roll]) -> Prediction: ...

    def score(self, rolls: list[Roll]) -> float:
        """Return simple next-chosen-die accuracy for historical data."""
        if len(rolls) < 2:
            return 0.0
        hits = 0
        total = 0
        for index in range(1, len(rolls)):
            actual = rolls[index].chosen_dice or rolls[index].dice[0]
            forecast = self.predict(rolls[:index])
            if max(forecast, key=forecast.get) == actual:
                hits += 1
            total += 1
        return hits / total if total else 0.0

    def reset(self) -> None:
        """Reset model state."""
        self.fit([])

    def save(self, path: Path) -> None:
        """Persist model state with pickle for offline desktop usage."""
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(pickle.dumps(self))

    @classmethod
    def load(cls, path: Path) -> "BasePredictor":
        """Load a persisted predictor."""
        return pickle.loads(path.read_bytes())
