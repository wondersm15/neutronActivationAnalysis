#!/usr/bin/env python3
"""
Phase 3B — ENDF nuclear data file downloader.

Downloads ENDF-6 formatted neutron sublibrary files for all isotopes present
in the activation tool's REACTIONS dictionary, from official nuclear data
library sources.

Usage:
    python tools/download_endf.py [--library LIB] [--dry-run] [--out-dir DIR]

Libraries:
    endf8   — ENDF/B-VIII.0  (IAEA NDS mirror, per-isotope ZIP)  [default]
    jeff33  — JEFF-3.3        (NEA Data Bank)
    jendl5  — JENDL-5.0       (JAEA, Japan)
    tendl23 — TENDL-2023      (PSI, Switzerland)
    eaf10   — EAF-2010        (NEA/IAEA, distributed with FISPACT-II)

Downloaded files are placed in:
    <out-dir>/<library>/n-{ZZZ}_{Sym}_{AAA}.endf   (ENDF/B, JEFF, JENDL)
    <out-dir>/<library>/{Sym}{AAA}.tendl            (TENDL)

Requirements:
    pip install requests
"""

import argparse
import io
import os
import sys
import time
import json
import zipfile
from pathlib import Path

try:
    import requests
    REQUESTS_OK = True
except ImportError:
    REQUESTS_OK = False
    print("WARNING: 'requests' not installed. Install with: pip install requests")

# ---------------------------------------------------------------------------
# Isotope registry — all 48 target isotopes in REACTIONS
# (Z, A, chemical symbol, ENDF/B-VIII.0 MAT number)
#
# MAT numbers read from IAEA NDS directory listing:
#   https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/n/
# Files are named: n_{MAT:04d}_{Z}-{Sym}-{A}.zip
# ---------------------------------------------------------------------------

ISOTOPES = [
    # (Z,  A,   Sym,   MAT )
    ( 7,  14,  "N",    725),
    ( 8,  16,  "O",    825),
    ( 8,  17,  "O",    828),
    (11,  23,  "Na",  1125),
    (13,  27,  "Al",  1325),
    (14,  28,  "Si",  1425),
    (14,  30,  "Si",  1431),
    (19,  41,  "K",   1931),
    (20,  48,  "Ca",  2049),
    (21,  45,  "Sc",  2125),
    (22,  47,  "Ti",  2228),
    (22,  48,  "Ti",  2231),
    (22,  50,  "Ti",  2237),
    (23,  51,  "V",   2328),
    (24,  50,  "Cr",  2425),
    (24,  52,  "Cr",  2431),
    (24,  53,  "Cr",  2434),
    (24,  54,  "Cr",  2437),
    (25,  55,  "Mn",  2525),
    (26,  54,  "Fe",  2625),
    (26,  56,  "Fe",  2631),
    (26,  57,  "Fe",  2634),
    (26,  58,  "Fe",  2637),
    (27,  59,  "Co",  2725),
    (28,  58,  "Ni",  2825),
    (28,  60,  "Ni",  2831),
    (28,  62,  "Ni",  2837),
    (28,  64,  "Ni",  2843),
    (29,  63,  "Cu",  2925),
    (29,  65,  "Cu",  2931),
    (30,  64,  "Zn",  3025),
    (41,  93,  "Nb",  4125),
    (42,  92,  "Mo",  4225),
    (42,  98,  "Mo",  4243),
    (42, 100,  "Mo",  4249),
    (47, 107,  "Ag",  4725),
    (47, 109,  "Ag",  4731),
    (55, 133,  "Cs",  5525),
    (56, 132,  "Ba",  5631),
    (63, 151,  "Eu",  6325),
    (63, 153,  "Eu",  6331),
    (73, 181,  "Ta",  7328),
    (74, 180,  "W",   7425),
    (74, 182,  "W",   7431),
    (74, 183,  "W",   7434),
    (74, 184,  "W",   7437),
    (74, 186,  "W",   7443),
    (83, 209,  "Bi",  8325),
]

# ---------------------------------------------------------------------------
# URL builders per library
# ---------------------------------------------------------------------------

def endf8_url(Z: int, A: int, sym: str, mat: int) -> str:
    """
    ENDF/B-VIII.0 — IAEA NDS mirror.
    Files are ZIP archives: n_{MAT:04d}_{Z}-{Sym}-{A}.zip
    Directory: https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/n/
    """
    return (f"https://www-nds.iaea.org/public/download-endf/ENDF-B-VIII.0/n/"
            f"n_{mat:04d}_{Z}-{sym}-{A}.zip")


def jeff33_url(Z: int, A: int, sym: str, mat: int = None) -> str:
    """
    JEFF-3.3 activation library — NEA Data Bank.
    Note: NEA may require registration for bulk downloads.
    Fallback: download the full tape from https://www.oecd-nea.org/dbdata/jeff/jeff33/
    and extract individual sections by MAT number.
    """
    return (f"https://www.oecd-nea.org/dbforms/data/eva/evatapes/jeff_33/neutrons/"
            f"n-{Z:03d}_{sym}_{A:03d}.jeff33")


def jendl5_url(Z: int, A: int, sym: str, mat: int = None) -> str:
    """
    JENDL-5.0 — Japan Atomic Energy Agency (JAEA).
    """
    return (f"https://wwwndc.jaea.go.jp/ftpnd/jendl/JENDL-5.0/"
            f"n-{Z:03d}_{sym}_{A:03d}.jendl5")


def tendl23_url(Z: int, A: int, sym: str, mat: int = None) -> str:
    """
    TENDL-2023 — Paul Scherrer Institut (PSI), Switzerland.
    Files are publicly accessible per-isotope.
    Format: {Sym}{A:03d}.tendl  (e.g. Co059.tendl)
    """
    return (f"https://tendl.web.psi.ch/tendl_2023/neutron_file/"
            f"{sym}/{sym}{A:03d}.tendl")


def eaf10_url(Z: int, A: int, sym: str, mat: int = None) -> str:
    """
    EAF-2010 — European Activation File.
    Distributed as part of FISPACT-II data package (NEA/IAEA).
    Download the full FISPACT-II data package from:
      https://www.oecd-nea.org/tools/abstract/detail/nea-1609
    and place the 'xs' directory contents in data/external/eaf10/.
    """
    return f"MANUAL_DOWNLOAD_REQUIRED:fispact2/eaf2010/{sym.lower()}{A}"


LIBRARY_CONFIG = {
    "endf8": {
        "name":        "ENDF/B-VIII.0",
        "url_fn":      endf8_url,
        "uses_zip":    True,    # IAEA serves per-isotope ZIPs; extract ENDF file inside
        "ext":         ".endf",
        "filename_fn": lambda Z, A, sym, mat=None: f"n-{Z:03d}_{sym}_{A:03d}.endf",
        "notes":       "IAEA NDS mirror — publicly available, no registration required.",
    },
    "jeff33": {
        "name":        "JEFF-3.3",
        "url_fn":      jeff33_url,
        "uses_zip":    False,
        "ext":         ".jeff33",
        "filename_fn": lambda Z, A, sym, mat=None: f"n-{Z:03d}_{sym}_{A:03d}.jeff33",
        "notes":       "NEA Data Bank — may require registration at oecd-nea.org.",
    },
    "jendl5": {
        "name":        "JENDL-5.0",
        "url_fn":      jendl5_url,
        "uses_zip":    False,
        "ext":         ".jendl5",
        "filename_fn": lambda Z, A, sym, mat=None: f"n-{Z:03d}_{sym}_{A:03d}.jendl5",
        "notes":       "Publicly available from wwwndc.jaea.go.jp.",
    },
    "tendl23": {
        "name":        "TENDL-2023",
        "url_fn":      tendl23_url,
        "uses_zip":    False,
        "ext":         ".tendl",
        "filename_fn": lambda Z, A, sym, mat=None: f"{sym}{A:03d}.tendl",
        "notes":       "Publicly available from tendl.web.psi.ch.",
    },
    "eaf10": {
        "name":        "EAF-2010",
        "url_fn":      eaf10_url,
        "uses_zip":    False,
        "ext":         ".eaf",
        "filename_fn": lambda Z, A, sym, mat=None: f"{sym.lower()}{A}.eaf",
        "notes":       (
            "EAF-2010 requires the FISPACT-II data package from NEA "
            "(registration required). See tools/README.md."
        ),
    },
}

# ---------------------------------------------------------------------------
# Download logic
# ---------------------------------------------------------------------------

DEFAULT_DATA_DIR = os.path.join(
    os.environ.get("ACTIVATION_DATA_DIR",
                   os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "external"))
)


def _fetch_raw(url: str, timeout: int = 120, retries: int = 2) -> bytes | None:
    """Fetch url, return raw bytes or None on failure."""
    for attempt in range(retries + 1):
        try:
            resp = requests.get(url, timeout=timeout, stream=True)
            if resp.status_code == 200:
                return resp.content
            elif resp.status_code == 404:
                return None
            else:
                if attempt < retries:
                    time.sleep(2 ** attempt)
        except requests.exceptions.RequestException:
            if attempt < retries:
                time.sleep(2 ** attempt)
    return None


def download_file(url: str, dest: Path, dry_run: bool = False,
                  uses_zip: bool = False, timeout: int = 120) -> bool:
    """
    Download url to dest.  If uses_zip=True, url is a ZIP archive; extract the
    first ENDF-6 file inside it and write to dest.  Returns True on success.
    """
    if dest.exists():
        print(f"    SKIP (exists): {dest.name}")
        return True

    if dry_run:
        print(f"    DRY-RUN: {url}")
        return True

    if url.startswith("MANUAL_DOWNLOAD_REQUIRED"):
        print(f"    MANUAL: {url}")
        return False

    if not REQUESTS_OK:
        print("    ERROR: requests not installed.")
        return False

    data = _fetch_raw(url, timeout=timeout)
    if data is None:
        print(f"    404 NOT FOUND: {url}")
        return False

    dest.parent.mkdir(parents=True, exist_ok=True)

    if uses_zip:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as zf:
                # Take the first file in the ZIP (should be the only ENDF-6 file)
                names = zf.namelist()
                if not names:
                    print(f"    ERROR: ZIP is empty: {url}")
                    return False
                endf_content = zf.read(names[0])
            with open(dest, 'wb') as f:
                f.write(endf_content)
            size_kb = len(endf_content) // 1024
            print(f"    OK  ({size_kb} KB, unzipped from {len(data)//1024} KB): {dest.name}")
        except zipfile.BadZipFile as exc:
            print(f"    ERROR: bad ZIP from {url}: {exc}")
            return False
    else:
        with open(dest, 'wb') as f:
            f.write(data)
        size_kb = len(data) // 1024
        print(f"    OK  ({size_kb} KB): {dest.name}")

    return True


def download_library(library: str, out_dir: Path, dry_run: bool = False) -> dict:
    """Download all ENDF files for the given library. Returns a status report."""
    cfg = LIBRARY_CONFIG[library]
    lib_dir = out_dir / library
    lib_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"Library: {cfg['name']}")
    print(f"Output:  {lib_dir}")
    print(f"Notes:   {cfg['notes']}")
    print(f"{'='*60}")

    results = {"library": library, "success": [], "failed": [], "skipped": []}

    for Z, A, sym, mat in ISOTOPES:
        url      = cfg["url_fn"](Z, A, sym, mat)
        filename = cfg["filename_fn"](Z, A, sym, mat)
        dest     = lib_dir / filename
        isotope  = f"{sym}-{A}"

        print(f"  {isotope:<12}", end=' ', flush=True)
        ok = download_file(url, dest, dry_run=dry_run, uses_zip=cfg["uses_zip"])

        if dry_run:
            results["skipped"].append(isotope)
        elif ok and dest.exists():
            results["success"].append(isotope)
        else:
            results["failed"].append(isotope)

    print(f"\n  Summary: {len(results['success'])} OK, "
          f"{len(results['failed'])} FAILED, "
          f"{len(results['skipped'])} SKIPPED")

    manifest_path = lib_dir / "manifest.json"
    with open(manifest_path, 'w') as f:
        json.dump({
            "library":      library,
            "library_name": cfg["name"],
            "downloaded":   results["success"],
            "failed":       results["failed"],
        }, f, indent=2)

    return results


# ---------------------------------------------------------------------------
# URL validation helper (HEAD requests, no download)
# ---------------------------------------------------------------------------

def validate_urls(library: str) -> None:
    """Send HEAD requests to confirm URL patterns are correct."""
    if not REQUESTS_OK:
        print("requests not installed.")
        return

    cfg = LIBRARY_CONFIG[library]
    print(f"\nValidating URLs for {cfg['name']}...")

    # Test with Co-59, Fe-56, Al-27
    test_cases = [(27, 59, "Co", 2725), (26, 56, "Fe", 2631), (13, 27, "Al", 1325)]
    for Z, A, sym, mat in test_cases:
        url = cfg["url_fn"](Z, A, sym, mat)
        if url.startswith("MANUAL"):
            print(f"  {sym}-{A}: MANUAL DOWNLOAD")
            continue
        try:
            resp = requests.head(url, timeout=10, allow_redirects=True)
            print(f"  {sym}-{A}: HTTP {resp.status_code}  {url}")
        except Exception as exc:
            print(f"  {sym}-{A}: ERROR  {exc}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Download ENDF-6 nuclear data files for all activation tool isotopes.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Download ENDF/B-VIII.0 (default)
  python tools/download_endf.py

  # Dry run — show what would be downloaded
  python tools/download_endf.py --dry-run

  # Validate URL patterns first
  python tools/download_endf.py --validate --library endf8

  # Download TENDL-2023
  python tools/download_endf.py --library tendl23

  # Download multiple libraries
  python tools/download_endf.py --library endf8 tendl23 jendl5
""")

    parser.add_argument(
        "--library", "-l", nargs="+",
        choices=list(LIBRARY_CONFIG.keys()),
        default=["endf8"],
        help="Which library/libraries to download (default: endf8).",
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true",
        help="Print what would be downloaded without downloading.",
    )
    parser.add_argument(
        "--out-dir", default=None,
        help=f"Root output directory (default: {DEFAULT_DATA_DIR}).",
    )
    parser.add_argument(
        "--validate", action="store_true",
        help="HEAD-request URL patterns to confirm they work; no download.",
    )
    args = parser.parse_args()

    out_dir = Path(args.out_dir) if args.out_dir else Path(DEFAULT_DATA_DIR)

    if args.validate:
        for lib in args.library:
            validate_urls(lib)
        return

    all_results = []
    for lib in args.library:
        results = download_library(lib, out_dir, dry_run=args.dry_run)
        all_results.append(results)

    print("\n" + "="*60)
    print("DOWNLOAD SUMMARY")
    print("="*60)
    for r in all_results:
        cfg = LIBRARY_CONFIG[r["library"]]
        total = len(r["success"]) + len(r["failed"])
        print(f"  {cfg['name']:<25}  {len(r['success']):>2}/{total:>2} files OK")

    any_failed = any(r["failed"] for r in all_results)
    if any_failed:
        print("\nSome downloads failed. Check the URLs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
