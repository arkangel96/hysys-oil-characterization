# Discussion history — 2026-07-24 (continued)

**Product:** Oil Characterization Assist  
**Repo:** https://github.com/arkangel96/hysys-oil-characterization  
**Note:** User paused development after this session (“I will stop from here”).

---

## 1. Target HYSYS output (agreed)

Success looks like stream **Raw Crude** (or FEED) Worksheet → Composition:

- Library lights: Methane, Ethane, Propane, i-Butane, n-Butane, H2O (as in plant FP)
- Hypocomponents: `NBP[0]xx*` with calculated mole fractions (blue)
- Produced only after Oil Manager: **characterize → install → attach**

Assist QA / JSON / Aspen entry plan are the front half. **NBP slate is HYSYS output**, not invented in Python.

---

## 2. From-scratch characterization (discussion procedure)

Basrah first, new `.hsc`:

0. New steady-state case; save manually  
1. Fluid package (PR provisional) + library lights  
2. Oil Manager assay: TBP mass, bulk from `basrah_assay.json`, user-input LE (3.21 wt% + LE-cut composition normalized)  
3. Characterize; review hypos (expect soft heavy end — TBP coverage gap)  
4. Install → attach to **Raw Crude**  
5. Confirm Composition matches lights + NBP pattern  
6. Then Mishrif; blend only with named licensor %  

Open choices left undiscussed to closure: C1–C4 vs C1–C5 as discrete lights; one case vs two.

---

## 3. COM communication with Aspen (honest capability)

| Capability | Status at pause |
|------------|-----------------|
| Connect / open case / read streams / solve | **Yes** (`hysys_api.py`) |
| Probe Oil Manager paths / members | **Yes** (read-only) |
| Write assay / Characterize / Install / Attach | **No** — gated `allow_COM_write=false` |
| Auto-build `NBP[0]*` composition | **No** — requires Oil Manager actions |

COM is the right link. Full write path is possible using Aspen `xhysys` OilManager/Assay enums already coded in `aspen_intelligence.py`, but not implemented yet.

**Architecture options discussed:**  
1) Guide + COM-read verify  
2) Full gated COM write  
3) Hybrid  

User intent: eventually be **capable of all** of probe + write + NBP result.

---

## 4. Effort estimate (if resumed)

| Phase | Scope | Order of magnitude |
|-------|--------|-------------------|
| A | Harden Oil Manager / composition **read** | ~0.5–1 day |
| B | COM discovery: create assay, set TBP/LE/bulk | ~1–3 days (version risk) |
| C | Characterize → Install → Attach + rollback, no auto-save | ~2–4 days after B |
| D | Verify lights + NBP; O4 gate | ~1 day |
| E | Polish Basrah/Mishrif | ~1–2 days |

**Total if COM cooperates:** ~1–2 weeks focused. Phase B is the main unknown.

Resume recommendation: Phase A on live HYSYS, then throwaway case for B/C.

---

## 5. Already on main before this note (same day)

- MRC assay / MB / BL / FINAL_TARGETS JSON  
- PE identity default (`pe_identity.py`)  
- Complementary rules + package  
- Aspen-coded intelligence (`aspen_intelligence.py`)  
- PE board: Load MRC Pack / QA / Aspen entry plan  

---

## 6. Pause checklist

- Discussion captured here  
- Push to GitHub requested  
- Next session: start COM Phase A when ready  

*End of 2026-07-24 stop point.*
