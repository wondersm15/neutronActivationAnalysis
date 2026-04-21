"""
extract_pointwise_3pt.py
------------------------
Interpolates σ_th (0.0253 eV), σ_2p5 (2.45 MeV), σ_14 (14.1 MeV) from the
downloaded pointwise JSON files for both ENDF/B-VIII.0 and FENDL-3.2c.

Outputs:
  data/endf_3pt.json
  data/fendl_3pt.json

Each file has the schema:
  {
    "Fe-56": {
      "(n,γ)": { "sigma_th": <float|null>, "sigma_2p5": <float|null>, "sigma_14": <float|null> },
      "(n,2n)": { ... },
      ...
    },
    ...
  }

null means the pointwise file was not found or the energy is outside the file range.

Run from the repo root:
  python tools/extract_pointwise_3pt.py
"""

import json
import math
import os
import sys

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

# Energies to interpolate (eV)
E_TH  = 0.0253       # thermal
E_2P5 = 2.45e6       # DD 2.45 MeV
E_14  = 14.1e6       # DT 14.1 MeV

ENERGY_POINTS = {
    "sigma_th":  E_TH,
    "sigma_2p5": E_2P5,
    "sigma_14":  E_14,
}

MT_MAP = {
    "(n,γ)": 102,
    "(n,p)": 103,
    "(n,α)": 107,
    "(n,2n)": 16,
    "(n,3n)": 17,
    "(n,d)": 104,
    "(n,t)": 105,
    "(n,np)": 28,
    "(n,nα)": 22,
}

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
POINTWISE_ROOT = os.path.join(REPO_ROOT, "data", "external", "pointwise")

LIBRARIES = {
    "endf8":    os.path.join(POINTWISE_ROOT, "endf8"),
    "fendl32c": os.path.join(POINTWISE_ROOT, "fendl32c"),
}

OUTPUT_FILES = {
    "endf8":    os.path.join(REPO_ROOT, "data", "endf_3pt.json"),
    "fendl32c": os.path.join(REPO_ROOT, "data", "fendl_3pt.json"),
}

# Warn when |Δ%| vs hardcoded data.py values exceeds this
WARN_DELTA_PCT = 200.0


# ---------------------------------------------------------------------------
# Interpolation
# ---------------------------------------------------------------------------

def loglog_interp(energy_arr, xsec_arr, E_query):
    """
    Log-log linear interpolation of σ(E_query) from sorted arrays.
    Returns None if E_query is outside the range of energy_arr or if
    adjacent cross-section values are <= 0 (can't take log).
    """
    n = len(energy_arr)
    if n < 2:
        return None
    if E_query < energy_arr[0] or E_query > energy_arr[-1]:
        return None

    # Binary search for bracketing interval
    lo, hi = 0, n - 1
    while hi - lo > 1:
        mid = (lo + hi) // 2
        if energy_arr[mid] <= E_query:
            lo = mid
        else:
            hi = mid

    E0, E1 = energy_arr[lo], energy_arr[hi]
    S0, S1 = xsec_arr[lo],  xsec_arr[hi]

    if S0 <= 0 or S1 <= 0 or E0 <= 0 or E1 <= 0:
        # Fall back to linear interpolation if log-log is not possible
        if E1 == E0:
            return S0
        t = (E_query - E0) / (E1 - E0)
        v = S0 + t * (S1 - S0)
        return v if v >= 0 else None

    # Log-log
    lE0, lE1 = math.log(E0), math.log(E1)
    lS0, lS1 = math.log(S0), math.log(S1)
    if lE1 == lE0:
        return S0
    lE_q = math.log(E_query)
    lS_q = lS0 + (lS1 - lS0) * (lE_q - lE0) / (lE1 - lE0)
    return math.exp(lS_q)


def isotope_to_sym_A(isotope):
    """'Fe-56' → ('Fe', 56)"""
    parts = isotope.split("-")
    if len(parts) != 2:
        return None, None
    sym = parts[0]
    try:
        A = int(parts[1])
    except ValueError:
        return None, None
    return sym, A


def pointwise_path(lib_dir, sym, A, mt):
    return os.path.join(lib_dir, f"{sym}_{A}_n{mt}.json")


def load_pointwise(path):
    """Load JSON; return (energy_list, xsec_list) or (None, None) on failure."""
    try:
        with open(path) as f:
            d = json.load(f)
        return d["energy"], d["cross section"]
    except Exception:
        return None, None


# ---------------------------------------------------------------------------
# Main extraction
# ---------------------------------------------------------------------------

def extract_for_library(lib_key, lib_dir, reactions_dict):
    """
    Returns a nested dict:
      { isotope: { reaction_str: { sigma_th, sigma_2p5, sigma_14 } } }
    and a stats dict for reporting.
    """
    result = {}
    stats = {
        "found": 0,
        "missing_file": 0,
        "out_of_range": {},   # key → list of energy labels
        "parse_error": 0,
    }

    for isotope, rxn_list in sorted(reactions_dict.items()):
        sym, A = isotope_to_sym_A(isotope)
        if sym is None:
            continue

        for rxn_entry in rxn_list:
            rxn_str = rxn_entry.get("reaction")
            if not rxn_str:
                continue
            mt = MT_MAP.get(rxn_str)
            if mt is None:
                continue

            path = pointwise_path(lib_dir, sym, A, mt)

            if not os.path.isfile(path):
                stats["missing_file"] += 1
                continue

            energy_arr, xsec_arr = load_pointwise(path)
            if energy_arr is None:
                stats["parse_error"] += 1
                continue

            stats["found"] += 1

            sigma_vals = {}
            for field, E_q in ENERGY_POINTS.items():
                v = loglog_interp(energy_arr, xsec_arr, E_q)
                sigma_vals[field] = v
                if v is None:
                    key = f"{isotope} {rxn_str}"
                    stats["out_of_range"].setdefault(key, []).append(field)

            if isotope not in result:
                result[isotope] = {}
            result[isotope][rxn_str] = sigma_vals

    return result, stats


# ---------------------------------------------------------------------------
# Comparison with hardcoded data.py values
# ---------------------------------------------------------------------------

def compare_with_hardcoded(extracted, reactions_dict, lib_key):
    """Print a diff table for large discrepancies."""
    print(f"\n  Comparing {lib_key} extracted values vs hardcoded data.py cross_sections['{lib_key}' or 'endf8']:")
    diffs = []
    for isotope, rxn_map in extracted.items():
        for rxn_str, vals in rxn_map.items():
            # find hardcoded entry
            hard = None
            for r in reactions_dict.get(isotope, []):
                if r.get("reaction") == rxn_str:
                    cs = r.get("cross_sections", {})
                    hard = cs.get(lib_key) or cs.get("endf8")
                    break
            if not hard:
                continue

            for field, E_label in [("sigma_th","σ_th"), ("sigma_2p5","σ_2p5"), ("sigma_14","σ_14")]:
                new_v = vals.get(field)
                old_v = hard.get(field)
                if new_v is None or old_v is None or old_v == 0:
                    continue
                delta_pct = 100.0 * (new_v - old_v) / old_v
                if abs(delta_pct) > WARN_DELTA_PCT:
                    diffs.append((abs(delta_pct), isotope, rxn_str, E_label, old_v, new_v, delta_pct))

    if not diffs:
        print("    No discrepancies > {:.0f}%.".format(WARN_DELTA_PCT))
        return

    diffs.sort(reverse=True)
    print(f"    {'Isotope':<12} {'Rxn':<8} {'E':>6}  {'Old (data.py)':>14}  {'New (pointwise)':>16}  {'Δ%':>8}")
    print("    " + "-" * 72)
    for _, iso, rxn, elbl, old_v, new_v, dpct in diffs:
        warn = " ⚠" if abs(dpct) >= 500 else ""
        print(f"    {iso:<12} {rxn:<8} {elbl:>6}  {old_v:>14.4g}  {new_v:>16.4g}  {dpct:>+8.1f}%{warn}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    # Import REACTIONS from data.py
    sys.path.insert(0, REPO_ROOT)
    from data import REACTIONS

    os.makedirs(os.path.join(REPO_ROOT, "data"), exist_ok=True)

    for lib_key, lib_dir in LIBRARIES.items():
        print(f"\n{'='*60}")
        print(f"  Library: {lib_key}  →  {lib_dir}")
        print(f"{'='*60}")

        if not os.path.isdir(lib_dir):
            print(f"  ERROR: directory not found, skipping.")
            continue

        extracted, stats = extract_for_library(lib_key, lib_dir, REACTIONS)

        total_rxns = sum(
            1 for iso, rxns in REACTIONS.items()
            for r in rxns if r.get("reaction") in MT_MAP
        )

        print(f"  Total reaction pairs in data.py: {total_rxns}")
        print(f"  Pointwise files found:           {stats['found']}")
        print(f"  Missing pointwise files:         {stats['missing_file']}")
        print(f"  Parse errors:                    {stats['parse_error']}")

        if stats["out_of_range"]:
            print(f"  Out-of-range interpolations:")
            for k, fields in sorted(stats["out_of_range"].items()):
                print(f"    {k}: {', '.join(fields)}")
        else:
            print(f"  Out-of-range interpolations:     0")

        # Summary of extracted values
        total_extracted = sum(len(v) for v in extracted.values())
        print(f"  Reactions with extracted data:   {total_extracted}")

        # Print a few sample values
        sample_isos = ["Fe-56", "Al-27", "Cu-63", "Co-59"]
        print("\n  Sample values (barns):")
        print(f"  {'Isotope':<12} {'Rxn':<8} {'σ_th':>10}  {'σ_2p5':>10}  {'σ_14':>10}")
        print("  " + "-" * 56)
        for iso in sample_isos:
            if iso in extracted:
                for rxn_str, vals in extracted[iso].items():
                    th  = f"{vals['sigma_th']:.4g}"  if vals['sigma_th']  is not None else "N/A"
                    p25 = f"{vals['sigma_2p5']:.4g}" if vals['sigma_2p5'] is not None else "N/A"
                    f14 = f"{vals['sigma_14']:.4g}"  if vals['sigma_14']  is not None else "N/A"
                    print(f"  {iso:<12} {rxn_str:<8} {th:>10}  {p25:>10}  {f14:>10}")

        compare_with_hardcoded(extracted, REACTIONS, lib_key)

        # Write output
        out_path = OUTPUT_FILES[lib_key]
        with open(out_path, "w") as f:
            json.dump(extracted, f, indent=2)
        print(f"\n  Written: {out_path}")

    print("\nDone.")


if __name__ == "__main__":
    main()
