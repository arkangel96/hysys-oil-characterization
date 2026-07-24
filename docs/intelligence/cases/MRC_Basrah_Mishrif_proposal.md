# MRC CDU 70,000 BPSD — Feed & product data (proposal extract)

**Source document:** ICDL 001 C 11 T 001 H — TECHNICAL PROPOSAL  
**Client:** MRC  
**Project / unit:** CDU 70000 BPSD + LPG UNIT  
**Section:** 2.4 Feed and Products Specification (Rev. B)  
**Captured:** 2026-07-24 (from user-pasted pages)  
**Status:** Proposal extract — prefer full INTERTEK reports when available for master assay

---

## 1. Feedstock design intent (§2.4.1)

- Unit designed to process **Basrah crude oils**
- Design **API range: 28–32**
- Represented by two **boundary** assays:
  1. **Basrah** crude oil
  2. **Mishrif** crude oil

### Lab supplement (page 2-9)

Original tender feed analyses were incomplete; PE supplemented with:

| Crude oil | Laboratory | Sample | Pages |
|-----------|------------|--------|-------|
| Basrah Crude Oil | INTERTEK | drawn 01-03-2010 at DS4, Iraq | 25 |
| Basrah Mishrif Crude Oil | INTERTEK | drawn 01-03-2010 at DS4, Iraq | 25 |

---

## 2. Bulk properties (blend-component qualities table)

| Property | Unit | Basrah | Mishrif |
|----------|------|--------|---------|
| API Gravity at 15.6 °C | — | 32.5 | 26.4 |
| Spec. Gravity at 15.6 °C | — | 0.863 | 0.896 |
| Kinematic viscosity at 20 °C | cSt | 12.92 | 35.33 |
| Kinematic viscosity at 40 °C | cSt | 7.17 | 16.64 |
| Sulphur | wt.% | 2.2 | 3.8 |
| H₂S | wt.ppm | 12 | 15 |
| Pour Point (MIN / MAX) | °C | &lt;-36 / -24 | &lt;-42 / -36 |
| R.V.P. | kg/cm² | 0.34 | 0.39 |
| BS&W | vol.% | 0.35 | 0.30 |
| Salt (Norm. / Design) | ppm | 33 / 200 | 10 / 200 |
| Carbon residue | wt.% | 4.42 | 7.10 |
| Asphaltene | wt.% | 2.2 | 3.9 |
| Ash content | wt.% | 0.019 | 0.009 |
| Total acid number | mgKOH/g | 0.250 | 0.262 |
| Vanadium | wt.ppm | 27 | 67 |
| Nickel | wt.ppm | 8 | 16 |
| KUOP characterization factor | — | 11.98 | 11.82 |

**PE note:** Tabulated APIs (32.5 / 26.4) sit **outside** the stated design band 28–32 → treat as light/heavy **bounds**, not the steady design slate.

### Unit conversions for assay schema (when encoding JSON)

| Proposal field | Schema field | Conversion |
|----------------|--------------|------------|
| R.V.P. kg/cm² | `rvp_kPa` | × 98.0665 → Basrah **33.34**, Mishrif **38.25** kPa (rounded) |
| Salt ppm (norm.) | store as note + optional `salt_ptb` | 1 ppm ≈ 0.35 ptb (approx.); keep **ppm in notes** until unit locked |
| BS&W vol.% | `water_wt_pct` not exact | store BS&W in notes; do not force as water wt% |

---

## 3. Light ends

| | Basrah | Mishrif |
|--|--------|---------|
| **Total light ends content** | **3.21 wt%** of crude | **3.26 wt%** of crude |

### Composition (wt% of light-ends cut — sums ≈ 100%)

| Component | Basrah | Mishrif |
|-----------|--------|---------|
| C1 | 0.000 | 0.000 |
| C2 | 0.54 | 0.01 |
| C3 | 16.63 | 5.98 |
| i-C4 | 8.24 | 7.90 |
| n-C4 | 27.25 | 27.41 |
| i-C5 | 15.99 | 23.09 |
| n-C5 | 31.34 | 35.60 |

**Oil Manager rule:** enter bulk LE of crude + composition of LE cut; do **not** enter the composition table as whole-crude composition.

---

## 4. Distillation TBP (cumulative wt%)

**Assumption (to confirm):** Column 1 = **Basrah** (lighter), Column 2 = **Mishrif** (heavier). Matches API / mid-curve yields.

| Temperature °C | Basrah (col 1) wt% | Mishrif (col 2) wt% |
|----------------|--------------------|---------------------|
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

### ASTM D86 (proposal)

All cells **empty** (`-`). Do **not** invent D86. Use **TBP as primary**.

### Coverage warning

Max cum. yield at 500 °C ≈ **71.84% / 64.55%**. Strict O2 “≥90 wt% TBP coverage” may fail until Intertek residue / higher-T points exist. **No silent extrapolation.**

---

## 5. Product specifications (§2.4.2) — CDU FINAL_TARGETs later

These are **not** Oil Manager assay inputs. Store for CDU Assist hand-off.

### LPG

| Property | Unit | Spec |
|----------|------|------|
| C2 | mol.% | 0.6 max |
| C3 winter / summer | mol.% | 31–41 / 22–32 |
| C4 winter / summer | mol.% | 54–64 / 63–73 |
| C5 | mol.% | 1.5 max |
| Olefins | mol.% | 0.1 max |
| Propane purity (in propane fraction) | vol.% | 95 min |
| Sulphur | wt.ppm | 50 max |
| H₂S (copper strip) | — | 1A |
| R.V.P. | kg/cm² a | 6.3–10 |
| Water | wt.% | Nil |

### Light naphtha — TBP cut C5–100 °C

| Property | Spec |
|----------|------|
| SG @ 15 °C | 0.650–0.690 |
| R.V.P. | 0.65 max kg/cm² a |
| ASTM D86 IBP | 35 min °C |
| ASTM D86 EBP | 150 max °C |
| Water | 100 max ppm |

### Heavy naphtha — TBP cut 100–170 °C

| Property | Spec |
|----------|------|
| SG @ 15 °C | 0.715–0.755 |
| ASTM D86 IBP | 90 min °C |
| ASTM D86 EBP | 178 max °C |
| Water | 100 max ppm |

### Kerosene — TBP cut 170–230 °C

| Property | Spec |
|----------|------|
| SG @ 15 °C | 0.785–0.810 |
| Total sulphur | 0.50 max wt.% (note 1) |
| Flash point | 40 min °C; +30 min (+20 min for blends with Mishrif) |
| ASTM D86 IBP | 135 min °C |
| ASTM D86 EBP | 250 max °C |

### Light gas oil — TBP cut 230–335 °C

| Property | Spec |
|----------|------|
| SG @ 15 °C | 0.825–0.855 |
| Total sulphur | 1.50 max wt.% (note 1) |
| Flash point | 70 min °C |
| Color ASTM | 0.5 max |
| ASTM D86 IBP | 200 min °C |
| ASTM D86 EBP | 350 max °C |

### Heavy gas oil — TBP cut 335–355 °C

| Property | Spec |
|----------|------|
| SG @ 15 °C | 0.870–0.910 |
| Total sulphur | 3.00 max wt.% (note 1) |
| Flash point | 90 min °C |
| Color ASTM | 2.5 max |
| ASTM D1160 95 vol% | 420 max °C |

### Atm. residue (reduced crude) — TBP cut 355+ °C

| Property | Spec |
|----------|------|
| SG @ 15 °C | 0.930–0.970 |
| Flash point | 120 min °C |
| Viscosity @ 50 °C | 350–3000 cSt |
| Viscosity @ 100 °C | 25–105 cSt |

---

## 6. Cut slate (yield checks after characterize)

```yaml
cut_slate_C:
  light_naphtha: [5, 100]      # C5 treated as ~5 °C proxy if needed
  heavy_naphtha: [100, 170]
  kerosene: [170, 230]
  light_gas_oil: [230, 335]
  heavy_gas_oil: [335, 355]
  residue: [355, null]
```

---

## 7. Material balance (§2.5 Rev. F) — design yields / feed rate

**Basis:** Dry crude oil (stated on Mishrif page).  
**Use:** Post-characterization yield check targets and FEED rate for HYSYS case — **not** Oil Manager assay inputs.

### 7.1 Basrah crude oil (§2.5.1)

| Fluid | %wt | %vol | Nom 100% kg/h | Nom 100% m³/h @15°C | Max 105% kg/h | Max 105% m³/h @15°C |
|-------|-----|------|---------------|---------------------|---------------|---------------------|
| Off Gas | 0.01 | — | 40 | — | 40 | — |
| Fuel Gas | 0.06 | — | 260 | — | 270 | — |
| Sour Gas | 0.01 | — | 50 | — | 50 | — |
| LPG | 1.66 | 2.56 | 6,650 | 11.9 | 6,990 | 12.5 |
| Light Naphtha | 8.35 | 10.76 | 33,420 | 49.9 | 35,100 | 52.4 |
| Heavy Naphtha | 12.53 | 13.50 | 50,160 | 62.6 | 52,660 | 65.8 |
| Kerosene | 8.50 | 9.14 | 34,010 | 42.4 | 35,710 | 44.5 |
| Light Gas Oil | 16.89 | 17.34 | 67,620 | 80.4 | 71,000 | 84.4 |
| Heavy Gas Oil | 3.36 | 3.24 | 13,444 | 15.0 | 14,114 | 15.8 |
| Atm. Residue (Red. Crude) | 48.62 | 43.45 | 194,606 | 201.5 | 204,336 | 211.6 |
| **Crude Oil (Total)** | **100.00** | **100.00** | **400,260** | **463.7** | **420,270** | **487.0** |

### 7.2 Mishrif crude oil (§2.5.2, page 2-14)

| Fluid | %wt | %vol | Nom 100% kg/h | Nom 100% m³/h @15°C | Max 105% kg/h | Max 105% m³/h @15°C |
|-------|-----|------|---------------|---------------------|---------------|---------------------|
| Off Gas | 0.06 | — | 270 | — | 280 | — |
| Fuel Gas | 0.04 | — | 180 | — | 190 | — |
| Sour Gas | 0.01 | — | 50 | — | 50 | — |
| LPG | 1.32 | 2.07 | 5,480 | 9.6 | 5,760 | 10.1 |
| Light Naphtha | 6.40 | 8.56 | 26,600 | 39.7 | 27,930 | 41.7 |
| Heavy Naphtha | 9.60 | 11.13 | 39,900 | 51.6 | 41,900 | 54.2 |
| Kerosene | 7.30 | 8.11 | 30,330 | 37.6 | 31,850 | 39.5 |
| Light Gas Oil | 14.59 | 15.42 | 60,650 | 71.5 | 63,680 | 75.1 |
| Heavy Gas Oil | 3.10 | 2.97 | 12,850 | 13.8 | 13,494 | 14.5 |
| Atm. Residue (Red. Crude) | 57.58 | 51.74 | 239,320 | 239.9 | 251,286 | 251.9 |
| **Crude Oil (Total)** | **100.00** | **100.00** | **415,630** | **463.7** | **436,420** | **487.0** |

### PE notes (material balance)

- Same **volumetric** crude rate at BL: **463.7 m³/h @15°C** (100%) / **487.0 m³/h** (105%) for both crudes; mass differs (Basrah lighter → lower kg/h).
- Mishrif has **more residue** (57.58 vs 48.62 wt%) and **less naphtha/kero/LGO** — consistent with heavier TBP / lower API.
- After Oil Manager characterize, compare TBP cut yields to these **%wt** columns (expect directionally similar; exact match depends on cut defs / recovery).
- FEED for HYSYS: start with **463.7 m³/h @15°C** (or mass equivalent) at battery-limit T/P.

---

## 8. Battery limit conditions (§2.6 Rev. B)

| Fluid | Temp. °C | Press. kg/cm² g |
|-------|----------|-----------------|
| Crude Oil | norm 40 / min 10 | 3.0 |
| LPG | 40 | 12.0 |
| Light Naphtha | 38 | 4.0 |
| Heavy Naphtha | 40 | 4.0 |
| Heavy Naphtha (hot stream) | 98–101 | 4.0 |
| Kerosene | 40 | 3.0 |
| Kerosene (hot stream) | 70–84 | 3.0 |
| Light Gas Oil | 45 | 4.0 |
| Light Gas Oil (hot stream) | 106–118 | 4.0 |
| Heavy Gas Oil | 45 | 3.0 |
| Atm. Residue | 90 | 5.0 |

**FEED stream seed (characterization → flowsheet):** T ≈ **40 °C**, P ≈ **3.0 kg/cm² g** (≈ 2.94 barg), rate from §7.

---

## 9. Open confirmations

1. Confirm TBP column 1 = Basrah, column 2 = Mishrif  
2. Obtain full INTERTEK 25-page packs (master over proposal extract)  
3. Licensor design blend % (if any) — do not invent  
4. HYSYS version + thermo package  

---

## 10. Next encoding step (after this doc)

Populate:

- `docs/intelligence/user_drop/examples/basrah_assay.json`
- `docs/intelligence/user_drop/examples/mishrif_assay.json`

from **§2–§4** only (assay).  

**Encoded JSON (2026-07-24):**

- `basrah_assay.json` / `mishrif_assay.json`
- `mrc_material_balance.json`
- `mrc_battery_limits.json`
- `mrc_final_targets.json`

Keep separately (not in assay bulk):

- **§5** product specs → `mrc_final_targets.json`
- **§7** material balance → `mrc_material_balance.json`
- **§8** battery limits → `mrc_battery_limits.json`
