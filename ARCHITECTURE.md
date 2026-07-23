# Architecture — Oil Characterization Assist v0.1

External COM assist for **crude assay / Oil Manager** in Aspen HYSYS.
**Sibling of CDU Assist** — separate process, code tree, and intelligence track.

```text
PyQt5 desktop UI (gui.py)
    -> assay_engine.py (PE states O0–O4 / OX)
    -> HYSYS COM adapter (hysys_api.py)
        -> Aspen HYSYS case (read-first; no auto-save)
```

## Safety

- Never auto-save `.hsc`
- No silent Oil Manager / property-package rewrite
- Writes only when explicitly designed later with snapshot/restore

## Relationship to CDU Assist

| Product | Owns |
|---------|------|
| This app | Assay completeness, characterization QA, feed OK |
| CDU Assist | Column specs, States A–F, Trial Map |

Hand-off: CDU tower trials only after this app reaches **O4** (assay accepted).

## Build phases

0. Scaffold + connect + PE board (this release)
1. COM discovery for Oils / Assays / Blends
2. Completeness checklist coded from lab sheet fields
3. Hypocomponent / cut QA
4. Optional reversible Oil Manager edits
5. Explicit hand-off payload for CDU Assist
