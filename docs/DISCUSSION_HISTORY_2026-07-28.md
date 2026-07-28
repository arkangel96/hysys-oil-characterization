# Discussion history — 2026-07-28

**Product:** Oil Characterization Assist  
**Case:** `sample.hsc` (Aspen HYSYS V14)

## Done

- Connected COM to open `sample.hsc`
- Read MRC proposal PDF (`MRC Diwanya Refinery_ABG Technical Proposal_RH (1).pdf`) for FEED data
- Verified Oil Manager inputs vs proposal:
  - `Basrah_Assay` / `Mishrif` — LE + TBP match
  - Blends ready; streams `basrah raw`, `Raw Crude Mishrif` have lights + NBP*
- FEED **composition** OK for CDU hand-off
- Not runnable yet on oil-only basis: need T/P/flow; tower work is separate
- Case later showed simplified CDU shell: PreFlash → Crude Heater → Mixer → T-100
- PFD narrative taken from proposal §2.2 (filters → desalter → H01 → C01 → products / LPG train)
- Disconnected, then reconnected on request

## PE notes left open

- Soft heavy end (TBP ~72% / ~65% @ 500 °C)
- Basrah / Mishrif = bounds, no invented blend %
- Prefer Intertek masters if they conflict with proposal extract
