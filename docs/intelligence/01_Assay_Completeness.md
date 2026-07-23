# OC-01 — Assay completeness

**Status:** DOCS  
**Inventory:** OC-01  
**Code hook:** `assay_engine.diagnose_case` (later)

## Engineering objective

Decide whether the HYSYS oil characterization is complete enough to trust as CDU feed.

## Required inputs (lab → Oil Manager)

| Input | Priority | Accept if |
|-------|----------|-----------|
| Distillation (TBP or ASTM convertible) | Must | Curve covers expected cut range |
| Density / API | Must | Consistent with distillation |
| Light ends (C2–C5 / library lights) | Strong | Mass balance closes reasonably |
| MW / sulfur / viscosity | Optional | When quality targets need them |
| Cut / product definitions | Strong | Align with plant slate |

## Observations (HYSYS)

- Oil / assay present and named
- Hypocomponent count plausible
- Feed stream linked to characterized oil
- Petroleum properties on feed vs lab sheet

## Rule (binding)

**No tower MV work** (CDU Assist) until completeness checklist passes → state **O4**.

## Automation checklist (to code)

- [ ] Read assay presence
- [ ] Flag missing must-have fields
- [ ] Compare density vs distillation sanity
- [ ] Report O2 vs O3 vs O4 explicitly
