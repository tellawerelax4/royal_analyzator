"""PySide6 dashboard for Royal Analyzer AI."""
from __future__ import annotations

try:
    from PySide6.QtWidgets import QLabel, QMainWindow, QVBoxLayout, QWidget
except ImportError:  # pragma: no cover - allows core tests without GUI deps
    QLabel = QMainWindow = QVBoxLayout = QWidget = None  # type: ignore[assignment]


class MainWindow(QMainWindow):  # type: ignore[misc, valid-type]
    """Dark themed desktop dashboard shell."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Royal Analyzer AI")
        self.resize(1280, 720)
        container = QWidget()
        layout = QVBoxLayout(container)
        title = QLabel("Royal Analyzer AI — статистический анализ, без гарантий выигрыша")
        title.setStyleSheet("font-size: 22px; color: #f1f5f9; padding: 16px;")
        layout.addWidget(title)
        self.setCentralWidget(container)
        self.setStyleSheet("QMainWindow { background: #0f172a; }")
