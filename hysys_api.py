"""HYSYS COM adapter for Oil Characterization Assist.

Independent copy of connect patterns — do not import from oil_charateization.
Never auto-saves the case. Does not rewrite Oil Manager / property packages
unless the user later adds an explicit, reversible write path.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from models import CaseSnapshot, StreamSummary


class HysysError(RuntimeError):
    """Raised when HYSYS cannot complete an automation request."""


class HysysController:
    PROG_IDS = ("HYSYS.Application", "HYSYS.Application.V15")

    def __init__(self) -> None:
        self.app: Any = None
        self.case: Any = None
        self.flowsheet: Any = None
        self.connected = False

    def connect(self, case_path: str | None = None) -> None:
        try:
            import pythoncom
            import win32com.client
        except ImportError as exc:
            raise HysysError("Live HYSYS connectivity requires Windows and pywin32.") from exc

        pythoncom.CoInitialize()
        errors: list[str] = []
        app = None
        for prog_id in self.PROG_IDS:
            try:
                app = win32com.client.GetActiveObject(prog_id)
                break
            except Exception as exc:
                errors.append(f"attach {prog_id}: {exc}")
        if app is None:
            for prog_id in self.PROG_IDS:
                try:
                    app = win32com.client.Dispatch(prog_id)
                    app.Visible = True
                    break
                except Exception as exc:
                    errors.append(f"start {prog_id}: {exc}")
        if app is None:
            raise HysysError("Could not attach to or start Aspen HYSYS. " + " | ".join(errors))

        try:
            if case_path:
                path = str(Path(case_path).resolve())
                self.case = app.SimulationCases.Open(path)
            else:
                self.case = self._active_case(app)
            if self.case is None:
                raise HysysError("HYSYS is running, but no simulation case is open.")
            self.app = app
            self.flowsheet = self.case.Flowsheet
            self.connected = True
        except Exception:
            self.disconnect()
            raise

    @staticmethod
    def _active_case(app: Any) -> Any:
        for getter in (
            lambda: app.ActiveDocument,
            lambda: app.SimulationCases.Item(0),
        ):
            try:
                case = getter()
                if case is not None:
                    return case
            except Exception:
                continue
        return None

    def disconnect(self) -> None:
        self.connected = False
        self.flowsheet = None
        self.case = None
        self.app = None

    def _require_connection(self) -> None:
        if not self.connected or self.flowsheet is None:
            raise HysysError("Not connected to a HYSYS case.")

    @staticmethod
    def _items(collection: Any) -> Iterable[Any]:
        count = int(collection.Count)
        for index in range(count):
            try:
                yield collection.Item(index)
            except Exception:
                yield collection.Item(index + 1)

    @staticmethod
    def _safe_float(value: Any) -> float | None:
        try:
            if value is None:
                return None
            number = float(value)
            if number != number:  # NaN
                return None
            return number
        except Exception:
            return None

    def get_case_title(self) -> str:
        self._require_connection()
        for attr in ("Title", "Name", "FullName"):
            try:
                value = getattr(self.case, attr, None)
                if value:
                    return str(value)
            except Exception:
                continue
        return "(untitled case)"

    def get_component_names(self) -> list[str]:
        self._require_connection()
        candidates = (
            lambda: self.flowsheet.FluidPackage.Components,
            lambda: self.case.BasisManager.FluidPackages.Item(0).Components,
        )
        for getter in candidates:
            try:
                components = getter()
                names: list[str] = []
                for item in self._items(components):
                    try:
                        names.append(str(item.Name))
                    except Exception:
                        continue
                if names:
                    return names
            except Exception:
                continue
        return []

    def list_streams(self) -> list[StreamSummary]:
        self._require_connection()
        streams: list[StreamSummary] = []
        try:
            materials = self.flowsheet.MaterialStreams
        except Exception as exc:
            raise HysysError(f"Cannot enumerate material streams: {exc}") from exc

        for stream in self._items(materials):
            try:
                name = str(stream.Name)
            except Exception:
                continue
            streams.append(
                StreamSummary(
                    name=name,
                    temperature=self._safe_float(getattr(stream, "Temperature", None)),
                    pressure=self._safe_float(getattr(stream, "Pressure", None)),
                    molar_flow=self._safe_float(getattr(stream, "MolarFlow", None)),
                    vapor_fraction=self._safe_float(getattr(stream, "VapourFraction", None)),
                )
            )
        return streams

    def probe_oil_manager(self) -> str:
        """Best-effort Oil Manager / assay presence note (read-only discovery)."""
        self._require_connection()
        from aspen_intelligence import OIL_MANAGER_MEMBERS, OIL_MANAGER_PROBE_PATHS

        notes: list[str] = []

        def _walk(root: Any, parts: tuple[str, ...]) -> Any:
            obj = root
            for part in parts:
                obj = getattr(obj, part, None)
                if obj is None:
                    return None
            return obj

        for path in OIL_MANAGER_PROBE_PATHS:
            try:
                obj = _walk(self.case, path)
                if obj is None:
                    continue
                label = ".".join(path)
                try:
                    count = int(obj.Count)
                    notes.append(f"{label}: Count={count}")
                except Exception:
                    notes.append(f"{label}: present")
                # If this looks like OilManager, list readable members
                if path[-1] == "OilManager":
                    readable = []
                    for member in OIL_MANAGER_MEMBERS:
                        try:
                            if getattr(obj, member, None) is not None:
                                readable.append(member)
                        except Exception:
                            continue
                    if readable:
                        notes.append("OilManager members: " + ", ".join(readable[:8]))
            except Exception as exc:
                notes.append(f"{'.'.join(path)}: error ({exc})")

        # Legacy BasisManager attribute scan
        basis = getattr(self.case, "BasisManager", None)
        if basis is not None:
            for attr in ("Oils", "OilManager", "Assays", "Blends"):
                if any(attr in n for n in notes):
                    continue
                try:
                    obj = getattr(basis, attr, None)
                    if obj is None:
                        continue
                    try:
                        notes.append(f"BasisManager.{attr}: Count={int(obj.Count)}")
                    except Exception:
                        notes.append(f"BasisManager.{attr}: present")
                except Exception:
                    continue

        if not notes:
            return (
                "No Oils/OilManager/Assays found yet (Aspen COM paths tried). "
                "See docs/intelligence/aspen/ and aspen_intelligence.py."
            )
        return "; ".join(notes)

    def snapshot(self) -> CaseSnapshot:
        self._require_connection()
        return CaseSnapshot(
            case_title=self.get_case_title(),
            component_names=self.get_component_names(),
            streams=self.list_streams(),
            oil_manager_hint=self.probe_oil_manager(),
        )

    def solve(self) -> None:
        self._require_connection()
        try:
            self.case.Solver.CanSolve = True
        except Exception:
            pass
        for method in ("Solve", "WaitForSolve"):
            try:
                getattr(self.case, method)()
                return
            except Exception:
                continue
        raise HysysError("Could not request a case solve on this HYSYS build.")
