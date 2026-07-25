"""Fill-plan unit tests — no live HYSYS."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from oil_characterize_fill import (
    ASSAY_SURFACE,
    build_basrah_fill_plan,
    format_fill_plan,
    preflight_oil_manager_fp,
)


class CharacterizeFillTests(unittest.TestCase):
    def test_oil_manager_not_library_for_feed(self) -> None:
        self.assertTrue(ASSAY_SURFACE["oil_manager"]["use_for_cdu_feed"])
        self.assertFalse(ASSAY_SURFACE["petroleum_assays_library"]["use_for_cdu_feed"])

    def test_basrah_plan_has_oil_change_and_bulk_used(self) -> None:
        plan = build_basrah_fill_plan()
        joined = " | ".join(plan.steps)
        self.assertIn("StartOilChange", joined)
        self.assertIn("BulkPropertiesUsed=True", joined)
        self.assertIn("BoilingTemperatureValue (°C)", joined)
        self.assertIn("NBP*", joined)
        self.assertIn("PREFLIGHT", joined)
        self.assertEqual(plan.stream_name, "Raw Crude")

    def test_preflight_rejects_1150c_slate(self) -> None:
        blockers = preflight_oil_manager_fp(
            ["Methane", "Ethane", "36-40C*", "40-50C*", "1150+C*"]
            + [f"{i}-{i+10}C*" for i in range(50, 200, 10)]
        )
        self.assertTrue(blockers)
        self.assertTrue(any("1150" in b or "cut hypo" in b or "Petroleum" in b for b in blockers))

    def test_preflight_rejects_missing_lights(self) -> None:
        blockers = preflight_oil_manager_fp(["Methane", "Ethane", "H2O"])
        self.assertTrue(any("Missing" in b for b in blockers))

    def test_preflight_ok_complist1(self) -> None:
        lights = [
            "Methane",
            "Ethane",
            "Propane",
            "i-Butane",
            "n-Butane",
            "i-Pentane",
            "n-Pentane",
            "H2O",
        ]
        self.assertEqual(preflight_oil_manager_fp(lights), [])

    def test_format_mentions_library_boundary(self) -> None:
        text = format_fill_plan()
        self.assertIn("Assay Library", text)
        self.assertIn("StartOilChange", text)
        self.assertIn("1150C", text)


if __name__ == "__main__":
    unittest.main()
