"""DOM parsing helpers for Bettery Royal dice results."""
from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser


_GRID_AREA_RE = re.compile(r"grid-area:\s*(\d+)\s*/\s*(\d+)", re.IGNORECASE)
_COLOR_RE = re.compile(r'color=["\']?(Red|Blue)["\']?', re.IGNORECASE)


@dataclass(slots=True, frozen=True)
class ParsedDie:
    """Single die parsed from the Bettery Royal styled DOM."""

    value: int
    color: str | None = None


class RoyalDiceHTMLParser(HTMLParser):
    """Extract dice from the observed Royal DOM snippet.

    The site renders each die as a container with `color="Red"` or `color="Blue"` and
    child pip divs positioned through CSS `grid-area`. Counting these pip children gives
    the die value, so the parser is resilient to generated class-name changes.
    """

    def __init__(self) -> None:
        super().__init__()
        self.dice: list[ParsedDie] = []
        self._current_color: str | None = None
        self._current_pips = 0
        self._depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {key.lower(): value or "" for key, value in attrs}
        raw_tag = self.get_starttag_text() or ""
        color = attrs_dict.get("color") or self._color_from_raw_tag(raw_tag)
        if color and color.lower() in {"red", "blue"}:
            self._current_color = color.title()
            self._current_pips = 0
            self._depth = 1
            return
        if self._current_color:
            self._depth += 1
            style = attrs_dict.get("style", "")
            if _GRID_AREA_RE.search(style):
                self._current_pips += 1

    def handle_endtag(self, tag: str) -> None:
        if not self._current_color:
            return
        self._depth -= 1
        if self._depth <= 0:
            if 1 <= self._current_pips <= 6:
                self.dice.append(ParsedDie(value=self._current_pips, color=self._current_color))
            self._current_color = None
            self._current_pips = 0
            self._depth = 0

    @staticmethod
    def _color_from_raw_tag(raw_tag: str) -> str | None:
        match = _COLOR_RE.search(raw_tag)
        return match.group(1) if match else None


def parse_royal_dice_html(html: str) -> list[ParsedDie]:
    """Parse all dice rendered in a Royal result/history HTML fragment."""
    parser = RoyalDiceHTMLParser()
    parser.feed(html)
    return parser.dice


def parse_last_roll(html: str) -> tuple[int, ...] | None:
    """Return the first complete five-dice roll from an HTML fragment."""
    dice = parse_royal_dice_html(html)
    if len(dice) < 5:
        return None
    return tuple(item.value for item in dice[:5])
