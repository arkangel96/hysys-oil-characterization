# COM discovery — Oil Manager / assay (Aspen-informed)

**Coded map:** `aspen_intelligence.py` (from Aspen `xhysys` Oil Manager / Assay enums)  
**Notes:** `docs/intelligence/aspen/README.md`

## Probe already coded

`HysysController.probe_oil_manager()` walks Aspen-informed paths:

- `case.OilManager`
- `case.BasisManager.OilManager`
- `case.BasisManager.Oils`
- `case.BasisManager.Assays`

When `OilManager` is present, it reports readable members from:

`Blends`, `CorrelationSets`, `DefaultD2887Type`, `DefaultD86Type`,
`FBPCutPoint`, `FBPCutPointValue`, `IBPCutPoint`, `IBPCutPointValue`,
`IbpFbpBasis`, `SetAssociatedFluidPackage`

## Recommended entry enums (PE default for MRC wt% assays)

| Setting | Name | Value |
|---------|------|-------|
| AssayType | `at_TBP` | 0 |
| AssayBasis | `ab_MassFraction` | -3 |
| LightEndsCalc | `alect_UserInputLightEnds` | -1 |
| LightEndsCompBasis | `alecb_MassFraction` | -3 |
| Extrapolation | **do not apply silently** | Aspen offers 1/2/3 |

Use `recommend_hysys_entry(assay)` for per-assay plan.

## Rules

- Discovery is **read-only** until inventory allows COM write.
- Never save the case from automation during discovery.
- Aspen CHM originals stay in `from aspen doc/` — do not commit extracts.
