"""Statistical metrics for Royal history analysis."""
from __future__ import annotations

from collections import Counter
from math import log2


from RoyalAnalyzer.app.core.models import Roll


def selected_values(rolls: list[Roll]) -> list[int]:
    """Return the chosen dice series, falling back to the first die."""
    return [roll.chosen_dice or roll.dice[0] for roll in rolls]


def frequencies(rolls: list[Roll]) -> dict[int, int]:
    """Count observed selected values."""
    counts = Counter(selected_values(rolls))
    return {value: counts[value] for value in range(1, 7)}


def shannon_entropy(rolls: list[Roll]) -> float:
    """Calculate Shannon entropy for selected values."""
    values = selected_values(rolls)
    if not values:
        return 0.0
    counts = Counter(values)
    total = len(values)
    return -sum((count / total) * log2(count / total) for count in counts.values())


def rolling_mean(rolls: list[Roll], window: int = 50) -> list[float]:
    """Calculate rolling mean over selected values."""
    values = selected_values(rolls)
    if len(values) < window:
        return []
    return [sum(values[index - window : index]) / window for index in range(window, len(values) + 1)]


def transition_matrix(rolls: list[Roll]) -> list[list[float]]:
    """Return a 6x6 transition matrix with row-normalized probabilities."""
    matrix = [[1.0 for _ in range(6)] for _ in range(6)]
    values = selected_values(rolls)
    for previous, current in zip(values, values[1:], strict=False):
        matrix[previous - 1][current - 1] += 1.0
    return [[cell / sum(row) for cell in row] for row in matrix]
