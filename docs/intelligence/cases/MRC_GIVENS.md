# MRC project givens — Oil Characterization Assist

**Source:** ICDL 001 C 11 T 001 H — TECHNICAL PROPOSAL (screenshots 2026-07-25)  
**Client:** MRC  
**Project / unit:** CDU 70000 BPSD + LPG UNIT  
**Status:** Proposal extract. Prefer full **INTERTEK** 25-page masters when they conflict.

This file is the **givens checklist** for Oil Manager work. Product specs and tower narrative are recorded only so they are **not** mistaken for assay inputs.

---

## 0. Product boundary (binding)

| Given | Oil Manager / FEED? | CDU Assist later? |
|-------|---------------------|-------------------|
| Basrah / Mishrif bulk + LE + TBP | **YES** | — |
| Empty ASTM D86 | Do **not** invent | — |
| Design API 28–32; tabulated 32.5 / 26.4 | Bounds only — **no invented blend %** | Sensitivity later |
| Inlet P, filters, preheat, desalter | Stream conditions / narrative | Process narrative |
| LPG / naphtha / kero / GO / residue specs | **NO** | FINAL_TARGETs |
| Material balance %wt yields | Yield **check** after characterize | Column targets |

---

## 1. Drawing / capacity references (§2.2 Process Flow — Rev. F)

| Drawing | Scope |
|---------|--------|
| ICDL 001 C 11 A 001 | CDU 70000 BPSD + LPG — **Basrah** Crude Oil |
| ICDL 001 C 11 A 003 | CDU 70000 BPSD + LPG — **Mishrif** Crude Oil |
| ICDL 001 C 17 A 001 | Sweetening Unit — LPG from Basrah Crude Oil |

**Capacity given:** 70,000 BPSD (per drawing titles).

---

## 2. Inlet / front-end process narrative (§2.2) — not Oil Manager assay

Recorded for FEED seed / CDU context only:

| Item | Given |
|------|--------|
| Inlet from distribution line | **3.0 kg/cm² g** |
| Mechanical filters | **M09** — two parallel; one operating, one cleaned / standby |
| Crude pumps | **P01** |
| Preheat exchangers | **E01–E05** → **135–140 °C** |
| Desalter | One-stage electrostatic **D04**, mud wash |
| Desalter pressure | **10.5–12.5 kg/cm² g** |

Battery-limit FEED seed (already in `mrc_battery_limits.json`): crude **~40 °C**, **3.0 kg/cm² g** at BL — distinct from desalter / transfer temperatures above.

---

## 3. Feedstock design intent (§2.4.1 Rev. B)

- Unit designed to process **Basrah crude oils**
- Design **API range: 28–32**
- Two **boundary** states (not a named blend %):
  1. **Basrah** crude oil  
  2. **Mishrif** crude oil  

### Lab supplement (proposal page 2-9)

Original tender feed analyses incomplete; PE used INTERTEK:

| Crude | Laboratory | Sample | Pages |
|-------|------------|--------|-------|
| Basrah Crude Oil | INTERTEK | drawn 01-03-2010 at DS4, Iraq | 25 |
| Basrah Mishrif Crude Oil | INTERTEK | drawn 01-03-2010 at DS4, Iraq | 25 |

---

## 4. Bulk qualities (proposal table)

| Property | Unit | Basrah | Mishrif |
|----------|------|--------|---------|
| API Gravity @ 15.6 °C | — | **32.5** | **26.4** |
| Spec. Gravity @ 15.6 °C | — | **0.863** | **0.896** |
| Kin. viscosity @ 20 °C | cSt | 12.92 | 35.33 |
| Kin. viscosity @ 40 °C | cSt | 7.17 | 16.64 |
| Sulphur | wt.% | 2.2 | 3.8 |
| H₂S | wt.ppm | 12 | 15 |
| Pour Point MIN / MAX | °C | &lt;-36 / -24 | &lt;-42 / -36 |
| R.V.P. | kg/cm² | 0.34 | 0.39 |
| BS&W | vol.% | 0.35 | 0.30 |
| Salt Norm. / Design | ppm | 33 / 200 | 10 / 200 |
| Carbon residue | wt.% | 4.42 | 7.10 |
| Asphaltene | wt.% | 2.2 | 3.9 |
| Ash content | wt.% | 0.019 | 0.009 |
| Total acid number | mgKOH/g | 0.250 | 0.262 |
| Vanadium | wt.ppm | 27 | 67 |
| Nickel | wt.ppm | 8 | 16 |
| KUOP character. factor | — | 11.98 | 11.82 |

**PE:** Tabulated APIs sit **outside** design band 28–32 → **LIGHT_BOUND / HEAVY_BOUND**. Do not invent a blend % to land inside 28–32.

**Oil Manager bulk entry (Basrah first):** SG **0.863** (API 32.5); set **Bulk Properties = Used**.

---

## 5. Light ends (proposal page 2-10)

| | Basrah | Mishrif |
|--|--------|---------|
| **Light ends content** | **3.21 wt%** of crude | **3.26 wt%** of crude |

### Composition — wt% **of the light-ends cut** (sums ≈ 100% of LE cut)

| Component | Basrah | Mishrif |
|-----------|--------|---------|
| C1 | 0.000 | 0.000 |
| C2 | 0.54 | 0.01 |
| C3 | 16.63 | 5.98 |
| i-C4 | 8.24 | 7.90 |
| n-C4 | 27.25 | 27.41 |
| i-C5 | 15.99 | 23.09 |
| n-C5 | 31.34 | 35.60 |

**Oil Manager:** User-input LE; bulk % of crude + cut composition. CompList lights: C1–nC5 + H2O (H2O = 0 if not in LE table).

---

## 6. Distillation T.B.P. (cumulative wt%)

**Column assumption (confirm vs Intertek):** Col 1 = Basrah (lighter), Col 2 = Mishrif (heavier).

| T °C | Basrah wt% | Mishrif wt% |
|------|------------|-------------|
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
| 500 | **71.84** | **64.55** |

### ASTM D86 (proposal)

All points **empty** (`-`). **Do not invent D86.** TBP is primary.

### Coverage

At 500 °C soft heavy end (~72% / ~65%). **No silent TBP extrapolation.** Full INTERTEK residue / higher-T preferred for O2 coverage.

---

## 7. What is encoded already (code hooks)

| Given | Where |
|-------|--------|
| Basrah bulk / LE / TBP | `docs/intelligence/cases/basrah_assay.json` + `BASRAH_OIL_MANAGER_SEED` |
| Mishrif bulk / LE / TBP | `docs/intelligence/cases/mishrif_assay.json` |
| Longer proposal extract (+ products, MB) | `MRC_Basrah_Mishrif_proposal.md` |
| Battery-limit FEED T/P | `mrc_battery_limits.json` |
| Fill recipe | `oil_characterize_fill.py` / `characterize_fill_live` |

---

## 8. Characterization order (from these givens)

1. **Basrah** Oil Manager TBP first (this pack)  
2. Then **Mishrif** as second oil  
3. Install → **Raw Crude** (lights + `NBP[0]*`)  
4. Yield check vs MB; CDU FINAL_TARGETs only at **O4** handoff  

*Documented from user screenshots 2026-07-25 — givens first, before further automate.*
