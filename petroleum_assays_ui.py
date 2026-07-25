"""Petroleum Assays / Assays Summary UI intelligence (HYSYS V14).

Learned from live screenshot 2026-07-25 (Properties → Petroleum Assays)
and AspenFeedStockAssayManager help (Assays Summary / Characterize).

This is **Aspen Assay Management** (refining / PIMS-style), NOT classic
Oil Manager. CDU FEED + NBP[0]* install for this product stays on
``oil_manager_ui`` / ``characterize_fill_live``.

Ribbon Oil group still shows Oil Manager + Convert to Refining Assay —
do not confuse the two entry points.
"""

from __future__ import annotations

from typing import Any


# Exact UI from V14 Assays Summary (empty table screenshot)
PETROLEUM_ASSAYS_UI_V14: dict[str, Any] = {
    "tree_path": ("Properties", "Petroleum Assays"),
    "tab_title": "Petroleum Assays",
    "form_title": "Assays Summary",
    "ribbon_tab": "Assay Management",  # when Petroleum Assays selected
    "display_filter": "All Region",
    "default_fluid_package_label": "Default Fluid Package",
    "table_columns": (
        "Assay",
        "Characterization Method",
        "Status",
        "Fluid Package",
        "From Source",
        "Density [lb/ft3]",
        "Sulfur %",
        "Viscosity @ 100 F [cSt]",
        "Watson K",
        "Add Property/Description",
    ),
    "table_has_filter_row": True,  # "=" filter cells under headers
    "buttons": (
        "Add",  # dropdown for New / library / etc.
        "Export",
        "Copy",
        "Delete",
    ),
    "buttons_disabled_when_empty": ("Export", "Copy", "Delete"),
    "add_opens": (
        "New assay (manual Input Assay path in Assay Management)",
        "Add Assays library picker (Aspen Assay Library) — see ADD_ASSAYS_DIALOG",
    ),
    "sibling_tree_items": (
        "Component Lists",
        "Fluid Packages",
        "Petroleum Assays",
        "Oil Manager",
        "Reactions",
        "Component Maps",
        "User Properties",
    ),
    "ribbon_groups_seen": (
        "Navigate",
        "Components",  # Map Components, Update Properties
        "Refining",  # Petroleum Assays, Hypotheticals Manager, Convert, Remove Duplicates
        "Oil",  # Oil Manager, Convert to Refining Assay, Associate Fluid Package, Definitions, Options
        "PVT Data",
    ),
    "use_for_mrc_cdu_feed": False,
    "reason_not_primary": (
        "Assays Summary / Petroleum Assays is Aspen Assay Management. "
        "MRC Basrah/Mishrif Intertek proposal → Oil Manager TBP → Blend.InstallIntoStream "
        "for Raw Crude + NBP[0]*. Library commercial assays are characterized models, not lab masters."
    ),
}


# Petroleum Assays Add workflow (live V14, 2026-07-25 → 2026-07-26)
# What actually happens when you click Add with no assay-compatible list:
PETROLEUM_ASSAYS_ADD_WORKFLOW_V14: dict[str, Any] = {
    "steps": (
        "Assays Summary → Add",
        "Assay Component Selection (gate — no assay-compatible list yet)",
        "Pick common list + OK  →  Aspen installs that preset into the case",
        "Add Assays (Aspen Assay Library picker) opens",
        "Select commercial assay row → OK (disabled until a row is selected)",
    ),
    "why_1150c_unlocked_library": (
        "Assay Component Selection is a *prerequisite gate*, not the assay itself. "
        "OK on 'Assay Components Celsius to 1150C' installs Aspen's whole-crude "
        "°C/1150 NBP component slate into the case. Once an assay-compatible list "
        "exists, Petroleum Assays proceeds to Add Assays (library). That is why "
        "this dialog appeared after your pick — expected, not an error."
    ),
    "what_1150c_is_not": (
        "Not Basrah/Mishrif assay data. Not Intertek TBP/LE/bulk. Not Oil Manager "
        "Input Assay. It is only the hypo/component temperature grid Petroleum "
        "Assays will use when characterizing library (or manual) assays."
    ),
    "mrc_after_this_dialog": (
        "Cancel Add Assays. Leave the installed Assay Components Celsius to 1150C "
        "list alone (or delete later if unwanted). Return to Oil Manager and fill "
        "from MRC_GIVENS — library Basrah Light-2014 is a commercial model, not "
        "the Intertek master."
    ),
    "use_for_mrc_cdu_feed": False,
}


# Assay Component Selection dialog (V14) — appears on Add when no assay-compatible
# component list exists. Options captured live 2026-07-25 (dropdown expanded).
ASSAY_COMPONENT_SELECTION_DIALOG_V14: dict[str, Any] = {
    "title": "Assay Component Selection",
    "prompt": (
        "There is no assay compatible component list added in this case. "
        "Please choose one of the common assay component lists from the drop down "
        "below, or return the Component List page and create a custom one."
    ),
    "dropdown": "common assay component lists (Aspen presets)",
    # Live V14 options (screenshot 2026-07-25 — still NOT in Aspen CHMs).
    "dropdown_options_known": (
        "Assay Components Celsius to 850C",
        "Assay Components Celsius to 1150C",
        "Assay Components Fahrenheit to 1500F",
        "Assay Components Fahrenheit to 2000F",
        "FCC Components Celsius",
        "FCC Components Fahrenheit",
        "Hydrocracker Components Celsius",
        "Hydrocracker Components Fahrenheit",
        "Reformer Components Celsius",
        "Reformer Components Fahrenheit",
    ),
    "dropdown_options_source": (
        "Live HYSYS V14 UI (Assay Component Selection dropdown expanded 2026-07-25). "
        "NOT in AspenFeedStockAssayManager / xhysys / ww10_* CHMs."
    ),
    # PE pick if forced onto this surface (whole-crude CDU assay, °C TBP):
    "preferred_if_forced": "Assay Components Celsius to 1150C",
    "preferred_why": (
        "Whole-crude assay slate in °C with high NBP ceiling (1150 °C) — covers "
        "heavy residue. 850 °C may clip vacuum-residue hypos. F presets are unit "
        "mirrors. FCC / Hydrocracker / Reformer are unit-specific slates, not "
        "whole-crude CDU FEED."
    ),
    "next_dialog_after_ok": "Add Assays",  # proven live 2026-07-26
    "buttons": ("OK", "Cancel"),
    "message_bar": (
        "Required Info : Components -- Empty component list",
        "Updated fluid package xml data is invalid.",
    ),
    # KEY LEARNING (PE): Petroleum Assays needs a large *assay-compatible*
    # component slate, NOT our 8-light CompList1 (C1-nC5 + H2O). CompList1 is
    # fine for Oil Manager hypo install but is rejected here as "empty".
    "why_it_blocks_us": (
        "CompList1 (8 lights) is not an assay-compatible component list. "
        "Petroleum Assays expects a common/large assay slate. This is hard "
        "confirmation the surfaces differ — do NOT retrofit CompList1 here."
    ),
    "mrc_action": "Cancel — return to Oil Manager for MRC Basrah/Mishrif FEED.",
    "use_for_mrc_cdu_feed": False,
}


# Add Assays dialog (Aspen Assay Library) — live after Component Selection OK
# (2026-07-26: opened after Assay Components Celsius to 1150C).
ADD_ASSAYS_DIALOG_V14: dict[str, Any] = {
    "title": "Add Assays",
    "opened_after": (
        "Assay Component Selection OK "
        "(or Add when an assay-compatible list already exists)"
    ),
    "search_criteria": (
        "Select library",  # default: All
        "Assay name",  # free text
        "Region",  # default: All Regions
        "Country",  # default: All Countries
    ),
    "search_defaults": {
        "Select library": "All",
        "Assay name": "",
        "Region": "All Regions",
        "Country": "All Countries",
    },
    "property_filter_columns": ("Property", "Minimum", "Maximum", "Unit"),
    "property_filters": (
        "Density [lb/ft3]",
        "Sulfur %",
        "KinematicViscosity @ 100 F [cSt]",
        "TAN [mg KOH/g]",
        "Pour Point [F]",
    ),
    "select_assay_section": "Select Assay",
    # Exact headers from live dump 2026-07-26 (see aspen_assay_library_catalog)
    "select_table_columns": (
        "Assay",
        "Library Name",
        "Assay Date",
        "Region",
        "Country",
        "Density lb/ft3",
        "Sulfur %",
        "KinematicViscosity @ 100 F cSt",
        "TAN(mg KOH/g) mg KOH/g",
        "Pour Point F",
        "Blank",
    ),
    "table_has_column_filters": True,
    "library_name_seen": "Aspen Assay Library",
    "catalog_module": "aspen_assay_library_catalog",
    "basrah_search": {
        "Assay name": "Basrah",
        "Region": "Middle East",
        "Country": "Iraq",
    },
    "example_hit": {
        "assay": "Basrah Light-2014",
        "library": "Aspen Assay Library",
        "region": "Middle East",
        "country": "Iraq",
        "how_to_find": "Type 'Basrah' in Assay name; Country=Iraq",
        "note": "Commercial library model — not Intertek master",
    },
    "buttons": ("Clear", "Commercial Library", "OK", "Cancel"),
    "ok_disabled_until_selection": True,  # gray until a row is selected
    "use_for_mrc_cdu_feed": False,
    "mrc_action": (
        "Cancel — Aspen Assay Library commercial assays are not Intertek masters. "
        "MRC Basrah/Mishrif stay on Oil Manager from MRC_GIVENS. "
        "Mishrif not present under that name in the library dump."
    ),
}


# Map MRC givens → summary-table columns (informational only; do not auto-fill here)
def mrc_bulk_to_summary_display(bulk: dict[str, Any]) -> dict[str, Any]:
    """Convert MRC bulk fields to Assays Summary display units (reference).

    Density in summary is lb/ft3; MRC gives SG @15.6 C.
    Approximate: lb/ft3 ≈ SG * 62.428 (water @60 F).
    Viscosity @100 F is not in MRC table (only 20/40 C) — leave None.
    """
    sg = bulk.get("specific_gravity_15C")
    density_lb_ft3 = None
    if sg is not None:
        density_lb_ft3 = round(float(sg) * 62.428, 4)
    return {
        "Density [lb/ft3]": density_lb_ft3,
        "Sulfur %": bulk.get("sulfur_wt_pct"),
        "Viscosity @ 100 F [cSt]": None,  # not in proposal bulk table
        "Watson K": bulk.get("kuop"),
        "note": "Display mapping only — do not use Petroleum Assays for MRC FEED fill",
    }


def format_petroleum_assays_ui_block() -> str:
    ui = PETROLEUM_ASSAYS_UI_V14
    wf = PETROLEUM_ASSAYS_ADD_WORKFLOW_V14
    lines = [
        "--- Petroleum Assays / Assays Summary (V14 learned) ---",
        "Tree: " + " → ".join(ui["tree_path"]),
        f"Form: {ui['form_title']} | Display: {ui['display_filter']}",
        "Columns: " + " | ".join(ui["table_columns"]),
        "Buttons: " + " | ".join(ui["buttons"]),
        f"Use for MRC CDU FEED: {ui['use_for_mrc_cdu_feed']}",
        ui["reason_not_primary"],
        "",
        "Add workflow (live):",
        *[f"  {i}. {s}" for i, s in enumerate(wf["steps"], 1)],
        f"  Why 1150C → library: {wf['why_1150c_unlocked_library']}",
        f"  MRC after Add Assays: {wf['mrc_after_this_dialog']}",
        "",
        "Add → Assay Component Selection dialog:",
        f"  {ASSAY_COMPONENT_SELECTION_DIALOG_V14['prompt']}",
        "  Options (live V14):",
        *[f"    • {o}" for o in ASSAY_COMPONENT_SELECTION_DIALOG_V14["dropdown_options_known"]],
        f"  If forced: {ASSAY_COMPONENT_SELECTION_DIALOG_V14['preferred_if_forced']}",
        f"  Next after OK: {ASSAY_COMPONENT_SELECTION_DIALOG_V14['next_dialog_after_ok']}",
        f"  Blocks because: {ASSAY_COMPONENT_SELECTION_DIALOG_V14['why_it_blocks_us']}",
        f"  MRC action: {ASSAY_COMPONENT_SELECTION_DIALOG_V14['mrc_action']}",
        "",
        "Add Assays (library) dialog:",
        f"  Title: {ADD_ASSAYS_DIALOG_V14['title']}",
        f"  Opens after: {ADD_ASSAYS_DIALOG_V14['opened_after']}",
        "  Select Assay columns: "
        + " | ".join(ADD_ASSAYS_DIALOG_V14["select_table_columns"]),
        f"  Basrah search: {ADD_ASSAYS_DIALOG_V14['basrah_search']}",
        f"  Example library hit: {ADD_ASSAYS_DIALOG_V14['example_hit']['assay']}",
        f"  OK disabled until row selected: {ADD_ASSAYS_DIALOG_V14['ok_disabled_until_selection']}",
        f"  → {ADD_ASSAYS_DIALOG_V14['mrc_action']}",
    ]
    try:
        from aspen_assay_library_catalog import format_assay_library_catalog_block

        lines.append("")
        lines.append(format_assay_library_catalog_block())
    except Exception:
        pass
    return "\n".join(lines)
