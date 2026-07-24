# Oil Characterization Assist v0.1

External desktop assist for **crude assay / Oil Manager** work in Aspen HYSYS
(Windows COM). Not an AspenTech product.

| | |
|---|---|
| **Product** | Oil Characterization Assist |
| **Version** | **0.1** (scaffold) |
| **Scope** | Assay completeness, characterization QA, blend / hypo checks, feed attach |
| **Sibling** | CDU Assist (`../oil_charateization/`) — tower only; do not merge |

## What it does (now)

- Connect to a running HYSYS case (READ-first)
- Structured Oil Manager inventory + FEED composition (lights / `NBP*`)
- MRC Basrah/Mishrif pack QA + material-balance yield check
- Gated COM write stubs (`allow_COM_write=false` — manual Oil Manager first)
- Export `handoff_o4.json` when O4 gate passes
- Never auto-saves the HYSYS case

**Edit the repo root only** (`main.py`, `gui.py`, …). Nested `oil_characterization/` is a duplicate.

## What it will do (intelligence track)

See [`docs/INTELLIGENCE_INVENTORY.md`](docs/INTELLIGENCE_INVENTORY.md) and
[`docs/intelligence/`](docs/intelligence/).

## Requirements

- Windows 10/11
- Aspen HYSYS installed and licensed
- 64-bit Python 3.11 or 3.12 matching HYSYS architecture

## Install

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Open a HYSYS case first, then:

```powershell
python main.py
```

Or double-click `Open Oil Characterization Assist.bat`.

## Boundary with CDU Assist

- This app: **feed / assay / Oil Manager**
- CDU Assist: **column MVs / converge / Trial Map**
- Hand-off rule: tower trials only after assay is **accepted** (feed OK)

## Discussion / intelligence

- Session notes: [`docs/DISCUSSION_HISTORY_2026-07-23.md`](docs/DISCUSSION_HISTORY_2026-07-23.md)
- Session notes (COM / from-scratch / pause): [`docs/DISCUSSION_HISTORY_2026-07-24.md`](docs/DISCUSSION_HISTORY_2026-07-24.md)
- User intelligence pack: [`docs/intelligence/user_drop/`](docs/intelligence/user_drop/)
- Inventory: [`docs/INTELLIGENCE_INVENTORY.md`](docs/INTELLIGENCE_INVENTORY.md)
