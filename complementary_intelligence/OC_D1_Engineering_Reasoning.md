# OC-D1 — Engineering Reasoning (Oil Characterization)

**Complementary to:** intelligence pack v1 + `00_PE_Mindset.md`  
**Does not supersede:** OC-01 completeness, LE/TBP coded QA

---

## Objective

Reason like an expert HYSYS PE preparing **credible CDU feed** via Oil Manager.

## Priority stack

1. Physical / assay honesty (LE basis, TBP monotonic, no invented curves)  
2. Traceable source (Intertek > proposal extract when they conflict)  
3. Successful characterize → install → FEED composition  
4. Directional yield check vs design material balance  
5. O4 hand-off readiness  
6. CDU FINAL_TARGETs (store only — do not drive Oil Manager)  

## Observation before action

Always collect:

- Crude ID / boundary role (light vs heavy)  
- Bulk: API/SG, vis, S, RVP, CCR, asphaltene, metals as available  
- Light ends: bulk wt% of crude + composition basis  
- TBP: T vs cum wt%; max coverage  
- Design book: material balance %, BL T/P (separate objects)  

## Hypotheses (typical)

| Symptom | Prefer | Avoid |
|---------|--------|-------|
| TBP coverage &lt; 90% | Request residue / Intertek; flag OX | Silent extrapolation |
| LE sums ~100% | Treat as LE-cut composition | Paste as whole-crude mole frac |
| Basrah heavier than Mishrif on TBP | Swap columns / mislabel | “Characterize anyway” |
| Hypos look wrong / FEED empty | Re-characterize / re-attach | Tune CDU reflux |
| Yields far from MB | Cut defs / assay gap | Blame condenser first |

## Experiment style

- One crude at a time  
- Smallest honest fix  
- Preserve rollback (no auto-save; snapshot case manually)  
- Explain every recommendation expert-to-expert  

## Done criterion (reasoning)

FEED Worksheet shows library lights + ordered NBP/hypo slate, oil attached,
yields not absurd vs MB, state **O4** only after hypo review.
