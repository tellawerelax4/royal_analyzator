"""Application settings for Royal Analyzer AI."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class AppSettings:
    """Runtime configuration with conservative defaults."""

    game_url: str = "https://bettery.ru/quick-games/game_royal"
    data_dir: Path = Path("data")
    database_path: Path = Path("data/royal_history.sqlite3")
    logs_dir: Path = Path("logs")
    analysis_interval_seconds: float = 2.0
    keepalive_min_seconds: float = 15.0
    keepalive_max_seconds: float = 45.0
    minimum_history: int = 100
    neural_minimum_history: int = 5000
    recommendation_threshold: float = 0.55
    enabled_models: set[str] = field(default_factory=lambda: {"frequency", "markov", "ngram"})


DEFAULT_SETTINGS = AppSettings()
