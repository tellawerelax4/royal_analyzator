"""Historical bankroll and model backtesting."""
from __future__ import annotations

from dataclasses import dataclass

from RoyalAnalyzer.app.core.models import Roll
from RoyalAnalyzer.app.predictors.base import BasePredictor


@dataclass(slots=True)
class BacktestResult:
    accuracy: float
    profit: float
    win_rate: float
    max_drawdown: float


class Backtester:
    """Runs flat-stake historical simulations."""

    def run(self, predictor: BasePredictor, rolls: list[Roll], stake: float = 1.0) -> BacktestResult:
        if len(rolls) < 2:
            return BacktestResult(0.0, 0.0, 0.0, 0.0)
        equity = 0.0
        peak = 0.0
        max_drawdown = 0.0
        wins = 0
        for index in range(1, len(rolls)):
            predictor.fit(rolls[:index])
            predicted = max(predictor.predict(rolls[:index]), key=predictor.predict(rolls[:index]).get)
            actual = rolls[index].chosen_dice or rolls[index].dice[0]
            if predicted == actual:
                wins += 1
                equity += stake
            else:
                equity -= stake
            peak = max(peak, equity)
            max_drawdown = max(max_drawdown, peak - equity)
        total = len(rolls) - 1
        return BacktestResult(wins / total, equity, wins / total, max_drawdown)
