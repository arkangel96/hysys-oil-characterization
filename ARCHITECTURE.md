# Architecture — Oil Characterization Assist v0.1

External COM assist for **crude assay / Oil Manager** in Aspen HYSYS.
**Sibling of CDU Assist** — separate process, code tree, and intelligence track.

```text
PyQt5 desktop UI (gui.py)
    -> assay_engine.py (PE states O0–O4 / OX) + handoff.py (O4 token)
    -> aspen_intelligence.py (enums / COM capability map)
    -> HYSYS COM adapter (hysys_api.py)
        -> Aspen HYSYS case (READ-first; gated writes; no auto-save)
```

**Code root:** edit repo root modules only. Nested `oil_characterization/` is a duplicate.

## Safety

- Never auto-save `.hsc`
- No silent Oil Manager / property-package rewrite
- `allow_COM_write=false` API guard on all `com_*` write stubs
- O4 handoff is a JSON file only — no CDU import / no auto-launch

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
