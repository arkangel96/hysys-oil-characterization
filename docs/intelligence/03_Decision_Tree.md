# OC-03 — Decision tree

**Status:** DOCS  
**Inventory:** OC-03

```text
Connect case
    │
    ├─ no streams / no case ──────────────► O0 / OX
    │
    ├─ Oil Manager COM unknown ───────────► O1 (discover COM; manual checklist)
    │
    ├─ assay missing / incomplete ────────► O2 (fix assay; no CDU hand-off)
    │
    ├─ assay plausible, checks pending ───► O3 (run OC-01 checklist)
    │
    └─ checklist pass ────────────────────► O4 → hand off to CDU Assist
```

## Smallest experiment

Prefer one evidence read or one reversible Oil Manager correction — never a batch of silent edits.
