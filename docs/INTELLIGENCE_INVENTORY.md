# Intelligence Inventory — Oil Characterization Assist

**Rule:** Do not add a new assay PE rule until it has a row here (status + doc + code hook).

| Status | Meaning |
|--------|---------|
| **CODED** | Runs in Python today |
| **PARTIAL** | Thin / discovery-only |
| **DOCS** | Spec exists — not executable yet |
| **PLANNED** | Agreed next — do not implement early |

## Layer snapshot

| Layer | Content | Status |
|-------|---------|--------|
| L0 | Connect / streams / components / Oil Manager probe | **CODED** |
| L1 | States O0–O4 / OX + PE board | **PARTIAL** (heuristic) |
| L2 | Assay completeness vs lab sheet | **DOCS** |
| L3 | Hypocomponent / cut / blend QA | **PLANNED** |
| L4 | Reversible Oil Manager writes | **PLANNED** |
| L5 | Hand-off token to CDU Assist (O4) | **PLANNED** |

## CODED

| Item | Where |
|------|--------|
| Connect / open / solve / disconnect | `hysys_api.py`, `gui.py` |
| Stream + component snapshot | `hysys_api.snapshot` |
| Oil Manager attribute probe | `hysys_api.probe_oil_manager` |
| Diagnosis O0–OX (first pass) | `assay_engine.diagnose_case` |
| PE board text | `assay_engine.format_pe_board` |

## DOCS / PLANNED

| ID | Item | Doc | Code hook |
|----|------|-----|-----------|
| OC-01 | Required assay inputs (TBP, dens, light ends…) | `intelligence/01_Assay_Completeness.md` | `assay_engine` |
| OC-02 | Failure modes / bad characterization | `intelligence/02_Failure_Modes.md` | `assay_engine` |
| OC-03 | Decision tree → accept / reject feed | `intelligence/03_Decision_Tree.md` | `assay_engine` |
| OC-04 | COM map for Oil Manager | `COM_DISCOVERY.md` | `hysys_api` |
| OC-05 | Hand-off to CDU Assist | `intelligence/04_Handoff_CDU.md` | later |

## Borrowed PE language (from CDU sibling — do not import code)

CDU Assist docs remain the tower authority. This product only reuses the idea:
**bad assay = feed problem — do not chase tower MVs.**
