"""O4 hand-off token writer for CDU Assist (file only — no import / no auto-launch)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from assay_engine import AssayDiagnosis, finalize_o4
from pe_identity import PRODUCT_NAME, PRODUCT_VERSION


def build_handoff_payload(
    diagnosis: AssayDiagnosis,
    *,
    accepted_by: str | None = None,
    notes: str = "",
) -> dict[str, Any]:
    """Minimal OC-05 contract + useful verify fields."""
    diagnosis = finalize_o4(diagnosis)
    assay = diagnosis.assay or {}
    source = assay.get("source") or {}
    bulk = assay.get("bulk") or {}
    tbp = (diagnosis.qa.metrics or {}).get("tbp") if diagnosis.qa else {}
    return {
        "product": PRODUCT_NAME,
        "product_version": PRODUCT_VERSION,
        "state": diagnosis.state,
        "case_title": diagnosis.case_title or "",
        "feed_stream": diagnosis.feed_stream or "FEED",
        "assay_tag": diagnosis.assay_id or "",
        "crude_id": assay.get("crude_id") or diagnosis.assay_id,
        "source_tag": source.get("tag"),
        "oil_installed": diagnosis.oil_installed,
        "feed_attached": diagnosis.feed_attached,
        "hypo_reviewed": diagnosis.hypo_reviewed,
        "bulk_summary": {
            "api_gravity": bulk.get("api_gravity"),
            "specific_gravity_15C": bulk.get("specific_gravity_15C"),
            "sulfur_wt_pct": bulk.get("sulfur_wt_pct"),
        },
        "tbp_summary": tbp or {},
        "flags": list(diagnosis.qa.flags) if diagnosis.qa else [],
        "notes": notes,
        "accepted_by": accepted_by,
        "accepted_at": datetime.now(timezone.utc).isoformat(),
        "handoff_to_cdu": diagnosis.handoff_to_cdu,
        "cdu_assist": {
            "auto_launch": False,
            "import_code": False,
            "instruction": "Open CDU Assist on the same HYSYS case; treat FEED as credible unless override.",
        },
    }


def write_handoff_o4(
    diagnosis: AssayDiagnosis,
    path: Path | str,
    *,
    accepted_by: str | None = None,
    notes: str = "",
) -> Path:
    """Write handoff_o4.json. Raises if O4 gate not passed."""
    diagnosis = finalize_o4(diagnosis)
    if not diagnosis.handoff_to_cdu or diagnosis.state != "O4":
        raise ValueError(
            f"Cannot write handoff — state={diagnosis.state}, "
            f"handoff_to_cdu={diagnosis.handoff_to_cdu}. "
            "Need O2/O3 assay + oil_installed + feed_attached + hypo_reviewed."
        )
    out = Path(path)
    if out.suffix.lower() == ".hsc":
        raise ValueError("Refusing to write handoff onto a .hsc case file.")
    payload = build_handoff_payload(diagnosis, accepted_by=accepted_by, notes=notes)
    out.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return out
