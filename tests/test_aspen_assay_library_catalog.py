"""Aspen Assay Library catalog — unit tests (no live HYSYS)."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from aspen_assay_library_catalog import (
    ASSAY_LIBRARY_SELECT_COLUMNS,
    CATALOG_META,
    MISHRIFF_IN_LIBRARY,
    assay_library_count,
    find_library_assays,
    format_assay_library_catalog_block,
    load_assay_library_catalog,
)


class AspenAssayLibraryCatalogTests(unittest.TestCase):
    def test_columns_match_live_dump(self) -> None:
        self.assertIn("Assay", ASSAY_LIBRARY_SELECT_COLUMNS)
        self.assertIn("Density lb/ft3", ASSAY_LIBRARY_SELECT_COLUMNS)
        self.assertIn("TAN(mg KOH/g) mg KOH/g", ASSAY_LIBRARY_SELECT_COLUMNS)
        self.assertIn("Blank", ASSAY_LIBRARY_SELECT_COLUMNS)
        self.assertEqual(len(ASSAY_LIBRARY_SELECT_COLUMNS), 11)

    def test_full_catalog_loaded(self) -> None:
        n = assay_library_count()
        self.assertGreaterEqual(n, 900)
        self.assertTrue(CATALOG_META["full_catalog_mirrored"])
        self.assertEqual(CATALOG_META["assay_count"], n)
        # first / known rows present
        names = {r["Assay"] for r in load_assay_library_catalog()}
        self.assertIn("Champion Export-1983", names)
        self.assertIn("Saturno Blend-2013", names)
        self.assertIn("Azeri Light-2014", names)
        self.assertIn("Basrah Light-2014", names)

    def test_find_saturno_and_azeri(self) -> None:
        saturno = find_library_assays("Saturno")
        self.assertTrue(any("Saturno" in h["Assay"] for h in saturno))
        azeri = find_library_assays("Azeri Light")
        self.assertGreaterEqual(len(azeri), 3)
        self.assertTrue(any(h["Assay"] == "Azeri Light-2014" for h in azeri))

    def test_find_basrah(self) -> None:
        hits = find_library_assays("basrah light")
        self.assertTrue(any(h["Assay"] == "Basrah Light-2014" for h in hits))
        for h in hits:
            self.assertEqual(h["Country"], "Iraq")

    def test_mishrif_absent_and_not_mrc_path(self) -> None:
        self.assertFalse(MISHRIFF_IN_LIBRARY)
        self.assertFalse(CATALOG_META["use_for_mrc_cdu_feed"])
        self.assertEqual(find_library_assays("Mishrif"), [])

    def test_format_block(self) -> None:
        text = format_assay_library_catalog_block()
        self.assertIn("Basrah Light-2014", text)
        self.assertIn("Saturno", text)
        self.assertIn("Azeri Light", text)
        self.assertIn("Cancel", text)


if __name__ == "__main__":
    unittest.main()
