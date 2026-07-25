"""Petroleum Assays UI map — unit tests (no live HYSYS)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from petroleum_assays_ui import (
    ADD_ASSAYS_DIALOG_V14,
    ASSAY_COMPONENT_SELECTION_DIALOG_V14,
    PETROLEUM_ASSAYS_ADD_WORKFLOW_V14,
    PETROLEUM_ASSAYS_UI_V14,
    format_petroleum_assays_ui_block,
    mrc_bulk_to_summary_display,
)


class PetroleumAssaysUiTests(unittest.TestCase):
    def test_not_for_mrc_feed(self) -> None:
        self.assertFalse(PETROLEUM_ASSAYS_UI_V14["use_for_mrc_cdu_feed"])
        self.assertFalse(ADD_ASSAYS_DIALOG_V14["use_for_mrc_cdu_feed"])

    def test_summary_columns_include_watson_k(self) -> None:
        cols = PETROLEUM_ASSAYS_UI_V14["table_columns"]
        self.assertIn("Watson K", cols)
        self.assertIn("Density [lb/ft3]", cols)
        self.assertIn("Assay", cols)

    def test_mrc_sg_to_density_display(self) -> None:
        mapped = mrc_bulk_to_summary_display(
            {"specific_gravity_15C": 0.863, "sulfur_wt_pct": 2.2, "kuop": 11.98}
        )
        self.assertAlmostEqual(mapped["Density [lb/ft3]"], 0.863 * 62.428, places=3)
        self.assertEqual(mapped["Sulfur %"], 2.2)
        self.assertEqual(mapped["Watson K"], 11.98)
        self.assertIsNone(mapped["Viscosity @ 100 F [cSt]"])

    def test_component_selection_blocks_complist1(self) -> None:
        dlg = ASSAY_COMPONENT_SELECTION_DIALOG_V14
        self.assertFalse(dlg["use_for_mrc_cdu_feed"])
        self.assertIn("assay compatible component list", dlg["prompt"])
        self.assertIn("CompList1", dlg["why_it_blocks_us"])
        self.assertIn("Cancel", dlg["mrc_action"])
        opts = dlg["dropdown_options_known"]
        self.assertEqual(len(opts), 10)
        self.assertIn("Assay Components Celsius to 1150C", opts)
        self.assertIn("FCC Components Celsius", opts)
        self.assertIn("Hydrocracker Components Fahrenheit", opts)
        self.assertIn("Reformer Components Celsius", opts)
        self.assertEqual(dlg["preferred_if_forced"], "Assay Components Celsius to 1150C")
        self.assertIn("Live HYSYS V14", dlg["dropdown_options_source"])
        self.assertEqual(dlg["next_dialog_after_ok"], "Add Assays")

    def test_add_workflow_1150c_unlocks_library(self) -> None:
        wf = PETROLEUM_ASSAYS_ADD_WORKFLOW_V14
        self.assertFalse(wf["use_for_mrc_cdu_feed"])
        self.assertIn("Add Assays", " → ".join(wf["steps"]))
        self.assertIn("prerequisite gate", wf["why_1150c_unlocked_library"])
        self.assertIn("Not Basrah", wf["what_1150c_is_not"])
        self.assertTrue(ADD_ASSAYS_DIALOG_V14["ok_disabled_until_selection"])
        self.assertIn("Cancel", ADD_ASSAYS_DIALOG_V14["mrc_action"])

    def test_format_mentions_oil_manager(self) -> None:
        text = format_petroleum_assays_ui_block()
        self.assertIn("Oil Manager", text)
        self.assertIn("Assays Summary", text)
        self.assertIn("Assay Component Selection", text)
        self.assertIn("Add Assays", text)
        self.assertIn("1150C", text)


if __name__ == "__main__":
    unittest.main()
