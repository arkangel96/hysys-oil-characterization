# COM discovery — Oil Manager / assay

**Status:** starter checklist  
**Goal:** map read-only COM paths for Oils, Assays, Blends, hypocomponents on your HYSYS build.

## Probe already coded

`HysysController.probe_oil_manager()` tries on `case.BasisManager`:

- `Oils`
- `OilManager`
- `Assays`
- `Blends`

Results appear on the PE board / activity log after Connect.

## Next discovery steps (manual + script)

1. With a characterized crude case open, Connect this app and note the probe string.
2. In a Python REPL (same venv), walk BasisManager attributes and dump `.Count` / `.Name`.
3. Record working ProgID / member names in a table below (fill as you discover):

| Object path | Readable? | Notes |
|-------------|-----------|-------|
| BasisManager.Oils | | |
| BasisManager.OilManager | | |
| Assay.TBP / distillation | | |
| Assay density / light ends | | |
| Blend composition | | |
| Install / attach to stream | | |

## Rules

- Discovery is **read-only** until inventory row OC-04 + OC write path exists.
- AspenTech COM names vary by release — always try variants.
- Never save the case from automation during discovery.
