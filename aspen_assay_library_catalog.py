"""Aspen Assay Library catalog (Add Assays → Select Assay, HYSYS V14).

Full live dump 2026-07-26 (~950 assays) after selecting
``Assay Components Celsius to 1150C`` → Add Assays.

Data file: ``config/aspen_assay_library_select_assay_v14.tsv``
(exact columns from HYSYS paste).

PE: commercial library ≠ Intertek masters. MRC Basrah/Mishrif FEED stays on
Oil Manager from ``MRC_GIVENS``. Mishrif is not present under that name.
"""

from __future__ import annotations

import csv
from functools import lru_cache
from pathlib import Path
from typing import Any

# Exact Select Assay table headers from live dump
ASSAY_LIBRARY_SELECT_COLUMNS: tuple[str, ...] = (
    "Assay",
    "Library Name",
    "Assay Date",
    "Region",
    "Country",
    "Density lb/ft3",
    "Sulfur %",
    "KinematicViscosity @ 100 F cSt",
    "TAN(mg KOH/g) mg KOH/g",
    "Pour Point F",
    "Blank",
)

ASSAY_LIBRARY_NAME = "Aspen Assay Library"

_CATALOG_TSV = (
    Path(__file__).resolve().parent / "config" / "aspen_assay_library_select_assay_v14.tsv"
)


def _parse_float(raw: str) -> float | None:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def _row_from_tsv(parts: list[str]) -> dict[str, Any]:
    # Pad / trim to column count
    while len(parts) < len(ASSAY_LIBRARY_SELECT_COLUMNS):
        parts.append("")
    parts = parts[: len(ASSAY_LIBRARY_SELECT_COLUMNS)]
    row = {
        "Assay": parts[0].strip(),
        "Library Name": parts[1].strip() or ASSAY_LIBRARY_NAME,
        "Assay Date": parts[2].strip(),
        "Region": parts[3].strip(),
        "Country": parts[4].strip(),
        "Density lb/ft3": _parse_float(parts[5]),
        "Sulfur %": _parse_float(parts[6]),
        "KinematicViscosity @ 100 F cSt": _parse_float(parts[7]),
        "TAN(mg KOH/g) mg KOH/g": _parse_float(parts[8]),
        "Pour Point F": _parse_float(parts[9]),
        "Blank": parts[10].strip() if len(parts) > 10 else "",
    }
    return row


@lru_cache(maxsize=1)
def load_assay_library_catalog() -> tuple[dict[str, Any], ...]:
    """Load full Aspen Assay Library Select Assay dump (~950 rows)."""
    if not _CATALOG_TSV.is_file():
        raise FileNotFoundError(f"Assay library TSV missing: {_CATALOG_TSV}")
    rows: list[dict[str, Any]] = []
    with _CATALOG_TSV.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f, delimiter="\t")
        header = next(reader, None)
        if not header or header[0].strip() != "Assay":
            raise ValueError(f"Unexpected assay library TSV header: {header!r}")
        for parts in reader:
            if not parts or not parts[0].strip():
                continue
            rows.append(_row_from_tsv(list(parts)))
    return tuple(rows)


def assay_library_count() -> int:
    return len(load_assay_library_catalog())


def assay_library_regions() -> tuple[str, ...]:
    regs = sorted({r["Region"] for r in load_assay_library_catalog() if r["Region"]})
    return tuple(regs)


def find_library_assays(
    name_substr: str = "",
    *,
    region: str | None = None,
    country: str | None = None,
) -> list[dict[str, Any]]:
    """Search the full catalog by assay-name substring / region / country."""
    needle = name_substr.strip().lower()
    reg = (region or "").strip().lower()
    ctry = (country or "").strip().lower()
    out: list[dict[str, Any]] = []
    for row in load_assay_library_catalog():
        if needle and needle not in str(row["Assay"]).lower():
            continue
        if reg and reg not in str(row["Region"]).lower():
            continue
        if ctry and ctry not in str(row["Country"]).lower():
            continue
        out.append(row)
    return out


def basrah_library_hits() -> list[dict[str, Any]]:
    return find_library_assays("Basrah")


def mishrif_in_library() -> bool:
    return bool(find_library_assays("Mishrif"))


# How to find Iraq / Basrah in the UI
ASSAY_LIBRARY_SEARCH_RECIPE: dict[str, Any] = {
    "for_basrah": {
        "Assay name": "Basrah",
        "Region": "Middle East",
        "Country": "Iraq",
        "Select library": "All",
    },
    "examples": {
        "Saturno": {"Assay name": "Saturno"},
        "Azeri Light": {"Assay name": "Azeri Light"},
        "Basrah": {"Assay name": "Basrah", "Country": "Iraq"},
    },
    "note": (
        "OK stays disabled until a row is selected. "
        "Any library pick imports Aspen's commercial model — "
        "not the MRC Intertek proposal TBP/LE/bulk."
    ),
}


def catalog_meta() -> dict[str, Any]:
    n = assay_library_count()
    return {
        "source": (
            "Live Add Assays dump after Assay Components Celsius to 1150C (2026-07-26)"
        ),
        "tsv": str(_CATALOG_TSV.name),
        "assay_count": n,
        "full_catalog_mirrored": True,
        "mishrif_present": mishrif_in_library(),
        "basrah_count": len(basrah_library_hits()),
        "use_for_mrc_cdu_feed": False,
        "mrc_action": (
            "Cancel Add Assays. Do not OK Basrah Light-2014 / Saturno / Azeri Light "
            "(or any library row) for MRC FEED. Oil Manager + MRC_GIVENS / Intertek."
        ),
    }


# Back-compat aliases used by earlier tests / PE board
BASRAH_LIBRARY_HITS: tuple[dict[str, Any], ...]  # filled lazily via __getattr__
MISHRIFF_IN_LIBRARY = False  # updated after first load in format block
CATALOG_META: dict[str, Any] = {}  # populated by refresh_compat()


def refresh_compat() -> None:
    """Refresh module-level aliases after TSV is available."""
    global BASRAH_LIBRARY_HITS, MISHRIFF_IN_LIBRARY, CATALOG_META
    BASRAH_LIBRARY_HITS = tuple(basrah_library_hits())
    MISHRIFF_IN_LIBRARY = mishrif_in_library()
    CATALOG_META = catalog_meta()


# Eager load so imports have counts without callers remembering refresh
try:
    refresh_compat()
except FileNotFoundError:
    BASRAH_LIBRARY_HITS = ()
    MISHRIFF_IN_LIBRARY = False
    CATALOG_META = {
        "full_catalog_mirrored": False,
        "use_for_mrc_cdu_feed": False,
        "assay_count": 0,
        "mrc_action": "Catalog TSV missing.",
    }


def format_assay_library_catalog_block() -> str:
    meta = catalog_meta()
    basrah = basrah_library_hits()
    saturno = find_library_assays("Saturno")
    azeri = find_library_assays("Azeri Light")
    lines = [
        "--- Aspen Assay Library (Add Assays Select Assay) ---",
        "Columns: " + " | ".join(ASSAY_LIBRARY_SELECT_COLUMNS),
        f"Library: {ASSAY_LIBRARY_NAME}",
        f"Assays coded (full dump): {meta['assay_count']}",
        f"Regions: {', '.join(assay_library_regions())}",
        f"Basrah hits: {len(basrah)} — "
        + ", ".join(r["Assay"] for r in basrah[:8])
        + ("…" if len(basrah) > 8 else ""),
        f"Saturno hits: {len(saturno)} — "
        + ", ".join(r["Assay"] for r in saturno),
        f"Azeri Light hits: {len(azeri)} — "
        + ", ".join(r["Assay"] for r in azeri[:6])
        + ("…" if len(azeri) > 6 else ""),
        f"Mishrif in library: {meta['mishrif_present']}",
        f"Full catalog mirrored: {meta['full_catalog_mirrored']}",
        meta["mrc_action"],
    ]
    return "\n".join(lines)
