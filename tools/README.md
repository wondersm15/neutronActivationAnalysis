# Phase 3B — Nuclear Data Preprocessing Pipeline

This directory contains the three-stage pipeline for populating multi-library
cross-section data into `data.py`.

---

## Prerequisites

```bash
pip install requests numpy
pip install endf          # optional but recommended (endf-python package)
```

If `endf-python` is not installed, the pipeline falls back to the built-in
ENDF-6 reader (`lib/endf6_reader.py`), which handles all standard activation
file formats using only numpy.

---

## Pipeline Overview

```
Stage 1:  download_endf.py   →  data/external/<library>/  (ENDF-6 files)
Stage 2:  preprocess.py      →  data/external/<library>_extracted.json
Stage 3:  update_data.py     →  data.py  (cross_sections updated)
```

---

## Stage 1 — Download ENDF-6 Files

Downloads one file per isotope from the official library sources.
All 48 target isotopes from `REACTIONS` are downloaded.

```bash
# ENDF/B-VIII.0 (publicly accessible, no account needed)
python tools/download_endf.py --library endf8

# Validate URL patterns first (fast, no full download)
python tools/download_endf.py --library endf8 --validate

# TENDL-2023 (also public)
python tools/download_endf.py --library tendl23

# JENDL-5.0 (public from JAEA)
python tools/download_endf.py --library jendl5

# JEFF-3.3 (may need NEA Data Bank registration)
python tools/download_endf.py --library jeff33

# EAF-2010 — MANUAL: download FISPACT-II data package from NEA
#   https://www.oecd-nea.org/tools/abstract/detail/nea-1609
#   Extract 'xs' directory → data/external/eaf10/

# Dry run to see what would be downloaded
python tools/download_endf.py --library endf8 --dry-run

# Download all public libraries
python tools/download_endf.py --library endf8 tendl23 jendl5
```

Files go to `data/external/<library>/` (or `$ACTIVATION_DATA_DIR/<library>/`).

### File naming conventions

| Library  | Filename pattern           | Example             |
|----------|---------------------------|---------------------|
| endf8    | `n-{ZZZ}_{Sym}_{AAA}.endf` | `n-027_Co_059.endf` |
| jeff33   | `n-{ZZZ}_{Sym}_{AAA}.jeff33` | `n-027_Co_059.jeff33` |
| jendl5   | `n-{ZZZ}_{Sym}_{AAA}.jendl5` | `n-027_Co_059.jendl5` |
| tendl23  | `{Sym}{AAA}.tendl`         | `Co059.tendl`       |
| eaf10    | `{sym}{A}.eaf`             | `co59.eaf`          |

---

## Stage 2 — Preprocess (Extract 3-Point Values)

Reads the downloaded ENDF-6 files and evaluates each cross-section at:

| Point      | Energy       | Purpose                                  |
|------------|-------------|------------------------------------------|
| sigma_th   | 0.0253 eV   | Thermal (2200 m/s, Maxwellian peak)      |
| sigma_2p5  | 2.5 MeV     | D-D neutron peak / fission spectrum      |
| sigma_14   | 14.1 MeV    | D-T fusion neutron peak                  |

```bash
# Extract ENDF/B-VIII.0 values
python tools/preprocess.py --library endf8

# Extract and validate against existing data.py values
python tools/preprocess.py --library endf8 --validate

# Verbose (print extracted values for every isotope)
python tools/preprocess.py --library endf8 --verbose

# JEFF-3.3
python tools/preprocess.py --library jeff33
```

Output: `data/external/endf8_extracted.json`

The `--validate` flag compares extracted sigma_th and sigma_14 against existing
`data.py` values and flags discrepancies >20%. This is the Phase 3C validation
step — review any flagged entries to decide whether to update data.py.

---

## Stage 3 — Update data.py

Patches `cross_sections` dicts in `data.py` with the extracted values.

**Default mode**: only fills `sigma_2p5: None` placeholders. Existing `sigma_th`
and `sigma_14` values (which have been manually validated) are not overwritten.

```bash
# Dry run first — show what would change
python tools/update_data.py --json data/external/endf8_extracted.json --dry-run

# Apply sigma_2p5 values
python tools/update_data.py --json data/external/endf8_extracted.json

# Add a new library (e.g. JEFF-3.3) to every cross_sections block
python tools/update_data.py --json data/external/jeff33_extracted.json --add-library

# Override existing values too (use carefully — validate discrepancies first)
python tools/update_data.py --json data/external/endf8_extracted.json --update-existing
```

A backup of `data.py` is written automatically before patching
(`data.py.bak-<library>`). A change log is saved to `data_update_<library>.json`.

---

## Full Workflow Example — Populating sigma_2p5 from ENDF/B-VIII.0

```bash
# 1. Download all 48 isotope files
python tools/download_endf.py --library endf8

# 2. Extract 3-point values and validate against data.py
python tools/preprocess.py --library endf8 --validate --verbose

# 3. Review discrepancies (if any)
cat data/external/endf8_discrepancies.json

# 4. Dry-run the update
python tools/update_data.py --json data/external/endf8_extracted.json --dry-run

# 5. Apply
python tools/update_data.py --json data/external/endf8_extracted.json

# 6. Run the app and verify
python app.py
```

---

## Adding a New Nuclear Library

Once JEFF-3.3 files are downloaded:

```bash
python tools/preprocess.py --library jeff33 --validate
python tools/update_data.py --json data/external/jeff33_extracted.json --add-library
```

Then in `index.html`, enable the jeff33 `<option>` (remove the `disabled` attribute).

---

## Data Directory

By default, ENDF files are read from `./data/external/`. Override with:

```bash
export ACTIVATION_DATA_DIR=/path/to/your/nuclear_data
python tools/preprocess.py --library endf8
```

---

## Files in this Directory

| File                    | Purpose                                          |
|-------------------------|--------------------------------------------------|
| `download_endf.py`      | Stage 1: download ENDF-6 files                   |
| `preprocess.py`         | Stage 2: extract 3-point cross-sections          |
| `update_data.py`        | Stage 3: patch data.py cross_sections            |
| `lib/endf6_reader.py`   | Pure-Python ENDF-6 MF3 parser (no ext. deps)    |
| `README.md`             | This file                                        |
