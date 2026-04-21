# Neutron Activation Analysis

A local web application for computing neutron activation, residual activity, and dose rates in pulsed-fusion-relevant structural materials. Built on Flask + Plotly, with nuclear data from ENDF/B-VIII.0 and FENDL-3.2c.

---

## Features

- **25 structural materials** — aluminum alloys, steels, copper, tungsten, titanium, and more
- **Multi-library cross sections** — ENDF/B-VIII.0 and FENDL-3.2c, with a per-reaction library disagreement column
- **Three neutron energy groups** — thermal (0.0253 eV), D-D (2.45 MeV), D-T (14.1 MeV)
- **Activity & dose rate vs. time** — time-dependent curves per isotope after end of irradiation
- **Gamma spectrum** — switchable between per-isotope-decay and per-irradiation-fluence normalization, with a cooling time slider
- **σ(E) plots** — full pointwise cross-section curves from downloaded ENDF/FENDL data
- **Material comparison** — overlay multiple materials and/or energy bins on a single dose-rate chart
- **Literature tab** — in-app display of markdown research notes and references

---

## Quick Start

```bash
# 1. Clone
git clone https://github.com/wondersm15/neutron-activation-analysis.git
cd neutron-activation-analysis

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python app.py

# 4. Open in browser
#    http://localhost:5050
```

The app runs fully offline. No external services or API keys required.

---

## Data Setup

### Bundled data (included in repo)

- `data.py` — nuclear reaction database: cross sections, decay data, gamma lines for all 25 materials
- `data/endf_3pt.json` and `data/fendl_3pt.json` — three-point cross sections extracted from pointwise files via `tools/extract_pointwise_3pt.py`
- `references.json` — structured bibliography
- `NotesFromOtherSources/` — markdown literature review notes displayed in the Literature tab

### Pointwise σ(E) data (not in repo — downloaded separately)

The **Cross Sections tab** plots full σ(E) curves, which require large pointwise JSON files (~95 MB per library). These are excluded from the repo and must be downloaded before that tab is functional:

```bash
# ENDF/B-VIII.0 (activation reactions + total cross sections)
python tools/download_pointwise.py --library endf8 --include-total

# FENDL-3.2c
python tools/download_pointwise.py --library fendl32c --include-total
```

Files are saved to `data/external/pointwise/<library>/`. The activation computation and all other tabs work without them.

### Re-extracting three-point values

If you add new pointwise data or switch libraries, regenerate the three-point JSON files:

```bash
python tools/extract_pointwise_3pt.py
```

This interpolates σ_th, σ_2.45MeV, and σ_14.1MeV from the downloaded pointwise files for both libraries and writes `data/endf_3pt.json` and `data/fendl_3pt.json`.

---

## Directory Structure

```
.
├── app.py                        # Flask application, API endpoints
├── physics.py                    # Activation physics, dose-rate computation
├── data.py                       # Nuclear reaction database (REACTIONS, MATERIALS)
├── requirements.txt
├── templates/
│   └── index.html                # Single-page frontend (Plotly + Chart.js)
├── data/
│   ├── endf_3pt.json             # ENDF/B-VIII.0 three-point cross sections
│   ├── fendl_3pt.json            # FENDL-3.2c three-point cross sections
│   └── external/                 # Downloaded pointwise files (git-ignored)
│       └── pointwise/
│           ├── endf8/            # ENDF/B-VIII.0 σ(E) JSON files
│           └── fendl32c/         # FENDL-3.2c σ(E) JSON files
├── tools/
│   ├── download_pointwise.py     # Download pointwise σ(E) data from openmc-data
│   ├── extract_pointwise_3pt.py  # Interpolate three-point values from pointwise files
│   ├── download_endf.py          # Download raw ENDF-6 files (legacy pipeline)
│   ├── preprocess.py             # Extract from ENDF-6 (legacy pipeline)
│   ├── update_data.py            # Patch data.py cross_sections (legacy pipeline)
│   ├── lib/endf6_reader.py       # Pure-Python ENDF-6 MF3 parser
│   └── README.md                 # Full pipeline documentation
├── NotesFromOtherSources/        # Literature review markdown notes
├── references.json               # Structured bibliography
├── ROADMAP.md                    # Feature roadmap
└── ACTIVITY_LOG.md               # Development log
```

---

## Nuclear Data Sources

| Library | Version | Source |
|---|---|---|
| ENDF/B-VIII.0 | 2018 | [NNDC/BNL](https://www.nndc.bnl.gov/endf/b8.0/) |
| FENDL-3.2c | 2023 | [IAEA NDS](https://www-nds.iaea.org/fendl/) |

Pointwise σ(E) files are served from the [openmc-data](https://github.com/openmc-dev/openmc_data) pre-processed dataset (fully reconstructed at 294 K, covering ~1×10⁻⁵ eV to 150 MeV).

Decay data and gamma line intensities are from ENDF/B-VIII.0 decay sub-library.

Dose conversion coefficients (H*(10)/Φ) are from ICRP Publication 74 (1996), Table A.21.

---

## Physics Notes

Activation is computed assuming instantaneous irradiation (delta-function pulse). For each product isotope:

```
N_activated = σ · Φ · (ρ · f / m_atom)
A(t) = λ · N_activated · exp(−λt)
```

where σ is the weighted cross section for the selected neutron energy group, Φ is the fluence (n/cm²), ρ is material density, f is the isotopic atom fraction, and λ = ln 2 / t½.

Products arising from the same target via different reactions are merged by nuclide before computing activity. Dose rate is computed from the summed gamma emission spectrum using ICRP-74 H*(10) fluence-to-dose conversion factors, assuming an isotropic point source at the specified distance.

---

## License

To be determined.
