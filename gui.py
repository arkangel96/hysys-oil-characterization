"""Desktop UI for Oil Characterization Assist (sibling of CDU Assist)."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from assay_engine import diagnose_case, format_pe_board
from hysys_api import HysysController, HysysError
from models import CaseSnapshot


class OilCharacterizationAssist(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Oil Characterization Assist v0.1")
        self.resize(1100, 700)
        self.hysys = HysysController()
        self.snapshot: CaseSnapshot | None = None
        self._build_ui()
        self._set_status("Disconnected — open HYSYS, then Connect.")

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        title = QLabel("Oil Characterization Assist")
        title.setFont(QFont("Segoe UI Semibold", 14))
        layout.addWidget(title)

        subtitle = QLabel(
            "Assay / Oil Manager assist — separate from CDU Assist. "
            "Intelligence grows in docs/intelligence/ + assay_engine.py."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        toolbar = QHBoxLayout()
        self.btn_connect = QPushButton("Connect")
        self.btn_open = QPushButton("Open Case…")
        self.btn_refresh = QPushButton("Refresh")
        self.btn_solve = QPushButton("Solve")
        self.btn_disconnect = QPushButton("Disconnect")
        for btn in (
            self.btn_connect,
            self.btn_open,
            self.btn_refresh,
            self.btn_solve,
            self.btn_disconnect,
        ):
            toolbar.addWidget(btn)
        toolbar.addStretch(1)
        layout.addLayout(toolbar)

        self.status = QLabel("")
        layout.addWidget(self.status)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, stretch=1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Material streams"))
        self.stream_table = QTableWidget(0, 5)
        self.stream_table.setHorizontalHeaderLabels(
            ["Stream", "T", "P", "MolarFlow", "VF"]
        )
        left_layout.addWidget(self.stream_table)
        left_layout.addWidget(QLabel("Fluid-package components"))
        self.comp_box = QTextEdit()
        self.comp_box.setReadOnly(True)
        self.comp_box.setMaximumHeight(140)
        left_layout.addWidget(self.comp_box)
        splitter.addWidget(left)

        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.addWidget(QLabel("Assay PE board"))
        self.pe_board = QTextEdit()
        self.pe_board.setReadOnly(True)
        self.pe_board.setFont(QFont("Consolas", 10))
        right_layout.addWidget(self.pe_board)
        right_layout.addWidget(QLabel("Activity log"))
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setMaximumHeight(160)
        right_layout.addWidget(self.log)
        splitter.addWidget(right)
        splitter.setSizes([550, 550])

        self.btn_connect.clicked.connect(self.on_connect)
        self.btn_open.clicked.connect(self.on_open_case)
        self.btn_refresh.clicked.connect(self.on_refresh)
        self.btn_solve.clicked.connect(self.on_solve)
        self.btn_disconnect.clicked.connect(self.on_disconnect)

        self._refresh_pe_board()

    def _set_status(self, text: str) -> None:
        self.status.setText(text)

    def _log(self, text: str) -> None:
        self.log.append(text)

    def _refresh_pe_board(self) -> None:
        diagnosis = diagnose_case(self.snapshot)
        self.pe_board.setPlainText(format_pe_board(diagnosis))

    def _apply_snapshot(self, snapshot: CaseSnapshot) -> None:
        self.snapshot = snapshot
        self.stream_table.setRowCount(0)
        for stream in snapshot.streams:
            row = self.stream_table.rowCount()
            self.stream_table.insertRow(row)
            values = [
                stream.name,
                self._fmt(stream.temperature),
                self._fmt(stream.pressure),
                self._fmt(stream.molar_flow),
                self._fmt(stream.vapor_fraction),
            ]
            for col, value in enumerate(values):
                self.stream_table.setItem(row, col, QTableWidgetItem(value))
        self.comp_box.setPlainText(
            ", ".join(snapshot.component_names) if snapshot.component_names else "(none)"
        )
        self._refresh_pe_board()
        self._set_status(
            f"Connected — {snapshot.case_title} | "
            f"{len(snapshot.streams)} streams | {len(snapshot.component_names)} components"
        )

    @staticmethod
    def _fmt(value: float | None) -> str:
        if value is None:
            return ""
        return f"{value:.4g}"

    def on_connect(self) -> None:
        try:
            self.hysys.connect()
            snap = self.hysys.snapshot()
            self._apply_snapshot(snap)
            self._log(f"Connected: {snap.case_title}")
            self._log(f"Oil Manager: {snap.oil_manager_hint}")
        except HysysError as exc:
            QMessageBox.warning(self, "Connect failed", str(exc))
            self._log(f"ERROR: {exc}")

    def on_open_case(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open HYSYS case",
            "",
            "HYSYS cases (*.hsc);;All files (*.*)",
        )
        if not path:
            return
        try:
            self.hysys.connect(case_path=path)
            snap = self.hysys.snapshot()
            self._apply_snapshot(snap)
            self._log(f"Opened case: {path}")
        except HysysError as exc:
            QMessageBox.warning(self, "Open case failed", str(exc))
            self._log(f"ERROR: {exc}")

    def on_refresh(self) -> None:
        if not self.hysys.connected:
            QMessageBox.information(self, "Refresh", "Connect first.")
            return
        try:
            snap = self.hysys.snapshot()
            self._apply_snapshot(snap)
            self._log("Refreshed snapshot.")
        except HysysError as exc:
            QMessageBox.warning(self, "Refresh failed", str(exc))
            self._log(f"ERROR: {exc}")

    def on_solve(self) -> None:
        if not self.hysys.connected:
            QMessageBox.information(self, "Solve", "Connect first.")
            return
        try:
            self.hysys.solve()
            self._log("Solve requested (case not auto-saved).")
            self.on_refresh()
        except HysysError as exc:
            QMessageBox.warning(self, "Solve failed", str(exc))
            self._log(f"ERROR: {exc}")

    def on_disconnect(self) -> None:
        self.hysys.disconnect()
        self.snapshot = None
        self.stream_table.setRowCount(0)
        self.comp_box.clear()
        self._refresh_pe_board()
        self._set_status("Disconnected.")
        self._log("Disconnected.")
