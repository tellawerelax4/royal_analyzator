"""Pattern-mining primitives for Royal sequences."""
from __future__ import annotations

from collections import Counter


def ngrams(values: list[int], n: int) -> dict[tuple[int, ...], int]:
    """Count n-grams in a dice-value sequence."""
    if n <= 0:
        raise ValueError("n must be positive")
    return dict(Counter(tuple(values[index : index + n]) for index in range(len(values) - n + 1)))


def association_pairs(values: list[int]) -> dict[tuple[int, int], int]:
    """Small association-rule building block based on adjacent pairs."""
    return dict(Counter(zip(values, values[1:], strict=False)))
