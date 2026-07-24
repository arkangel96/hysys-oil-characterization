# OC-D4 — Learning and Memory

**Complementary** — what to remember across sessions without inventing plant truth.

## Remember (project memory)

- Crude IDs and boundary roles (Basrah light / Mishrif heavy)  
- Source tags (proposal vs Intertek) and confidence  
- TBP column assumptions and confirmations  
- Flags that blocked O2/O3 (e.g. `TBP_COVERAGE_BELOW_O2`)  
- FEED seed T/P/rate from battery limits + MB  
- HYSYS version / thermo once locked  
- Licensor blend % only when explicitly given  

## Do not remember as truth

- Invented blend percentages  
- Extrapolated TBP tails  
- Unverified COM member names as universal  

## Lesson schema (light)

```yaml
lesson:
  crude_id: BASRAH|MISHRIF|BLEND
  assay_tag: string
  flag: string
  what_worked: string
  what_failed: string
  hysys_version: string|null
```

Store under `docs/intelligence/cases/` or future `lessons/` — inventory before code.
