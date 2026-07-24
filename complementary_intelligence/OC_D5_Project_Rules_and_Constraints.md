# OC-D5 — Project Rules and Constraints

**Complementary hard rules** for Oil Characterization Assist.

## Engineering rules

- Physical / assay honesty overrides “make HYSYS green”  
- One crude characterization path at a time  
- Explain every recommendation  
- FINAL_TARGETs (products) never used as assay inputs  
- Material balance %wt = yield check, not Oil Manager distillation input  
- Boundary APIs outside design band stay bounds — no silent “fix” to 28–32  

## Safety / integrity rules

- Never auto-save `.hsc`  
- Never silent Oil Manager / FP rewrite  
- Never silent TBP extrapolation  
- Never invent licensor blend %  
- Never O4 without hypo review + FEED attach  

## Scope

**In scope**

- Crude assay QA and Oil Manager preparation  
- Hypocomponent / install / FEED readiness for atmospheric CDU  
- MRC Basrah / Mishrif (and named blends when specified)  
- Hand-off packet to CDU Assist  

**Out of scope (v1)**

- CDU column MV trials / Trial Map (CDU Assist)  
- VDU / simple column products  
- Dynamics  
- Plant-wide economics  

## Coding rules

- Inventory gate for new PE rules  
- Complementary docs do not override coded QA without reconciliation  
- Config / JSON-driven case data  
- Human-readable PE board and logs  

```yaml
constraints:
  domain: oil_characterization_cdu_feed
  never:
    - auto_save_hsc
    - silent_oil_manager_write
    - silent_tbp_extrapolation
    - invent_blend_percent
    - o4_without_hypo_review
  defaults:
    thermo_package: PR
    manual_oil_manager_first: true
    allow_COM_write: false
```
