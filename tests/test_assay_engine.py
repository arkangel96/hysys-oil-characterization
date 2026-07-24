"""Unit tests for assay_engine — no HYSYS required."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assay_engine import (
    compare_boundary_tbp,
    completeness_check,
    diagnose_case,
    diagnose_mrc_pack,
    load_assay,
    normalize_light_ends,
)
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


def test_mrc_basrah_light_ends_pass() -> None:
    assay = load_assay("BASRAH")
    le = normalize_light_ends(assay)
    assert le.status == "PASS"
    assert 98 <= le.metrics["raw_sum"] <= 102


def test_mrc_assays_flag_tbp_coverage() -> None:
    for crude in ("BASRAH", "MISHRIF"):
        qa = completeness_check(load_assay(crude))
        assert qa.status == "OX"
        assert "TBP_COVERAGE_BELOW_O2" in qa.flags


def test_mrc_pack_loads() -> None:
    d = diagnose_mrc_pack()
    assert d.assay_id == "MRC_PACK"
    assert d.state == "OX"
    assert d.handoff_to_cdu is False


def test_boundary_tbp_compare() -> None:
    result = compare_boundary_tbp(load_assay("BASRAH"), load_assay("MISHRIF"))
    assert result.status == "PASS"
    assert result.metrics["common_points"] >= 5


if __name__ == "__main__":
    test_no_snapshot_is_o0()
    test_no_streams_is_ox()
    test_many_components_is_o3()
    test_mrc_basrah_light_ends_pass()
    test_mrc_assays_flag_tbp_coverage()
    test_mrc_pack_loads()
    test_boundary_tbp_compare()
    print("ok")
