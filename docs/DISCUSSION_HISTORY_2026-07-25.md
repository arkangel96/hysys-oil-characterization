# Discussion history — 2026-07-25

**Product:** Oil Characterization Assist  
**Repo:** https://github.com/arkangel96/hysys-oil-characterization  
**Case used live:** `c:\Users\USER\Documents\cdu tool\oil charac\sample.hsc` (after crash restart)  
**HYSYS:** Aspen HYSYS **V14**

---

## 1. Aim restated (user)

Automate **from-scratch** oil characterization in HYSYS:

- User supplies company crude info (MRC Basrah / Mishrif proposal)
- Assist drives Oil Manager → characterize → install → **Raw Crude** with library lights + `NBP[0]*`
- Aspen manuals under `from aspen doc` / `F:\tools\oil characeriszation\from aspen doc` are the intelligence buffer

Earlier letter **C** (READ-first) still applies for safety; full write automation is the product goal.

---

## 2. Target composition (user screenshot)

Material Stream **Raw Crude** → Worksheet → Composition:

- Methane, Ethane, Propane, i-Butane, n-Butane, H2O (and later **i/n-Pentane** as discrete lights — see §4)
- Then `NBP[0]49*` … heavy hypos with calculated mole fractions

---

## 3. MRC crude data (user screenshots — proposal)

Same ICDL 001 C 11 T 001 H extract already in cases JSON:

- Design API band 28–32; Basrah 32.5 / Mishrif 26.4 = **bounds**, no invented blend %
- LE bulk 3.21 / 3.26 wt% of crude; LE composition = **of LE cut**
- TBP mass to 500 °C (~72% / ~65%) → soft heavy end; **no silent extrapolation**; D86 empty → do not invent
- Process narrative (desalter, transfer T, PAs) = **CDU later**, not Oil Manager inputs

---

## 4. Decisions locked this session

| Topic | Decision |
|-------|----------|
| Start crude | **Basrah first**, then Mishrif as second oil |
| Library lights | **C1–nC5 + H2O** (LE table has major iC5/nC5) |
| Characterization tool | **Oil Manager** — not Petroleum Assays, not Hypotheticals Manager |
| Property package | **Peng-Robinson** (Package Type HYSYS) |
| Case | Throwaway / `sample.hsc` — never auto-save from Assist |

---

## 5. Live COM / UI learning (V14)

### Worked

| Action | How |
|--------|-----|
| Attach to running HYSYS | `GetActiveObject('HYSYS.Application')` |
| Add CompList + library lights | `ComponentLists.Add` / `Components.Add(name)` |
| Add FluidPackage + attach list | `FluidPackages.Add` / `ComponentList =` |
| Select Peng-Robinson | **UI Automation one click** on list TextBlock (COM `PropertyPackageName = "Peng-Robinson"` rejected: value not in range) |
| Create TBP assay | `Assays.Add(name, "TBP")` → AssayType=0 |
| Delete assays | `Assays.Remove(name)` — matches Input Assay **Delete** |
| Associate FP to Oil Manager | `OilManager.SetAssociatedFluidPackage('Basis-1')` |

### Blocked / gaps

| Issue | Notes |
|-------|--------|
| COM set PropertyPackageName | Fails even with exact UI string; UIA click then COM **read** works |
| Assay TBP/LE/bulk writers | Access denied / E_FAIL until data-entry path fully proven; candidates coded in `oil_manager_ui` / `hysys_api.com_enter_tbp_assay_seed` (gated) |
| Empty `Component List - 1` | COM Remove Access Denied — delete in Component Lists UI |
| Aggressive Delete UIA loop | **Crashed HYSYS** once — rule: **one click**, no loops |

### Oil Manager UI map (coded)

Tree: Oil Manager → Input Assay | Output Blend  
Tabs: Oil Manager | Correlation Sets | Oil Output Settings  
Buttons: Clear All | Calculate All | Input Assay | Output Blend | Install Oil  
Console when empty TBP: bulk SG recommended; “boiling point temperature table is not ready”

Ignore banner “Use HYSYS Petroleum Refining…” for CDU FEED job.

---

## 6. Code landed (pushed `f887df7`)

- Structured OM + FEED composition READ
- MRC QA / MB yield / merge / O4 handoff (`handoff.py`)
- Gated COM write stubs + `allow_COM_write=false`
- `hysys_ui_automation.py` — Peng-Robinson select
- `oil_manager_ui.py` — Oil Manager workflow + Basrah seed
- Aspen COM capability map docs

---

## 7. Pause / next on live case

**State at note time:** `sample.hsc` with CompList1 (8 lights), Basis-1 + Peng-Robinson selected; assays cleaned (0).

**Next:**

1. User deletes orphan **Component List - 1** if still present  
2. Oil Manager → Input Assay → **one** Basrah TBP  
3. Enter bulk SG 0.863 / API 32.5, LE 3.21 + cut composition, TBP mass curve  
4. Calculate All → Output Blend → Install → **Raw Crude**  
5. Verify Worksheet composition vs target pattern  

---

## 8. Continuation (same day) — Basrah shell created

**Live READ after attach to `sample.hsc`:**

| Item | Result |
|------|--------|
| CompList1 | 8 lights (C1–nC5 + H2O) |
| Basis-1 | Peng-Robinson ✓ |
| Assays | was 0 |
| Streams | 0 |

**Done via COM (no case save):**

1. `OilManager.SetAssociatedFluidPackage('Basis-1')` OK  
2. `Assays.Add('Basrah', 'TBP')` → Count=1, AssayType=0  
3. `ComponentLists.Remove('Component List - 1')` → **OK** (previously Access Denied; now works with CompList1 attached to Basis-1)  

**Still blocked (Access Denied on all *Value / nested .Value writers):**  
bulk density/API, TBP % + T, LE calc/type/%, LE composition, Basis.  
Nested COM objects exist (`BulkMassDensity`, `BoilingTemperature`, `AssayPercentForBoilingTemperature`, `LightEndsComposition`) with `IsKnown=False` / empty arrays — READ works, WRITE denied.

**Next (manual UI — required until write path proven):**

1. Oil Manager → Input Assay → open **Basrah** (already present)  
2. Enter seed from `BASRAH_OIL_MANAGER_SEED` / § below  
3. Calculate All → Output Blend → Install → **Raw Crude**  
4. Verify Worksheet composition  

### Basrah Input Assay sheet (proposal / MRC)

| Field | Value |
|-------|--------|
| Assay type | TBP (already) |
| Bulk SG @15 °C | **0.863** |
| Bulk API | **32.5** |
| Light ends | User input; **3.21** wt% of crude |
| LE cut wt% (sums ~100 of LE cut) | C1=0, C2=0.54, C3=16.63, iC4=8.24, nC4=27.25, iC5=15.99, nC5=31.34, H2O=0 |
| TBP mass curve °C / cum wt% | 40/2.73, 70/6.30, 100/10.72, 120/13.70, 140/16.68, 170/21.15, 190/24.14, 210/27.15, 250/33.59, 270/37.11, 300/42.21, 360/52.26, 400/58.52, 500/71.84 |

No silent TBP extrapolation past 500 °C (~72%). No invented D86.

---

## 9. Automate Input Assay (same day — learn + code)

**UI learned (screenshot + UIA):** Input Assay list → double-click **Basrah** DataGridCell → assay form  
Tabs: Input Data | Calculation Defaults | Working Curves | Plots | User Curves | Notes  
Input Data: Assay Percent / Temperature **[F]**; Calculate; status “Assay Was Not Calculated”

**COM breakthrough:** writers **Access Denied** until form open; with form open:

| Setter | Result |
|--------|--------|
| `BulkMassDensityValue=863` | OK (IsKnown) |
| `LightEndsCalculationType=-1`, `LE%=3.21`, LE composition ×8 | OK |
| `Basis=-3` (mass) | OK |
| TBP % + T (14 pts, °C→°F) | OK |
| `Calculate()` | OK — “Assay Was Not Calculated” cleared |

**Coded:**

- `oil_manager_ui.ASSAY_FORM_UI_V14` + `celsius_to_fahrenheit`
- `hysys_ui_automation.open_input_assay_row_ui`
- `HysysController.open_input_assay_ui` / `enter_tbp_assay_seed_live`

**Still next:** Output Blend → Install → **Raw Crude** composition verify. Blends still 0 after Calculate.

---

## 10. AspenFeedStockAssayManager + autonomous fill (same day evening)

Read `from aspen doc/AspenFeedStockAssayManager.chm` (_extract/AssayManager) and `xhysys` assay/OilManager topics.

**Split:** Assay Manager = Petroleum Assays / PIMS characterize methodology. Oil Manager COM writers = xhysys (`BulkPropertiesUsed`, StartOilChange, InstallIntoStream). CDU FEED stays Oil Manager — not Aspen Assay Library Add Assays.

**Coded:** `oil_characterize_fill.py` + `HysysController.characterize_fill_live`  
StartOilChange → BulkPropertiesUsed + TBP °C + LE → Calculate → Blend → Install → EndOilChange → verify NBP*.

*End of Aspen doc learn / fill coding.**
