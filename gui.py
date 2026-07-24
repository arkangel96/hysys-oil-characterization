"""Desktop UI for Oil Characterization Assist (sibling of CDU Assist)."""

from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
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

from assay_engine import (
    diagnose_assay,
    diagnose_case,
    diagnose_mrc_pack,
    finalize_o4,
    format_pe_board,
    load_assay,
    merge_diagnosis,
)
from complementary_rules import DEFAULTS
from handoff import write_handoff_o4
from hysys_api import HysysController, HysysError
from models import CaseSnapshot
from pe_identity import PRODUCT_NAME, PRODUCT_VERSION


class OilCharacterizationAssist(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(
            f"{PRODUCT_NAME} v{PRODUCT_VERSION} — Expert Oil Characterization PE"
        )
        self.resize(1180, 780)
        self.hysys = HysysController()
        self.snapshot: CaseSnapshot | None = None
        self._assay_mode = "none"
        self._last_diagnosis = None
        self._build_ui()
        self._set_status(
            "Default: expert Aspen HYSYS oil-characterization PE — Load MRC Pack or Connect."
        )

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        title = QLabel(PRODUCT_NAME)
        title.setFont(QFont("Segoe UI Semibold", 14))
        layout.addWidget(title)

        subtitle = QLabel(
            "Default role: expert Aspen HYSYS process engineer — oil characterization "
            "(Oil Manager → NBP/hypos → FEED). Peer to CDU PE. Separate from CDU Assist tower trials."
        )
        subtitle.setWordWrap(True)
        layout.addWidget(subtitle)

        assay_bar = QHBoxLayout()
        self.btn_mrc = QPushButton("Load MRC Pack")
        self.btn_basrah = QPushButton("QA Basrah")
        self.btn_mishrif = QPushButton("QA Mishrif")
        for btn in (self.btn_mrc, self.btn_basrah, self.btn_mishrif):
            assay_bar.addWidget(btn)
        assay_bar.addStretch(1)
        layout.addLayout(assay_bar)

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

        verify_bar = QHBoxLayout()
        self.chk_hypo = QCheckBox("Hypo / NBP slate reviewed (PE)")
        self.btn_handoff = QPushButton("Export handoff_o4.json")
        self.btn_com_write = QPushButton("COM write (gated — OFF)")
        self.btn_com_write.setEnabled(False)
        self.btn_com_write.setToolTip(
            "allow_COM_write=false — characterize manually in Oil Manager; Assist verifies."
        )
        verify_bar.addWidget(self.chk_hypo)
        verify_bar.addWidget(self.btn_handoff)
        verify_bar.addWidget(self.btn_com_write)
        verify_bar.addStretch(1)
        layout.addLayout(verify_bar)

        com_note = QLabel(
            f"COM write gate: allow_COM_write={DEFAULTS.get('allow_COM_write')} — "
            "manual Oil Manager first; Assist READ-verifies install/attach/NBP."
        )
        com_note.setWordWrap(True)
        layout.addWidget(com_note)

        self.status = QLabel("")
        layout.addWidget(self.status)

        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter, stretch=1)

        left = QWidget()
        left_layout = QVBoxLayout(left)
        left_layout.addWidget(QLabel("Material streams (HYSYS)"))
        self.stream_table = QTableWidget(0, 5)
        self.stream_table.setHorizontalHeaderLabels(
            ["Stream", "T", "P", "MolarFlow", "VF"]
        )
        left_layout.addWidget(self.stream_table)

        left_layout.addWidget(QLabel("Oil Manager inventory"))
        self.om_box = QTextEdit()
        self.om_box.setReadOnly(True)
        self.om_box.setMaximumHeight(120)
        left_layout.addWidget(self.om_box)

        left_layout.addWidget(QLabel("FEED composition (lights / NBP)"))
        self.feed_table = QTableWidget(0, 3)
        self.feed_table.setHorizontalHeaderLabels(["Component", "Fraction", "Kind"])
        left_layout.addWidget(self.feed_table)

        left_layout.addWidget(QLabel("Fluid-package components"))
        self.comp_box = QTextEdit()
        self.comp_box.setReadOnly(True)
        self.comp_box.setMaximumHeight(100)
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
        splitter.setSizes([560, 560])

        self.btn_mrc.clicked.connect(self.on_load_mrc_pack)
        self.btn_basrah.clicked.connect(lambda: self.on_qa_crude("BASRAH"))
        self.btn_mishrif.clicked.connect(lambda: self.on_qa_crude("MISHRIF"))
        self.btn_connect.clicked.connect(self.on_connect)
        self.btn_open.clicked.connect(self.on_open_case)
        self.btn_refresh.clicked.connect(self.on_refresh)
        self.btn_solve.clicked.connect(self.on_solve)
        self.btn_disconnect.clicked.connect(self.on_disconnect)
        self.chk_hypo.stateChanged.connect(lambda _s: self._refresh_pe_board())
        self.btn_handoff.clicked.connect(self.on_export_handoff)
        self.btn_com_write.clicked.connect(self.on_com_write_blocked)

        self._refresh_pe_board()

    def _hypo_reviewed(self) -> bool:
        return bool(self.chk_hypo.isChecked())

    def _set_status(self, text: str) -> None:
        self.status.setText(text)

    def _log(self, text: str) -> None:
        self.log.append(text)

    def _current_diagnosis(self):
        hypo = self._hypo_reviewed()
        if self._assay_mode in {"mrc", "merged"}:
            diag = diagnose_mrc_pack(self.snapshot)
            diag.hypo_reviewed = hypo
            if self.snapshot is not None:
                diag.oil_installed = self.snapshot.feed_evidence.oil_installed
                diag.feed_attached = self.snapshot.feed_evidence.feed_attached
                diag.feed_stream = self.snapshot.feed_evidence.feed_stream
                diag.case_title = self.snapshot.case_title
            return finalize_o4(diag)
        if self._assay_mode in {"BASRAH", "MISHRIF"}:
            assay_diag = diagnose_assay(load_assay(self._assay_mode))
            if self.snapshot is not None:
                case_diag = diagnose_case(self.snapshot, hypo_reviewed=hypo)
                return merge_diagnosis(assay_diag, case_diag, hypo_reviewed=hypo)
            assay_diag.hypo_reviewed = hypo
            return finalize_o4(assay_diag)
        case_diag = diagnose_case(self.snapshot, hypo_reviewed=hypo)
        return finalize_o4(case_diag)

    def _refresh_pe_board(self) -> None:
        diagnosis = self._current_diagnosis()
        # Propagate hypo checkbox onto diagnosis for gate
        diagnosis.hypo_reviewed = self._hypo_reviewed()
        if self.snapshot is not None and not diagnosis.oil_installed:
            diagnosis.oil_installed = self.snapshot.feed_evidence.oil_installed
            diagnosis.feed_attached = self.snapshot.feed_evidence.feed_attached
            diagnosis.feed_stream = self.snapshot.feed_evidence.feed_stream
            diagnosis.case_title = self.snapshot.case_title
        diagnosis = finalize_o4(diagnosis)
        self._last_diagnosis = diagnosis
        self.pe_board.setPlainText(format_pe_board(diagnosis))

    def on_load_mrc_pack(self) -> None:
        try:
            self._assay_mode = "merged" if self.snapshot is not None else "mrc"
            diagnosis = self._current_diagnosis()
            diagnosis.hypo_reviewed = self._hypo_reviewed()
            if self.snapshot is not None:
                diagnosis.oil_installed = self.snapshot.feed_evidence.oil_installed
                diagnosis.feed_attached = self.snapshot.feed_evidence.feed_attached
                diagnosis.feed_stream = self.snapshot.feed_evidence.feed_stream
                diagnosis.case_title = self.snapshot.case_title
            diagnosis = finalize_o4(diagnosis)
            self._last_diagnosis = diagnosis
            self.pe_board.setPlainText(format_pe_board(diagnosis))
            self._set_status(f"MRC pack QA — state {diagnosis.state}")
            self._log(f"Loaded MRC pack — state {diagnosis.state}")
        except Exception as exc:
            QMessageBox.warning(self, "MRC pack failed", str(exc))
            self._log(f"ERROR: {exc}")

    def on_qa_crude(self, crude_id: str) -> None:
        try:
            self._assay_mode = crude_id
            self._refresh_pe_board()
            diagnosis = self._last_diagnosis
            self._set_status(f"{crude_id} assay QA — state {diagnosis.state}")
            self._log(f"QA {crude_id} — state {diagnosis.state}")
            if diagnosis.qa and diagnosis.qa.flags:
                self._log("Flags: " + ", ".join(diagnosis.qa.flags))
        except Exception as exc:
            QMessageBox.warning(self, "Assay QA failed", str(exc))
            self._log(f"ERROR: {exc}")

    def _fill_om_pane(self, snapshot: CaseSnapshot) -> None:
        oil = snapshot.oil_manager
        lines = [
            f"found={oil.found} path={oil.path or '(none)'}",
            f"assays ({oil.assay_count}): {', '.join(oil.assay_names) or '(none)'}",
            f"oils ({len(oil.oil_names)}): {', '.join(oil.oil_names) or '(none)'}",
            f"blends ({oil.blend_count}):",
        ]
        for blend in oil.blends:
            lines.append(
                f"  • {blend.name} ready={blend.is_ready_to_install} "
                f"assays={blend.assay_names}"
            )
        if oil.readable_members:
            lines.append("members: " + ", ".join(oil.readable_members))
        if oil.notes:
            lines.append("notes: " + "; ".join(oil.notes[:6]))
        if oil.error:
            lines.append("error: " + oil.error)
        self.om_box.setPlainText("\n".join(lines))

    def _fill_feed_table(self, snapshot: CaseSnapshot) -> None:
        self.feed_table.setRowCount(0)
        comp = snapshot.feed_composition
        if comp is None:
            return
        # Prefer showing lights + NBP first
        ordered = sorted(
            comp.components,
            key=lambda c: (0 if c.kind == "light" else 1 if c.kind == "nbp" else 2, c.name),
        )
        for item in ordered:
            if item.kind == "other" and (item.fraction or 0) == 0:
                continue
            row = self.feed_table.rowCount()
            self.feed_table.insertRow(row)
            frac = "" if item.fraction is None else f"{item.fraction:.6g}"
            for col, value in enumerate([item.name, frac, item.kind]):
                self.feed_table.setItem(row, col, QTableWidgetItem(value))

    def _apply_snapshot(self, snapshot: CaseSnapshot) -> None:
        self.snapshot = snapshot
        if self._assay_mode in {"mrc", "BASRAH", "MISHRIF", "merged"}:
            self._assay_mode = "merged" if self._assay_mode == "mrc" else self._assay_mode
        else:
            self._assay_mode = "hysys"
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
        self._fill_om_pane(snapshot)
        self._fill_feed_table(snapshot)
        self._refresh_pe_board()
        ev = snapshot.feed_evidence
        self._set_status(
            f"Connected — {snapshot.case_title} | "
            f"{len(snapshot.streams)} streams | {len(snapshot.component_names)} comps | "
            f"FEED={ev.feed_stream} NBP={ev.nbp_count}"
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
            self._log(
                f"FEED evidence: installed={snap.feed_evidence.oil_installed} "
                f"attached={snap.feed_evidence.feed_attached}"
            )
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
            self._log("Refreshed snapshot (Oil Manager + FEED composition).")
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
        self._assay_mode = "none"
        self.stream_table.setRowCount(0)
        self.feed_table.setRowCount(0)
        self.comp_box.clear()
        self.om_box.clear()
        self._refresh_pe_board()
        self._set_status("Disconnected.")
        self._log("Disconnected.")

    def on_com_write_blocked(self) -> None:
        QMessageBox.information(
            self,
            "COM write gated",
            "allow_COM_write=false.\n\n"
            "Characterize / Install / Attach manually in Oil Manager.\n"
            "Use Refresh so Assist can verify FEED lights + NBP.\n"
            "Write stubs exist in hysys_api but will not fire until inventory flips the gate.",
        )
        self._log("COM write blocked by allow_COM_write=false.")

    def on_export_handoff(self) -> None:
        self._refresh_pe_board()
        diagnosis = self._last_diagnosis
        if diagnosis is None:
            QMessageBox.information(self, "Handoff", "No diagnosis yet.")
            return
        diagnosis.hypo_reviewed = self._hypo_reviewed()
        if self.snapshot is not None:
            diagnosis.oil_installed = (
                diagnosis.oil_installed or self.snapshot.feed_evidence.oil_installed
            )
            diagnosis.feed_attached = (
                diagnosis.feed_attached or self.snapshot.feed_evidence.feed_attached
            )
            diagnosis.feed_stream = diagnosis.feed_stream or self.snapshot.feed_evidence.feed_stream
            diagnosis.case_title = diagnosis.case_title or self.snapshot.case_title
        diagnosis = finalize_o4(diagnosis)
        if not diagnosis.handoff_to_cdu:
            QMessageBox.warning(
                self,
                "Handoff blocked",
                "O4 gate not passed.\n"
                "Need assay O2/O3 (not OX), oil_installed, feed_attached, and hypo reviewed.\n"
                f"Current state={diagnosis.state} "
                f"install={diagnosis.oil_installed} attach={diagnosis.feed_attached} "
                f"hypo={diagnosis.hypo_reviewed}",
            )
            self._log("Handoff export blocked by O4 gate.")
            return
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export handoff_o4.json",
            str(Path.cwd() / "handoff_o4.json"),
            "JSON (*.json)",
        )
        if not path:
            return
        try:
            out = write_handoff_o4(diagnosis, path, notes="Exported from Oil Characterization Assist")
            self._log(f"Wrote handoff token: {out}")
            QMessageBox.information(
                self,
                "Handoff written",
                f"Wrote {out}\n\nOpen CDU Assist on the same HYSYS case. No auto-launch.",
            )
        except Exception as exc:
            QMessageBox.warning(self, "Handoff failed", str(exc))
            self._log(f"ERROR: {exc}")
