"""Aspen-sourced intelligence for HYSYS oil characterization (coded).

Pertinent knowledge curated from Aspen help CHMs in `from aspen doc/`:
- xhysys.chm — HYSYS Oil Manager / Assay COM enumerations & OilManager members
- AspenFeedStockAssayManager.chm — conventional characterization methodology

Does NOT copy Aspen copyrighted help verbatim into the product UI.
Does NOT enable silent COM writes. Enums support future gated automation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SOURCE_NOTE = (
    "Curated from Aspen HYSYS Customization (xhysys) Oil Manager / Assay enums "
    "and Aspen Feedstock Assay Management characterize overview. "
    "Not an AspenTech product; verify against your HYSYS build."
)


# --- HYSYS COM enumerations (xhysys) -----------------------------------------

ASSAY_TYPE = {
    "at_TBP": 0,
    "at_D86": 1,
    "at_D1160": 2,
    "at_D86D1160": 3,
    "at_ASTMD2887": 4,
    "at_Chromatograph": 5,
    "at_EFV": 6,
    "at_BulkPropertiesOnly": 7,
}

ASSAY_BASIS = {
    "ab_LiquidVolumeFraction": -1,
    "ab_MoleFraction": -2,
    "ab_MassFraction": -3,
}

ASSAY_CURVE_TYPE = {
    "ac_NotUsed": 0,
    "ac_Dependent": 1,
    "ac_Independent": 2,
}

ASSAY_EXTRAPOLATION_METHOD = {
    "aem_LeastSquares": 1,
    "aem_LaGrange": 2,
    "aem_Probability": 3,
}

ASSAY_LIGHT_ENDS_CALCULATION = {
    "alect_IgnoreLightEnds": 0,
    "alect_UserInputLightEnds": -1,
    "alect_AutoCalculateLightEnds": -4,
}

ASSAY_LIGHT_ENDS_COMPOSITION_BASIS = {
    "alecb_LiquidVolumeFraction": -1,
    "alecb_MoleFraction": -2,
    "alecb_MassFraction": -3,
    "alecb_MoleFlow": -5,
    "alecb_MassFlow": -6,
    "alecb_LiquidVolumeFlow": -7,
}


# OilManager members pertinent to FEED characterization (xhysys OilManager topic)
OIL_MANAGER_MEMBERS = (
    "Blends",
    "CorrelationSets",
    "DefaultD2887Type",
    "DefaultD86Type",
    "FBPCutPoint",
    "FBPCutPointValue",
    "IBPCutPoint",
    "IBPCutPointValue",
    "IbpFbpBasis",
    "SetAssociatedFluidPackage",
)

# Probe paths to try when discovering Oil Manager on a live case
OIL_MANAGER_PROBE_PATHS = (
    ("BasisManager", "OilManager"),
    ("OilManager",),
    ("BasisManager", "Oils"),
    ("BasisManager", "Assays"),
)


# --- Characterization methodology (Assay Management conventional) ------------

CHARACTERIZATION_RULES = (
    "Characterize = build an assay model from limited lab data (estimate, re-cut, fill props).",
    "Conventional method uses many micro-cuts from IBP to FBP (narrow boiling slices).",
    "Prefer entered TBP distillation; otherwise build TBP from cut yields if adequate.",
    "Components lighter than n-Pentane belong in whole crude and light-end cut — not all naphtha cuts.",
    "Blend assays are made from already-characterized assays (no Input Assay on the blend).",
    "HYSYS exposes assay extrapolation methods — our PE gate forbids silent TBP extrapolation.",
)


@dataclass
class AspenEntryPlan:
    """Recommended HYSYS Oil Manager entry settings for an assay JSON."""

    assay_type_name: str
    assay_type_value: int
    assay_basis_name: str
    assay_basis_value: int
    light_ends_calc_name: str
    light_ends_calc_value: int
    light_ends_comp_basis_name: str
    light_ends_comp_basis_value: int
    allow_extrapolation: bool
    notes: list[str] = field(default_factory=list)
    oil_manager_members: tuple[str, ...] = OIL_MANAGER_MEMBERS


def recommend_hysys_entry(assay: dict[str, Any]) -> AspenEntryPlan:
    """Map our assay JSON → Aspen/HYSYS Oil Manager entry choices (PE default)."""
    notes: list[str] = [
        SOURCE_NOTE,
        "Manual Oil Manager first — this plan is guidance, not a COM write.",
    ]

    tbp_points = (assay.get("tbp") or {}).get("points") or []
    d86_points = (assay.get("astm_d86") or {}).get("points") or []
    has_tbp = len(tbp_points) >= 5
    has_d86 = any(
        p.get("temperature_C") is not None and p.get("cumulative_vol_pct") is not None
        for p in d86_points
    )

    if has_tbp:
        type_name = "at_TBP"
        notes.append("TBP present — prefer AssayType at_TBP (0). Do not invent D86.")
    elif has_d86:
        type_name = "at_D86"
        notes.append("Only D86 present — AssayType at_D86; convert carefully.")
    else:
        type_name = "at_BulkPropertiesOnly"
        notes.append("No distillation — bulk-only is weak for CDU FEED; obtain TBP.")

    # Our MRC pack uses cumulative wt% TBP and LE as wt% of cut → mass basis
    basis_name = "ab_MassFraction"
    notes.append("Assay basis ab_MassFraction — matches proposal wt% TBP / LE.")

    le = assay.get("light_ends") or {}
    bulk_le = le.get("light_ends_bulk_wt_pct_of_crude")
    comps = le.get("components") or {}
    has_le = bulk_le is not None and any(v is not None for v in comps.values())

    if has_le:
        le_calc = "alect_UserInputLightEnds"
        notes.append(
            "User-input light ends (alect_UserInputLightEnds). "
            "Composition is OF_LIGHT_ENDS_CUT in our JSON — normalize to whole-crude before OM."
        )
    else:
        le_calc = "alect_IgnoreLightEnds"
        notes.append("No LE data — IgnoreLightEnds until lab LE available.")

    le_comp_basis = "alecb_MassFraction"
    notes.append("LE composition basis alecb_MassFraction (wt%).")

    # Binding PE: never silent extrapolation even though Aspen offers methods
    allow_extrap = False
    notes.append(
        "Extrapolation methods exist (LeastSquares/LaGrange/Probability) — "
        "do NOT apply silently to fake TBP coverage (our OX gate)."
    )

    return AspenEntryPlan(
        assay_type_name=type_name,
        assay_type_value=ASSAY_TYPE[type_name],
        assay_basis_name=basis_name,
        assay_basis_value=ASSAY_BASIS[basis_name],
        light_ends_calc_name=le_calc,
        light_ends_calc_value=ASSAY_LIGHT_ENDS_CALCULATION[le_calc],
        light_ends_comp_basis_name=le_comp_basis,
        light_ends_comp_basis_value=ASSAY_LIGHT_ENDS_COMPOSITION_BASIS[le_comp_basis],
        allow_extrapolation=allow_extrap,
        notes=notes,
    )


def format_aspen_block(assay: dict[str, Any] | None = None) -> str:
    """PE-board block: Aspen methodology + optional entry plan."""
    lines = [
        "--- Aspen intelligence (coded) ---",
        SOURCE_NOTE,
        "",
        "Characterize methodology:",
    ]
    for rule in CHARACTERIZATION_RULES:
        lines.append(f"  • {rule}")

    lines.append("")
    lines.append("OilManager COM members (discover/read):")
    lines.append("  " + ", ".join(OIL_MANAGER_MEMBERS))

    if assay is None:
        lines.append("")
        lines.append("Load an assay JSON for HYSYS entry plan (type/basis/LE enums).")
        return "\n".join(lines)

    plan = recommend_hysys_entry(assay)
    lines.append("")
    lines.append("Recommended HYSYS entry (this assay):")
    lines.append(
        f"  AssayType: {plan.assay_type_name} = {plan.assay_type_value}"
    )
    lines.append(
        f"  AssayBasis: {plan.assay_basis_name} = {plan.assay_basis_value}"
    )
    lines.append(
        f"  LightEndsCalc: {plan.light_ends_calc_name} = {plan.light_ends_calc_value}"
    )
    lines.append(
        f"  LightEndsCompBasis: {plan.light_ends_comp_basis_name} = "
        f"{plan.light_ends_comp_basis_value}"
    )
    lines.append(f"  Allow silent extrapolation: {plan.allow_extrapolation}")
    lines.append("")
    lines.append("Notes:")
    for note in plan.notes:
        lines.append(f"  → {note}")
    return "\n".join(lines)


def enum_lookup(table: dict[str, int], value: int) -> str | None:
    for name, val in table.items():
        if val == value:
            return name
    return None
