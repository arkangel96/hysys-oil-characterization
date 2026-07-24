"""Tests for Aspen-coded intelligence."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aspen_intelligence import (
    ASSAY_TYPE,
    COM_CAPABILITY_MAP,
    classify_component_name,
    format_aspen_block,
    recommend_hysys_entry,
)
from assay_engine import diagnose_mrc_pack, format_pe_board, load_assay


def test_basrah_entry_plan_is_tbp_mass() -> None:
    plan = recommend_hysys_entry(load_assay("BASRAH"))
    assert plan.assay_type_name == "at_TBP"
    assert plan.assay_type_value == ASSAY_TYPE["at_TBP"]
    assert plan.assay_basis_name == "ab_MassFraction"
    assert plan.light_ends_calc_name == "alect_UserInputLightEnds"
    assert plan.allow_extrapolation is False


def test_pe_board_includes_aspen_block() -> None:
    text = format_pe_board(diagnose_mrc_pack())
    assert "Aspen intelligence (coded)" in text
    assert "at_TBP" in text
    assert "OilManager" in text or "micro-cuts" in text
    assert "COM capability map" in text


def test_format_aspen_without_assay() -> None:
    text = format_aspen_block(None)
    assert "Characterize methodology" in text


def test_classify_nbp_and_lights() -> None:
    assert classify_component_name("NBP[0]100*") == "nbp"
    assert classify_component_name("Methane") == "light"
    assert classify_component_name("n-Butane") == "light"
    assert classify_component_name("Water") == "light"


def test_com_capability_map_has_gated_writes() -> None:
    writes = [r for r in COM_CAPABILITY_MAP if r["access"] == "write"]
    assert writes
    assert any(r["status"] == "gated_stub" for r in writes)
    assert any(r["capability"] == "auto_save_hsc" and r["status"] == "forbidden" for r in writes)


if __name__ == "__main__":
    test_basrah_entry_plan_is_tbp_mass()
    test_pe_board_includes_aspen_block()
    test_format_aspen_without_assay()
    test_classify_nbp_and_lights()
    test_com_capability_map_has_gated_writes()
    print("ok")
