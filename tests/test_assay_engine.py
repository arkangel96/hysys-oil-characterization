"""Unit tests for assay_engine — no HYSYS required."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assay_engine import diagnose_case
from models import CaseSnapshot, StreamSummary


def test_no_snapshot_is_o0() -> None:
    d = diagnose_case(None)
    assert d.state == "O0"
    assert d.handoff_to_cdu is False


def test_no_streams_is_ox() -> None:
    snap = CaseSnapshot(case_title="t", streams=[], component_names=["C1"])
    d = diagnose_case(snap)
    assert d.state == "OX"


def test_many_components_is_o3() -> None:
    snap = CaseSnapshot(
        case_title="crude",
        component_names=[f"N{i}" for i in range(25)],
        streams=[StreamSummary(name="FEED")],
        oil_manager_hint="Oils: Count=1",
    )
    d = diagnose_case(snap)
    assert d.state == "O3"
    assert d.handoff_to_cdu is False


if __name__ == "__main__":
    test_no_snapshot_is_o0()
    test_no_streams_is_ox()
    test_many_components_is_o3()
    print("ok")
