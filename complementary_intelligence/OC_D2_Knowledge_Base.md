# OC-D2 — Knowledge Base (Oil Characterization)

**Complementary map** — detail lives in pack v1 + MRC cases; this indexes topics.

## Assay / input knowledge

| Topic | Owner doc / data |
|-------|------------------|
| Completeness O2/O3/OX | Pack v1 OC-01; `assay_engine.completeness_check` |
| Light ends basis | Pack v1 LE rules; `normalize_light_ends` |
| TBP QA | Pack v1; `validate_tbp` |
| MRC Basrah / Mishrif values | `docs/intelligence/cases/*_assay.json` |
| Material balance yields | `mrc_material_balance.json` |
| Battery limits / FEED seed | `mrc_battery_limits.json` |
| Product specs | `mrc_final_targets.json` (CDU later) |

## Oil Manager / HYSYS knowledge

| Topic | Notes |
|-------|-------|
| Bulk properties | API/SG, vis, S, RVP, CCR, asphaltene, TAN |
| Light components | Whole-crude amounts after LE normalize |
| Distillation | TBP mass preferred when D86 empty |
| Characterize | Generates hypocomponents / NBP* |
| Install + attach | Required for FEED composition |
| Thermo | PR provisional until project locks FP |

## Failure modes (short)

- Unresolved LE basis  
- Non-monotonic / short TBP  
- API vs SG contradiction  
- Swapped boundary curves  
- Characterize without install/attach  
- Using product ASTM specs as assay inputs  

## CDU interface knowledge

- Bad feed → CDU State A style problem (feed OK?)  
- FINAL_TARGETs for products ≠ assay  
- Hand-off artifact: `handoff_o4.json` template in pack config  
