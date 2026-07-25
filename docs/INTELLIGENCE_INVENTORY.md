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
| L0 | Connect / streams / structured Oil Manager + FEED composition READ | **CODED** |
| L1 | States O0–O4 / OX + PE board | **CODED** |
| L2 | Assay completeness / LE / TBP QA + MRC JSON load + MB yield check | **CODED** (proposal TBP coverage → OX) |
| L2b | PE mindset = expert CDU + Oil Manager (same as user) | **DOCS** `00_PE_Mindset.md` + Cursor rule |
| L3 | Hypocomponent / cut / blend QA (live NBP classify + blend_fraction gate) | **PARTIAL** |
| L3b | Target output contract (FEED composition / NBP slate verify) | **CODED** read-verify |
| L4 | Oil Manager writes | **PARTIAL** — `characterize_fill_live` (StartOilChange + seed + blend + install); verify NBP* still required |
| L5 | Hand-off token to CDU Assist (O4) | **CODED** `handoff.py` |

## CODED

| Item | Where |
|------|--------|
| Connect / open / solve / disconnect | `hysys_api.py`, `gui.py` |
| Structured Oil Manager + stream composition | `hysys_api.read_oil_manager` / `read_stream_composition` |
| FEED install/attach evidence | `hysys_api.build_feed_evidence` → `models.FeedAttachEvidence` |
| Diagnosis O0–OX (structured HYSYS) | `assay_engine.diagnose_case` |
| LE normalize + TBP QA + completeness | `assay_engine` |
| MB yield check + blend_fraction + feed seed | `assay_engine.material_balance_yield_check` etc. |
| Load MRC Basrah/Mishrif JSON + merge live | `diagnose_mrc_pack` / `merge_diagnosis` |
| Boundary TBP compare | `assay_engine.compare_boundary_tbp` |
| Aspen COM capability map | `aspen_intelligence.COM_CAPABILITY_MAP` |
| Gated COM write stubs | `hysys_api.com_*` + API `allow_COM_write` guard |
| Open Input Assay + enter TBP seed (live) | `open_input_assay_ui` / `enter_tbp_assay_seed_live` + `oil_manager_ui` form map |
| Autonomous Oil Manager fill recipe | `oil_characterize_fill.py` + `HysysController.characterize_fill_live` |
| O4 handoff token | `handoff.write_handoff_o4` + GUI Export |
| PE board + Load MRC / QA / hypo checkbox | `gui.py` |

## DOCS / PLANNED

| ID | Item | Doc | Code hook |
|----|------|-----|-----------|
| OC-PE-00 | Expert CDU + Oil Manager PE mindset (match user) | `intelligence/00_PE_Mindset.md` + `.cursor/rules/oil-char-assay-pe.mdc` | **DOCS** |
| OC-PE-01 | Coded default PE identity (banner, habits, next-actions) | `pe_identity.py` → PE board / GUI | **CODED** |
| OC-COMP-00 | Complementary intelligence package (D1–D6) | `complementary_intelligence/` | **DOCS** |
| OC-COMP-01 | Executable complementary gates (never-rules, O4 block) | `complementary_rules.py` → PE board | **CODED** |
| OC-ASPEN-01 | Aspen characterize methodology (microcuts, TBP prefer, LE &lt;nC5) | `docs/intelligence/aspen/README.md` + `aspen_intelligence.CHARACTERIZATION_RULES` | **CODED** |
| OC-ASPEN-02 | HYSYS OilManager / Assay COM enums + entry plan | `aspen_intelligence.py` → PE board + reads | **CODED** |
| OC-ASPEN-04 | Petroleum Assays / Assays Summary UI map (not MRC FEED path) | `petroleum_assays_ui.py` + COM map section | **CODED** |
| OC-ASPEN-05 | Assay Component Selection — 10 Aspen presets (live V14); OK → Add Assays; MRC Cancel; if forced → Celsius to 1150C | `petroleum_assays_ui.ASSAY_COMPONENT_SELECTION_DIALOG_V14` + `PETROLEUM_ASSAYS_ADD_WORKFLOW_V14` | **CODED** |
| OC-ASPEN-07 | Aspen Assay Library full Select Assay dump (~950 assays: Saturno, Azeri Light, Basrah…) | `config/aspen_assay_library_select_assay_v14.tsv` + `aspen_assay_library_catalog.py` | **CODED** |
| OC-ASPEN-06 | Doc-source audit — only 2/5 CHMs are HYSYS; 3 are WinWrap Basic; no HYSYS user guide | `aspen_intelligence.DOC_SOURCE_INVENTORY` / `DOC_SEARCH_MISSES` / `DOC_COVERAGE_GAP` | **CODED** |
| OC-01 | Required assay inputs (TBP, dens, light ends…) | `intelligence/01_Assay_Completeness.md` | **CODED** `completeness_check` |
| OC-02 | Failure modes / bad characterization | `intelligence/02_Failure_Modes.md` | **PARTIAL** via QA flags |
| OC-02b | Oil Manager FP failure — no Assay Components 1150C; lights-first; LE COM preflight | `intelligence/02b_Oil_Manager_FP_Failure.md` + `preflight_oil_manager_fp` | **CODED** |
| OC-03 | Decision tree → accept / reject feed | `intelligence/03_Decision_Tree.md` | **PARTIAL** `diagnose_assay` |
| OC-04 | COM map for Oil Manager | `COM_DISCOVERY.md` | `hysys_api` **CODED** |
| OC-05 | Hand-off to CDU Assist | `intelligence/04_Handoff_CDU.md` | **CODED** `handoff.py` |
| OC-MRC-00 | MRC project givens checklist (screenshots → Oil Manager vs CDU) | `intelligence/cases/MRC_GIVENS.md` | **DOCS** |
| OC-MRC-01 | MRC proposal feed/product extract (Basrah/Mishrif) | `intelligence/cases/MRC_Basrah_Mishrif_proposal.md` | markdown |
| OC-MRC-02 | Basrah / Mishrif assay JSON (proposal encode) | `intelligence/cases/basrah_assay.json`, `mishrif_assay.json` | **CODED** load + QA |
| OC-MRC-03 | Material balance + battery limits + FINAL_TARGETS JSON | `mrc_*.json` | **CODED** yield check + load |

## Borrowed PE language (from CDU sibling — do not import code)

CDU Assist docs remain the tower authority. This product only reuses the idea:
**bad assay = feed problem — do not chase tower MVs.**
