"""Autonomous Oil Manager fill recipe — Aspen docs + live V14 lessons.

Sources (local, not shipped):
- ``from aspen doc/AspenFeedStockAssayManager.chm`` — characterize methodology
  (Petroleum Assays / PIMS). PE rules only; not the Oil Manager COM surface.
- ``from aspen doc/xhysys.chm`` — Oil Manager / Assay / Blend COM writers
  (BulkPropertiesUsed, *Value Lets, Blend.AddAssay / InstallIntoStream,
  BasisManager.StartOilChange / EndOilChange).

Product path for CDU FEED remains **Oil Manager** (not Aspen Assay Library
Add Assays dialog). Never auto-saves ``.hsc``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from aspen_intelligence import (
    ASSAY_BASIS,
    ASSAY_CURVE_TYPE,
    ASSAY_LIGHT_ENDS_CALCULATION,
    ASSAY_LIGHT_ENDS_COMPOSITION_BASIS,
    ASSAY_TYPE,
)
from oil_manager_ui import BASRAH_OIL_MANAGER_SEED


# --- Tool choice (AspenFeedStockAssayManager vs Oil Manager) -----------------

ASSAY_SURFACE = {
    "oil_manager": {
        "use_for_cdu_feed": True,
        "ribbon": "Oil Manager",
        "com_root": "BasisManager.OilManager",
        "characterize_verb": "Calculate (assay) / UI Calculate",
        "install": "Blend.InstallIntoStream",
    },
    "petroleum_assays_library": {
        "use_for_cdu_feed": False,
        "ribbon": "Petroleum Assays → Add Assays",
        "ui_dialog": "Add Assays (Aspen Assay Library)",
        "ui_module": "petroleum_assays_ui",
        "note": (
            "Library assays (e.g. Basrah Light-2014) are characterized models, "
            "not MRC/Intertek lab masters. Do not substitute for Oil Manager Basrah."
        ),
        "source_chm": "AspenFeedStockAssayManager",
    },
    "petroleum_assays_summary": {
        "use_for_cdu_feed": False,
        "ribbon": "Petroleum Assays / Assays Summary",
        "ui_module": "petroleum_assays_ui.PETROLEUM_ASSAYS_UI_V14",
        "note": "Empty Assays Summary table — Assay Management surface, not Oil Manager.",
    },
}

# Live failure 2026-07-26 (sample.hsc): OK on Assay Components Celsius to 1150C
# → Basis-2 with ~100 cut hypos → Oil Manager LE composition COM empty → never Ready.
# Doc: docs/intelligence/02b_Oil_Manager_FP_Failure.md
OIL_MANAGER_REQUIRED_LIGHTS: tuple[str, ...] = (
    "Methane",
    "Ethane",
    "Propane",
    "i-Butane",
    "n-Butane",
    "i-Pentane",
    "n-Pentane",
)
# Optional CompList pad — not in Intertek LE table
OIL_MANAGER_OPTIONAL_H2O = "H2O"

# Names that prove Petroleum Assays "assay-compatible" slate was installed
ASSAY_COMPATIBLE_SLATE_MARKERS: tuple[str, ...] = (
    "36-40C*",
    "1150+C*",
    "Assay Components",
    "850C",
    "1150C",
)


def preflight_oil_manager_fp(component_names: list[str] | tuple[str, ...]) -> list[str]:
    """Return blockers — empty list means FP is OK to attempt Oil Manager LE fill.

    Refuses Petroleum Assays Celsius/1150-style cut slates and missing C1–nC5 lights.
    """
    names = [str(n) for n in component_names]
    upper = {n.upper() for n in names}
    blockers: list[str] = []

    for marker in ASSAY_COMPATIBLE_SLATE_MARKERS:
        if any(marker.upper() in n.upper() for n in names):
            blockers.append(
                f"FP looks like Petroleum Assays slate (saw {marker!r}) — "
                "Oil Manager LE COM will fail. Use C1–nC5 CompList only; "
                "do not OK Assay Components Celsius to 1150C for MRC FEED."
            )
            break

    # Celsius cut hypos e.g. 40-50C*
    cut_hypos = [n for n in names if n.endswith("C*") or n.endswith("F*")]
    if len(cut_hypos) >= 10:
        blockers.append(
            f"FP has {len(cut_hypos)} cut hypos (*C/*F) — Assay Management slate, "
            "not Oil Manager lights-first CompList."
        )

    missing = [L for L in OIL_MANAGER_REQUIRED_LIGHTS if L.upper() not in upper]
    if missing:
        blockers.append(
            "Missing Oil Manager lights before LE write: "
            + ", ".join(missing)
            + ". Add CompList (C1–nC5) first — Intertek LE needs those pure comps."
        )

    return blockers


# Hard PE order after 2026-07-26 failure (do not thrash Petroleum Assays mid-fill)
MRC_OIL_MANAGER_ORDER: tuple[str, ...] = (
    "1. Component list = C1–nC5 (+ H2O optional) ONLY — never Assay Components 1150C",
    "2. Fluid package PR attached; Basis Input Complete",
    "3. Oil Manager SetAssociatedFluidPackage(that FP)",
    "4. Bulk Used + SG; LE user-input (Intertek 7 comps); TBP °C mass",
    "5. Calculate → Blend → Install → verify NBP* count (not Status alone)",
)


# xhysys BasisManager oil-edit transaction (docs)
OIL_CHANGE_TRANSACTION = (
    "BasisManager.StartOilChange",
    "… assay / blend writes …",
    "BasisManager.EndOilChange",  # when CanEndOilChange
)


@dataclass
class CharacterizeFillPlan:
    """Ordered COM steps to fill TBP assay → blend → install."""

    assay_name: str
    blend_name: str
    stream_name: str
    fluid_package: str
    seed: dict[str, Any]
    steps: list[str] = field(default_factory=list)
    pe_gates: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


def build_basrah_fill_plan(
    seed: dict[str, Any] | None = None,
    *,
    assay_name: str | None = None,
    blend_name: str = "BasrahBlend",
    stream_name: str = "Raw Crude",
    fluid_package: str = "Basis-1",
) -> CharacterizeFillPlan:
    seed = dict(seed or BASRAH_OIL_MANAGER_SEED)
    assay = assay_name or str(seed.get("assay_name") or "Basrah")
    plan = CharacterizeFillPlan(
        assay_name=assay,
        blend_name=blend_name,
        stream_name=stream_name,
        fluid_package=fluid_package,
        seed=seed,
    )
    plan.pe_gates = [
        "PREFLIGHT: FP = C1–nC5 lights only — refuse Assay Components 1150C / *C* cut slate",
        "Prefer lab/Intertek master over Aspen Assay Library commercial assay",
        "TBP primary; never invent D86",
        "LE composition = of LE cut (~100%), not whole crude — Intertek 7 comps only",
        "No silent TBP extrapolation past last lab point",
        "Bulk Properties Used + bulk SG (Aspen: bulk density missing → Watson K skip)",
        "COM BoilingTemperatureValue in °C (UI [F] is display)",
        "Never auto-save .hsc",
        "If LE COM empty → stop (wrong FP), do not thrash Petroleum Assays",
    ]
    plan.steps = [
        "PREFLIGHT preflight_oil_manager_fp(FP.Components) — abort if blockers",
        f"SetAssociatedFluidPackage({fluid_package!r})",
        "BasisManager.StartOilChange  # xhysys — allows oil edits",
        f"Assays.Add({assay!r}, 'TBP') if missing  # AssayType at_TBP={ASSAY_TYPE['at_TBP']}",
        "Open assay form (UIA) if writers Access Denied without oil-change/form",
        f"Basis={ASSAY_BASIS['ab_MassFraction']}  # Mass",
        "BulkPropertiesUsed=True",
        f"BulkMassDensityValue = SG*{1000}  # kg/m3 from bulk_sg_15C",
        f"InputDensityType/MW/Viscosity = ac_NotUsed ({ASSAY_CURVE_TYPE['ac_NotUsed']})",
        f"LightEndsCalculationType=alect_UserInputLightEnds ({ASSAY_LIGHT_ENDS_CALCULATION['alect_UserInputLightEnds']})",
        f"LightEndsCompositionBasis=alecb_MassFraction ({ASSAY_LIGHT_ENDS_COMPOSITION_BASIS['alecb_MassFraction']})",
        "LightEndsPercentInAssayValue + LightEndsCompositionValue (C1–nC5 order; H2O=0 if present)",
        "AssayPercentForBoilingTemperatureValue + BoilingTemperatureValue (°C)",
        "assay.Calculate() / UI Calculate  # until Assay Was Calculated",
        f"Blends.Add({blend_name!r}) if missing",
        f"blend.AddAssay({assay!r})",
        "wait IsReadyToInstall — if False after LE, STOP (do not Install)",
        f"Ensure MaterialStream {stream_name!r} exists",
        f"blend.InstallIntoStream({stream_name!r})",
        "BasisManager.EndOilChange",
        "VERIFY: FP Components include NBP*; Raw Crude composition nonzero (not Status alone)",
    ]
    plan.notes = [
        "AspenFeedStockAssayManager = Petroleum Assays methodology; Oil Manager = this product COM.",
        "Library 'Add Assays' dialog is out of scope for MRC Basrah fill.",
        "Output Blend Status 'Installed - in <stream> on <FP>' can lie — count NBP* hypos.",
        "Do not set BoilingTemperatureExtrapolationMethod unless engineer opts in.",
        "2026-07-26: Basis-2 Assay Components 1150C blocked LE — see 02b_Oil_Manager_FP_Failure.md",
        *MRC_OIL_MANAGER_ORDER,
    ]
    return plan


def format_fill_plan(plan: CharacterizeFillPlan | None = None) -> str:
    plan = plan or build_basrah_fill_plan()
    lines = [
        "--- Oil characterize fill (Aspen-informed) ---",
        f"Assay={plan.assay_name} Blend={plan.blend_name} "
        f"Stream={plan.stream_name} FP={plan.fluid_package}",
        "Oil Manager surface (not Aspen Assay Library).",
        "",
        "PE gates:",
    ]
    for g in plan.pe_gates:
        lines.append(f"  • {g}")
    lines.append("")
    lines.append("Steps:")
    for i, s in enumerate(plan.steps, 1):
        lines.append(f"  {i}. {s}")
    lines.append("")
    lines.append("Notes:")
    for n in plan.notes:
        lines.append(f"  • {n}")
    return "\n".join(lines)
