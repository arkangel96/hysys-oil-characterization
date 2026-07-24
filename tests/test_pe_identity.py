"""Tests for default PE identity."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from assay_engine import diagnose_case, format_pe_board
from pe_identity import BINDING_HABITS, DEFAULT_ROLE, pe_banner


def test_default_role_is_expert_oil_char() -> None:
    assert "oil characterization" in DEFAULT_ROLE["title"].lower()
    assert "Aspen HYSYS" in DEFAULT_ROLE["title"]


def test_pe_board_shows_identity_by_default() -> None:
    text = format_pe_board(diagnose_case(None))
    assert "Default role:" in text or "Default PE identity" in text
    assert "expert" in text.lower()
    assert "Oil Manager" in text or "oil characterization" in text.lower()
    assert any(h.split()[0] in text or h[:20] in text for h in BINDING_HABITS[:1]) or "Binding habits" in text


def test_banner() -> None:
    b = pe_banner()
    assert "Oil Characterization Assist" in b
    assert "expert" in b.lower()


if __name__ == "__main__":
    test_default_role_is_expert_oil_char()
    test_pe_board_shows_identity_by_default()
    test_banner()
    print("ok")
