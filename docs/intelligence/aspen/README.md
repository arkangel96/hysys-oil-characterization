# Aspen-sourced intelligence (curated)

**Source folder (local, not shipped in git):** `../../from aspen doc/`  
**Coded module:** `aspen_intelligence.py`  
**Capability map:** [`COM_CAPABILITY_MAP.md`](COM_CAPABILITY_MAP.md)  
**Inventory:** OC-ASPEN-01, OC-ASPEN-02, OC-ASPEN-03

## What we learned

### 1. Aspen Feedstock Assay Management (PIMS / Assay Manager)
- Characterization builds a **model** from limited lab data (estimate outside range, re-cut, fill properties).
- Conventional path uses **micro-cuts** IBP→FBP.
- Prefer **TBP** input; cut yields can build TBP if adequate.
- Lights lighter than **n-C5** → whole crude + light-end cut.
- Blends from **characterized** assays only.
- **Property Match Setting** Cut/Bulk/Both (V12+) — Oil Manager analogue is `BulkPropertiesUsed`.
- UI “Add Assays” / Aspen Assay Library = commercial characterized models — **not** Oil Manager MRC Basrah.

### 2. Aspen HYSYS COM (`xhysys`) — Oil Manager / Blend / Stream

Pertinent surfaces coded in `aspen_intelligence.py`:

- `AssayType_enum`, `AssayBasis_enum`, LE calc/basis enums, `AssayCurveType_enum`
- `AssayExtrapolationMethod_enum` (exists — **PE forbids silent use**)
- `BasisManager.StartOilChange` / `EndOilChange` — oil-edit transaction
- Assay writers: `BulkPropertiesUsed`, `BulkMassDensityValue`, TBP/LE `*Value`
- `OilManager`: Blends, CorrelationSets, IBP/FBP, `SetAssociatedFluidPackage`
- `Blend`: `AddAssay`, `IsReadyToInstall`, `InstallIntoStream`, ComponentNBP*
- `ProcessStream`: `ComponentMassFractionValue` / mole equivalents

### 3. Autonomous fill (coded)

`oil_characterize_fill.build_basrah_fill_plan` + `HysysController.characterize_fill_live`
fills Oil Manager from MRC seed. Always **verify NBP*** on FP / Raw Crude composition
after install — Output Blend Status can show Installed with zero hypos.

## PE conflict we keep intentional

Aspen exposes extrapolation methods. Our Assist keeps  
`allow_silent_tbp_extrapolation = false` so short proposal TBP stays **OX** until Intertek residue data exists.

## Usage

```python
from aspen_intelligence import recommend_hysys_entry, format_aspen_block, classify_component_name
from assay_engine import load_assay

plan = recommend_hysys_entry(load_assay("BASRAH"))
print(format_aspen_block(load_assay("BASRAH")))
print(classify_component_name("NBP[0]100*"))
```
