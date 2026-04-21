# Phase 3 — Multi-Library Nuclear Data Integration

## Design Summary

Move from hardcoded ENDF/B-VIII.0 two-point data to a system that:
1. Bundles three-point cross-sections (thermal, 2.5 MeV, 14.1 MeV) from multiple evaluated libraries
2. Optionally loads full pointwise σ(E) from a local nuclear data directory for cross-section plotting
3. Cross-validates all bundled values against independent libraries, flagging disagreements

**Deployment model:** Hybrid. The core activation tool remains self-contained (bundled JSON data, no external dependencies beyond Flask). The Cross Sections tab reads from an external data directory if present; shows "nuclear data not installed" otherwise.

---

## Sub-Phases

### 3A — Add 2.5 MeV Energy Point + Data Layer Refactor

**What:** Add σ_2.5 (2.5 MeV cross-section) as a third standard energy point alongside σ_th and σ_14 for every reaction. Refactor data.py so that the bundled data structure cleanly supports multi-library values.

**Data structure change (data.py REACTIONS):**

Current:
```python
{
    "reaction": "(n,γ)",
    "product": "Co-60",
    "sigma_th": 37.2,       # ENDF/B-VIII.0
    "sigma_14": 2.02,       # ENDF/B-VIII.0
    ...
}
```

Proposed:
```python
{
    "reaction": "(n,γ)",
    "product": "Co-60",
    "cross_sections": {
        "endf8": {"sigma_th": 37.2, "sigma_2p5": 0.185, "sigma_14": 2.02},
        "jeff33": {"sigma_th": 37.18, "sigma_2p5": 0.190, "sigma_14": 2.05},
        "jendl5": {"sigma_th": 37.2, "sigma_2p5": 0.183, "sigma_14": 2.00},
    },
    ...
}
```

This keeps all data bundled in data.py but makes cross-library comparison first-class. The physics engine selects which library to use (default: ENDF/B-VIII.0; user-selectable in GUI).

**Frontend changes:**
- Sidebar: add 2.5 MeV fluence input alongside thermal and 14 MeV
- Activation table: add σ_2.5 column; σ·f computation uses all three energies
- Sidebar or header: library selector dropdown (ENDF/B-VIII.0 | JEFF-3.3 | JENDL-5)

**Estimated scope:** ~200 lines data.py restructure, ~80 lines physics.py, ~100 lines index.html.

---

### 3B — Nuclear Data Preprocessing Pipeline

**What:** Build a preprocessing script that reads raw ENDF-6 evaluation files, extracts pointwise cross-sections for our specific reactions, evaluates at the three standard energies, and outputs preprocessed JSON.

**Parser choice:** `endf-python` (PyPI package `endf`). Lightweight pure-Python ENDF-6 parser with minimal dependencies. Chosen over `openmc.data` to keep the dependency tree light — the preprocessing script only needs to read MF=3 (cross-section) data and interpolate at specific energies; `endf-python` handles this without pulling in numpy/h5py.

**Script: `tools/preprocess_nuclear_data.py`**

Inputs:
- Path to ENDF-6 library directory (e.g., `~/nuclear_data/endf-b-viii.0/neutrons/`)
- Reaction map (our REACTIONS dict — which target isotopes + MT numbers we need)

Outputs:
- `data/endf8_xsec.json` — three-point values for all our reactions
- `data/jeff33_xsec.json` — same
- `data/jendl5_xsec.json` — same
- `data/endf8_pointwise.json` (optional, larger) — full σ(E) for plotting
- `data/validation_report.json` — cross-library diff report

The three-point JSON files get committed to the repo (small — a few KB each). The pointwise files go in the external data directory (not committed).

**MT number mapping needed:** Each reaction in our REACTIONS dict needs to be mapped to the ENDF MT number used in the evaluation files. Examples:
- (n,γ) = MT 102
- (n,p) = MT 103
- (n,α) = MT 107
- (n,2n) = MT 16
- (n,d) = MT 104
- (n,t) = MT 105
- (n,nα) = MT 22

This mapping is deterministic and can be built into the script.

**Estimated scope:** ~400 lines Python script + ~100 lines config/mapping.

---

### 3C — Cross-Validation & Diff Report

**What:** Systematically compare our bundled ENDF/B-VIII.0 values (currently hand-entered) against fresh extractions from the raw evaluation files. Flag discrepancies.

**Output: `data/validation_report.json`**
```json
{
    "Co-59|(n,γ)|Co-60": {
        "bundled": {"sigma_th": 37.2, "sigma_14": 2.02},
        "extracted_endf8": {"sigma_th": 37.18, "sigma_14": 2.015},
        "jeff33": {"sigma_th": 37.18, "sigma_14": 2.05},
        "jendl5": {"sigma_th": 37.2, "sigma_14": 2.00},
        "max_discrepancy_pct": {"sigma_th": 0.05, "sigma_14": 2.5},
        "flag": false
    },
    ...
}
```

Threshold for flagging: >10% discrepancy between any two libraries at any energy point. These get highlighted in the GUI (activation table row background or badge).

**Also catches:**
- Transcription errors in our hand-entered data
- Reactions where ENDF and JEFF genuinely disagree (known for some threshold reactions)
- Missing reactions: isotope/channel combinations present in JEFF but absent from our REACTIONS dict

**Estimated scope:** ~150 lines (mostly comparison logic + report formatting). Runs as part of the preprocessing pipeline.

---

### 3D — Cross Sections Tab (GUI)

**What:** New tab in the GUI showing full σ(E) curves from threshold to 20 MeV for all reactions of the currently selected material. Multi-library overlay. Interactive (Plotly).

**Prerequisites:** External data directory with pointwise cross-section files. Tab shows "Nuclear data libraries not installed — see README for setup instructions" if the data directory is not configured.

**Features:**
- For each reaction in the current material, plot σ(E) from selected libraries
- Multi-library overlay on same axes (ENDF = blue, JEFF = red, JENDL = green)
- Log-log axes (standard for cross-section plots)
- Vertical markers at thermal (0.0253 eV), 2.5 MeV, and 14.1 MeV evaluation points
- Reaction selector (dropdown or checkbox list — not all reactions plotted simultaneously)
- Zoom/pan via Plotly

**Backend:**
- New endpoint: `/api/crosssection/<target>/<mt>` — returns pointwise data for a specific reaction from all available libraries
- Reads from external data directory (JSON files or HDF5)
- Returns `{energy_eV: [...], sigma_b: {...}}` per library

**Estimated scope:** ~200 lines Python (endpoint + data reading), ~250 lines JS (Plotly rendering, controls).

---

## Data Acquisition Plan

All five libraries use the ENDF-6 format (or derivatives) and are freely downloadable:

| Library | Source | Download | Size (neutron sublib) | Notes |
|---------|--------|----------|----------------------|-------|
| ENDF/B-VIII.0 | NNDC/BNL | https://www.nndc.bnl.gov/endf-b8.0/download.html | ~450 MB | US evaluation; current primary |
| JEFF-3.3 | NEA Data Bank | https://www.oecd-nea.org/dbdata/jeff/jeff33/ | ~400 MB | EU evaluation; preferred by EUROfusion/FISPACT-II |
| JENDL-5 | JAEA | https://wwwndc.jaea.go.jp/jendl/j5/j5.html | ~500 MB | Japan; excellent for shielding/activation |
| TENDL-2023 | PSI/TALYS | https://tendl.web.psi.ch/tendl_2023/tendl2023.html | ~2 GB (full) | TALYS-based; broadest isotope coverage for gap-filling |
| EAF-2010 | CCFE/UKAEA | https://fispact.ukaea.uk/nuclear-data/eaf-2010/ | ~50 MB | Activation-specific; used with FISPACT-II |

We only need the neutron reaction sublibraries (not decay, fission yield, etc.). Within those, we only need evaluations for our ~50 target isotopes — targeted downloads rather than full libraries.

**Selective download approach:** Download only the specific isotope evaluation files we need. Each library organizes files by Z-A number (e.g., `n-026-Fe-054.endf` for Fe-54). For 50 isotopes × 5 libraries = ~250 files, total ~100–200 MB.

**TENDL note:** TENDL-2023 has evaluation files for virtually every isotope up to Bi — useful for filling gaps where ENDF/JEFF/JENDL lack data. However, TENDL values for well-measured isotopes are generally less trusted than the three major evaluations.

**EAF note:** EAF-2010 is activation-focused — it includes reaction channels (e.g., exotic high-energy paths) that the general-purpose libraries sometimes omit. Its format is ENDF-6 compatible but with some EAF-specific extensions. Need to verify `endf-python` handles these cleanly.

**EXFOR experimental data:** Available via IAEA NDS API (https://nds.iaea.org/exfor/) or bulk download. EXFOR provides measured cross-section data points (not evaluations) from published experiments. Used as overlay on evaluated curves to show where evaluations are constrained by measurement vs. extrapolated by models.

## External Data Directory

**Location resolution order:**
1. `ACTIVATION_DATA_DIR` environment variable (if set)
2. `./data/external/` (relative to repo root, default)

**Expected directory structure:**
```
data/external/
├── endf-b-viii.0/
│   └── neutrons/
│       ├── n-026-Fe-054.endf
│       ├── n-027-Co-059.endf
│       └── ...
├── jeff-3.3/
│   └── neutrons/
│       └── ...
├── jendl-5/
│   └── neutrons/
│       └── ...
├── tendl-2023/
│   └── neutrons/
│       └── ...
├── eaf-2010/
│   └── ...
└── exfor/
    └── ...  (cached EXFOR queries or bulk data)
```

`data/external/` is in `.gitignore` — not committed. A setup script (`tools/download_nuclear_data.py`) will fetch the specific isotope files needed.

---

## Implementation Order

1. **3A** — Data layer restructure: refactor REACTIONS to multi-library `cross_sections` dict schema; add `sigma_2p5: null` placeholder column; update physics.py and frontend to handle new structure + 2.5 MeV fluence input. No new values yet — ENDF/B-VIII.0 thermal and 14 MeV values migrated as-is.
2. **3B** — Preprocessing pipeline + data download script: `tools/download_nuclear_data.py` (targeted isotope downloads), `tools/preprocess_nuclear_data.py` (ENDF-6 → JSON via `endf-python`). First run populates all five libraries' three-point values including 2.5 MeV. Also extracts pointwise σ(E) for the Cross Sections tab.
3. **3C** — Cross-validation: compare hand-entered bundled values against fresh extractions; flag discrepancies >10%; generate diff report. Also identifies missing reactions present in JEFF/JENDL/TENDL but absent from our REACTIONS dict.
4. **3D** — Cross Sections tab + EXFOR overlay: Plotly-based σ(E) plots, multi-library overlay, log-log axes, energy markers, EXFOR experimental data points. Reads from external data directory.

**Critical path:** 3A can proceed immediately (schema refactor only). 3B requires Marc to download nuclear data files to his machine. 3C and 3D depend on 3B output. 3C and 3D can run in parallel once data is available.

---

## Resolved Decisions

All open questions resolved (2026-04-03):

1. **Parser:** `endf-python` — lightweight, minimal dependencies.
2. **Library scope:** All five: ENDF/B-VIII.0, JEFF-3.3, JENDL-5, TENDL-2023, EAF-2010.
3. **Data directory:** Default `./data/external/` + `ACTIVATION_DATA_DIR` env var override.
4. **2.5 MeV values:** Wait for raw ENDF files — extract exact values via preprocessing pipeline. No training-knowledge estimates.
5. **EXFOR overlay:** Yes, include in Phase 3D scope.
