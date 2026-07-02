"""PySide6 dashboard for Royal Analyzer AI."""
from __future__ import annotations

import random
from datetime import datetime

from RoyalAnalyzer.app.config.settings import DEFAULT_SETTINGS
from RoyalAnalyzer.app.core.models import Roll
from RoyalAnalyzer.app.predictors.ensemble import VotingEnsemble
from RoyalAnalyzer.app.statistics.metrics import frequencies, shannon_entropy

from PySide6.QtCore import QThread, Qt, QTimer, Signal
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import (
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)


class CollectorThread(QThread):
    """Background Playwright worker that streams Royal rolls to the GUI."""

    roll_received = Signal(object)
    status_changed = Signal(str)

    def __init__(self, url: str) -> None:
        super().__init__()
        self.url = url
        self._running = True

    def stop(self) -> None:
        self._running = False
        self.requestInterruption()

    def run(self) -> None:  # noqa: D102 - Qt thread entry point
        import asyncio

        asyncio.run(self._run_async())

    async def _run_async(self) -> None:
        from playwright.async_api import async_playwright

        from RoyalAnalyzer.app.collectors.playwright_collector import RoyalPlaywrightCollector

        collector = RoyalPlaywrightCollector(self.url)
        self.status_changed.emit(f"Открываю страницу: {self.url}")
        async with async_playwright() as playwright:
            browser = await playwright.chromium.launch(headless=False)
            page = await browser.new_page(viewport={"width": 1280, "height": 720})
            await page.goto(self.url, wait_until="domcontentloaded", timeout=60_000)
            self.status_changed.emit("Страница открыта. Ищу dice DOM color=Red/Blue и историю бросков...")
            keepalive_task = asyncio.create_task(collector.keepalive(page))
            try:
                async for roll in collector.iter_page_rolls(page):
                    if not self._running or self.isInterruptionRequested():
                        break
                    self.roll_received.emit(roll)
                    self.status_changed.emit(f"Получен бросок: {' '.join(map(str, roll.dice))}")
            finally:
                await collector.stop()
                keepalive_task.cancel()
                await browser.close()


class DiceWidget(QWidget):  # type: ignore[misc, valid-type]
    """Small painted die widget."""

    PIPS = {
        1: [(0.5, 0.5)],
        2: [(0.28, 0.28), (0.72, 0.72)],
        3: [(0.28, 0.28), (0.5, 0.5), (0.72, 0.72)],
        4: [(0.28, 0.28), (0.72, 0.28), (0.28, 0.72), (0.72, 0.72)],
        5: [(0.28, 0.28), (0.72, 0.28), (0.5, 0.5), (0.28, 0.72), (0.72, 0.72)],
        6: [(0.28, 0.22), (0.72, 0.22), (0.28, 0.5), (0.72, 0.5), (0.28, 0.78), (0.72, 0.78)],
    }

    def __init__(self, value: int = 1, color: str = "#2563eb") -> None:
        super().__init__()
        self.value = value
        self.color = color
        self.setFixedSize(48, 48)

    def set_value(self, value: int) -> None:
        self.value = value
        self.update()

    def paintEvent(self, event: object) -> None:  # noqa: N802 - Qt API
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setBrush(QColor(self.color))
        painter.setPen(QColor("#334155"))
        painter.drawRoundedRect(2, 2, 44, 44, 8, 8)
        painter.setBrush(QColor("#ffffff"))
        painter.setPen(Qt.PenStyle.NoPen)
        for x_ratio, y_ratio in self.PIPS.get(self.value, []):
            painter.drawEllipse(int(x_ratio * 48) - 4, int(y_ratio * 48) - 4, 8, 8)


class MainWindow(QMainWindow):  # type: ignore[misc, valid-type]
    """Dark themed desktop dashboard with live status, history and predictions."""

    def __init__(self) -> None:
        super().__init__()
        self.rolls: list[Roll] = []
        self.predictor = VotingEnsemble()
        self.demo_timer = QTimer(self)
        self.demo_timer.timeout.connect(self._add_demo_roll)
        self.collector_thread: CollectorThread | None = None

        self.setWindowTitle("Royal Analyzer AI")
        self.resize(1180, 720)
        self.setStyleSheet(self._stylesheet())

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(14)

        layout.addLayout(self._build_header())
        layout.addLayout(self._build_cards())
        layout.addLayout(self._build_body())
        self._log("Приложение готово. Нажмите 'Демо' для проверки интерфейса или 'Сбор с сайта' для открытия игры и чтения истории.")

    def _build_header(self) -> QHBoxLayout:  # type: ignore[valid-type]
        row = QHBoxLayout()
        title = QLabel("Royal Analyzer AI")
        title.setObjectName("title")
        subtitle = QLabel("Статистический анализ Royal · рекомендации не гарантируют выигрыш")
        subtitle.setObjectName("subtitle")
        title_box = QVBoxLayout()
        title_box.addWidget(title)
        title_box.addWidget(subtitle)
        row.addLayout(title_box, stretch=1)

        self.demo_button = QPushButton("Демо")
        self.demo_button.clicked.connect(self._toggle_demo)
        self.collect_button = QPushButton("Сбор с сайта")
        self.collect_button.clicked.connect(self._show_collector_hint)
        row.addWidget(self.demo_button)
        row.addWidget(self.collect_button)
        return row

    def _build_cards(self) -> QGridLayout:  # type: ignore[valid-type]
        grid = QGridLayout()
        self.last_roll_card = self._card("Последний бросок", "—")
        self.prediction_card = self._card("Следующий прогноз", "—")
        self.best_model_card = self._card("Лучшая модель", "Voting Ensemble")
        self.entropy_card = self._card("Shannon entropy", "0.000")
        for index, card in enumerate([self.last_roll_card, self.prediction_card, self.best_model_card, self.entropy_card]):
            grid.addWidget(card, 0, index)
        return grid

    def _build_body(self) -> QHBoxLayout:  # type: ignore[valid-type]
        row = QHBoxLayout()
        left = QVBoxLayout()
        dice_panel = QFrame()
        dice_panel.setObjectName("panel")
        dice_layout = QHBoxLayout(dice_panel)
        self.dice_widgets = [DiceWidget(1, "#dc2626"), DiceWidget(1, "#2563eb"), DiceWidget(1, "#dc2626"), DiceWidget(1, "#2563eb"), DiceWidget(1, "#dc2626")]
        for widget in self.dice_widgets:
            dice_layout.addWidget(widget)
        left.addWidget(dice_panel)

        self.history = QTableWidget(0, 8)
        self.history.setHorizontalHeaderLabels(["Время", "D1", "D2", "D3", "D4", "D5", "Выбор", "Комбинация"])
        left.addWidget(self.history, stretch=1)
        row.addLayout(left, stretch=3)

        right = QVBoxLayout()
        self.frequency_label = QLabel("Частоты: —")
        self.frequency_label.setObjectName("metric")
        right.addWidget(self.frequency_label)
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        right.addWidget(self.log, stretch=1)
        row.addLayout(right, stretch=2)
        return row

    def _card(self, title: str, value: str) -> QFrame:  # type: ignore[valid-type]
        frame = QFrame()
        frame.setObjectName("card")
        layout = QVBoxLayout(frame)
        label = QLabel(title)
        label.setObjectName("cardTitle")
        number = QLabel(value)
        number.setObjectName("cardValue")
        frame.value_label = number  # type: ignore[attr-defined]
        layout.addWidget(label)
        layout.addWidget(number)
        return frame

    def _toggle_demo(self) -> None:
        if self.demo_timer.isActive():
            self.demo_timer.stop()
            self.demo_button.setText("Демо")
            self._log("Демо-поток остановлен.")
            return
        self.demo_timer.start(1500)
        self.demo_button.setText("Стоп демо")
        self._log("Демо-поток запущен: добавляются случайные броски для проверки dashboard.")

    def _show_collector_hint(self) -> None:
        if self.collector_thread and self.collector_thread.isRunning():
            self.collector_thread.stop()
            self.collector_thread.wait(3000)
            self.collector_thread = None
            self.collect_button.setText("Сбор с сайта")
            self._log("Сбор с сайта остановлен.")
            return
        self.collector_thread = CollectorThread(DEFAULT_SETTINGS.game_url)
        self.collector_thread.roll_received.connect(self.add_roll)
        self.collector_thread.status_changed.connect(self._log)
        self.collector_thread.start()
        self.collect_button.setText("Стоп сбор")
        self._log("Запускаю Playwright-сборщик. Не нажимайте игровые кнопки ставок в открытом браузере.")

    def _add_demo_roll(self) -> None:
        values = tuple(random.randint(1, 6) for _ in range(5))
        self.add_roll(Roll(dice=values, chosen_dice=values[0]))

    def add_roll(self, roll: Roll) -> None:
        """Add a roll to dashboard state and refresh visible widgets."""
        self.rolls.append(roll)
        self.predictor.fit(self.rolls)
        for widget, value in zip(self.dice_widgets, roll.dice, strict=True):
            widget.set_value(value)
        self._append_history_row(roll)
        self._refresh_metrics()

    def _append_history_row(self, roll: Roll) -> None:
        row = self.history.rowCount()
        self.history.insertRow(row)
        values = [
            datetime.now().strftime("%H:%M:%S"),
            *map(str, roll.dice),
            str(roll.chosen_dice or "—"),
            str(roll.combination),
        ]
        for column, value in enumerate(values):
            self.history.setItem(row, column, QTableWidgetItem(value))
        self.history.scrollToBottom()

    def _refresh_metrics(self) -> None:
        latest = self.rolls[-1]
        prediction = self.predictor.predict(self.rolls)
        best_value = max(prediction, key=prediction.get)
        probability = prediction[best_value]
        self.last_roll_card.value_label.setText(" ".join(map(str, latest.dice)))  # type: ignore[attr-defined]
        self.prediction_card.value_label.setText(f"{best_value} · {probability:.1%}")  # type: ignore[attr-defined]
        self.entropy_card.value_label.setText(f"{shannon_entropy(self.rolls):.3f}")  # type: ignore[attr-defined]
        freq = frequencies(self.rolls)
        self.frequency_label.setText("Частоты: " + " · ".join(f"{key}: {value}" for key, value in freq.items()))

    def _log(self, message: str) -> None:
        self.log.append(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")

    @staticmethod
    def _stylesheet() -> str:
        return """
        QMainWindow, QWidget { background: #0f172a; color: #e5e7eb; font-family: Segoe UI; }
        #title { font-size: 28px; font-weight: 700; color: #f8fafc; }
        #subtitle { color: #94a3b8; }
        QPushButton { background: #2563eb; color: white; border: 0; border-radius: 8px; padding: 10px 16px; font-weight: 600; }
        QPushButton:hover { background: #1d4ed8; }
        #card, #panel, QTableWidget, QTextEdit { background: #111827; border: 1px solid #334155; border-radius: 14px; }
        #cardTitle { color: #94a3b8; font-size: 13px; }
        #cardValue { color: #f8fafc; font-size: 24px; font-weight: 700; }
        #metric { background: #111827; border: 1px solid #334155; border-radius: 14px; padding: 14px; }
        QHeaderView::section { background: #1e293b; color: #e5e7eb; padding: 6px; border: 0; }
        QTableWidget::item { padding: 6px; }
        """
