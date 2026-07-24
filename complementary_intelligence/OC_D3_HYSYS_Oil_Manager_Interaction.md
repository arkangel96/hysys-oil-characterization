# OC-D3 — HYSYS Oil Manager Interaction

**Complementary to:** pack v1 “Oil Manager PE Map” + `docs/COM_DISCOVERY.md`

## Read first (allowed anytime)

- Case / fluid package / material streams  
- Oil Manager / Oils / Assays presence (COM probe)  
- FEED conditions + composition after install  
- Petroleum properties on FEED when exposed  

## Write only with explicit PE intent (later / gated)

| Action | Status |
|--------|--------|
| Enter assay bulk / LE / TBP | Manual first (`manual_oil_manager_first: true`) |
| Characterize / install / attach | Manual first; COM write **inventory-gated** |
| Change property package | Never silent |
| Auto-save `.hsc` | **Never** |

## Interaction sequence (engineering)

```text
1. QA assay JSON (Assist)
2. Enter Oil Manager fields (manual)
3. Characterize
4. Review hypo count, NBP order, SG/MW trend, heavy end
5. Install oil → attach to FEED
6. Confirm Worksheet Composition (lights + NBP*)
7. Optional: yield check vs material balance
8. handoff_o4.json → CDU Assist
```

## Output contract (target)

Success looks like FEED **Composition**: library components + `NBP[0]…*` (or project naming)
with consistent mole/mass fractions. Exact cut width / naming from **engineering document**
when provided (`OC-OUT-01` — planned). Do not invent Aspen cut scheme.

## Units

- Prefer worksheet / Oil Manager display units  
- Convert proposal units on ingest (e.g. RVP kg/cm² → kPa) and keep both if useful  
