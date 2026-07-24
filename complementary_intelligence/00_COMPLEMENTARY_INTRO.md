# Complementary Intelligence — Oil Characterization Assist

## Purpose

This folder holds a **complementary** engineering intelligence package for
Aspen HYSYS **crude oil characterization / Oil Manager** work that feeds
**CDU / atmospheric** simulation.

It **helps and strengthens** — it does **not** replace:

| Source | Role |
|--------|------|
| `oil_characterization_intelligence_pack_v1/` | Core PE pack (states, LE, TBP, O4) |
| `docs/INTELLIGENCE_INVENTORY.md` + coded `assay_engine.py` | **Active judgment today** |
| `docs/intelligence/00_PE_Mindset.md` | Binding “how we think” |
| `docs/intelligence/cases/` | MRC Basrah/Mishrif data |
| **This package** | Complementary OS — reasoning, knowledge, HYSYS interaction, learning, rules |

## Non-negotiable relationship rules

- Do **not** treat this package as superseding the v1 pack or Inventory.
- Do **not** declare older rules inactive.
- Do **not** run two rival brains (pack vs complementary vs code).
- When texts differ: **reconcile in discussion**; until then prefer the
  **more specific validated rule** (LE basis, no silent TBP extrapolation,
  no invented blend %, no auto-save, manual Oil Manager first).
- New ideas become active only after an **Inventory row** + thin code hook
  (if executable).

## Priority order (guidance)

1. Inventory + coded Assist rules  
2. Intelligence pack v1 (`oil_characterization_intelligence.md`)  
3. This complementary framework  
4. Project case notes (MRC)  
5. General PE knowledge  

## Engineering identity

Think like an **expert Aspen HYSYS PE** for oil characterization **and** CDU
feed readiness (same class as the user):

- Observe / QA before characterize  
- Honest TBP and light-ends basis  
- Deliverable = FEED with library lights + hypocomponents (NBP*), not a green checklist alone  
- Hand off to CDU Assist only at **O4**  
- Never chase tower MVs to hide a bad assay  

## Package contents

| File | Role |
|------|------|
| [`00_COMPLEMENTARY_INTRO.md`](00_COMPLEMENTARY_INTRO.md) | This file — relationship rules |
| [`OC_D1_Engineering_Reasoning.md`](OC_D1_Engineering_Reasoning.md) | How to reason (assay → FEED) |
| [`OC_D2_Knowledge_Base.md`](OC_D2_Knowledge_Base.md) | Domain knowledge map |
| [`OC_D3_HYSYS_Oil_Manager_Interaction.md`](OC_D3_HYSYS_Oil_Manager_Interaction.md) | What to read/write (and not) |
| [`OC_D4_Learning_and_Memory.md`](OC_D4_Learning_and_Memory.md) | What to remember across cases |
| [`OC_D5_Project_Rules_and_Constraints.md`](OC_D5_Project_Rules_and_Constraints.md) | Hard constraints |
| [`OC_D6_Workspace_Specification.md`](OC_D6_Workspace_Specification.md) | Where files live vs CDU Assist |
