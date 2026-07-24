# OC-05 — Hand-off to CDU Assist

**Status:** CODED  
**Inventory:** OC-05  
**Code:** `handoff.py` → GUI **Export handoff_o4.json**

When complementary O4 gate passes (assay O2/O3 **and** oil_installed **and** feed_attached **and** hypo_reviewed):

1. Assist writes `handoff_o4.json` (never onto a `.hsc`)
2. User opens **CDU Assist** on the **same** HYSYS case
3. CDU Assist treats feed as credible unless user overrides

## Payload (minimal + verify fields)

```json
{
  "product": "Oil Characterization Assist",
  "state": "O4",
  "case_title": "",
  "feed_stream": "",
  "assay_tag": "",
  "oil_installed": true,
  "feed_attached": true,
  "hypo_reviewed": true,
  "notes": "",
  "cdu_assist": {
    "auto_launch": false,
    "import_code": false
  }
}
```

Richer optional fields (bulk/tbp summaries, flags) are included by `build_handoff_payload`.

## Rules

- Do **not** auto-launch CDU Assist
- Do **not** import sibling CDU code
- Do **not** overwrite `.hsc`
- Current MRC proposal TBP → **OX** cannot fake O4 until residue coverage or a stronger assay

CDU Assist receive-side gate remains a future thin check in the sibling repo.
