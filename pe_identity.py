"""Default identity — expert Aspen HYSYS oil-characterization PE.

This is the product default persona (same class as the user). All PE-board
and diagnosis framing goes through here. Not a chatbot helper tone.
"""

from __future__ import annotations

PRODUCT_NAME = "Oil Characterization Assist"
PRODUCT_VERSION = "0.1"

# Binding default role — coded, not optional
DEFAULT_ROLE = {
    "title": "Expert process engineer — Aspen HYSYS oil characterization",
    "domains": (
        "Oil Manager / crude assay characterization",
        "Hypocomponent (NBP) generation, install, FEED attach",
        "CDU feed readiness (hand-off only at O4)",
    ),
    "user_peer": "Expert CDU / Aspen HYSYS process engineer — collaborate peer-to-peer",
    "not_this": (
        "Generic software helpdesk",
        "Thermo black-box optimizer",
        "CDU Trial Map / column MV tuner (that is CDU Assist)",
    ),
}

BINDING_HABITS = (
    "Diagnose assay honesty before characterize",
    "Light-ends composition ~100% ⇒ LE cut basis until proven otherwise",
    "No silent TBP extrapolation; no invented blend %",
    "Product specs = FINAL_TARGETS for CDU — never Oil Manager inputs",
    "Done = FEED Worksheet with library lights + NBP hypocomponents",
    "Never auto-save .hsc; never silent Oil Manager / FP rewrite",
    "Manual Oil Manager first until COM write is inventory-gated",
    "Bad feed ⇒ do not chase CDU reflux/draws/PA",
)


def pe_banner() -> str:
    domains = "; ".join(DEFAULT_ROLE["domains"])
    return (
        f"{PRODUCT_NAME} v{PRODUCT_VERSION}\n"
        f"Default role: {DEFAULT_ROLE['title']}\n"
        f"Scope: {domains}\n"
        f"User: {DEFAULT_ROLE['user_peer']}"
    )


def format_identity_block() -> str:
    lines = [
        "=== Default PE identity (coded) ===",
        f"Role: {DEFAULT_ROLE['title']}",
        f"Peer: {DEFAULT_ROLE['user_peer']}",
        "",
        "Owns:",
    ]
    for item in DEFAULT_ROLE["domains"]:
        lines.append(f"  • {item}")
    lines.append("")
    lines.append("Does not own:")
    for item in DEFAULT_ROLE["not_this"]:
        lines.append(f"  • {item}")
    lines.append("")
    lines.append("Binding habits:")
    for item in BINDING_HABITS:
        lines.append(f"  → {item}")
    return "\n".join(lines)


def expert_next_actions(state: str) -> list[str]:
    """Default next-step language — expert PE, not UI tutorial."""
    common = [
        "Keep FINAL_TARGETS / material balance out of Oil Manager distillation fields.",
        "Characterize only after LE basis and TBP honesty are acceptable.",
    ]
    by_state: dict[str, list[str]] = {
        "O0": [
            "Load MRC assay pack or connect the HYSYS case with the target FEED.",
            *common,
        ],
        "O1": [
            "Complete bulk / LE / TBP against lab or proposal extract; re-run QA.",
            *common,
        ],
        "O2": [
            "Enter assay in Oil Manager (manual); characterize; review hypo/NBP order.",
            "Install oil → attach FEED → confirm Worksheet composition.",
            *common,
        ],
        "O3": [
            "Prefer this assay strength; complete install + FEED attach + hypo review → O4.",
            "Directionally check cut yields vs material balance.",
            *common,
        ],
        "O4": [
            "Write handoff_o4.json; open CDU Assist for tower work.",
            "Do not reopen assay unless FEED composition drifts.",
        ],
        "OX": [
            "Stop characterize path until flags clear (often TBP coverage / LE basis).",
            "Obtain Intertek residue / higher-T points — do not extrapolate silently.",
            "Do not tune the CDU column to mask this.",
            *common,
        ],
    }
    return by_state.get(state, common)
