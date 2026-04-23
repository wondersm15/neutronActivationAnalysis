# Neutron Activation Analysis — Codebase Guide

This file is the entry point for agents or contributors coming into this codebase
cold. Read it before touching any files. For data pipeline setup, see `tools/README.md`.
For a user-facing overview, see `README.md`.

---

## Architecture Overview

A local Flask web application. The entire UI is a single HTML page
(`templates/index.html`) with inline JavaScript that talks to a Flask backend
over a small REST API. There is no build step, no bundler, no database.

```
Browser (index.html)
    │
    │  REST API (JSON)
    ▼
app.py  ──→  data.py      Nuclear reaction + material database
        ──→  physics.py   Activation physics, dose-rate computation
        ──→  data/         Extracted cross-section JSON files
```

Run with `python app.py` and open `http://localhost:5050`.

---

## Module Responsibilities

### `app.py`
Flask application. Defines all API endpoints. Does not contain physics or data
logic — it delegates to `data.py` and `physics.py` and returns JSON.

| Endpoint | Method | Purpose |
|---|---|---|
| `GET /` | — | Serves `templates/index.html` |
| `GET /api/materials` | — | Returns all material names grouped by category |
| `GET /api/material/<name>` | — | Returns full material info: composition, activation table, xsec reactions |
| `GET /api/isotope/<isotope>` | — | Returns reactions for a single isotope |
| `POST /api/compute` | JSON body | Computes activity + dose rate vs. time for one or more materials |
| `GET /api/xsec/<isotope>` | `?reaction=&library=` | Returns pointwise σ(E) data from downloaded JSON files |
| `GET /api/literature` | — | Returns markdown files from `NotesFromOtherSources/` |
| `GET /api/references` | — | Returns `references.json` |

### `data.py`
The nuclear data layer. Contains two large dicts and several helpers.

**`REACTIONS`** — the core database. Maps isotope string (e.g. `"Fe-56"`) to a
list of reaction dicts. Each reaction dict has:
- `reaction`: string, e.g. `"(n,γ)"`
- `product`: string, e.g. `"Fe-57"`
- `cross_sections`: `{"endf8": {"sigma_th": ..., "sigma_2p5": ..., "sigma_14": ...}, "fendl32c": {...}}`
- `t_half`, `t_half_s`, `decay_mode`, `gammas`, `threshold`, `notes`, (optionally) `waste_class`

**Important**: the hardcoded `cross_sections` values in `REACTIONS` are
documentation fallbacks. At module startup, `_load_extracted_3pt()` reads
`data/endf_3pt.json` and `data/fendl_3pt.json` and overwrites them in-memory.
Do not edit the hardcoded values expecting them to take effect at runtime.

**`MATERIALS`** — maps material name (e.g. `"Stainless Steel 316 (nuclear-grade impurities)"`)
to a dict with `description`, `density_g_cc`, `category`, `isotopes` (atom fractions),
and optionally `impurities`. Materials are named with an explicit impurity tag: `(baseline)`
indicates the pure-composition idealization with no trace impurities modeled; `(with impurities)`,
`(commercial-grade impurities)`, `(nuclear-grade impurities)`, `(ITER-grade impurities)`, or
`(industrial impurities)` indicate variants that include trace activation drivers (Co, Eu, Nb,
Cs, Sc, etc.) at representative levels. Several materials have both a `(baseline)` and a
`(... impurities)` variant — they are deliberate pairs for bracketing activation predictions,
not duplicates to be deduplicated.

**`_load_extracted_3pt()`** — runs once at import time. Merges the extracted JSON
files into `REACTIONS`. Safe to re-run (idempotent).

**`get_material_activation(material_name, library="endf8")`** — the main query
function. Returns a list of activation row dicts, one per (isotope, reaction) pair
in the material. Each row includes `sigma_th`, `sigma_2p5`, `sigma_14`,
`sigma_f_th`, `sigma_f_2p5`, `sigma_f_14` (σ × atom_frac), `delta_14_pct`
(FENDL vs ENDF signed % at 14.1 MeV), and full decay metadata.

### `physics.py`
Activation physics and dose-rate computation.

**`compute_activation(material_name, fluence_th, fluence_14, ...)`** — the main
compute entry point. Steps:
1. Computes N_activated = σ · Φ · (ρ·f / m_atom) for each reaction
2. Merges products with the same nuclide (different reaction paths → same isotope)
3. Builds a log-spaced time array from 10 s to 10× the longest half-life
4. For each time point: A(t) = λ · N₀ · exp(−λt) and DR = A · dose_coeff
5. Returns `{time_s, products, total_activity_Bq_per_g, total_dose_rate_uSv_per_h, ...}`

Dose conversion uses ICRP-74 H*(10)/Φ coefficients (log-log interpolated),
assuming isotropic point source at `distance_cm`.

---

## Frontend Architecture (`templates/index.html`)

A ~2300-line single-file SPA. Uses Chart.js (gamma spectrum), Plotly (activity /
dose-rate / cross-section plots), and noUiSlider (half-life range filter, gamma
cooling time). No frameworks.

### Global State Variables

| Variable | Type | Meaning |
|---|---|---|
| `currentMaterial` | string\|null | Name of the selected material |
| `currentData` | object\|null | Response from `/api/material/<name>` |
| `currentCompute` | object\|null | Response from `/api/compute` for the current material |
| `currentTab` | string | Active tab: `'activation'`, `'activity'`, `'gamma'`, `'comparison'`, `'composition'`, `'xsec'`, `'literature'` |
| `disabledReactions` | Set\<string\> | Reaction keys (`"target\|reaction\|product"`) currently unchecked in the activation table |
| `hlLogLow`, `hlLogHigh` | number | Half-life filter range in log₁₀(seconds) |
| `gammaNormMode` | `'decay'`\|`'fluence'` | Gamma spectrum normalization mode |
| `gammaCoolLogT` | number | Cooling time for gamma fluence mode, log₁₀(seconds) |
| `gammaComputeCache` | object\|null | Cached `/api/compute` result for fluence-mode gamma; invalidated on material or fluence change |
| `xsecActiveTraces` | Set\<string\> | `"isotope\|\|reaction"` keys with visible σ(E) traces |
| `xsecLibraryMode` | string | `'endf8'`, `'fendl32c'`, or `'both'` |

### Data Flow: Material Selection → Tab Render

```
User clicks material button
    → selectMaterial(name)
        → GET /api/material/<name>
        → currentData = response
        → gammaComputeCache = null  (invalidate gamma weights)
        → showTab(currentTab)
            → renderActivationTable()   (activation tab)
            → renderActivityTab()       (activity tab — shows prompt if not computed)
            → renderGammaChart()        (gamma tab)
            → renderXsecTab()           (cross sections tab)
            → ...
```

### Data Flow: Compute → Activity/Dose Plots

```
User clicks "Compute Activity & Dose"
    → computeForCurrent()
        → POST /api/compute  (with sidebar fluence + library inputs)
        → currentCompute = response.results[currentMaterial]
        → renderActivityTab()
            → filterProductsByHalfLife(products)
            → builds Plotly traces per product
            → Plotly.newPlot(...)
```

### Data Flow: Gamma Fluence Mode

```
User switches to "Per-irradiation-fluence"
    → gammaNormMode = 'fluence'
    → initGammaCoolSlider()  (creates noUiSlider if not already present)
    → renderGammaChart()
        → getGammaWeights()
            → if gammaComputeCache valid: use it
            → else: POST /api/compute  (mirrors sidebar fluence inputs)
            → _interpolateWeights(result)  at t = 10^gammaCoolLogT seconds
        → scales each gamma line: y = (intensity_pct / 100) × activity_Bq_per_g
        → fraction-of-max filter applied
        → Chart.js bar chart
```

### Key Functions

| Function | Purpose |
|---|---|
| `init()` | Entry point: fetches material list, inits slider, wires event listeners |
| `selectMaterial(name, btn)` | Fetches material data, updates all state, re-renders current tab |
| `showTab(tab)` | Switches visible tab panel and calls the appropriate render function |
| `getFilteredActivation()` | Returns `currentData.activation` filtered by half-life slider, flux regime checkboxes, and σ·f threshold |
| `enrichSigmaF(rows)` | Computes `row.sigma_f` as weighted sum of enabled energy bins × atom fractions |
| `renderActivationTable()` | Builds the activation product table DOM from filtered rows |
| `renderGammaChart()` | Async. Builds Chart.js gamma spectrum in either normalization mode |
| `computeForCurrent()` | POSTs to `/api/compute`, stores result in `currentCompute`, re-renders activity tab |
| `renderActivityTab()` | Builds Plotly activity + dose-rate time-series plots |
| `renderXsecTab()` | Fetches and plots pointwise σ(E) from `/api/xsec/<isotope>` |
| `computeComparison()` | Fetches and plots dose-rate for multiple material × energy combinations |
| `getIrradParams()` | Reads sidebar fluence inputs and returns `{fluence_th, fluence_2p5, fluence_14, library}` |
| `getGammaWeights()` | Fetches (or returns cached) activity weights for fluence-mode gamma |
| `updateDeltaColumnVisibility()` | Shows/hides the ENDF/FENDL Δ% column based on 14 MeV filter state |

---

## How To Extend

### Add a new material

In `data.py`:
1. Add the material to `MATERIALS` with `description`, `density_g_cc`, `category`, and `isotopes` (atom fractions summing to ≤1).
2. Ensure every isotope in `isotopes` is present in `REACTIONS`. If new isotopes are needed, add their reactions too.
3. Add any new isotopes to `ISOTOPE_MASS`.

### Add a new reaction to an existing isotope

In `data.py`, add a new dict to the isotope's list in `REACTIONS`. Required fields: `reaction`, `product`, `cross_sections`, `threshold`, `t_half`, `t_half_s`, `decay_mode`, `gammas`, `notes`. Then re-run `tools/extract_pointwise_3pt.py` to populate the cross-section values from the pointwise files.

### Add a new nuclear library

See `tools/README.md` → "Adding a New Nuclear Library". Requires changes in four places: `download_pointwise.py`, `data.py` (`_load_extracted_3pt`), `app.py` (`_LIBRARY_SUBDIR`, `_LIBRARY_LABEL`), and `index.html` (`#inp-library` option).

### Add a new tab

1. Add a tab button in the sidebar `<div class="tab-buttons">` section of `index.html`.
2. Add a `<div id="tab-<name>">` panel in the main content area.
3. Add the tab name to the two `forEach` loops in `hideAllTabs()` and `showTab()`.
4. Add a render call in `showTab()` for the new tab.

---

## Design Decisions Worth Knowing

**Single-file frontend**: `templates/index.html` contains all HTML, CSS, and JavaScript inline. This was a deliberate choice to keep the project dependency-free and easy to run locally without a build step. Resist the temptation to split it — the operational simplicity is the point.

**Hardcoded cross sections as fallback**: `REACTIONS` in `data.py` carries inline cross_sections dicts that look authoritative but are not. They exist so the file is human-readable as a reference, and so the app degrades gracefully if the extracted JSON files are missing. The authoritative source is `data/endf_3pt.json` / `data/fendl_3pt.json`.

**No persistent state**: the app has no database. Everything is computed on the fly from the in-memory `data.py` structures. The "cache" variables in `index.html` (`currentCompute`, `gammaComputeCache`) are browser session state only.

**Activation model is single-pulse — correct-by-design for ≤ns irradiation**: `compute_activation` treats the irradiation as one instantaneous pulse depositing the full fluence Φ. For the intended use case (~1 ns neutron pulses from pulsed-power drivers), this is physically correct, not an approximation: the pulse duration is many orders of magnitude shorter than the shortest half-life in the database, so no appreciable decay occurs during irradiation and the "instantaneous" idealization is exact. For repeated pulses, activity from each shot can be superposed as time-shifted exponentials on the same decay curves; the single-shot response is the building block.

**Products merged by nuclide**: if Fe-56 can be activated to Mn-56 via both (n,p) and some other path, the activities are summed before plotting. This matches how a detector would measure it.

**Log-log interpolation for σ(E)**: nuclear cross sections vary over many orders of magnitude; linear interpolation between tabulated points would introduce large errors in the resonance region. The pointwise files have dense enough energy grids that log-log linear interpolation between adjacent points is accurate.

---

## Known Limitations

**Daughter chains are not modeled.** Each activation product decays independently on its own λ. If product A decays to daughter B with a different half-life and dose coefficient (e.g., Mo-99 → Tc-99m → Tc-99), the code does not carry forward B's activity or its gamma contribution. For most activation products this is a small effect because either the daughter is stable, the daughter is very short-lived compared to the parent (so its activity equals the parent's and its own gammas are already folded into the measured spectrum), or the daughter's dose coefficient is comparable to the parent's. It matters for any product whose daughter has a substantially different half-life and a strong gamma signature — flag for case-by-case review.

**Impurity coverage is literature-representative, not measured.** Trace-element atom fractions in `MATERIALS` (Co, Eu, Nb, Cs, Sc in steels, concretes, and tungsten) come from published ranges for the relevant grade (ORNL/SCK-CEN/ITER documents), not vendor spec sheets or ICP-MS analysis of specific lots. For Kretekast the trace impurities are labelled PLACEHOLDER in-code because no SWX-277 measurement has been provided yet. Activation predictions at 1 y cooling and beyond are dominated by these trace impurities, so order-of-magnitude agreement is the right expectation until vendor data is obtained. Marked as future work in the TODO block at the top of `data.py`.

**Hardcoded cross_sections drift.** The per-reaction `cross_sections` dicts in `REACTIONS` are a human-readable documentation fallback — they do not feed the compute path at runtime (that's `_load_extracted_3pt()` from the pointwise JSON). A reconciliation sweep in `tools/check_hardcoded_vs_runtime.py` and the pytest in `tests/test_cross_sections.py` guard against the hardcoded values silently drifting more than 1% from the authoritative pointwise runtime values. Run the sweep after any edit that touches `cross_sections` dicts.

**ICRP-74 dose conversion at low energy.** The H*(10)/Φ coefficient table in `physics.py` is the standard ICRP-74 ambient dose equivalent table. Log-log interpolation below ~10 keV is less well-constrained than above it; any product whose dominant gammas sit in the low-keV range is a candidate for cross-check against a more modern evaluation. Marked as future work in the TODO block at the top of `data.py`.

**Pure-beta products carry no external gamma dose by design.** Nine activation products have empty `gammas` lists in `REACTIONS` because they are pure or near-pure beta emitters with no significant gamma output: H-3 (tritium), B-12, C-14, Ca-41, Ca-45, P-32, Pb-205, Pb-209, S-35. These products appear correctly in the activation table and their activities are computed, but they contribute zero to the dose-rate curves and gamma spectrum. This is physically correct — they present no external gamma hazard — not a data gap. Beta dose and internal dose pathways are not modeled anywhere in the app.

**Cross sections for all 84 REACTIONS isotopes are authoritative.** The pointwise σ(E) files for all isotopes in `REACTIONS` — including the 36 added in the Phase 6 expansion — were already present in `data/external/pointwise/endf8/` and `fendl32c/`. Running `extract_pointwise_3pt.py` after the Phase 6 additions populated `data/endf_3pt.json` and `data/fendl_3pt.json` with ENDF-interpolated values for all 84 isotopes. One notable extraction correction: Ti-46(n,p)→Sc-46 at 14 MeV is σ=0.289 b (ENDF), versus the 0.020 b hardcoded estimate — Sc-46 is a more significant dose contributor in Ti-rich materials than the initial estimate suggested.
