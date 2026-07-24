"""Tests for complementary_rules — no HYSYS required."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assay_engine import diagnose_mrc_pack, format_pe_board
from complementary_rules import DEFAULTS, apply_complementary_gate


def test_o4_blocked_without_install() -> None:
    gate = apply_complementary_gate(qa_status="O3", flags=[], hypo_reviewed=True)
    assert gate.o4_blocked is True
    assert any("installed oil" in r for r in gate.reasons)


def test_o4_allowed_when_complete() -> None:
    gate = apply_complementary_gate(
        qa_status="O3",
        flags=[],
        hypo_reviewed=True,
        oil_installed=True,
        feed_attached=True,
    )
    assert gate.o4_blocked is False


def test_no_silent_tbp_extrapolation_default() -> None:
    assert DEFAULTS["allow_silent_tbp_extrapolation"] is False
    gate = apply_complementary_gate(
        qa_status="OX",
        flags=["TBP_COVERAGE_BELOW_O2"],
    )
    assert any("tbp_extrapolation" in r for r in gate.reasons)


def test_pe_board_includes_complementary() -> None:
    text = format_pe_board(diagnose_mrc_pack())
    assert "Complementary rules (OC-COMP)" in text
    assert "silent_tbp_extrapolation" in text
    assert "O4 allowed: NO" in text


if __name__ == "__main__":
    test_o4_blocked_without_install()
    test_o4_allowed_when_complete()
    test_no_silent_tbp_extrapolation_default()
    test_pe_board_includes_complementary()
    print("ok")
