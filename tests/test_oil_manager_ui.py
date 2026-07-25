"""Oil Manager UI seed helpers — unit only (no live HYSYS)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from oil_manager_ui import (
    ASSAY_FORM_UI_V14,
    BASRAH_OIL_MANAGER_SEED,
    celsius_to_fahrenheit,
    format_oil_manager_ui_block,
)


class OilManagerUiTests(unittest.TestCase):
    def test_celsius_to_fahrenheit_basrah_ends(self) -> None:
        temps = celsius_to_fahrenheit(BASRAH_OIL_MANAGER_SEED["tbp_temperature_C"])
        self.assertAlmostEqual(temps[0], 104.0)
        self.assertAlmostEqual(temps[-1], 932.0)
        self.assertEqual(len(temps), len(BASRAH_OIL_MANAGER_SEED["tbp_cumulative_wt_pct"]))

    def test_form_map_com_gate(self) -> None:
        self.assertTrue(ASSAY_FORM_UI_V14["com_write_requires_form_open"])
        self.assertEqual(ASSAY_FORM_UI_V14["com_boiling_t_unit"], "C")
        self.assertEqual(
            ASSAY_FORM_UI_V14["assay_definition_defaults"]["Bulk Properties"], "Used"
        )

    def test_format_block_mentions_live_path(self) -> None:
        text = format_oil_manager_ui_block()
        self.assertIn("enter_tbp_assay_seed_live", text)
        self.assertIn("form open", text.lower())


if __name__ == "__main__":
    unittest.main()
