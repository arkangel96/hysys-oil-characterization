# OC-02 — Failure modes (bad characterization)

**Status:** DOCS  
**Inventory:** OC-02

| Failure | Evidence | Response |
|---------|----------|----------|
| Missing distillation | Empty / short curve | State O2 — request lab TBP/ASTM |
| Density vs TBP conflict | Unphysical API vs boiling range | State OX — fix assay before hypo gen |
| No hypocomponents | Fluid package looks like pure library only | State O2 — characterize / install oil |
| Wrong oil on feed | Stream not attached to intended assay | State O2 — re-attach |
| Over-cut / under-cut defs | Cuts ignore plant slate | State O2 — revise cuts; do not tune CDU |
| Silent property-package change | Unexpected FP swap | State OX — stop automation |
| Assay Components 1150C on Oil Manager FP | Many `*C*` hypos; LE COM empty; blend not Ready | State OX — rebuild C1–nC5 CompList; see `02b_Oil_Manager_FP_Failure.md` |
| LE COM empty / IsReadyToInstall=False | Wrong FP or lights missing | State O2 — fix CompList first; do not open Petroleum Assays |
| Aspen Library Basrah Light-* as Intertek | Commercial model ≠ DS4 2010 master | State OX — use MRC_GIVENS / Intertek only |

## PE habit

Treat characterization failure as **feed truth** failure — not reflux / draw failure.

**2026-07-26 lesson:** Petroleum Assays gate + 1150C slate burns the Oil Manager LE path. Lights-first CompList, then characterize. Coded: `preflight_oil_manager_fp`.
