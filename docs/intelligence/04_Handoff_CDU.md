# OC-05 — Hand-off to CDU Assist

**Status:** PLANNED  
**Inventory:** OC-05

When state reaches **O4**:

1. Record assay tag / oil name / hypo count / feed stream name
2. User opens **CDU Assist** on the same case
3. CDU Assist treats feed as credible unless user overrides

Optional later: write a small `handoff_o4.json` next to the case (never overwrite `.hsc`).

```json
{
  "product": "Oil Characterization Assist",
  "state": "O4",
  "case_title": "",
  "feed_stream": "",
  "assay_tag": "",
  "notes": ""
}
```

Do not auto-launch CDU Assist until both products are stable.
