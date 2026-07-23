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

- Connect to a running HYSYS case
- List material streams + fluid-package components
- Show an **Assay PE board** (intelligence states — grow in docs + code)
- Never auto-saves the HYSYS case

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
