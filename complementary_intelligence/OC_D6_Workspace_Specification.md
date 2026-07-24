# OC-D6 — Workspace Specification

## Repos / folders

| Path | Role |
|------|------|
| `oil_characterization/` | **This product** — app + inventory + cases |
| `oil_characterization/complementary_intelligence/` | Complementary OS (this package) |
| `oil_characterization_intelligence_pack_v1/` | Standalone pack copy (canonical PE text) |
| `oil_charateization/` | CDU Assist sibling — do not import |

## Where to put what

| Artifact | Location |
|----------|----------|
| Binding PE mindset | `docs/intelligence/00_PE_Mindset.md` |
| Assay QA code | `assay_engine.py` |
| MRC assay / MB / BL / targets | `docs/intelligence/cases/` |
| User drops | `docs/intelligence/user_drop/` |
| Complementary rules | `complementary_intelligence/` |
| Cursor always-on role | `.cursor/rules/oil-char-assay-pe.mdc` |

## Consolidation note

Prefer **one active truth**: Inventory + cases + `assay_engine`.  
Pack v1 folder and complementary folder **clarify**; they must not diverge into conflicting LE/TBP rules. Reconcile before coding conflicts.
