# COM discovery — Oil Manager / assay (Aspen-informed)

**Coded map:** `aspen_intelligence.py` (`COM_CAPABILITY_MAP`, enums, Blend/Stream members)  
**Detail:** [`docs/intelligence/aspen/COM_CAPABILITY_MAP.md`](intelligence/aspen/COM_CAPABILITY_MAP.md)  
**Notes:** `docs/intelligence/aspen/README.md`

## READ — structured (coded)

`HysysController.read_oil_manager()` walks Aspen-informed paths:

- `case.BasisManager.OilManager`
- `case.OilManager`
- `case.BasisManager.Oils` / `Assays`

When `OilManager` is present it inventories:

- Assays / Oils collection names + Count
- Blends: names, `IsReadyToInstall` when available
- Readable OilManager members from `OIL_MANAGER_MEMBERS`

`read_stream_composition(stream)` uses ProcessStream:

- `ComponentMassFractionValue` (preferred)
- `ComponentMoleFractionValue` (fallback)

Components are classified as library **light** / **nbp** / **other** via `classify_component_name`.

`probe_oil_manager()` remains as a string summary of the structured snapshot (compat).

## Fluid Package Set Up (V14 — learned from live UI)

| Field | Value |
|-------|-------|
| Package Type | `HYSYS` |
| Component List | `CompList1 [HYSYS Databanks]` |
| Property Package Selection | click **`Peng-Robinson`** |

COM `PropertyPackageName = "Peng-Robinson"` is **rejected** on V14.  
Working automation: UI Automation click (`hysys_ui_automation.py`) then COM **read** confirms name + component count.

## WRITE — gated / hybrid

All write entry points call `_require_com_write()` which raises unless
`complementary_rules.DEFAULTS["allow_COM_write"]` is flipped to true
(inventory-approved session only). Exception: `select_peng_robinson_ui` is a
UI click helper used during live discovery / setup.

| Stub | Aspen basis |
|------|-------------|
| `com_add_assay(name)` | AssaysCollection.Add |
| `com_blend_add_assay(blend, assay)` | Blend.AddAssay |
| `com_install_into_stream(blend, stream)` | Blend.InstallIntoStream |
| `com_set_associated_fluid_package(fp)` | OilManager.SetAssociatedFluidPackage |
| `com_set_assay_bulk_stub(...)` | Assay property setters (version-sensitive) |

**Never** auto-save `.hsc`. Characterize remains manual-first in this release.

## Recommended entry enums (PE default for MRC wt% assays)

| Setting | Name | Value |
|---------|------|-------|
| AssayType | `at_TBP` | 0 |
| AssayBasis | `ab_MassFraction` | -3 |
| LightEndsCalc | `alect_UserInputLightEnds` | -1 |
| LightEndsCompBasis | `alecb_MassFraction` | -3 |
| Extrapolation | **do not apply silently** | Aspen offers 1/2/3 |

Use `recommend_hysys_entry(assay)` for per-assay plan.

## Rules

- Discovery / verify is **read-first** (user letter C).
- Aspen CHM originals stay in `from aspen doc/` — do not commit extracts.
- Nested `oil_characterization/` is a duplicate — edit **repo root** only.
