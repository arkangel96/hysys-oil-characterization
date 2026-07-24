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
| L1 | States O0–O4 / OX + PE board | **CODED** |
| L2 | Assay completeness / LE / TBP QA + MRC JSON load | **CODED** (proposal TBP coverage → OX) |
| L2b | PE mindset = expert CDU + Oil Manager (same as user) | **DOCS** `00_PE_Mindset.md` + Cursor rule |
| L3 | Hypocomponent / cut / blend QA | **PLANNED** |
| L3b | Target output contract (FEED composition / NBP slate) | **PLANNED** — await eng. doc paste |
| L4 | Reversible Oil Manager writes | **PLANNED** |
| L5 | Hand-off token to CDU Assist (O4) | **PLANNED** |

## CODED

| Item | Where |
|------|--------|
| Connect / open / solve / disconnect | `hysys_api.py`, `gui.py` |
| Stream + component snapshot | `hysys_api.snapshot` |
| Oil Manager attribute probe | `hysys_api.probe_oil_manager` |
| Diagnosis O0–OX (HYSYS heuristic) | `assay_engine.diagnose_case` |
| LE normalize + TBP QA + completeness | `assay_engine` |
| Load MRC Basrah/Mishrif JSON | `assay_engine.load_assay` / `diagnose_mrc_pack` |
| Boundary TBP compare | `assay_engine.compare_boundary_tbp` |
| PE board + Load MRC / QA buttons | `gui.py` |

## DOCS / PLANNED

| ID | Item | Doc | Code hook |
|----|------|-----|-----------|
| OC-PE-00 | Expert CDU + Oil Manager PE mindset (match user) | `intelligence/00_PE_Mindset.md` + `.cursor/rules/oil-char-assay-pe.mdc` | **DOCS** |
| OC-PE-01 | Coded default PE identity (banner, habits, next-actions) | `pe_identity.py` → PE board / GUI | **CODED** |
| OC-COMP-00 | Complementary intelligence package (D1–D6) | `complementary_intelligence/` | **DOCS** |
| OC-COMP-01 | Executable complementary gates (never-rules, O4 block) | `complementary_rules.py` → PE board | **CODED** |
| OC-ASPEN-01 | Aspen characterize methodology (microcuts, TBP prefer, LE &lt;nC5) | `docs/intelligence/aspen/README.md` + `aspen_intelligence.CHARACTERIZATION_RULES` | **CODED** |
| OC-ASPEN-02 | HYSYS OilManager / Assay COM enums + entry plan | `aspen_intelligence.py` → PE board + `probe_oil_manager` | **CODED** |
| OC-01 | Required assay inputs (TBP, dens, light ends…) | `intelligence/01_Assay_Completeness.md` | **CODED** `completeness_check` |
| OC-02 | Failure modes / bad characterization | `intelligence/02_Failure_Modes.md` | **PARTIAL** via QA flags |
| OC-03 | Decision tree → accept / reject feed | `intelligence/03_Decision_Tree.md` | **PARTIAL** `diagnose_assay` |
| OC-04 | COM map for Oil Manager | `COM_DISCOVERY.md` | `hysys_api` |
| OC-05 | Hand-off to CDU Assist | `intelligence/04_Handoff_CDU.md` | later |
| OC-MRC-01 | MRC proposal feed/product extract (Basrah/Mishrif) | `intelligence/cases/MRC_Basrah_Mishrif_proposal.md` | markdown |
| OC-MRC-02 | Basrah / Mishrif assay JSON (proposal encode) | `intelligence/cases/basrah_assay.json`, `mishrif_assay.json` | **CODED** load + QA |
| OC-MRC-03 | Material balance + battery limits + FINAL_TARGETS JSON | `mrc_*.json` | **CODED** load in `diagnose_mrc_pack` |

## Borrowed PE language (from CDU sibling — do not import code)

CDU Assist docs remain the tower authority. This product only reuses the idea:
**bad assay = feed problem — do not chase tower MVs.**
