"""COM write gate — API must refuse when allow_COM_write is false."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from complementary_rules import DEFAULTS
from hysys_api import HysysController, HysysError


class ComWriteGateTests(unittest.TestCase):
    def test_allow_com_write_default_false(self) -> None:
        self.assertFalse(DEFAULTS["allow_COM_write"])

    def test_com_write_stubs_blocked(self) -> None:
        ctl = HysysController()
        ctl.connected = True
        ctl.flowsheet = MagicMock()
        ctl.case = MagicMock()
        with self.assertRaises(HysysError) as ctx:
            ctl.com_add_assay("Basrah")
        self.assertIn("allow_COM_write", str(ctx.exception))
        with self.assertRaises(HysysError):
            ctl.com_install_into_stream("Blend1", "FEED")
        with self.assertRaises(HysysError):
            ctl.com_set_associated_fluid_package("Basis-1")


if __name__ == "__main__":
    unittest.main()
