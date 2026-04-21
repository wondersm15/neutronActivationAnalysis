#!/usr/bin/env python3
"""
Download fully-reconstructed pointwise σ(E) JSON files.

Sources: openmc-data-storage GitHub org (ENDF/B-VIII.0, JEFF-3.3).
Format:  {"energy": [...eV...], "cross section": [...barns...], ...metadata...}

Files cover ~1e-5 eV → 20 MeV with full resonance reconstruction at 294 K.
These are used for σ(E) plots in the Cross Sections tab, NOT for activation
calculations (which use the bundled three-point values in data.py).

Usage:
    # Download ENDF/B-VIII.0 activation reactions + total XS
    python tools/download_pointwise.py --library endf8 --include-total

    # Validate JEFF-3.3 URLs before downloading
    python tools/download_pointwise.py --library jeff33 --validate

    # Download JEFF-3.3 activation reactions + total XS
    python tools/download_pointwise.py --library jeff33 --include-total

    # Download all libraries in one shot
    python tools/download_pointwise.py --library all --include-total

    # Dry run
    python tools/download_pointwise.py --library jeff33 --dry-run
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False
    print("WARNING: 'requests' not installed. Run: pip install requests")

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT  = Path(__file__).resolve().parent.parent
POINTWISE_DIR = PROJECT_ROOT / "data" / "external" / "pointwise"

# ---------------------------------------------------------------------------
# Library configuration
# ---------------------------------------------------------------------------

LIBRARY_CONFIG = {
    "endf8": {
        "label":        "ENDF/B-VIII.0",
        "base_url":     (
            "https://raw.githubusercontent.com/openmc-data-storage/"
            "ENDF-B-VIII.0-NNDC-json/main/json_files"
        ),
        "file_pattern": "{sym}_{A}_ENDFB-8.0_n_{mt}_{temp}K.json",
        "out_subdir":   "endf8",
    },
    "fendl32c": {
        "label":        "FENDL-3.2c",
        "base_url":     (
            "https://raw.githubusercontent.com/openmc-data-storage/"
            "FENDL-3.2c-json/main/FENDL-3.2c_json"
        ),
        "file_pattern": "{sym}_{A}_FENDL-3.2c_n_{mt}_{temp}K.json",
        "out_subdir":   "fendl32c",
    },
}

# ---------------------------------------------------------------------------
# Reaction type → MT number
# ---------------------------------------------------------------------------

REACTION_TO_MT = {
    "(n,γ)":   102,
    "(n,p)":   103,
    "(n,α)":   107,
    "(n,2n)":   16,
    "(n,3n)":   17,
    "(n,d)":   104,
    "(n,t)":   105,
    "(n,np)":   28,
    "(n,nα)":   22,
    "(n,total)": 1,
}

# ---------------------------------------------------------------------------
# Build download lists
# ---------------------------------------------------------------------------

def _load_reactions():
    """Import REACTIONS from data.py; exit on failure."""
    data_py = PROJECT_ROOT / "data.py"
    if not data_py.exists():
        sys.exit(f"ERROR: could not find {data_py}")
    sys.path.insert(0, str(PROJECT_ROOT))
    try:
        from data import REACTIONS
        return REACTIONS
    except ImportError as exc:
        sys.exit(f"ERROR: could not import data.py: {exc}")


def build_activation_download_list() -> list[tuple[str, str, int, int]]:
    """
    Return a deduplicated list of (label, sym, A, mt) for every activation
    reaction defined in data.py REACTIONS.
    """
    REACTIONS = _load_reactions()
    seen   = set()
    result = []

    for isotope_label, rxn_list in REACTIONS.items():
        parts = isotope_label.split("-")
        if len(parts) != 2:
            continue
        sym, a_str = parts
        try:
            A = int(a_str)
        except ValueError:
            continue

        for rxn in rxn_list:
            reaction_str = rxn.get("reaction", "")
            mt = REACTION_TO_MT.get(reaction_str)
            if mt is None:
                continue
            key = (sym, A, mt)
            if key not in seen:
                seen.add(key)
                result.append((isotope_label, sym, A, mt))

    return result


def build_total_download_list() -> list[tuple[str, str, int, int]]:
    """
    Return a deduplicated list of (label, sym, A, mt=1) for every unique
    isotope in data.py REACTIONS.  MT=1 is the total neutron cross section.
    """
    REACTIONS = _load_reactions()
    seen   = set()
    result = []

    for isotope_label in REACTIONS:
        parts = isotope_label.split("-")
        if len(parts) != 2:
            continue
        sym, a_str = parts
        try:
            A = int(a_str)
        except ValueError:
            continue
        key = (sym, A)
        if key not in seen:
            seen.add(key)
            result.append((isotope_label, sym, A, 1))

    return result


# ---------------------------------------------------------------------------
# URL / path builders
# ---------------------------------------------------------------------------

def make_url(sym: str, A: int, mt: int, lib_key: str, temp_K: int = 294) -> str:
    cfg = LIBRARY_CONFIG[lib_key]
    fname = cfg["file_pattern"].format(sym=sym, A=A, mt=mt, temp=temp_K)
    return f"{cfg['base_url']}/{fname}"


def make_dest(sym: str, A: int, mt: int, lib_key: str) -> Path:
    out_dir = POINTWISE_DIR / LIBRARY_CONFIG[lib_key]["out_subdir"]
    return out_dir / f"{sym}_{A}_n{mt}.json"


# ---------------------------------------------------------------------------
# Download
# ---------------------------------------------------------------------------

def download_one(url: str, dest: Path, dry_run: bool = False,
                 timeout: int = 30, retries: int = 2) -> bool:
    if dest.exists():
        print(f"    SKIP (exists): {dest.name}")
        return True
    if dry_run:
        print(f"    DRY-RUN: {url}")
        return True
    if not REQUESTS_OK:
        print("    ERROR: requests not installed")
        return False

    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
            if resp.status_code == 200:
                dest.parent.mkdir(parents=True, exist_ok=True)
                data = resp.json()
                if "energy" not in data or "cross section" not in data:
                    print(f"    ERROR: missing energy/cross section keys in {url}")
                    return False
                n_pts = len(data["energy"])
                with open(dest, 'w') as f:
                    json.dump(data, f)
                print(f"    OK  ({n_pts} pts): {dest.name}")
                return True
            elif resp.status_code == 404:
                print(f"    404 (not in repo): {dest.name}")
                return False
            else:
                if attempt < retries:
                    time.sleep(2 ** attempt)
        except Exception as exc:
            if attempt < retries:
                time.sleep(2 ** attempt)
            else:
                print(f"    ERROR: {exc}")
    return False


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download pointwise σ(E) JSON files.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--library", "-l", default="endf8",
        choices=list(LIBRARY_CONFIG.keys()) + ["all"],
        help="Which library to download (default: endf8). Use 'all' for every library.",
    )
    parser.add_argument(
        "--include-total", action="store_true",
        help="Also download MT=1 (total cross section) for every isotope.",
    )
    parser.add_argument("--dry-run", "-n", action="store_true")
    parser.add_argument(
        "--validate", action="store_true",
        help="HEAD-request 3 sample URLs per library to verify repo access.",
    )
    args = parser.parse_args()

    lib_keys = list(LIBRARY_CONFIG.keys()) if args.library == "all" else [args.library]

    for lib_key in lib_keys:
        cfg = LIBRARY_CONFIG[lib_key]
        print(f"\n{'='*60}")
        print(f"  Library: {cfg['label']}  ({lib_key})")
        print(f"  Output:  {POINTWISE_DIR / cfg['out_subdir']}")
        print(f"{'='*60}")

        activation_targets = build_activation_download_list()
        total_targets      = build_total_download_list() if args.include_total else []
        targets            = activation_targets + [
            t for t in total_targets
            if (t[1], t[2], t[3]) not in {(a[1], a[2], a[3]) for a in activation_targets}
        ]

        print(f"  Activation reactions: {len(activation_targets)}")
        if args.include_total:
            extra = len(targets) - len(activation_targets)
            print(f"  Total XS (MT=1) new:  {extra}")
        print(f"  Total files to check: {len(targets)}")
        print()

        if args.validate:
            if not REQUESTS_OK:
                print("requests not installed.")
                continue
            print("Validating 3 sample URLs...")
            samples = [t for t in activation_targets
                       if t[0] in ("Co-59", "Fe-56", "Ni-58")][:3]
            for label, sym, A, mt in samples:
                url = make_url(sym, A, mt, lib_key)
                try:
                    resp = requests.head(url, timeout=10, allow_redirects=True)
                    status = f"HTTP {resp.status_code}"
                except Exception as exc:
                    status = f"ERROR  {exc}"
                print(f"  {label:<12} MT={mt:<4} {status}")
                print(f"  {url}")
            continue

        ok_count = skip_count = fail_count = 0

        for label, sym, A, mt in targets:
            url  = make_url(sym, A, mt, lib_key)
            dest = make_dest(sym, A, mt, lib_key)
            rxn_label = "(n,total)" if mt == 1 else f"MT={mt}"
            print(f"  {label:<12} {rxn_label:<10}", end=" ", flush=True)

            if dest.exists():
                print(f"  SKIP (exists): {dest.name}")
                skip_count += 1
                continue

            ok = download_one(url, dest, dry_run=args.dry_run)
            if args.dry_run:
                skip_count += 1
            elif ok:
                ok_count += 1
            else:
                fail_count += 1

        print()
        print(f"  Done: {ok_count} downloaded, {skip_count} skipped, {fail_count} failed")
        if fail_count > 0:
            print("  Note: 404s are expected for reactions not present in this library.")


if __name__ == "__main__":
    main()
