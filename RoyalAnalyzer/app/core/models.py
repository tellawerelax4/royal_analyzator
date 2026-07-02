"""Domain models and Royal combination detection."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import StrEnum


class Combination(StrEnum):
    """Supported Royal dice combinations."""

    PENTA = "Пента"
    QUADRO = "Квадро"
    HET = "Хет"
    SERIES = "Серия"
    DOUBLE_TRICK = "Дабл-трик"
    TRICK = "Трик"
    DOUBLE = "Дабл"
    NONE = "Нет комбинации"


@dataclass(slots=True)
class Roll:
    """A single Royal round result."""

    dice: tuple[int, int, int, int, int]
    chosen_dice: int | None = None
    combination: Combination | None = None
    round_id: str | None = None
    session_id: str | None = None
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    id: int | None = None

    def __post_init__(self) -> None:
        if len(self.dice) != 5 or any(value < 1 or value > 6 for value in self.dice):
            raise ValueError("Royal roll must contain exactly five dice values in range 1..6")
        if self.combination is None:
            self.combination = detect_combination(self.dice)


def detect_combination(dice: tuple[int, int, int, int, int]) -> Combination:
    """Detect the strongest known Royal combination for five dice."""
    counts = sorted(Counter(dice).values(), reverse=True)
    unique = sorted(set(dice))
    if counts == [5]:
        return Combination.PENTA
    if counts == [4, 1]:
        return Combination.QUADRO
    if counts == [3, 2]:
        return Combination.HET
    if unique in ([1, 2, 3, 4, 5], [2, 3, 4, 5, 6]):
        return Combination.SERIES
    if counts == [2, 2, 1]:
        return Combination.DOUBLE_TRICK
    if counts == [3, 1, 1]:
        return Combination.TRICK
    if counts == [2, 1, 1, 1]:
        return Combination.DOUBLE
    return Combination.NONE
