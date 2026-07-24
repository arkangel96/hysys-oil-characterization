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
| **Petroleum Assays** (Refining) | **No (this job).** Aspen Assay Management / refining assay form (`Assays Summary/Petroleum Assays` in Assay Manager help). Different surface; COM `PetroleumAssays` empty on blank case. |
| **Hypotheticals Manager** | **No.** Manual hypo editor. Hypos are **output** of Oil Manager characterize, not where you enter TBP/LE. |

Message bar `Assay Was Not Calculated` confirms Oil Manager assays exist but are not yet calculated — stay on Oil Manager.

Orphan UI note: empty `Component List - 1` causes red Required Info — keep only `CompList1` with the 8 lights. Delete the empty list in the Component Lists table when convenient.

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

**COM write candidates (xhysys Assay*):**  
`AssayPercentForBoilingTemperatureValue` + `BoilingTemperatureValue`,  
`BulkMassDensityValue` / API, `LightEndsPercentInAssayValue`,  
`LightEndsCompositionValue` (8 slots = FP lights), `Calculate()`.

**Coded:** [`oil_manager_ui.py`](../../../oil_manager_ui.py) — UI map + Basrah seed + workflow.

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
| Assays.Add(name, "TBP") | COM | **PROVEN live** (type=0) |
| AssaysCollection.Add | `Function Add(Item) As Variant` | **GATED stub** |
| Blend.AddAssay | `Sub AddAssay(AssayName)` | **GATED stub** |
| Blend.InstallIntoStream | `Sub InstallIntoStream(StreamName)` | **GATED stub** |
| OilManager.SetAssociatedFluidPackage | `Sub SetAssociatedFluidPackage(name)` | **PROVEN live** |
| Assay TBP / LE / bulk setters | Assay* object properties | Access denied until PP selected — **retry next** |
| Characterize / Calculate blend | UI-first; COM method varies by build | **Manual first** |

## PE gates (intentional)

- Never auto-save `.hsc`
- No silent TBP extrapolation (Aspen offers LeastSquares/LaGrange/Probability — we forbid silent use)
- Manual Oil Manager first until inventory flips `allow_COM_write`
