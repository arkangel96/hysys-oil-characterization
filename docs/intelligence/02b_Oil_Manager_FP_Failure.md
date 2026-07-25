# OC-02b — Live failure lesson: Petroleum Assays slate ≠ Oil Manager FEED

**Status:** CODED (gates in `oil_characterize_fill.py`)  
**Inventory:** OC-02b  
**Case:** `sample.hsc` 2026-07-26 — MRC Basrah attempt

## What went wrong (do not repeat)

| Mistake | Why it burned time |
|---------|-------------------|
| Opened **Petroleum Assays → Add** | Wrong surface for Intertek Basrah/Mishrif FEED |
| OK’d **Assay Components Celsius to 1150C** | Installed ~100 hypo cuts onto Basis-2 — Assay Management slate, not Oil Manager lights |
| Tried Oil Manager LE COM on that FP | `LightEndsCompositionValue` stays empty / SetValues fails → **IsReadyToInstall=False** |
| Bulk + TBP COM still “worked” | Fake progress — blend never Ready without LE slate match |
| Catalogued Aspen Assay Library (~950) mid-job | Reference only; not the Intertek master path |

## Correct Oil Manager order (MRC)

1. **Component list first** — library lights only: Methane…n-Pentane (+ H2O optional @ 0). **Not** Assay Components °C/1150.
2. Fluid package (PR) attached to that list — Basis complete.
3. Oil Manager → associate **that** FP.
4. Input Assay: bulk Used + SG, LE user-input (7 Intertek comps + H2O=0 if present), TBP mass °C.
5. Calculate → Blend → Install → **verify NBP*** (Status can lie).

## Hard bans (automation + PE board)

- Do **not** install Assay Components Celsius/Fahrenheit / FCC / HCR / Reformer presets for MRC Oil Manager FEED.
- Do **not** OK Aspen Assay Library Basrah Light-* as substitute for Intertek DS4.
- Do **not** run `characterize_fill_live` if FP already has `*C*` / `1150` assay-cut hypos or missing C1–nC5 lights.
- If LE composition COM fails → **stop**; fix CompList, do not thrash UIA/Petroleum Assays.

## Intertek LE slate (Basrah) — only these

C1=0, C2=0.54, C3=16.63, iC4=8.24, nC4=27.25, iC5=15.99, nC5=31.34 (of LE cut); LE content 3.21 wt% of crude. H2O not in Intertek table.
