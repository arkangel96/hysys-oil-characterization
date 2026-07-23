"""Oil Characterization Assist — entry point (separate from CDU Assist)."""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication

from gui import OilCharacterizationAssist


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = OilCharacterizationAssist()
    window.show()
    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
