#!/usr/bin/env python3
"""
Phase 3B — ENDF-6 preprocessing script.

Reads downloaded ENDF-6 files and extracts cross-section values at three
standard energy points:

    sigma_th  : 0.0253 eV     (thermal, 2200 m/s Maxwellian peak)
    sigma_2p5 : 2.5e6 eV      (D-D neutron peak / fission spectrum representative)
    sigma_14  : 14.1e6 eV     (D-T fusion neutron peak)

Outputs a JSON file:  data/external/<library>_extracted.json

That JSON is the input for update_data.py, which patches these values into
data.py's cross_sections dicts.

Usage:
    python tools/preprocess.py [--library LIB] [--data-dir DIR] [--out FILE]

Requirements:
    pip install numpy
    pip install endf          (optional — falls back to built-in parser if absent)

Parser selection:
    If the 'endf' package is installed, it is used preferentially (handles
    all ENDF-6 format edge cases).  Otherwise the built-in tools/lib/endf6_reader.py
    is used (pure Python + numpy, covers all standard activation file formats).
"""

import argparse
import json
import os
import sys
import traceback
from pathlib import Path

import numpy as np

# Project root is one level above this script
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "tools"))

from data import REACTIONS
from lib.endf6_reader import read_mf3_section, interpolate_xs

# ---------------------------------------------------------------------------
# Try to import endf-python (preferred parser)
# ---------------------------------------------------------------------------
try:
    import endf as endf_pkg
    ENDF_PKG_AVAILABLE = True
    print("INFO: Using endf-python package for parsing.")
except ImportError:
    ENDF_PKG_AVAILABLE = False
    print("INFO: endf-python not installed — using built-in ENDF-6 reader.")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Energy evaluation points (eV)
ENERGY_TH   = 0.0253         # thermal (2200 m/s)
ENERGY_2P5  = 2.5e6          # 2.5 MeV
ENERGY_14   = 14.1e6         # 14.1 MeV

QUERY_ENERGIES = [ENERGY_TH, ENERGY_2P5, ENERGY_14]

# ENDF reaction type → MT number
REACTION_TO_MT = {
    "(n,γ)":  102,
    "(n,p)":  103,
    "(n,α)":  107,
    "(n,2n)": 16,
    "(n,3n)": 17,
    "(n,d)":  104,
    "(n,t)":  105,
    "(n,np)": 28,
    "(n,nα)": 22,
}

# Library-specific file naming and path conventions
LIBRARY_FILENAME = {
    # library_key: lambda Z, A, sym -> filename (without directory)
    "endf8":   lambda Z, A, sym: f"n-{Z:03d}_{sym}_{A:03d}.endf",
    "jeff33":  lambda Z, A, sym: f"n-{Z:03d}_{sym}_{A:03d}.jeff33",
    "jendl5":  lambda Z, A, sym: f"n-{Z:03d}_{sym}_{A:03d}.jendl5",
    "tendl23": lambda Z, A, sym: f"{sym}{A:03d}.tendl",
    "eaf10":   lambda Z, A, sym: f"{sym.lower()}{A}.eaf",
}

ELEMENT_Z = {
    'H':1,'He':2,'Li':3,'Be':4,'B':5,'C':6,'N':7,'O':8,'F':9,'Ne':10,
    'Na':11,'Mg':12,'Al':13,'Si':14,'P':15,'S':16,'Cl':17,'Ar':18,
    'K':19,'Ca':20,'Sc':21,'Ti':22,'V':23,'Cr':24,'Mn':25,'Fe':26,
    'Co':27,'Ni':28,'Cu':29,'Zn':30,'Ga':31,'Ge':32,'As':33,'Se':34,
    'Br':35,'Kr':36,'Rb':37,'Sr':38,'Y':39,'Zr':40,'Nb':41,'Mo':42,
    'Tc':43,'Ru':44,'Rh':45,'Pd':46,'Ag':47,'Cd':48,'In':49,'Sn':50,
    'Sb':51,'Te':52,'I':53,'Xe':54,'Cs':55,'Ba':56,'La':57,'Ce':58,
    'Pr':59,'Nd':60,'Pm':61,'Sm':62,'Eu':63,'Gd':64,'Tb':65,'Dy':66,
    'Ho':67,'Er':68,'Tm':69,'Yb':70,'Lu':71,'Hf':72,'Ta':73,'W':74,
    'Re':75,'Os':76,'Ir':77,'Pt':78,'Au':79,'Hg':80,'Tl':81,'Pb':82,
    'Bi':83,'Po':84,
}


# ---------------------------------------------------------------------------
# File locator
# ---------------------------------------------------------------------------

def find_endf_file(library: str, isotope: str, data_dir: Path) -> Path | None:
    """
    Locate the ENDF-6 file for a given isotope in the library data directory.
    Tries the standard filename pattern for the library; also tries common
    alternate patterns if the standard name is not found.
    """
    sym, A_str = isotope.split('-')
    A = int(A_str)
    Z = ELEMENT_Z.get(sym, 0)

    lib_dir = data_dir / library
    if not lib_dir.exists():
        return None

    # Try the standard filename
    fn_fn = LIBRARY_FILENAME.get(library)
    if fn_fn:
        path = lib_dir / fn_fn(Z, A, sym)
        if path.exists():
            return path

    # Fallback: scan for any file that contains the element+mass in its name
    # e.g. someone might name it "Co59.endf" or "Co-59.endf"
    for f in sorted(lib_dir.iterdir()):
        name = f.name.lower()
        if sym.lower() in name and str(A) in name and f.suffix in ('.endf', '.jeff33', '.jendl5', '.tendl', '.eaf', '.txt'):
            return f

    return None


# ---------------------------------------------------------------------------
# Extraction — endf-python backend
# ---------------------------------------------------------------------------

def _extract_endf_pkg(filepath: Path, mt: int) -> dict:
    """
    Use the endf-python package to extract cross-section at query energies.
    Returns {energy_eV: sigma_barns or None}.
    """
    tape = endf_pkg.Tape.from_file(str(filepath))

    # endf-python Tape iterates over Material objects
    xs_data = None
    for material in tape:
        try:
            # Access MF3 / MT section
            # In endf-python >= 0.9, sections are accessed via material[MF][MT]
            mf3 = material[3]
            if mt in mf3:
                sect = mf3[mt]
                xs_data = sect
                break
        except (KeyError, TypeError):
            continue

    if xs_data is None:
        return {e: None for e in QUERY_ENERGIES}

    # endf-python returns cross-section data in a dict-like section.
    # The actual API depends on the version; try common attribute names:
    results = {}
    try:
        # Try method: section has .xs attribute (a callable or interpolation table)
        # endf-python 0.9+: xs is a Callable that evaluates at E (eV)
        if callable(getattr(xs_data, 'xs', None)):
            for e in QUERY_ENERGIES:
                try:
                    results[e] = float(xs_data.xs(e))
                except Exception:
                    results[e] = None
        else:
            raise AttributeError("xs not callable")
    except (AttributeError, TypeError):
        # Fallback: use the raw TAB1 data from endf-python section dict
        # endf-python stores TAB1 as section['data'] with 'x' and 'y' arrays
        try:
            tab = xs_data.get('data') or xs_data
            energies = np.asarray(tab['x'])
            xsvals   = np.asarray(tab['y'])
            nbt = np.asarray(tab.get('NBT', [len(energies)]), dtype=int)
            int_ = np.asarray(tab.get('INT', [2]), dtype=int)
            for e in QUERY_ENERGIES:
                results[e] = interpolate_xs(energies, xsvals, nbt, int_, e)
        except Exception:
            for e in QUERY_ENERGIES:
                results[e] = None

    return results


# ---------------------------------------------------------------------------
# Extraction — built-in parser backend
# ---------------------------------------------------------------------------

def _extract_builtin(filepath: Path, mt: int) -> dict:
    """
    Use the built-in ENDF-6 reader (tools/lib/endf6_reader.py).
    """
    from lib.endf6_reader import read_mf3_section, interpolate_xs

    section = read_mf3_section(str(filepath), mt)
    if section is None:
        return {e: None for e in QUERY_ENERGIES}

    results = {}
    for e in QUERY_ENERGIES:
        results[e] = interpolate_xs(
            section["energies"], section["xs"],
            section["NBT"], section["INT"], e
        )
    return results


# ---------------------------------------------------------------------------
# Main extraction loop
# ---------------------------------------------------------------------------

def extract_all(library: str, data_dir: Path, verbose: bool = False) -> dict:
    """
    Iterate over all (isotope, reaction) pairs in REACTIONS and extract
    cross-section values at the 3 standard energy points.

    Returns a nested dict:
      {
        "library": str,
        "isotopes": {
          "Co-59": {
            "file":   "path/to/n-027_Co_059.endf",
            "MAT":    2725,
            "reactions": {
              "(n,γ)": {
                "MT":        102,
                "sigma_th":  37.2,    # barns or null
                "sigma_2p5": 0.512,   # barns or null
                "sigma_14":  0.0027,  # barns or null
              },
              ...
            }
          },
          ...
        }
      }
    """
    output = {
        "library":  library,
        "isotopes": {},
    }

    extract_fn = _extract_endf_pkg if ENDF_PKG_AVAILABLE else _extract_builtin

    isotopes_processed = 0
    isotopes_missing   = 0

    for isotope, reactions in REACTIONS.items():
        filepath = find_endf_file(library, isotope, data_dir)
        if filepath is None:
            if verbose:
                print(f"  {isotope:<12}  FILE NOT FOUND — skipping")
            isotopes_missing += 1
            continue

        iso_entry = {
            "file":      str(filepath.relative_to(data_dir.parent)),
            "MAT":       None,
            "reactions": {},
        }

        unique_mts = {}
        for rxn in reactions:
            mt = REACTION_TO_MT.get(rxn["reaction"])
            if mt and rxn["reaction"] not in unique_mts:
                unique_mts[rxn["reaction"]] = mt

        for reaction_str, mt in unique_mts.items():
            try:
                raw = extract_fn(filepath, mt)
            except Exception as exc:
                if verbose:
                    print(f"  {isotope:<12}  MT={mt}  ERROR: {exc}")
                    traceback.print_exc()
                raw = {e: None for e in QUERY_ENERGIES}

            # Round to 4 significant figures to keep JSON readable
            def sig4(v):
                if v is None or v != v:  # None or NaN
                    return None
                if v == 0.0:
                    return 0.0
                import math
                mag = math.floor(math.log10(abs(v)))
                factor = 10 ** (3 - mag)
                return round(v * factor) / factor

            iso_entry["reactions"][reaction_str] = {
                "MT":        mt,
                "sigma_th":  sig4(raw.get(ENERGY_TH)),
                "sigma_2p5": sig4(raw.get(ENERGY_2P5)),
                "sigma_14":  sig4(raw.get(ENERGY_14)),
            }

        output["isotopes"][isotope] = iso_entry
        isotopes_processed += 1

        # Progress
        rxn_summary = "  ".join(
            f"{r}: th={v['sigma_th']} 2p5={v['sigma_2p5']} 14={v['sigma_14']}"
            for r, v in iso_entry["reactions"].items()
        )
        status = "OK" if iso_entry["reactions"] else "no reactions"
        print(f"  {isotope:<12}  {status}  {rxn_summary if verbose else ''}")

    print(f"\n  Processed: {isotopes_processed}  Missing files: {isotopes_missing}")
    return output


# ---------------------------------------------------------------------------
# Validation — compare extracted values against current data.py values
# ---------------------------------------------------------------------------

def validate_against_datspy(extracted: dict, tolerance_pct: float = 20.0) -> list:
    """
    Compare extracted sigma_th and sigma_14 values against the existing
    values in data.py.  Returns a list of discrepancy records.

    A discrepancy is flagged when the extracted value differs from the
    existing value by more than tolerance_pct percent.
    """
    library = extracted["library"]
    discrepancies = []

    for isotope, rxns in REACTIONS.items():
        if isotope not in extracted["isotopes"]:
            continue
        iso_ext = extracted["isotopes"][isotope]

        for rxn in rxns:
            reaction_str = rxn["reaction"]
            if reaction_str not in iso_ext["reactions"]:
                continue

            ext = iso_ext["reactions"][reaction_str]
            existing_xs = rxn.get("cross_sections", {}).get("endf8", {})

            for energy_key, ext_key in [("sigma_th", "sigma_th"), ("sigma_14", "sigma_14")]:
                existing_val = existing_xs.get(energy_key)
                extracted_val = ext.get(ext_key)

                if existing_val is None or extracted_val is None:
                    continue
                if existing_val == 0 or extracted_val == 0:
                    continue

                pct_diff = abs(extracted_val - existing_val) / existing_val * 100
                if pct_diff > tolerance_pct:
                    discrepancies.append({
                        "isotope":   isotope,
                        "reaction":  reaction_str,
                        "energy":    energy_key,
                        "existing":  existing_val,
                        "extracted": extracted_val,
                        "pct_diff":  round(pct_diff, 1),
                        "library":   library,
                    })

    return discrepancies


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    default_data_dir = os.environ.get(
        "ACTIVATION_DATA_DIR",
        str(PROJECT_ROOT / "data" / "external")
    )

    parser = argparse.ArgumentParser(
        description="Extract 3-point cross-sections from ENDF-6 files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Extract ENDF/B-VIII.0 values (files must already be in data/external/endf8/)
  python tools/preprocess.py

  # Extract JEFF-3.3
  python tools/preprocess.py --library jeff33

  # Extract all libraries and report discrepancies vs current data.py
  python tools/preprocess.py --library endf8 --validate

  # Verbose (print extracted values per isotope)
  python tools/preprocess.py --verbose
""")

    parser.add_argument(
        "--library", "-l",
        default="endf8",
        choices=["endf8", "jeff33", "jendl5", "tendl23", "eaf10"],
        help="Nuclear data library to process (default: endf8).",
    )
    parser.add_argument(
        "--data-dir", default=default_data_dir,
        help=f"Root data directory containing library subdirs (default: {default_data_dir}).",
    )
    parser.add_argument(
        "--out", default=None,
        help="Output JSON path (default: data/external/<library>_extracted.json).",
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="After extraction, compare results vs current data.py values and report discrepancies.",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true",
        help="Print extracted values per isotope.",
    )
    parser.add_argument(
        "--tolerance", type=float, default=20.0,
        help="Discrepancy threshold %% for --validate (default: 20%%).",
    )

    args = parser.parse_args()

    data_dir = Path(args.data_dir)
    library  = args.library

    lib_dir = data_dir / library
    if not lib_dir.exists() or not any(lib_dir.iterdir()):
        print(f"ERROR: No files found in {lib_dir}")
        print(f"       Run 'python tools/download_endf.py --library {library}' first.")
        sys.exit(1)

    print(f"Extracting cross-sections from {library} ENDF-6 files...")
    print(f"Data dir: {data_dir / library}")
    print(f"Parser:   {'endf-python' if ENDF_PKG_AVAILABLE else 'built-in endf6_reader'}")
    print()

    extracted = extract_all(library, data_dir, verbose=args.verbose)

    # Write JSON output
    out_path = Path(args.out) if args.out else data_dir / f"{library}_extracted.json"
    with open(out_path, 'w') as f:
        json.dump(extracted, f, indent=2)
    print(f"\nWrote extracted data to: {out_path}")

    # Validation report
    if args.validate:
        print(f"\nValidating against current data.py values (tolerance: {args.tolerance}%)...")
        discrepancies = validate_against_datspy(extracted, tolerance_pct=args.tolerance)

        if not discrepancies:
            print("  All values within tolerance. ✓")
        else:
            print(f"  {len(discrepancies)} discrepancies found:\n")
            print(f"  {'Isotope':<12} {'Reaction':<8} {'Energy':<12} "
                  f"{'Existing':>12} {'Extracted':>12} {'Diff%':>8}  Library")
            for d in sorted(discrepancies, key=lambda x: -x["pct_diff"]):
                print(f"  {d['isotope']:<12} {d['reaction']:<8} {d['energy']:<12} "
                      f"{d['existing']:>12.4g} {d['extracted']:>12.4g} "
                      f"{d['pct_diff']:>7.1f}%  {d['library']}")
            disc_path = data_dir / f"{library}_discrepancies.json"
            with open(disc_path, 'w') as f:
                json.dump(discrepancies, f, indent=2)
            print(f"\n  Written to: {disc_path}")

    return extracted


if __name__ == "__main__":
    main()
