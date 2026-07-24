"""HYSYS UI automation helpers (V14) — when COM setters refuse the PP list.

Live learning (2026-07-25, Aspen HYSYS V14 Fluid Package: Basis-1 Set Up):

UI contract
-----------
- Package Type dropdown: ``HYSYS``
- Component List Selection: e.g. ``CompList1 [HYSYS Databanks]``
- Property Package Selection: scrollable list; must leave ``<none>``
- Visible name to click for crude work: ``Peng-Robinson``
- Success: red ``Select property package`` clears; COM then reports
  ``FluidPackage.PropertyPackageName == "Peng-Robinson"`` and Components > 0

COM gap
-------
``FluidPackage.PropertyPackageName = "Peng-Robinson"`` raises
"Value does not fall within the expected range" on this build even though
the UI string is exactly that. After a UI select, **read** of the same
property works.

Strategy
--------
Create FluidPackage + ComponentList via COM; select property package via
UI Automation click on the list item text ``Peng-Robinson``.
"""

from __future__ import annotations

import time
from dataclasses import dataclass


# Exact strings from V14 Fluid Package Set Up (user screenshot + live probe)
FP_UI = {
    "window_title_contains": "Aspen HYSYS",
    "package_type": "HYSYS",
    "property_package_selection_label": "Property Package Selection",
    "property_package_none": "<none>",
    "peng_robinson": "Peng-Robinson",
    "status_need_pp": "Select property package",
}


@dataclass
class UiSelectResult:
    ok: bool
    method: str = ""
    detail: str = ""
    property_package_name: str = ""
    component_count: int = 0


def select_peng_robinson_in_fluid_package_ui(
    *,
    verify_com_fp: object | None = None,
    settle_s: float = 1.0,
) -> UiSelectResult:
    """Click ``Peng-Robinson`` once in Fluid Package Set Up (V14).

    Preconditions (user or prior COM):
    - Fluid Package: Basis-1 Set Up visible
    - Package Type = HYSYS
    - Component List = CompList1
    - Property Package Selection list scrolled so ``Peng-Robinson`` is on screen

    Live proof (sample.hsc 2026-07-25): after one UIA click,
    ``PropertyPackageName == 'Peng-Robinson'`` and ``Components.Count == 8``.

    Do **not** loop clicks — aggressive UI loops have crashed HYSYS V14.
    """
    try:
        return _select_via_powershell_bridge(verify_com_fp=verify_com_fp, settle_s=settle_s)
    except Exception as exc:
        return UiSelectResult(ok=False, method="uia", detail=str(exc))


def _select_via_powershell_bridge(
    *,
    verify_com_fp: object | None,
    settle_s: float,
) -> UiSelectResult:
    import subprocess
    import textwrap

    target = FP_UI["peng_robinson"]
    script = textwrap.dedent(
        f"""
        Add-Type -AssemblyName UIAutomationClient
        Add-Type -AssemblyName UIAutomationTypes
        Add-Type @"
        using System;
        using System.Runtime.InteropServices;
        public class OcMouse {{
          [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
          [DllImport("user32.dll")] public static extern void mouse_event(int dwFlags, int dx, int dy, int cButtons, int dwExtraInfo);
          public static void Click(int x, int y) {{
            SetCursorPos(x,y);
            mouse_event(0x02,0,0,0,0);
            mouse_event(0x04,0,0,0,0);
          }}
        }}
        "@
        $root = [System.Windows.Automation.AutomationElement]::RootElement
        $hysys = $null
        foreach ($w in $root.FindAll([System.Windows.Automation.TreeScope]::Children, [System.Windows.Automation.Condition]::TrueCondition)) {{
          if ($w.Current.Name -match 'Aspen HYSYS') {{ $hysys = $w; break }}
        }}
        if (-not $hysys) {{ Write-Output 'ERR:no_hysys_window'; exit 2 }}
        $prCond = New-Object System.Windows.Automation.PropertyCondition(
          [System.Windows.Automation.AutomationElement]::NameProperty, '{target}')
        $pr = $hysys.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $prCond)
        if (-not $pr) {{ Write-Output 'ERR:peng_robinson_not_visible'; exit 3 }}
        $r = $pr.Current.BoundingRectangle
        if ($r.Width -le 0 -or $r.Height -le 0) {{ Write-Output 'ERR:no_bounds'; exit 4 }}
        $x = [int]($r.Left + $r.Width/2)
        $y = [int]($r.Top + $r.Height/2)
        [OcMouse]::Click($x, $y)
        Write-Output "OK:clicked:$x,$y"
        """
    )
    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", script],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    out = (completed.stdout or "").strip()
    if completed.returncode != 0 or not out.startswith("OK:"):
        return UiSelectResult(
            ok=False,
            method="uia_powershell",
            detail=out or (completed.stderr or f"exit {completed.returncode}"),
        )

    time.sleep(settle_s)
    name = ""
    ncomp = 0
    if verify_com_fp is not None:
        try:
            name = str(getattr(verify_com_fp, "PropertyPackageName", "") or "")
        except Exception:
            name = ""
        try:
            ncomp = int(verify_com_fp.Components.Count)
        except Exception:
            ncomp = 0

    ok = (name == FP_UI["peng_robinson"]) or (ncomp > 0)
    return UiSelectResult(
        ok=ok,
        method="uia_powershell",
        detail=out,
        property_package_name=name,
        component_count=ncomp,
    )


def learn_block() -> str:
    """PE-board / docs blurb from live V14 Fluid Package Set Up."""
    return "\n".join(
        [
            "--- Fluid Package UI (V14 learned) ---",
            f"Package Type: {FP_UI['package_type']}",
            "Component List Selection: CompList1 [HYSYS Databanks]",
            f"Property Package Selection: choose {FP_UI['peng_robinson']!r} (not {FP_UI['property_package_none']!r})",
            "COM PropertyPackageName setter rejected on V14; UI click then COM-read works.",
            f"Status bar before select: {FP_UI['status_need_pp']!r}",
        ]
    )
