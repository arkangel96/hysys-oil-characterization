"""Oil Manager UI / workflow intelligence (HYSYS V14 + xhysys manuals).

Learned from live Oil Manager screen (2026-07-25) and Aspen COM topics:
OilManager, Blend.InstallIntoStream, Assay* BoilingTemperature / LightEnds /
BulkMassDensity properties.

UI map (Oil Manager tab)
------------------------
Tree: Properties → Oil Manager → Input Assay | Output Blend
Main tabs: Oil Manager | Correlation Sets | Oil Output Settings
Table: Oil Installation Information
  columns: Oil Name | Ready | Install | Stream Name | Flowsheet
Buttons: Clear All | Calculate All | Input Assay | Output Blend | Install Oil
Install Oil enabled only when a blend is Ready.

Aspen banner may suggest Petroleum Assays — we still use Oil Manager for
CDU FEED + NBP[0]* install (see CHARACTERIZATION_TOOL_CHOICE).

Console learning (BasrahTBP3)
-----------------------------
- "Highly recommended that the bulk SG be input..."
- "Assay could not be calculated. The boiling point temperature table is not ready."
⇒ Calculate All needs: bulk density/SG (or API) + TBP boiling T table + yields.

Workflow (manual / live COM)
------------------------------
1. Keep CompList1 + Basis-1 Peng-Robinson (delete empty Component List - 1)
2. Oil Manager → Input Assay → one TBP assay (Assays.Add(name, \"TBP\"))
3. Open assay form (double-click row) — required before COM writers
4. Enter bulk SG/API, user-input LE (cut basis), TBP mass curve
   (live: enter_tbp_assay_seed_live — converts T °C→°F for Input Data [F])
5. Calculate All (assay.Calculate / UI Calculate)
6. Output Blend → add assay → Ready
7. Install Oil → Stream Name Raw Crude (Blend.InstallIntoStream)
8. Verify Worksheet Composition: lights + NBP[0]*
"""

from __future__ import annotations

from typing import Any


# Exact UI strings from V14 Oil Manager screenshot
OIL_MANAGER_UI_V14 = {
    "tree_path": ("Properties", "Oil Manager"),
    "tree_children": ("Input Assay", "Output Blend"),
    "main_tabs": ("Oil Manager", "Correlation Sets", "Oil Output Settings"),
    "install_table_columns": (
        "Oil Name",
        "Ready",
        "Install",
        "Stream Name",
        "Flowsheet",
    ),
    "buttons": (
        "Clear All",
        "Calculate All",
        "Input Assay",
        "Output Blend",
        "Install Oil",
    ),
    "banner_petroleum_assays": (
        "Use HYSYS Petroleum Refining for improved assay management"
    ),
    "ignore_banner_for_cdu_feed": True,
    "target_stream_name": "Raw Crude",
    "messages": {
        "assay_not_calculated": "Assay Was Not Calculated",
        "need_bulk_sg": "Highly recommended that the bulk SG be input",
        "tbp_table_not_ready": "boiling point temperature table is not ready",
        "orphan_component_list": "Component List - 1",
    },
}


# COM property candidates for TBP assay data entry (xhysys Assay* topics)
# Prefer *Value Let properties on the assay object.
ASSAY_TBP_WRITE_CANDIDATES = {
    "bulk_density": ("BulkMassDensityValue", "DensityValue", "BulkAPIGravityValue"),
    "tbp_yield_pct": ("AssayPercentForBoilingTemperatureValue",),
    "tbp_temperature_C": ("BoilingTemperatureValue",),
    "light_ends_calc": ("LightEndsCalculationType",),  # -1 = UserInput
    "light_ends_pct": ("LightEndsPercentInAssayValue",),
    "light_ends_composition": ("LightEndsCompositionValue", "LightEndsComposition.Values"),
    "basis_mass": ("Basis",),  # -3 = ab_MassFraction
    "calculate": ("Calculate",),
}

# Basrah proposal seed (MRC) — for Input Assay after COM write unlocked
BASRAH_OIL_MANAGER_SEED: dict[str, Any] = {
    "assay_name": "Basrah",
    "assay_add_type": "TBP",
    "bulk_sg_15C": 0.863,
    "bulk_api": 32.5,
    "light_ends_bulk_wt_pct_of_crude": 3.21,
    # Order must match CompList1: Methane, Ethane, Propane, i-Butane, n-Butane,
    # i-Pentane, n-Pentane, H2O — LE cut wt% (sums ~100)
    "light_ends_cut_wt_pct": (0.0, 0.54, 16.63, 8.24, 27.25, 15.99, 31.34, 0.0),
    "tbp_temperature_C": (
        40, 70, 100, 120, 140, 170, 190, 210, 250, 270, 300, 360, 400, 500,
    ),
    "tbp_cumulative_wt_pct": (
        2.73, 6.30, 10.72, 13.70, 16.68, 21.15, 24.14, 27.15,
        33.59, 37.11, 42.21, 52.26, 58.52, 71.84,
    ),
    "notes": (
        "TBP coverage soft at 500 C (~72%) — no silent extrapolation (OX).",
        "D86 empty — do not invent.",
        "Console requires bulk SG + boiling point temperature table before Calculate.",
        "COM writers need assay form open (double-click Input Assay row).",
        "BoilingTemperatureValue uses COM °C (UI [F] is display). Do not pre-convert seed to °F.",
        "Bulk Properties must be Used + SG — Not Used → bulk SG warning / Watson K skip.",
    ),
}


OIL_MANAGER_WORKFLOW = (
    "Delete orphan empty Component List - 1; keep CompList1 + Basis-1 PR",
    "Oil Manager → Input Assay: Assays.Remove junk; keep one TBP assay",
    "Enter bulk SG/API + user-input LE (cut composition) + TBP mass curve",
    "Calculate All — clear 'Assay Was Not Calculated' / TBP table not ready",
    "Output Blend → add characterized assay → Ready=True",
    "Install Oil → Stream Name = Raw Crude (Simulation stream)",
    "Verify Worksheet Composition: C1–C5/H2O lights + NBP[0]* hypos",
)

# Output Blend list UI (V14) — screenshot 2026-07-25
OUTPUT_BLEND_UI_V14 = {
    "tree": ("Oil Manager", "Output Blend"),
    "table_columns": ("Blend", "Correlation Set", "Status"),
    "buttons": ("Add", "Copy", "Delete", "Oil Manager", "Input Assay"),
    "status_installed_pattern": "Installed - in <{stream}> on <{fluid_package}>",
    "example_row": {
        "blend": "BasrahBlend",
        "correlation_set": "Default Set",
        "status": "Installed - in <Raw Crude> on <Basis-1>",
    },
    "com_add": "OilManager.Blends.Add(blendName)",
    "com_add_assay": "Blend.AddAssay(assayName)",
    "com_install": "Blend.InstallIntoStream(streamName)",
    # Live note: Status string can show Installed while FP still has only library
    # lights (no NBP*) — verify CompList / Worksheet Composition, not Status alone.
    "verify_after_install": (
        "FluidPackage.Components includes NBP*",
        "Raw Crude Worksheet Composition: lights + NBP[0]* mole/mass fractions",
    ),
}

# Input Assay table UI (V14) — Add / Copy / Delete / Oil Manager / Output Blend
INPUT_ASSAY_UI_V14 = {
    "tree": ("Oil Manager", "Input Assay"),
    "table_columns": ("Assay", "Correlation Set"),
    "buttons": (
        "Add...",
        "Copy",
        "Delete",
        "Oil Manager",
        "Output Blend",
        "Import",
        "Export",
        "Oil Input Preferences...",
    ),
    "grid_class": "OdfDataGrid",
    "assay_cell_class": "DataGridCell",
    "open_assay": "double-click Assay DataGridCell (one shot — no loops)",
    "warning_icon": "yellow caution on Input Assay tree = incomplete / not calculated",
    "com_delete": "OilManager.Assays.Remove(assayName)",  # proven live V14
    "com_add_tbp": "OilManager.Assays.Add(assayName, 'TBP')",  # AssayType=0
}

# Basrah assay form (V14 live 2026-07-25) — after double-click row
ASSAY_FORM_UI_V14 = {
    "tabs": (
        "Input Data",
        "Calculation Defaults",
        "Working Curves",
        "Plots",
        "User Curves",
        "Notes",
    ),
    "assay_definition_labels": (
        "Assay Data Type",
        "Bulk Properties",
        "Light Ends",
        "Molecular Wt. Curve",
        "Density Curve",
        "Viscosity Curves",
        "TBP Distillation Conditions",
    ),
    "input_data": {
        "assay_basis": "Assay Basis",  # UI: Mass
        "distillation_radio": "Distillation",
        "grid_columns": ("Assay Percent", "Temperature"),
        "temperature_unit_seen": "[F]",  # display only
        "min_points_msg": "At least 5 points are required",
        "table_ready": "Table is Ready",
        "add_points": ("Num of Points to Add", "Add Data Points"),
    },
    # Live Assay Definition values (Basrah screenshot 2026-07-25)
    "assay_definition_defaults": {
        "Bulk Properties": "Used",  # screenshot had Not Used — causes bulk SG warning
        "Assay Data Type": "TBP",
        "Light Ends": "Input Composition",
        "Molecular Wt. Curve": "Not Used",
        "Density Curve": "Not Used",
        "Viscosity Curves": "Not Used",
        "TBP Distillation Conditions": "Atmospheric",
        "Assay Basis": "Mass",
    },
    "buttons": (
        "Handling & Fitting",
        "Edit Assay...",
        "Calculate",
        "Input Assay",
        "Output Blend",
    ),
    "status_calculated": "Assay Was Calculated",
    "status_not_calculated": "Assay Was Not Calculated",
    # Proven: COM *Value writers Access Denied until this form is open;
    # with form open, BulkMassDensity / LE / TBP / Calculate work.
    "com_write_requires_form_open": True,
    # COM BoilingTemperatureValue is °C (SI). UI [F] converts for display.
    # Writing °F numbers made UI show ~2x wrong (104 written → 219.2 F shown).
    "com_boiling_t_unit": "C",
}


def celsius_to_fahrenheit(temps_c: list[float] | tuple[float, ...]) -> list[float]:
    return [float(t) * 9.0 / 5.0 + 32.0 for t in temps_c]



def format_oil_manager_ui_block() -> str:
    ui = OIL_MANAGER_UI_V14
    lines = [
        "--- Oil Manager UI (V14 learned) ---",
        "Tree: " + " → ".join(ui["tree_path"]) + " → Input Assay | Output Blend",
        "Tabs: " + " | ".join(ui["main_tabs"]),
        "Install table: " + " | ".join(ui["install_table_columns"]),
        "Buttons: " + " | ".join(ui["buttons"]),
        f"Ignore Petroleum Assays banner for CDU FEED: {ui['ignore_banner_for_cdu_feed']}",
        f"Target install stream: {ui['target_stream_name']}",
        "",
        "Workflow:",
    ]
    for step in OIL_MANAGER_WORKFLOW:
        lines.append(f"  → {step}")
    lines.append("")
    lines.append("Console blockers seen on BasrahTBP3:")
    lines.append(f"  • {ui['messages']['need_bulk_sg']}")
    lines.append(f"  • {ui['messages']['tbp_table_not_ready']}")
    lines.append("")
    lines.append("Input Assay Delete (COM proven):")
    lines.append(f"  {INPUT_ASSAY_UI_V14['com_delete']}")
    lines.append(f"  Add TBP: {INPUT_ASSAY_UI_V14['com_add_tbp']}")
    lines.append("")
    form = ASSAY_FORM_UI_V14
    lines.append("Assay form (double-click row):")
    lines.append("  Tabs: " + " | ".join(form["tabs"]))
    lines.append(
        f"  COM write requires form open: {form['com_write_requires_form_open']}"
    )
    lines.append(
        f"  Boiling T COM unit: {form['com_boiling_t_unit']} "
        f"(UI {form['input_data']['temperature_unit_seen']})"
    )
    lines.append("  Live path: open_input_assay_ui → enter_tbp_assay_seed_live")
    return "\n".join(lines)
