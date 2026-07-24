"""HYSYS COM adapter for Oil Characterization Assist.

Independent copy of connect patterns — do not import from oil_charateization.
Never auto-saves the case. Oil Manager writes are gated by allow_COM_write.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

from aspen_intelligence import (
    BLEND_READ_MEMBERS,
    OIL_MANAGER_MEMBERS,
    OIL_MANAGER_PROBE_PATHS,
    classify_component_name,
)
from complementary_rules import DEFAULTS
from models import (
    BlendSummary,
    CaseSnapshot,
    ComponentFraction,
    FeedAttachEvidence,
    OilManagerSnapshot,
    StreamComposition,
    StreamSummary,
)


class HysysError(RuntimeError):
    """Raised when HYSYS cannot complete an automation request."""


class HysysController:
    PROG_IDS = ("HYSYS.Application", "HYSYS.Application.V15")
    FEED_CANDIDATES = ("FEED", "Raw Crude", "RawCrude", "CRUDE", "Crude", "Feed")

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

    def _require_com_write(self) -> None:
        """API guard — complementary PE text is not enough."""
        if not DEFAULTS.get("allow_COM_write", False):
            raise HysysError(
                "COM write blocked: allow_COM_write=false "
                "(manual Oil Manager first; flip only when inventory-approved)."
            )

    @staticmethod
    def _items(collection: Any) -> Iterable[Any]:
        count = int(collection.Count)
        for index in range(count):
            try:
                yield collection.Item(index)
            except Exception:
                try:
                    yield collection.Item(index + 1)
                except Exception:
                    continue

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

    @staticmethod
    def _safe_name(obj: Any) -> str | None:
        for attr in ("Name", "name", "Tag"):
            try:
                value = getattr(obj, attr, None)
                if value:
                    return str(value)
            except Exception:
                continue
        return None

    @staticmethod
    def _walk(root: Any, parts: tuple[str, ...]) -> Any:
        obj = root
        for part in parts:
            obj = getattr(obj, part, None)
            if obj is None:
                return None
        return obj

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
            name = self._safe_name(stream)
            if not name:
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

    def _collection_names(self, collection: Any) -> list[str]:
        names: list[str] = []
        if collection is None:
            return names
        try:
            for item in self._items(collection):
                name = self._safe_name(item)
                if name:
                    names.append(name)
        except Exception:
            try:
                count = int(collection.Count)
                for i in range(count):
                    try:
                        item = collection.Item(i)
                    except Exception:
                        item = collection.Item(i + 1)
                    name = self._safe_name(item)
                    if name:
                        names.append(name)
            except Exception:
                pass
        return names

    def _read_blend(self, blend: Any) -> BlendSummary:
        name = self._safe_name(blend) or "(unnamed blend)"
        ready: bool | None = None
        try:
            ready = bool(blend.IsReadyToInstall)
        except Exception:
            ready = None
        assay_names: list[str] = []
        try:
            assays = getattr(blend, "Assays", None)
            assay_names = self._collection_names(assays)
        except Exception:
            pass
        # Touch readable members for discovery notes (ignore failures)
        for member in BLEND_READ_MEMBERS:
            try:
                getattr(blend, member, None)
            except Exception:
                continue
        return BlendSummary(name=name, is_ready_to_install=ready, assay_names=assay_names)

    def read_oil_manager(self) -> OilManagerSnapshot:
        """Structured Oil Manager / assay / blend inventory (read-only)."""
        self._require_connection()
        snap = OilManagerSnapshot()

        oil_manager = None
        for path in OIL_MANAGER_PROBE_PATHS:
            try:
                obj = self._walk(self.case, path)
                if obj is None:
                    continue
                label = ".".join(path)
                if path[-1] == "OilManager":
                    oil_manager = obj
                    snap.found = True
                    snap.path = label
                    snap.notes.append(f"OilManager at {label}")
                else:
                    try:
                        count = int(obj.Count)
                        snap.notes.append(f"{label}: Count={count}")
                    except Exception:
                        snap.notes.append(f"{label}: present")
                    names = self._collection_names(obj)
                    if path[-1] in {"Assays", "Oils"} and names:
                        if path[-1] == "Assays":
                            snap.assay_names = names
                        else:
                            snap.oil_names = names
            except Exception as exc:
                snap.notes.append(f"{'.'.join(path)}: error ({exc})")

        if oil_manager is None:
            basis = getattr(self.case, "BasisManager", None)
            if basis is not None:
                try:
                    oil_manager = getattr(basis, "OilManager", None)
                    if oil_manager is not None:
                        snap.found = True
                        snap.path = "BasisManager.OilManager"
                except Exception:
                    pass

        if oil_manager is None and not snap.assay_names and not snap.oil_names:
            snap.error = "No Oils/OilManager/Assays found on Aspen COM paths."
            return snap

        if oil_manager is not None:
            readable: list[str] = []
            for member in OIL_MANAGER_MEMBERS:
                try:
                    if getattr(oil_manager, member, None) is not None:
                        readable.append(member)
                except Exception:
                    continue
            snap.readable_members = readable

            for coll_attr, target in (("Assays", "assay"), ("Oils", "oil")):
                try:
                    coll = getattr(oil_manager, coll_attr, None)
                    names = self._collection_names(coll)
                    if names:
                        if target == "assay":
                            snap.assay_names = names
                        else:
                            snap.oil_names = names
                        snap.notes.append(f"OilManager.{coll_attr}: {len(names)} named")
                except Exception as exc:
                    snap.notes.append(f"OilManager.{coll_attr}: {exc}")

            try:
                blends = getattr(oil_manager, "Blends", None)
                if blends is not None:
                    for blend in self._items(blends):
                        snap.blends.append(self._read_blend(blend))
                    snap.notes.append(f"Blends: {len(snap.blends)}")
            except Exception as exc:
                snap.notes.append(f"Blends: {exc}")

        return snap

    def probe_oil_manager(self) -> str:
        """String summary of structured Oil Manager read (compat)."""
        snap = self.read_oil_manager()
        if snap.error and not snap.found and not snap.assay_names:
            return (
                "No Oils/OilManager/Assays found yet (Aspen COM paths tried). "
                "See docs/intelligence/aspen/ and aspen_intelligence.py."
            )
        parts: list[str] = []
        if snap.path:
            parts.append(f"path={snap.path}")
        if snap.assay_names:
            parts.append(f"assays={len(snap.assay_names)} [{', '.join(snap.assay_names[:5])}]")
        if snap.oil_names:
            parts.append(f"oils={len(snap.oil_names)}")
        if snap.blends:
            ready = sum(1 for b in snap.blends if b.is_ready_to_install)
            parts.append(f"blends={len(snap.blends)} ready={ready}")
        if snap.readable_members:
            parts.append("members: " + ", ".join(snap.readable_members[:8]))
        parts.extend(snap.notes[:4])
        return "; ".join(parts) if parts else "Oil Manager present (empty inventory)."

    def _get_stream_object(self, stream_name: str) -> Any:
        materials = self.flowsheet.MaterialStreams
        # Prefer Item by name
        for getter in (
            lambda: materials.Item(stream_name),
            lambda: getattr(materials, stream_name),
        ):
            try:
                stream = getter()
                if stream is not None:
                    return stream
            except Exception:
                continue
        for stream in self._items(materials):
            if self._safe_name(stream) == stream_name:
                return stream
        raise HysysError(f"Material stream not found: {stream_name!r}")

    def read_stream_composition(self, stream_name: str) -> StreamComposition:
        """Read mass or mole composition for a material stream (read-only)."""
        self._require_connection()
        result = StreamComposition(stream_name=stream_name)
        try:
            stream = self._get_stream_object(stream_name)
        except HysysError as exc:
            result.error = str(exc)
            return result

        # Prefer mass; fall back to mole
        for basis, prop in (
            ("mass", "ComponentMassFractionValue"),
            ("mole", "ComponentMoleFractionValue"),
            ("mass", "ComponentMassFraction"),
            ("mole", "ComponentMoleFraction"),
        ):
            try:
                raw = getattr(stream, prop, None)
                if raw is None:
                    continue
                values = list(raw) if not isinstance(raw, (list, tuple)) else list(raw)
                names = self.get_component_names()
                # Some builds expose names on the stream
                try:
                    name_var = getattr(stream, "ComponentName", None)
                    if name_var is not None:
                        maybe = list(name_var) if not isinstance(name_var, (list, tuple)) else list(name_var)
                        if maybe and all(isinstance(x, str) or x is not None for x in maybe):
                            names = [str(x) for x in maybe]
                except Exception:
                    pass
                comps: list[ComponentFraction] = []
                for i, val in enumerate(values):
                    fname = names[i] if i < len(names) else f"comp_{i}"
                    frac = self._safe_float(val)
                    if frac is None:
                        continue
                    comps.append(
                        ComponentFraction(
                            name=str(fname),
                            fraction=frac,
                            kind=classify_component_name(str(fname)),
                        )
                    )
                if comps:
                    result.basis = basis
                    result.components = comps
                    return result
            except Exception as exc:
                result.error = f"{prop}: {exc}"
                continue

        if not result.components:
            # Fallback: classify fluid-package names only (no fractions)
            names = self.get_component_names()
            result.basis = "unknown"
            result.components = [
                ComponentFraction(name=n, fraction=None, kind=classify_component_name(n))
                for n in names
            ]
            if not result.error:
                result.error = "Composition values unavailable; classified FP names only."
        return result

    def pick_feed_stream(self, streams: list[StreamSummary] | None = None) -> str:
        """Prefer FEED / Raw Crude naming; else first material stream."""
        stream_list = streams if streams is not None else self.list_streams()
        names = [s.name for s in stream_list]
        lower_map = {n.lower(): n for n in names}
        for cand in self.FEED_CANDIDATES:
            if cand.lower() in lower_map:
                return lower_map[cand.lower()]
        return names[0] if names else ""

    def build_feed_evidence(
        self,
        oil: OilManagerSnapshot,
        composition: StreamComposition | None,
        feed_stream: str,
    ) -> FeedAttachEvidence:
        evidence = FeedAttachEvidence(feed_stream=feed_stream)
        evidence.blend_ready = oil.any_blend_ready
        if composition is not None:
            evidence.nbp_count = composition.nbp_count
            evidence.light_count = composition.light_count
            evidence.feed_attached = composition.has_nbp_slate and composition.light_count >= 1
            if composition.has_nbp_slate:
                evidence.notes.append(
                    f"FEED {feed_stream}: {composition.nbp_count} NBP/hypo + "
                    f"{composition.light_count} library lights ({composition.basis})"
                )
            elif composition.error:
                evidence.notes.append(composition.error)
        # Installed oil: blend ready OR named oils present with NBP on FEED
        evidence.oil_installed = bool(
            oil.any_blend_ready
            or (oil.oil_names and evidence.nbp_count >= 3)
            or (oil.blend_count > 0 and evidence.nbp_count >= 3)
        )
        if evidence.oil_installed:
            evidence.notes.append("Oil install evidence: blend ready and/or NBP slate on FEED.")
        elif oil.found:
            evidence.notes.append("Oil Manager found — characterize/install still unverified.")
        return evidence

    def snapshot(self, feed_stream: str | None = None) -> CaseSnapshot:
        self._require_connection()
        streams = self.list_streams()
        oil = self.read_oil_manager()
        feed = feed_stream or self.pick_feed_stream(streams)
        composition = self.read_stream_composition(feed) if feed else None
        evidence = self.build_feed_evidence(oil, composition, feed)
        return CaseSnapshot(
            case_title=self.get_case_title(),
            component_names=self.get_component_names(),
            streams=streams,
            oil_manager_hint=self.probe_oil_manager(),
            oil_manager=oil,
            feed_composition=composition,
            feed_evidence=evidence,
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

    # --- Gated COM write stubs (Phase 3; default allow_COM_write=false) -------

    def _oil_manager_object(self) -> Any:
        self._require_connection()
        for path in OIL_MANAGER_PROBE_PATHS:
            if path[-1] != "OilManager":
                continue
            obj = self._walk(self.case, path)
            if obj is not None:
                return obj
        raise HysysError("OilManager COM object not found on this case.")

    def com_add_assay(self, assay_name: str) -> None:
        self._require_com_write()
        om = self._oil_manager_object()
        assays = getattr(om, "Assays", None)
        if assays is None:
            raise HysysError("OilManager.Assays not available.")
        assays.Add(assay_name)

    def com_add_tbp_assay(self, assay_name: str) -> None:
        """Create TBP assay — live V14: Assays.Add(name, 'TBP') → AssayType=0."""
        self._require_com_write()
        om = self._oil_manager_object()
        assays = getattr(om, "Assays", None)
        if assays is None:
            raise HysysError("OilManager.Assays not available.")
        assays.Add(assay_name, "TBP")

    def com_remove_assay(self, assay_name: str) -> None:
        """Delete Input Assay by name — live V14: Assays.Remove(name).

        Matches Oil Manager → Input Assay → Delete button.
        """
        self._require_com_write()
        om = self._oil_manager_object()
        assays = getattr(om, "Assays", None)
        if assays is None:
            raise HysysError("OilManager.Assays not available.")
        try:
            assays.Remove(assay_name)
        except Exception as exc:
            raise HysysError(f"Assays.Remove({assay_name!r}) failed: {exc}") from exc

    def com_remove_assays(self, names: list[str]) -> list[str]:
        """Remove several assays; returns list of successfully removed names."""
        removed: list[str] = []
        for name in names:
            try:
                self.com_remove_assay(name)
                removed.append(name)
            except HysysError:
                continue
        return removed

    def remove_assays_live(self, names: list[str]) -> list[str]:
        """Explicit user-authorized delete — bypasses allow_COM_write for cleanup.

        Use only when the engineer asks to delete assays (Input Assay Delete).
        """
        self._require_connection()
        om = self._oil_manager_object()
        assays = getattr(om, "Assays", None)
        if assays is None:
            raise HysysError("OilManager.Assays not available.")
        removed: list[str] = []
        for name in names:
            try:
                assays.Remove(name)
                removed.append(name)
            except Exception:
                continue
        return removed

    def com_blend_add_assay(self, blend_name: str, assay_name: str) -> None:
        self._require_com_write()
        om = self._oil_manager_object()
        blends = getattr(om, "Blends", None)
        if blends is None:
            raise HysysError("OilManager.Blends not available.")
        blend = blends.Item(blend_name)
        blend.AddAssay(assay_name)

    def com_install_into_stream(self, blend_name: str, stream_name: str) -> None:
        self._require_com_write()
        om = self._oil_manager_object()
        blends = getattr(om, "Blends", None)
        if blends is None:
            raise HysysError("OilManager.Blends not available.")
        blend = blends.Item(blend_name)
        try:
            if not bool(blend.IsReadyToInstall):
                raise HysysError(f"Blend {blend_name!r} IsReadyToInstall=False.")
        except HysysError:
            raise
        except Exception:
            pass
        blend.InstallIntoStream(stream_name)

    def com_set_associated_fluid_package(self, fluid_package_name: str) -> None:
        self._require_com_write()
        om = self._oil_manager_object()
        om.SetAssociatedFluidPackage(fluid_package_name)

    def select_peng_robinson_ui(self) -> str:
        """V14: COM PropertyPackageName Let fails — click PP list via UI Automation.

        Fluid Package Set Up must be visible (Package Type HYSYS, list showing
        Peng-Robinson). Returns confirmation string.
        """
        self._require_connection()
        from hysys_ui_automation import select_peng_robinson_in_fluid_package_ui

        fp = None
        try:
            fp = self.case.BasisManager.FluidPackages.Item(0)
        except Exception:
            fp = None
        result = select_peng_robinson_in_fluid_package_ui(verify_com_fp=fp)
        if not result.ok:
            raise HysysError(
                f"Could not select Peng-Robinson in Fluid Package UI: {result.detail}"
            )
        return (
            f"Peng-Robinson selected via {result.method}; "
            f"COM read name={result.property_package_name!r} "
            f"components={result.component_count}"
        )

    def com_set_assay_bulk_stub(
        self,
        assay_name: str,
        *,
        api: float | None = None,
        molecular_weight: float | None = None,
    ) -> None:
        """Version-sensitive assay property setters — gated stub only."""
        self._require_com_write()
        om = self._oil_manager_object()
        assays = getattr(om, "Assays", None)
        if assays is None:
            raise HysysError("OilManager.Assays not available.")
        assay = assays.Item(assay_name)
        if api is not None:
            for attr in ("BulkAPIGravityValue", "APIGravityValue", "API", "APIGravity", "BulkAPI"):
                try:
                    setattr(assay, attr, api)
                    break
                except Exception:
                    continue
        if molecular_weight is not None:
            for attr in ("BulkMolecularWeightValue", "MolecularWeight", "MW", "BulkMW"):
                try:
                    setattr(assay, attr, molecular_weight)
                    break
                except Exception:
                    continue

    def com_enter_tbp_assay_seed(self, assay_name: str, seed: dict | None = None) -> str:
        """Enter bulk / LE / TBP from oil_manager_ui seed (gated). Returns status text."""
        self._require_com_write()
        from oil_manager_ui import ASSAY_TBP_WRITE_CANDIDATES, BASRAH_OIL_MANAGER_SEED

        seed = seed or BASRAH_OIL_MANAGER_SEED
        om = self._oil_manager_object()
        assay = om.Assays.Item(assay_name)
        notes: list[str] = []

        # Bulk density / API
        sg = seed.get("bulk_sg_15C")
        api = seed.get("bulk_api")
        if api is not None:
            for attr in ASSAY_TBP_WRITE_CANDIDATES["bulk_density"]:
                if "API" not in attr and attr != "BulkAPIGravityValue":
                    continue
                try:
                    setattr(assay, attr, float(api))
                    notes.append(f"set {attr}={api}")
                    break
                except Exception as exc:
                    notes.append(f"{attr} fail:{exc}")
        if sg is not None:
            # kg/m3 ≈ SG * 1000 at 15 C (approx for BulkMassDensityValue)
            rho = float(sg) * 1000.0
            for attr, val in (
                ("BulkMassDensityValue", rho),
                ("DensityValue", rho),
            ):
                try:
                    setattr(assay, attr, val)
                    notes.append(f"set {attr}={val}")
                    break
                except Exception as exc:
                    notes.append(f"{attr} fail:{exc}")

        # TBP paired percent + temperature
        temps = list(seed.get("tbp_temperature_C") or [])
        yields = list(seed.get("tbp_cumulative_wt_pct") or [])
        if temps and yields:
            try:
                assay.AssayPercentForBoilingTemperatureValue = yields
                notes.append("set AssayPercentForBoilingTemperatureValue")
            except Exception as exc:
                notes.append(f"AssayPercent fail:{exc}")
            try:
                assay.BoilingTemperatureValue = temps
                notes.append("set BoilingTemperatureValue")
            except Exception as exc:
                notes.append(f"BoilingTemperatureValue fail:{exc}")

        # Light ends
        le_pct = seed.get("light_ends_bulk_wt_pct_of_crude")
        le_comp = seed.get("light_ends_cut_wt_pct")
        try:
            assay.LightEndsCalculationType = -1  # UserInput
            notes.append("LightEndsCalculationType=-1")
        except Exception as exc:
            notes.append(f"LE calc fail:{exc}")
        if le_pct is not None:
            try:
                assay.LightEndsPercentInAssayValue = float(le_pct)
                notes.append(f"LE%={le_pct}")
            except Exception as exc:
                notes.append(f"LE% fail:{exc}")
        if le_comp is not None:
            try:
                assay.LightEndsCompositionValue = list(le_comp)
                notes.append("LE composition set")
            except Exception as exc:
                try:
                    assay.LightEndsComposition.Values = list(le_comp)
                    notes.append("LE Composition.Values set")
                except Exception as exc2:
                    notes.append(f"LE comp fail:{exc}; {exc2}")

        return "; ".join(notes)
