"""Application entry point."""
from __future__ import annotations

import sys

from RoyalAnalyzer.app.gui.main_window import MainWindow


def main() -> int:
    """Start the PySide6 application."""
    from PySide6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
