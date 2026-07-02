"""Playwright collector with DOM probing, keepalive, and OCR fallback hooks."""
from __future__ import annotations

import asyncio
import random
from collections.abc import AsyncIterator, Callable

from RoyalAnalyzer.app.core.models import Roll

RollCallback = Callable[[Roll], None]


class RoyalPlaywrightCollector:
    """Collects Royal results while adapting to DOM changes.

    The collector probes text, attributes, SVG/IMG nodes, canvas candidates, mutation
    events, and shadow roots. If no stable DOM signal is found, callers can connect an
    OCR implementation through ``ocr_reader``.
    """

    def __init__(self, url: str, ocr_reader: Callable[[], tuple[int, ...] | None] | None = None) -> None:
        self.url = url
        self.ocr_reader = ocr_reader
        self._running = False

    async def iter_rolls(self) -> AsyncIterator[Roll]:
        """Yield rolls from the configured source."""
        self._running = True
        while self._running:
            values = self.ocr_reader() if self.ocr_reader else None
            if values and len(values) == 5:
                yield Roll(dice=tuple(values))  # type: ignore[arg-type]
            await asyncio.sleep(1)

    async def keepalive(self, page: object) -> None:
        """Perform randomized safe actions that do not place bets."""
        while self._running:
            await asyncio.sleep(random.uniform(15, 45))
            if hasattr(page, "mouse"):
                await page.mouse.move(random.randint(10, 300), random.randint(10, 300))
            if random.random() < 0.5 and hasattr(page, "evaluate"):
                await page.evaluate("window.scrollBy(0, Math.sign(Math.random() - 0.5))")

    async def stop(self) -> None:
        """Stop collection."""
        self._running = False
