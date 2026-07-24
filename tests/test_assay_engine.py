"""Unit tests for assay_engine — no HYSYS required."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assay_engine import (
    check_blend_fraction,
    compare_boundary_tbp,
    completeness_check,
    diagnose_case,
    diagnose_mrc_pack,
    finalize_o4,
    load_assay,
    material_balance_yield_check,
    merge_diagnosis,
    normalize_light_ends,
)
from models import (
    CaseSnapshot,
    ComponentFraction,
    FeedAttachEvidence,
    OilManagerSnapshot,
    StreamComposition,
    StreamSummary,
)


def test_no_snapshot_is_o0() -> None:
    d = diagnose_case(None)
    assert d.state == "O0"
    assert d.handoff_to_cdu is False


def test_no_streams_is_ox() -> None:
    snap = CaseSnapshot(case_title="t", streams=[], component_names=["C1"])
    d = diagnose_case(snap)
    assert d.state == "OX"


def test_nbp_feed_is_o3() -> None:
    """Structured FEED lights+NBP evidence → O3 (not bare component count)."""
    snap = CaseSnapshot(
        case_title="crude",
        component_names=[f"NBP[{i}]" for i in range(10)] + ["Methane", "Propane"],
        streams=[StreamSummary(name="FEED")],
        oil_manager=OilManagerSnapshot(
            found=True,
            path="BasisManager.OilManager",
            assay_names=["Basrah"],
            oil_names=["BasrahOil"],
        ),
        feed_composition=StreamComposition(
            stream_name="FEED",
            basis="mass",
            components=[
                ComponentFraction("Methane", 0.01, "light"),
                ComponentFraction("Propane", 0.02, "light"),
                *[ComponentFraction(f"NBP[{i}]", 0.05, "nbp") for i in range(5)],
            ],
        ),
        feed_evidence=FeedAttachEvidence(
            feed_stream="FEED",
            oil_installed=True,
            feed_attached=True,
            nbp_count=5,
            light_count=2,
        ),
    )
    d = diagnose_case(snap)
    assert d.state == "O3"
    assert d.oil_installed is True
    assert d.feed_attached is True
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
    assert any("MB yield check" in e for e in d.evidence)


def test_boundary_tbp_compare() -> None:
    result = compare_boundary_tbp(load_assay("BASRAH"), load_assay("MISHRIF"))
    assert result.status == "PASS"
    assert result.metrics["common_points"] >= 5


def test_material_balance_yield_check() -> None:
    for crude in ("BASRAH", "MISHRIF"):
        qa = material_balance_yield_check(crude)
        assert qa.status == "PASS"
        assert abs(qa.metrics["wt_pct_sum"] - 100.0) < 0.5
        assert qa.metrics["oil_manager_input"] is False


def test_blend_fraction_null_on_boundary() -> None:
    assay = load_assay("BASRAH")
    qa = check_blend_fraction(assay)
    assert qa.status == "PASS"
    assert qa.metrics.get("blend_fraction") is None


def test_invented_blend_fraction_flagged() -> None:
    assay = load_assay("BASRAH")
    bad = dict(assay)
    bad["design"] = dict(assay.get("design") or {})
    bad["design"]["blend_fraction"] = 0.55
    qa = check_blend_fraction(bad)
    assert qa.status == "FAIL"
    assert "INVENTED_BLEND_FRACTION_ON_BOUNDARY" in qa.flags


def test_o4_requires_hypo_and_install() -> None:
    from assay_engine import AssayDiagnosis, QAResult

    d = AssayDiagnosis(
        state="O3",
        summary="strong",
        qa=QAResult("O3"),
        oil_installed=True,
        feed_attached=True,
        hypo_reviewed=False,
        assay_id="TEST",
    )
    d = finalize_o4(d)
    assert d.state == "O3"
    assert d.handoff_to_cdu is False

    d.hypo_reviewed = True
    d = finalize_o4(d)
    assert d.state == "O4"
    assert d.handoff_to_cdu is True


def test_merge_keeps_ox() -> None:
    from assay_engine import AssayDiagnosis

    assay_diag = AssayDiagnosis(state="OX", summary="blocked", assay_id="BASRAH")
    case_diag = AssayDiagnosis(
        state="O3",
        summary="live ok",
        oil_installed=True,
        feed_attached=True,
        hypo_reviewed=True,
    )
    merged = merge_diagnosis(assay_diag, case_diag, hypo_reviewed=True)
    assert merged.state == "OX"
    assert merged.handoff_to_cdu is False


if __name__ == "__main__":
    test_no_snapshot_is_o0()
    test_no_streams_is_ox()
    test_nbp_feed_is_o3()
    test_mrc_basrah_light_ends_pass()
    test_mrc_assays_flag_tbp_coverage()
    test_mrc_pack_loads()
    test_boundary_tbp_compare()
    test_material_balance_yield_check()
    test_blend_fraction_null_on_boundary()
    test_invented_blend_fraction_flagged()
    test_o4_requires_hypo_and_install()
    test_merge_keeps_ox()
    print("ok")
