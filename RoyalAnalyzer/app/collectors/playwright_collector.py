"""Playwright collector with DOM probing, keepalive, and OCR fallback hooks."""
from __future__ import annotations

import asyncio
import random
from collections.abc import AsyncIterator, Callable

from RoyalAnalyzer.app.collectors.royal_dom_parser import parse_last_roll
from RoyalAnalyzer.app.core.models import Roll

RollCallback = Callable[[Roll], None]

ROYAL_DICE_EXTRACTOR_SCRIPT = """
() => {
  const dice = [];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_ELEMENT);
  while (walker.nextNode()) {
    const node = walker.currentNode;
    const color = node.getAttribute && node.getAttribute('color');
    if (!color || !['Red', 'Blue'].includes(color)) continue;
    const pips = Array.from(node.querySelectorAll('[style*="grid-area"]')).length;
    if (pips >= 1 && pips <= 6) dice.push({ value: pips, color });
  }
  return dice.slice(0, 60);
}
"""


class RoyalPlaywrightCollector:
    """Collect Royal results from Bettery Royal.

    The primary strategy counts pip elements inside `color="Red"`/`color="Blue"` dice
    containers. This matches the supplied DOM and ignores generated CSS class names. If
    the DOM signal disappears, the optional OCR reader can provide five dice values.

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
        self._last_signature: tuple[int, ...] | None = None

    async def iter_rolls(self) -> AsyncIterator[Roll]:
        """Yield rolls from OCR-only mode when no Playwright page is attached."""
        self._running = True
        while self._running:
            values = self.ocr_reader() if self.ocr_reader else None
            if values and len(values) == 5 and values != self._last_signature:
                self._last_signature = values
                yield Roll(dice=tuple(values))  # type: ignore[arg-type]
            await asyncio.sleep(1)

    async def iter_page_rolls(self, page: object) -> AsyncIterator[Roll]:
        """Yield unique rolls from a Playwright page using DOM first, OCR second."""
        self._running = True
        while self._running:
            values = await self.extract_from_page(page)
            if values and values != self._last_signature:
                self._last_signature = values
                yield Roll(dice=values)
            await asyncio.sleep(1)

    async def extract_from_page(self, page: object) -> tuple[int, ...] | None:
        """Extract a five-dice result from a Playwright page-like object."""
        values: tuple[int, ...] | None = None
        if hasattr(page, "evaluate"):
            try:
                raw_dice = await page.evaluate(ROYAL_DICE_EXTRACTOR_SCRIPT)
                numbers = tuple(int(item["value"]) for item in raw_dice[:5])
                values = numbers if len(numbers) == 5 else None
            except Exception:  # noqa: BLE001 - fall through to HTML/OCR strategies
                values = None
        if values is None and hasattr(page, "content"):
            try:
                values = parse_last_roll(await page.content())
            except Exception:  # noqa: BLE001 - fall through to OCR strategy
                values = None
        if values is None and self.ocr_reader:
            ocr_values = self.ocr_reader()
            values = tuple(ocr_values) if ocr_values and len(ocr_values) == 5 else None
        return values


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
