# data/ — Nuclear Data Files

This directory holds the committed data files that the app reads at startup,
and the git-ignored `external/` directory that holds downloaded pointwise files.

---

## Committed Files

### `endf_3pt.json` and `fendl_3pt.json`

Three-point cross sections extracted from the downloaded pointwise σ(E) files
by `tools/extract_pointwise_3pt.py`. Loaded at app startup by `_load_extracted_3pt()`
in `data.py` to populate `REACTIONS[isotope][reaction]["cross_sections"]`.

**Schema:**
```json
{
  "Fe-56": {
    "(n,γ)":  { "sigma_th": 2.604, "sigma_2p5": 0.001714, "sigma_14": 0.0007956 },
    "(n,p)":  { "sigma_th": null,  "sigma_2p5": null,      "sigma_14": 0.1133   },
    "(n,2n)": { "sigma_th": null,  "sigma_2p5": null,      "sigma_14": 0.4314   }
  },
  ...
}
```

**Fields:**

| Field       | Energy     | Description |
|-------------|------------|-------------|
| `sigma_th`  | 0.0253 eV  | Thermal cross section at 2200 m/s (Maxwellian peak). `null` if the reaction has a threshold above thermal. |
| `sigma_2p5` | 2.45 MeV   | Cross section at D-D fusion neutron peak energy. `null` for threshold reactions above 2.45 MeV. |
| `sigma_14`  | 14.1 MeV   | Cross section at D-T fusion neutron peak energy. Present for all reactions. |

All values are in **barns** (1 b = 10⁻²⁴ cm²). `null` means the energy point
is below the reaction threshold or outside the range of the pointwise file.

**Coverage:**
- `endf_3pt.json` — 48 isotopes, 77 reactions (ENDF/B-VIII.0)
- `fendl_3pt.json` — 48 isotopes, 74 reactions (FENDL-3.2c; 3 Eu reactions
  absent because FENDL-3.2c does not cover rare earth trace impurity isotopes)

**Regenerating:**
```bash
python tools/extract_pointwise_3pt.py
```
Requires pointwise files in `data/external/pointwise/`. The script prints a
full coverage report and flags large ENDF/FENDL discrepancies.

---

## Git-Ignored Directory

### `external/pointwise/`

Downloaded pointwise σ(E) JSON files. Not committed (~95 MB per library).
Required for the Cross Sections tab to display σ(E) curves.

```
external/pointwise/
├── endf8/          ← ENDF/B-VIII.0, ~125 files
│   ├── Fe_56_n102.json     (n,γ) on Fe-56
│   ├── Fe_56_n16.json      (n,2n) on Fe-56
│   ├── Fe_56_n1.json       total XS on Fe-56
│   └── ...
└── fendl32c/       ← FENDL-3.2c, ~120 files
    └── ...
```

**Filename convention:** `{Symbol}_{A}_n{MT}.json`

| MT | Reaction  |
|----|-----------|
| 1  | (n,total) |
| 16 | (n,2n)    |
| 102| (n,γ)     |
| 103| (n,p)     |
| 107| (n,α)     |

**File contents (from openmc-data-storage, pre-processed at 294 K):**
```json
{
  "energy":        [1e-5, 1.5e-5, ..., 1.5e8],   // eV, ~10k–50k points
  "cross section": [2.1,  1.8,    ..., 0.001],    // barns
  "Element": "Fe",
  "Mass number": 56,
  "MT reaction number": 102,
  "Library": "ENDF/B-VIII.0",
  ...
}
```

**Download:**
```bash
python tools/download_pointwise.py --library endf8 --include-total
python tools/download_pointwise.py --library fendl32c --include-total
```
