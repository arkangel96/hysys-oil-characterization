"""Aspen-sourced intelligence for HYSYS oil characterization (coded).

Pertinent knowledge curated from Aspen help CHMs in `from aspen doc/`:
- xhysys.chm — HYSYS Oil Manager / Assay / Blend / ProcessStream COM
- AspenFeedStockAssayManager.chm — conventional characterization methodology

Does NOT copy Aspen copyrighted help verbatim into the product UI.
Does NOT enable silent COM writes. Enums + map support gated automation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


SOURCE_NOTE = (
    "Curated from Aspen HYSYS Customization (xhysys) Oil Manager / Assay / Blend "
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


# OilManager members (xhysys OilManager topic)
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

# Blend members pertinent to FEED install (xhysys blend_object)
BLEND_READ_MEMBERS = (
    "Assays",
    "IsReadyToInstall",
    "CutOptionType",
    "ComponentName",
    "ComponentNBP",
    "ComponentNBPValue",
    "NumberOfCuts",
    "NumberOfCutsValue",
)

BLEND_WRITE_METHODS = (
    "AddAssay",
    "RemoveAssay",
    "InstallIntoStream",
)

# ProcessStream composition reads (xhysys ProcessStream)
STREAM_COMPOSITION_PROPS = (
    "ComponentMassFractionValue",
    "ComponentMoleFractionValue",
    "ComponentName",
)

# Probe paths to try when discovering Oil Manager on a live case
OIL_MANAGER_PROBE_PATHS = (
    ("BasisManager", "OilManager"),
    ("OilManager",),
    ("BasisManager", "Oils"),
    ("BasisManager", "Assays"),
)

# Names that look like library lights (case-insensitive contains / exact-ish)
LIBRARY_LIGHT_TOKENS = (
    "methane",
    "ethane",
    "propane",
    "i-butane",
    "ibutane",
    "n-butane",
    "nbutane",
    "i-pentane",
    "ipentane",
    "n-pentane",
    "npentane",
    "h2o",
    "water",
    "nitrogen",
    "co2",
    "h2s",
    "hydrogen",
)

# Hypo / NBP name patterns
NBP_NAME_PREFIXES = ("NBP", "Hypo", "HC_")


# HYSYS Properties ribbon — which tool for crude FEED characterization (V14 UI + manuals)
# Screenshot Home: Refining | Oil | Hypotheticals
CHARACTERIZATION_TOOL_CHOICE = {
    "primary": "Oil Manager",
    "ribbon_group": "Oil",
    "why": (
        "xhysys COM documents OilManager / Assays / Blend.InstallIntoStream — "
        "this produces library lights + NBP[0]* on FEED/Raw Crude Worksheet "
        "(target composition contract)."
    ),
    "not_petroleum_assays": (
        "Petroleum Assays (Refining) is Aspen Assay Management / refining assay UI. "
        "Useful later for assay library work; not the COM path we use for CDU FEED "
        "install of Oil Manager hypocomponents."
    ),
    "not_hypotheticals_manager": (
        "Hypotheticals Manager edits hypo components manually. "
        "Hypos are the OUTPUT of Oil Manager characterize — do not enter TBP/LE there."
    ),
    "com_objects": (
        "BasisManager.OilManager",
        "OilManager.Assays",
        "OilManager.Blends",
        "Blend.InstallIntoStream",
    ),
}


def format_tool_choice_block() -> str:
    c = CHARACTERIZATION_TOOL_CHOICE
    return "\n".join(
        [
            "--- HYSYS tool choice (manual + V14 UI) ---",
            f"Use: {c['primary']} (ribbon: {c['ribbon_group']})",
            f"Why: {c['why']}",
            f"Not Petroleum Assays: {c['not_petroleum_assays']}",
            f"Not Hypotheticals Manager: {c['not_hypotheticals_manager']}",
            "COM: " + ", ".join(c["com_objects"]),
        ]
    )


# Fluid Package Set Up — V14 UI contract (screenshot + live COM/UIA 2026-07-25)
FLUID_PACKAGE_UI_V14 = {
    "package_type": "HYSYS",
    "component_list_selection_suffix": "[HYSYS Databanks]",
    "property_package_selection": "Peng-Robinson",
    "property_package_none": "<none>",
    "status_need_pp": "Select property package",
    "com_setter_works": False,  # PropertyPackageName Let rejected on V14
    "uia_click_works": True,  # click list text then COM-read succeeds
}

# Capability map: read vs gated write (OC-ASPEN-03)
COM_CAPABILITY_MAP: tuple[dict[str, str], ...] = (
    {"capability": "connect_open_streams_solve", "access": "read", "status": "coded"},
    {"capability": "oil_manager_inventory", "access": "read", "status": "coded"},
    {"capability": "assays_collection_names", "access": "read", "status": "coded"},
    {"capability": "blend_is_ready_to_install", "access": "read", "status": "coded"},
    {"capability": "stream_composition_mass_mole", "access": "read", "status": "coded"},
    {"capability": "classify_lights_vs_nbp", "access": "read", "status": "coded"},
    {"capability": "verify_install_attach", "access": "read", "status": "coded"},
    {"capability": "component_list_add_lights", "access": "write", "status": "proven_live"},
    {"capability": "fluid_package_add_attach_list", "access": "write", "status": "proven_live"},
    {
        "capability": "select_peng_robinson",
        "access": "write",
        "status": "proven_uia",  # COM Let fails; UI click works
    },
    {"capability": "assays_add_tbp", "access": "write", "status": "proven_live"},
    {"capability": "assays_collection_add", "access": "write", "status": "gated_stub"},
    {"capability": "blend_add_assay", "access": "write", "status": "gated_stub"},
    {"capability": "blend_install_into_stream", "access": "write", "status": "gated_stub"},
    {"capability": "set_associated_fluid_package", "access": "write", "status": "proven_live"},
    {"capability": "assay_tbp_le_bulk_setters", "access": "write", "status": "gated_stub"},
    {"capability": "auto_save_hsc", "access": "write", "status": "forbidden"},
)


# --- Characterization methodology (Assay Management conventional) ------------

CHARACTERIZATION_RULES = (
    "Characterize = build an assay model from limited lab data (estimate, re-cut, fill props).",
    "Conventional method uses many micro-cuts from IBP to FBP (narrow boiling slices).",
    "Prefer entered TBP distillation; otherwise build TBP from cut yields if adequate.",
    "Components lighter than n-Pentane belong in whole crude and light-end cut — not all naphtha cuts.",
    "Blend assays are made from already-characterized assays (no Input Assay on the blend).",
    "HYSYS exposes assay extrapolation methods — our PE gate forbids silent TBP extrapolation.",
    "Blend.InstallIntoStream(StreamName) installs calculated oil into a named material stream.",
    "Blend.IsReadyToInstall must be true before install (read-verify path).",
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


def classify_component_name(name: str) -> str:
    """Return 'light', 'nbp', or 'other' for a fluid-package / stream component name."""
    lower = (name or "").strip().lower()
    if not lower:
        return "other"
    for token in LIBRARY_LIGHT_TOKENS:
        if token in lower.replace(" ", ""):
            return "light"
    upper = (name or "").strip().upper()
    for prefix in NBP_NAME_PREFIXES:
        if upper.startswith(prefix.upper()):
            return "nbp"
    if "NBP[" in upper or "NBP*" in upper:
        return "nbp"
    return "other"


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

    allow_extrap = False
    notes.append(
        "Extrapolation methods exist (LeastSquares/LaGrange/Probability) — "
        "do NOT apply silently to fake TBP coverage (our OX gate)."
    )
    notes.append(
        "After characterize: confirm Blend.IsReadyToInstall, then InstallIntoStream(FEED)."
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


def format_com_capability_block() -> str:
    lines = ["COM capability map (Aspen-curated):"]
    for row in COM_CAPABILITY_MAP:
        lines.append(
            f"  • {row['capability']}: {row['access']} — {row['status']}"
        )
    lines.append("")
    lines.append("Fluid Package Set Up (V14 UI):")
    lines.append(f"  Package Type: {FLUID_PACKAGE_UI_V14['package_type']}")
    lines.append(
        f"  Property Package Selection: {FLUID_PACKAGE_UI_V14['property_package_selection']}"
    )
    lines.append(
        f"  COM setter works: {FLUID_PACKAGE_UI_V14['com_setter_works']} | "
        f"UIA click works: {FLUID_PACKAGE_UI_V14['uia_click_works']}"
    )
    return "\n".join(lines)


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
    lines.append("")
    lines.append("Blend members (read/verify):")
    lines.append("  " + ", ".join(BLEND_READ_MEMBERS))
    lines.append("")
    lines.append(format_com_capability_block())
    lines.append("")
    lines.append(format_tool_choice_block())
    lines.append("")
    from oil_manager_ui import format_oil_manager_ui_block

    lines.append(format_oil_manager_ui_block())

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
