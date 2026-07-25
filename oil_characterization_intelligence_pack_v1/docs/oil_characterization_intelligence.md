# Oil Characterization Intelligence Pack
## Basrah / Mishrif CDU Feed Characterization — Version 1.0

## Purpose
This package defines the process-engineering decision layer for crude assay ingestion, QA, Oil Manager preparation, and CDU hand-off.

## States
- O0: no assay loaded
- O1: raw assay captured
- O2: minimum usable assay
- O3: strong/preferred assay
- OX: rejected or unreliable assay
- O4: characterized and accepted for CDU hand-off

## Assay Object
```json
{
  "crude_id": "BASRAH",
  "source": {"tag":"INTERTEK","confidence":"high"},
  "bulk": {"api_gravity":null,"specific_gravity_15C":null,"sulfur_wt_pct":null,"viscosity_cSt_40C":null,"rvp_kPa":null,"ccr_wt_pct":null,"asphaltenes_wt_pct":null,"tan_mgKOH_g":null,"vanadium_wt_ppm":null,"nickel_wt_ppm":null},
  "light_ends": {"basis":"OF_LIGHT_ENDS_CUT","light_ends_bulk_wt_pct_of_crude":null,"components":{"C1":null,"C2":null,"C3":null,"iC4":null,"nC4":null,"iC5":null,"nC5":null}},
  "tbp": {"basis":"cumulative_wt_pct","temperature_unit":"C","points":[]},
  "design": {"role":"LIGHT_BOUND","blend_fraction":null},
  "characterization": {"status":"O0","flags":[]}
}
```

## OC-01 Completeness
### Must-have for O2
- crude ID and traceable source tag
- API or SG
- at least one viscosity point
- sulfur
- valid TBP curve with at least 90 wt% coverage
- resolved light-ends basis
- total light-ends fraction, or explicit statement that it is unavailable

### Strong fields for O3
- API and SG consistency
- multiple viscosity points
- RVP, CCR, asphaltenes, nitrogen, TAN, water, salt, V and Ni
- complete C1–C5 split
- master assay source
- TBP coverage at least 97 wt%

### OX triggers
- invalid/non-monotonic TBP
- impossible bulk values
- unresolved light-ends basis
- unknown and unverifiable source
- severe internal contradictions

## Light-Ends Rules
A C1–C5 table that sums to about 100% is normally composition of the isolated light-ends cut, not whole crude.

Never enter it directly as whole-crude composition unless the source explicitly says whole-crude basis.

If total LE is `LE_bulk_wt_pct_of_crude` and component fraction is `component_wt_pct_of_LE`:

```text
component_wt_pct_of_crude = LE_bulk_wt_pct_of_crude × component_wt_pct_of_LE / 100
```

Rules:
- 98–102% sum: accept and normalize
- 95–105%: normalize with warning
- outside 95–105%: reject for review
- never infer total LE from component distribution alone

## TBP QA
Mandatory checks:
1. temperature monotonic increasing
2. cumulative wt% monotonic increasing
3. cumulative wt% within 0–100
4. no conflicting duplicate points
5. adequate residue coverage
6. no impossible jumps
7. Basrah normally lighter than Mishrif

Boundary expectation:
- at common temperature, Basrah cumulative yield should generally exceed Mishrif
- at common cumulative yield, Basrah temperature should generally be lower
- repeated inversion suggests swapped columns, unit error, or mislabeled crude

## Oil Manager PE Map
Exact labels are version-dependent, but the engineering map is:
- assay identity/source → assay information
- API/SG, viscosities, sulfur, RVP, CCR, asphaltenes, TAN → bulk properties
- C1–C5 whole-crude amounts → light components
- TBP temperature vs cumulative wt% → distillation curve
- unused stored properties remain in external assay object
- characterize → review hypos → install oil → attach to FEED

## O4 Gate
All must pass:
- assay accepted as O2 or O3
- source traceable
- light-ends basis resolved and normalized
- TBP valid
- bulk properties internally consistent
- Oil Manager characterization complete
- hypocomponents reviewed
- installed oil created
- installed oil attached to FEED
- FEED recalculates
- `handoff_o4.json` created

## P1 MRC Project Logic
```yaml
crude_boundaries:
  Basrah: {role: LIGHT_BOUND, tabulated_api: 32.5}
  Mishrif: {role: HEAVY_BOUND, tabulated_api: 26.4}
  design_feed_api_range: [28.0, 32.0]
```
Run 100% Basrah, 100% Mishrif, then the named licensor blend. Do not invent blend percentages. API-matched blends are sensitivity cases only.

## Cut Slate for Post-Characterization Yield Checks
```yaml
cut_slate_C:
  light_naphtha: [5,100]
  heavy_naphtha: [100,170]
  kerosene: [170,230]
  gas_oil: [230,335]
  heavy_gas_oil: [335,355]
  residue: [355,null]
```
These are yield-check ranges, not Oil Manager inputs.

## Product-Spec Storage
Store LPG/naphtha/kero/GO/residue specifications as `FINAL_TARGETS` for later CDU use. Never use them as crude-assay inputs.

## Hypocomponent QA
Check hypo count, boiling-point order, SG/MW trends, heavy-end coverage, installed oil, and FEED attachment.

## Required Project Inputs to Lock the Pack
1. confirm Basrah/Mishrif TBP columns
2. full Intertek tables if longer than proposal
3. design feed slate or licensor blend percentages
4. HYSYS version
5. exact Oil Manager labels/screens
6. preferred thermo package; PR is provisional
7. actual Basrah and Mishrif assay values

## Conservative Defaults
```yaml
defaults:
  thermo_package: PR
  allow_api_estimated_blend: false
  allow_silent_tbp_extrapolation: false
  allow_unresolved_light_ends_basis: false
  allow_O4_without_hypo_review: false
  allow_COM_write: false
  manual_oil_manager_first: true
```
