"""SQLite persistence for Royal roll history."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from RoyalAnalyzer.app.core.models import Combination, Roll


class RollRepository:
    """Stores and retrieves Royal rolls using SQLite."""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _init_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS rolls (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    dice1 INTEGER NOT NULL,
                    dice2 INTEGER NOT NULL,
                    dice3 INTEGER NOT NULL,
                    dice4 INTEGER NOT NULL,
                    dice5 INTEGER NOT NULL,
                    chosen_dice INTEGER,
                    combination TEXT NOT NULL,
                    round_id TEXT,
                    session_id TEXT
                )
                """
            )
            connection.execute("CREATE INDEX IF NOT EXISTS idx_rolls_time ON rolls(timestamp)")

    def add_roll(self, roll: Roll) -> int:
        """Persist a roll and return its database identifier."""
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO rolls (
                    timestamp, dice1, dice2, dice3, dice4, dice5,
                    chosen_dice, combination, round_id, session_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    roll.timestamp.isoformat(),
                    *roll.dice,
                    roll.chosen_dice,
                    str(roll.combination),
                    roll.round_id,
                    roll.session_id,
                ),
            )
            return int(cursor.lastrowid)

    def list_rolls(self, limit: int | None = None) -> list[Roll]:
        """Return rolls ordered by insertion time."""
        query = "SELECT * FROM rolls ORDER BY id"
        params: tuple[int, ...] = ()
        if limit is not None:
            query += " LIMIT ?"
            params = (limit,)
        with self._connect() as connection:
            rows = connection.execute(query, params).fetchall()
        return [
            Roll(
                id=row["id"],
                dice=(row["dice1"], row["dice2"], row["dice3"], row["dice4"], row["dice5"]),
                chosen_dice=row["chosen_dice"],
                combination=Combination(row["combination"]),
                round_id=row["round_id"],
                session_id=row["session_id"],
            )
            for row in rows
        ]
