# Aspen-sourced intelligence (curated)

**Source folder (local, not shipped in git):** `../../from aspen doc/`  
**Coded module:** `aspen_intelligence.py`  
**Inventory:** OC-ASPEN-01, OC-ASPEN-02

## What we learned

### 1. Aspen Feedstock Assay Management (PIMS / Assay Manager)
- Characterization builds a **model** from limited lab data (estimate outside range, re-cut, fill properties).
- Conventional path uses **micro-cuts** IBP→FBP.
- Prefer **TBP** input; cut yields can build TBP if adequate.
- Lights lighter than **n-C5** → whole crude + light-end cut.
- Blends from **characterized** assays only.

### 2. Aspen HYSYS COM (`xhysys`) — Oil Manager
Pertinent enums coded in `aspen_intelligence.py`:

- `AssayType_enum` (TBP, D86, D1160, …)
- `AssayBasis_enum`
- `AssayLightEndsCalculationType_enum`
- `AssayLightEndsCompositionBasis_enum`
- `AssayExtrapolationMethod_enum` (exists — **our PE forbids silent use**)
- `OilManager` members: Blends, CorrelationSets, IBP/FBP, SetAssociatedFluidPackage, …

## PE conflict we keep intentional

Aspen exposes extrapolation methods. Our Assist keeps  
`allow_silent_tbp_extrapolation = false` so short proposal TBP stays **OX** until Intertek residue data exists.

## Usage

```python
from aspen_intelligence import recommend_hysys_entry, format_aspen_block
from assay_engine import load_assay

plan = recommend_hysys_entry(load_assay("BASRAH"))
print(format_aspen_block(load_assay("BASRAH")))
```
