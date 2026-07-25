# Aspen COM capability map (curated)

**Source:** `from aspen doc/_extract/xhysys` + Assay Manager characterize overview  
**Coded:** `aspen_intelligence.py` (`COM_CAPABILITY_MAP`, enums, members)  
**Adapter:** `hysys_api.py`  
**Gate:** `complementary_rules.DEFAULTS["allow_COM_write"]` = **false**

## READ (coded / hardening)

| Capability | Aspen topic | Status |
|------------|-------------|--------|
| Connect / open case / streams / solve | Application / Flowsheet | **CODED** |
| OilManager path discovery | `OilManager.htm` | **CODED** structured |
| AssaysCollection inventory | `AssaysCollection.htm` | **CODED** read Count/names |
| Blends inventory + `IsReadyToInstall` | `blend_object.htm` | **CODED** read |
| Stream composition (mass/mole) | `ProcessStream.htm` | **CODED** read |
| Library lights vs `NBP*` / hypo names | HypoGroup + FP components | **CODED** classify |
| Install/attach evidence from FEED | Blend + composition heuristics | **CODED** verify |

## HYSYS Properties ribbon — tool choice (V14 UI + manuals)

| Ribbon control | Use for Basrah/Mishrif → Raw Crude FEED? |
|----------------|------------------------------------------|
| **Oil Manager** (Oil group) | **YES — primary.** `BasisManager.OilManager` → Assays → Blend → `InstallIntoStream`. Matches target lights + `NBP[0]*`. |
| **Petroleum Assays** (Refining) | **No (this job).** Assays Summary + Add Assays library. Coded UI map: [`petroleum_assays_ui.py`](../../../petroleum_assays_ui.py). |
| **Hypotheticals Manager** | **No.** Manual hypo editor. Hypos are **output** of Oil Manager characterize, not where you enter TBP/LE. |

Message bar `Assay Was Not Calculated` confirms Oil Manager assays exist but are not yet calculated — stay on Oil Manager.

Orphan UI note: empty `Component List - 1` causes red Required Info — keep only `CompList1` with the 8 lights. COM `ComponentLists.Remove('Component List - 1')` **works** once Basis-1 is attached to CompList1 (proven on sample.hsc continuation).

## Petroleum Assays / Assays Summary (V14 learned 2026-07-25)

**Screen:** Properties → Petroleum Assays → Assays Summary (empty until Add)

| UI | Meaning |
|----|---------|
| Display | e.g. All Region |
| Default Fluid Package | dropdown (empty until set) |
| Table columns | Assay \| Characterization Method \| Status \| Fluid Package \| From Source \| Density lb/ft3 \| Sulfur % \| Viscosity @100 F cSt \| Watson K \| Add Property/Description |
| Buttons | Add (dropdown) \| Export \| Copy \| Delete |
| Add → library | Opens **Add Assays** (Aspen Assay Library) — e.g. Basrah Light-2014 |

**Add workflow (proven live 2026-07-26):**
1. Assays Summary → Add  
2. **Assay Component Selection** (gate if no assay-compatible list)  
3. OK on a common list (e.g. **Assay Components Celsius to 1150C**) → Aspen installs that preset slate into the case  
4. **Add Assays** library picker opens (this is expected — not an error)  
5. Select commercial assay row → OK (gray until a row is selected)

**Why 1150C made Add Assays appear:** Component Selection is a *prerequisite gate*, not the assay. OK installs Aspen's whole-crude °C/1150 NBP component slate. Once that exists, Petroleum Assays proceeds to the library picker. 1150C is **not** Basrah/Mishrif data — only the hypo/temperature grid for Assay Management.

**LIVE FAIL 2026-07-26:** 1150C on Basis-2 → Oil Manager LE COM empty → blend not Ready. Gate: `preflight_oil_manager_fp` / `02b_Oil_Manager_FP_Failure.md`. Do **not** use that FP for MRC Oil Manager.

**Add → `Assay Component Selection` (live 2026-07-25):** “There is no assay compatible component list added in this case…”  
**Dropdown options (captured live — not in any supplied CHM):**

| Preset | Role |
|--------|------|
| Assay Components Celsius to 850C | Whole-crude slate °C, lower NBP ceiling |
| **Assay Components Celsius to 1150C** | Whole-crude Assay Mgmt slate — **banned for MRC Oil Manager FEED** (LE COM fails) |
| Assay Components Fahrenheit to 1500F | °F mirror of ~850 °C band |
| Assay Components Fahrenheit to 2000F | °F mirror of ~1150 °C band |
| FCC Components Celsius / Fahrenheit | Unit-specific — not whole-crude CDU |
| Hydrocracker Components Celsius / Fahrenheit | Unit-specific |
| Reformer Components Celsius / Fahrenheit | Unit-specific |

**Add Assays → Select Assay table (live dump 2026-07-26):**

Columns: Assay \| Library Name \| Assay Date \| Region \| Country \| Density lb/ft3 \| Sulfur % \| KinematicViscosity @ 100 F cSt \| TAN(mg KOH/g) mg KOH/g \| Pour Point F \| Blank

**Basrah / Saturno / Azeri / … in Aspen Assay Library** — **full dump coded** (~950 assays) in [`config/aspen_assay_library_select_assay_v14.tsv`](../../../config/aspen_assay_library_select_assay_v14.tsv); search via [`aspen_assay_library_catalog.py`](../../../aspen_assay_library_catalog.py) (`find_library_assays`).  
**Mishrif:** not present under that name. **MRC:** Cancel — commercial library ≠ Intertek.

Message bar: `Required Info : Components -- Empty component list` + `Updated fluid package xml data is invalid.`  
`CompList1` (8 lights) is **not** assay-compatible. **MRC action: Cancel** both Component Selection *and* Add Assays (Oil Manager). Library commercial assays ≠ Intertek masters.

**Coded:** [`petroleum_assays_ui.py`](../../../petroleum_assays_ui.py) — UI map + MRC bulk→display mapping (reference only).  
**CDU FEED:** stay on Oil Manager — do not fill Assays Summary for MRC Basrah/Mishrif.

---

## Doc-source audit (2026-07-25) — what `from aspen doc/` really contains

| CHM | HYSYS doc? | Covers |
|-----|-----------|--------|
| `AspenFeedStockAssayManager.chm` | **Yes** | Assay Management / Petroleum Assays (PIMS) methodology |
| `xhysys.chm` | **Yes** | HYSYS Customization COM: OilManager, Assay, Blend, ProcessStream |
| `ww10_000.chm` | No | WinWrap Basic **language** reference (Abs, Dim, DlgText…) |
| `ww10_com.chm` | No | WinWrap Basic COM host reference |
| `ww10_cxx.chm` | No | WinWrap Basic C++/ATL/MFC integration tutorials |

The three `ww10_*` files are the macro-engine manuals bundled with HYSYS — **zero** HYSYS UI content.

**Coverage gap:** no HYSYS *user guide* CHM was supplied. HYSYS product dialogs are undocumented in our sources.

**Verified absent** (1665 extracted files scanned; control phrase `Characterization Error` confirmed the scan was live): `Assay Component Selection`, `assay compatible`, `common assay component`, `compatible component list`, `Empty component list`. Coded as `DOC_SEARCH_MISSES` in [`aspen_intelligence.py`](../../../aspen_intelligence.py) — do not re-run blind.

---

## Oil Manager UI (V14 learned 2026-07-25)

**Screen:** Properties → Oil Manager (tabs: Oil Manager | Correlation Sets | Oil Output Settings)

| UI | Meaning |
|----|---------|
| Oil Installation table | Oil Name / Ready / Install / Stream Name / Flowsheet |
| Input Assay | Enter TBP assay (bulk + LE + distillation) |
| Output Blend | Build blend from characterized assay(s) |
| Calculate All | Run assay.Calculate — needed before Ready |
| Install Oil | `Blend.InstallIntoStream(StreamName)` — gray until Ready |
| **Delete** (Input Assay) | COM **`Assays.Remove(name)`** — proven live V14 (deleted Basrah*) |

**Ignore** banner “Use HYSYS Petroleum Refining…” for this CDU FEED job — stay on Oil Manager.

**Console blockers (BasrahTBP3 live):**
1. Bulk SG recommended before characterize
2. “boiling point temperature table is not ready” → TBP T + yield not entered
3. Orphan `Component List - 1` (empty) → delete; keep CompList1

**Input Assay form (Basrah live 2026-07-25):**  
Tabs: Input Data | Calculation Defaults | Working Curves | Plots | User Curves | Notes  
Left: Assay Data Type / Bulk Properties / Light Ends / MW / Density / Viscosity curves  
Input Data: Assay Basis + Assay Percent / Temperature **[F]** grid (≥5 pts)  
Buttons: Edit Assay… | Calculate | Output Blend  

**COM write gate (critical):** `*Value` setters are **Access Denied** until the assay form is open (double-click row). With form open: bulk ρ, LE user-input + composition, TBP arrays, `Calculate()` all work.  

**AspenFeedStockAssayManager vs Oil Manager:** Assay Manager CHM = Petroleum Assays / PIMS characterize (micro-cuts, Property Match). Oil Manager COM writers are in **xhysys**. CDU FEED automation uses Oil Manager only; Aspen Assay Library “Add Assays” is not the MRC Basrah path.

**Coded fill:** [`oil_characterize_fill.py`](../../../oil_characterize_fill.py) + `characterize_fill_live` — StartOilChange → BulkPropertiesUsed + TBP °C + LE → Calculate → Blend → InstallIntoStream → EndOilChange → verify NBP*.

**Coded:** [`oil_manager_ui.py`](../../../oil_manager_ui.py) — UI map + Basrah seed + workflow.  
**Coded:** [`hysys_ui_automation.open_input_assay_row_ui`](../../../hysys_ui_automation.py) + [`HysysController.enter_tbp_assay_seed_live`](../../../hysys_api.py).

## Fluid Package Set Up (V14 UI learned 2026-07-25)

Live screen `Fluid Package: Basis-1` → **Set Up**:

| UI field | Value for crude FEED work |
|----------|---------------------------|
| Package Type | `HYSYS` |
| Component List Selection | `CompList1 [HYSYS Databanks]` (after COM Add lights) |
| Property Package Selection | click **`Peng-Robinson`** (leave `<none>`) |
| Status before | red `Select property package` |

**COM gap:** `PropertyPackageName = "Peng-Robinson"` raises *value not in expected range* on V14.  
**Working path:** UI Automation click on list text `Peng-Robinson` → COM **read** returns `Peng-Robinson` and `Components.Count == 8`.  
**Code:** `hysys_ui_automation.select_peng_robinson_in_fluid_package_ui`.

## WRITE (gated / hybrid)

| Capability | Aspen signature | Status |
|------------|-----------------|--------|
| ComponentLists.Add + Components.Add | COM | **PROVEN live** |
| FluidPackages.Add + ComponentList= | COM | **PROVEN live** |
| Select Peng-Robinson | UI click (COM setter broken V14) | **PROVEN live** |
| `BasisManager.StartOilChange` / `EndOilChange` | COM | **DOCUMENTED** xhysys — oil-edit transaction; coded in `characterize_fill_live` |
| Assays.Add(name, "TBP") | COM | **PROVEN live** (type=0) — Basrah created on sample.hsc |
| Open Input Assay row | UIA one double-click on `DataGridCell` | **PROVEN live** — unlocks COM writers |
| `BulkPropertiesUsed=True` + `BulkMassDensityValue` | COM | **DOCUMENTED** xhysys; live must set Used (screenshot Not Used → SG warning) |
| Assay TBP / LE setters | `*Value` arrays, LE calc=-1 | **PROVEN** when form open; temps in **°C** |
| `assay.Calculate()` | COM | **PROVEN** (parameterless; docs' Calculate(val) is RealVariable API) |
| Blend.Add / AddAssay / IsReadyToInstall | COM | **PROVEN live** |
| Blend.InstallIntoStream | COM | **PROVEN call**; must create stream first; **verify NBP*** (Status can show Installed with 0 hypos) |
| Aspen Assay Library Add Assays | UI (Petroleum Assays) | **Out of scope** for MRC Oil Manager Basrah FEED |

## PE gates (intentional)

- Never auto-save `.hsc`
- No silent TBP extrapolation (Aspen offers LeastSquares/LaGrange/Probability — we forbid silent use)
- Manual Oil Manager first until inventory flips `allow_COM_write`
