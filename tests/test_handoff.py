"""Tests for O4 handoff token writer."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assay_engine import AssayDiagnosis, QAResult, finalize_o4
from handoff import build_handoff_payload, write_handoff_o4


def _o4_ready() -> AssayDiagnosis:
    d = AssayDiagnosis(
        state="O3",
        summary="strong",
        qa=QAResult("O3"),
        oil_installed=True,
        feed_attached=True,
        hypo_reviewed=True,
        assay_id="BASRAH",
        case_title="MRC_CDU",
        feed_stream="FEED",
        assay={
            "crude_id": "BASRAH",
            "source": {"tag": "TEST"},
            "bulk": {"api_gravity": 32.5},
        },
    )
    return finalize_o4(d)


class HandoffTests(unittest.TestCase):
    def test_build_payload_o4(self) -> None:
        d = _o4_ready()
        self.assertEqual(d.state, "O4")
        payload = build_handoff_payload(d, notes="ok")
        self.assertEqual(payload["state"], "O4")
        self.assertTrue(payload["handoff_to_cdu"])
        self.assertFalse(payload["cdu_assist"]["auto_launch"])
        self.assertEqual(payload["feed_stream"], "FEED")

    def test_write_handoff_file(self) -> None:
        d = _o4_ready()
        with tempfile.TemporaryDirectory() as td:
            out = write_handoff_o4(d, Path(td) / "handoff_o4.json")
            data = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual(data["state"], "O4")
            self.assertEqual(data["product"], "Oil Characterization Assist")

    def test_write_refuses_non_o4(self) -> None:
        d = AssayDiagnosis(state="OX", summary="blocked", hypo_reviewed=True)
        with self.assertRaises(ValueError):
            write_handoff_o4(d, "handoff_o4.json")

    def test_write_refuses_hsc(self) -> None:
        d = _o4_ready()
        with tempfile.TemporaryDirectory() as td:
            with self.assertRaises(ValueError):
                write_handoff_o4(d, Path(td) / "case.hsc")


if __name__ == "__main__":
    unittest.main()
