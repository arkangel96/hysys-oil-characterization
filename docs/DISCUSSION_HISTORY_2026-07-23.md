# Discussion history — Oil Characterization Assist

**Product:** Oil Characterization Assist (sibling of CDU Assist)  
**Repo:** https://github.com/arkangel96/hysys-oil-characterization  
**Dates:** 2026-07-23  
**Participants:** User (expert CDU / HYSYS PE) + Agent (Oil Manager / assay characterization specialist)

---

## 1. Product decision

- **Do not** fold oil characterization into CDU Assist (would mix Oil Manager COM surface with tower MV / Trial Map logic).
- **Do** build a **separate program** in sibling folder `oil_characterization/`.
- Same outer workspace is fine; **no cross-imports**; shared ideas only (COM shell pattern, “feed OK?”, PE language).
- Thin gate later in CDU Assist: assay credible → hand off; no Oil Manager workflow inside the tower tool.

**Family concept:**

```text
Tower Assist family
├── CDU Assist              ← column / converge / Trial Map
├── Oil Characterization    ← assay / Oil Manager / feed OK
└── VDU Assist              ← later, separate
```

---

## 2. What existed vs what we built

### CDU Assist (`oil_charateization` / hysys-CDU-assist)

- Strong coded tower intelligence (States A–F, PE board, Trial Map).
- Assay / Oil Manager: mostly PE role + docs (`10_Crude_Assay.md`) — **not** a coded Oil Manager expert.

### Oil Characterization Assist (this repo)

- Scaffold: Connect / streams / components / Oil Manager probe / PE board states **O0–O4 / OX**.
- Intelligence inventory + starter docs.
- User intelligence pack under `docs/intelligence/user_drop/` (v1.0).

**Honest status at end of session:** expert guidance in chat + solid PE pack on disk; app engine still thin heuristics until pack is promoted and assays filled.

---

## 3. MRC project — CDU 70,000 BPSD + LPG (feedstock)

**Doc:** ICDL 001 C 11 T 001 H — Technical Proposal (Client MRC)  
**Unit:** CDU 70000 BPSD + LPG UNIT  
**Design feed:** Basrah crude oils, design API band **28–32**  
**Boundary assays:** Basrah and Mishrif (Intertek, samples drawn 01-03-2010 at DS4, Iraq; ~25 pages each referenced)

### Tabulated bulk (proposal extract)

| Property | Basrah | Mishrif |
|----------|--------|---------|
| API @ 15.6 °C | 32.5 | 26.4 |
| SG @ 15.6 °C | 0.863 | 0.896 |
| Vis @ 20 °C (cSt) | 12.92 | 35.33 |
| Vis @ 40 °C (cSt) | 7.17 | 16.64 |
| Sulphur (wt%) | 2.2 | 3.8 |
| H2S (wt ppm) | 12 | 15 |
| RVP (kg/cm²) | 0.34 | 0.39 |
| BS&W (vol%) | 0.35 | 0.30 |
| Salt norm/design (ppm) | 33/200 | 10/200 |
| CCR (wt%) | 4.42 | 7.10 |
| Asphaltene (wt%) | 2.2 | 3.9 |
| Ash (wt%) | 0.019 | 0.009 |
| TAN (mgKOH/g) | 0.250 | 0.262 |
| V / Ni (wt ppm) | 27 / 8 | 67 / 16 |
| KUOP | 11.98 | 11.82 |
| Light ends bulk (wt% of crude) | 3.21 | 3.26 |

**Note:** Tabulated APIs sit **outside** the stated design band 28–32 → treat as **light / heavy bounds**, not the steady design slate.

### Light ends (composition of LE cut ≈ 100%, not whole crude)

| Component | Basrah wt% of LE | Mishrif wt% of LE |
|-----------|------------------|-------------------|
| C1 | 0.000 | 0.000 |
| C2 | 0.54 | 0.01 |
| C3 | 16.63 | 5.98 |
| i-C4 | 8.24 | 7.90 |
| n-C4 | 27.25 | 27.41 |
| i-C5 | 15.99 | 23.09 |
| n-C5 | 31.34 | 35.60 |

### TBP (cumulative wt% vs T °C) — proposal page 2-10

Assumption to **confirm**: column 1 = Basrah (lighter), column 2 = Mishrif (heavier).

| T °C | Col1 wt% | Col2 wt% |
|------|----------|----------|
| 40 | 2.73 | 2.83 |
| 70 | 6.30 | 4.89 |
| 100 | 10.72 | 7.67 |
| 120 | 13.70 | 9.71 |
| 140 | 16.68 | 12.13 |
| 170 | 21.15 | 16.24 |
| 190 | 24.14 | 18.83 |
| 210 | 27.15 | 21.50 |
| 250 | 33.59 | 26.88 |
| 270 | 37.11 | 29.77 |
| 300 | 42.21 | 33.96 |
| 360 | 52.26 | 43.25 |
| 400 | 58.52 | 49.38 |
| 500 | 71.84 | 64.55 |

ASTM D86 in proposal: empty — use **TBP as primary**; do not invent D86.  
Coverage at 500 °C ≈ 72% / 65% → may fail a strict “≥90 wt% for O2” rule until Intertek residue / higher-T data exists; **no silent extrapolation**.

### Product TBP cut slate (yield checks, not Oil Manager inputs)

| Product | TBP cut °C |
|---------|------------|
| Light naphtha | C5–100 |
| Heavy naphtha | 100–170 |
| Kerosene | 170–230 |
| Light gas oil | 230–335 |
| Heavy gas oil | 335–355 |
| Atm. residue | 355+ |

LPG and product quality specs (SG, ASTM, S, flash, etc.) are **CDU FINAL_TARGETs** — store for later; do not feed them as crude-assay inputs.

---

## 4. Agreed HYSYS characterization path

1. Fluid package (PR provisional) + library lights as needed.  
2. Two separate assays: Basrah, Mishrif — bulk + LE (correct basis) + TBP.  
3. Characterize → review hypos → install → attach to FEED.  
4. Run 100% Basrah, 100% Mishrif, then **named licensor blend only** (do not invent %).  
5. API-matched blends = sensitivity only.  
6. Hand off to CDU Assist only at **O4**.

**Critical Oil Manager rule:** C1–C5 table summing ~100% = composition of **light-ends cut**; convert with:

```text
component_wt_pct_of_crude = LE_bulk_wt_pct_of_crude × component_wt_pct_of_LE / 100
```

---

## 5. Intelligence needed (build order)

### P0
1. Assay data model  
2. Completeness checker (OC-01) → O2 / O3  
3. Light-ends normalize / reject rules  
4. TBP QA (+ Basrah lighter than Mishrif)  
5. Oil Manager PE field map (manual first)  
6. O4 accept gate  

### P1 (MRC)
7. Boundary / design API logic  
8. Cut slate yield checks  
9. Blend policy (no invented %)  
10. Product-spec library as FINAL_TARGETs  

### P2
11. Hypocomponent QA  
12. COM discovery / optional reversible writes  
13. `handoff_o4.json`  

**Build order agreed:** fill assay data → promote docs/inventory → **then** merge code into app (not code-first).

---

## 6. User intelligence pack (saved 2026-07-23)

Location: `docs/intelligence/user_drop/`

| Path | Content |
|------|---------|
| `docs/oil_characterization_intelligence.md` | Full PE pack v1.0 (states, OC-01, LE, TBP, O4, MRC, cuts, defaults) |
| `assay_engine/assay_engine.py` | Coded LE normalize, TBP validate, completeness → O2/O3/OX |
| `config/assay_template.json` | Assay schema |
| `config/handoff_o4_template.json` | O4 hand-off schema |
| `examples/basrah_assay.json` | Stub (API 32.5, LIGHT_BOUND) — **not yet fully filled** |
| `examples/mishrif_assay.json` | Stub (API 26.4, HEAVY_BOUND) — **not yet fully filled** |

### Review notes on the pack

- Framework is strong and aligned with discussion.  
- Example JSONs still need proposal numbers filled.  
- Unit care: proposal RVP kg/cm² → template `rvp_kPa`; salt ppm vs `salt_ptb`.  
- Viscosity @ 20 °C exists in proposal — completeness code should accept it (not only 40/50/100).  
- TBP coverage gap vs O2 ≥90% rule — flag honestly; wait for Intertek or higher-T points.

---

## 7. GitHub

- New public repo created (separate from CDU Assist):  
  **https://github.com/arkangel96/hysys-oil-characterization**  
- CDU Assist remains: https://github.com/arkangel96/hysys-CDU-assist  

---

## 8. Open items (next session)

1. Confirm TBP column 1 = Basrah, column 2 = Mishrif.  
2. Fill `basrah_assay.json` / `mishrif_assay.json` from proposal (and Intertek when available).  
3. Promote `user_drop` pack into curated `docs/intelligence/` + inventory rows.  
4. Merge `user_drop` engine into app-root `assay_engine.py` and PE board.  
5. Lock HYSYS version, thermo, licensor blend %, Oil Manager labels.

---

*Saved so the characterization discussion is recoverable alongside the code.*
