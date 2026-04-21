#!/usr/bin/env python3
"""
Phase 3B — Patch data.py cross_sections from preprocessed JSON.

Reads the extracted cross-section JSON produced by preprocess.py and
updates the cross_sections dicts in data.py.

For each reaction entry in data.py:
  - sigma_2p5: set from extracted value (was None placeholder)
  - sigma_th / sigma_14: updated only if --update-existing is specified
    (default: leave existing values alone — they've been manually validated)

Produces a diff report of every value changed.

Usage:
    python tools/update_data.py [--library LIB] [--json FILE] [--dry-run]
    python tools/update_data.py --json data/external/endf8_extracted.json
    python tools/update_data.py --library jeff33 --add-library
"""

import argparse
import ast
import json
import os
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PY = PROJECT_ROOT / "data.py"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args():
    parser = argparse.ArgumentParser(
        description="Update data.py cross_sections from preprocessed ENDF JSON.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Populate sigma_2p5 in endf8 library from extracted JSON
  python tools/update_data.py --json data/external/endf8_extracted.json

  # Dry run — show changes without writing
  python tools/update_data.py --json data/external/endf8_extracted.json --dry-run

  # Add a new library (jeff33) to every reaction's cross_sections dict
  python tools/update_data.py --json data/external/jeff33_extracted.json --add-library

  # Update all values including sigma_th/sigma_14 (replaces existing)
  python tools/update_data.py --json data/external/endf8_extracted.json --update-existing
""")

    parser.add_argument(
        "--json", required=True,
        help="Path to the extracted JSON produced by preprocess.py.",
    )
    parser.add_argument(
        "--dry-run", "-n", action="store_true",
        help="Print what would change without writing data.py.",
    )
    parser.add_argument(
        "--add-library", action="store_true",
        help=(
            "Add a new library key to every cross_sections dict.  "
            "Use when populating jeff33/jendl5/tendl23/eaf10 for the first time."
        ),
    )
    parser.add_argument(
        "--update-existing", action="store_true",
        help=(
            "Also overwrite existing sigma_th and sigma_14 values.  "
            "Default: only fill None placeholders (sigma_2p5) and new libraries."
        ),
    )
    parser.add_argument(
        "--backup", default=None,
        help=(
            "Path for backup of original data.py before patching.  "
            "Default: data.py.bak-<library>."
        ),
    )
    return parser.parse_args()


# ---------------------------------------------------------------------------
# Load extracted JSON
# ---------------------------------------------------------------------------

def load_extracted(json_path: str) -> dict:
    with open(json_path) as f:
        data = json.load(f)
    library = data.get("library")
    if not library:
        sys.exit("ERROR: extracted JSON has no 'library' field.")
    return data


# ---------------------------------------------------------------------------
# Source-code level patching strategy
# ---------------------------------------------------------------------------
#
# Rather than executing data.py and mutating Python objects (fragile for such
# a large file), we do string-level patching of the source.
#
# The cross_sections block in data.py looks like:
#
#     "cross_sections": {
#         "endf8": {"sigma_th": 37.2, "sigma_2p5": None, "sigma_14": 0.0027},
#     },
#
# For the endf8 library we only need to replace `"sigma_2p5": None` with
# `"sigma_2p5": VALUE` within the matching reaction context.
#
# For adding a new library we insert a new line:
#     "jeff33": {"sigma_th": V, "sigma_2p5": V, "sigma_14": V},
#
# Strategy: parse the source character-by-character to find REACTIONS dict,
# then patch individual "sigma_2p5": None occurrences with context matching.
#
# To match context (which reaction we're in), we walk the REACTIONS source
# in the same order as the REACTIONS dict itself, so positions correspond 1:1.
# ---------------------------------------------------------------------------

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


def format_sigma(val: float | None) -> str:
    """Format a cross-section value for source code insertion."""
    if val is None:
        return "None"
    if val == 0.0:
        return "0.0"
    # Use 4 significant figures
    if abs(val) >= 0.01 and abs(val) < 10000:
        return f"{val:.4g}"
    return f"{val:.4g}"


def build_endf8_line(sigma_th, sigma_2p5, sigma_14, indent: str) -> str:
    """Build the 'endf8': {...} line."""
    th  = format_sigma(sigma_th)
    p25 = format_sigma(sigma_2p5)
    s14 = format_sigma(sigma_14)
    return f'{indent}    "endf8": {{"sigma_th": {th}, "sigma_2p5": {p25}, "sigma_14": {s14}}},'


def build_library_line(library: str, sigma_th, sigma_2p5, sigma_14, indent: str) -> str:
    """Build a '<library>': {...} line for a new library."""
    th  = format_sigma(sigma_th)
    p25 = format_sigma(sigma_2p5)
    s14 = format_sigma(sigma_14)
    return f'{indent}    "{library}": {{"sigma_th": {th}, "sigma_2p5": {p25}, "sigma_14": {s14}}},'


# ---------------------------------------------------------------------------
# Patch: replace full endf8 line (sigma_th + sigma_2p5 + sigma_14)
# ---------------------------------------------------------------------------

def patch_endf8_full(source: str, extracted: dict) -> tuple[str, list]:
    """
    Replace the entire "endf8": {...} line for every matched reaction.

    Rules per field:
      sigma_2p5 — always set from extracted (was None placeholder)
      sigma_14  — always replace with extracted ENDF/B-VIII.0 value
      sigma_th  — replace only if extracted value is non-zero; if extracted
                  is 0.0 it means MF=3 does not cover thermal energies (the
                  cross-section lives in MF=2 resonance parameters), so the
                  existing literature value is preserved.

    Returns (patched_source, changes).
    """
    iso_data = extracted.get("isotopes", {})

    lookup: dict[tuple[str, str], dict] = {}
    for isotope, iso_info in iso_data.items():
        for reaction_str, rxn_info in iso_info.get("reactions", {}).items():
            lookup[(isotope, reaction_str)] = rxn_info

    changes = []
    lines   = source.split('\n')
    out_lines = []

    in_reactions     = False
    current_isotope  = None
    current_reaction = None
    current_product  = None

    REACTIONS_START_RE = re.compile(r'^REACTIONS\s*=\s*\{')
    ISOTOPE_KEY_RE     = re.compile(r'^\s+"([A-Z][a-z]?\-\d+)":\s*\[')
    REACTION_KEY_RE    = re.compile(r'\s+"reaction":\s+"([^"]+)"')
    PRODUCT_KEY_RE     = re.compile(r'\s+"product":\s+"([^"]+)"')
    ENDF8_LINE_RE      = re.compile(
        r'^(\s*)"endf8":\s+\{"sigma_th":\s*([^,]+),\s*"sigma_2p5":\s*([^,]+),\s*"sigma_14":\s*([^}]+)\}(,?)'
    )
    REACTIONS_END_RE   = re.compile(r'^MATERIALS\s*=\s*\{')

    for lno, line in enumerate(lines):
        if REACTIONS_START_RE.match(line.strip()):
            in_reactions = True
        if REACTIONS_END_RE.match(line.strip()):
            in_reactions = False

        if in_reactions:
            m_iso = ISOTOPE_KEY_RE.match(line)
            if m_iso:
                current_isotope  = m_iso.group(1)
                current_reaction = None
                current_product  = None

            m_rxn = REACTION_KEY_RE.search(line)
            if m_rxn:
                current_reaction = m_rxn.group(1)

            m_prod = PRODUCT_KEY_RE.search(line)
            if m_prod:
                current_product = m_prod.group(1)

            m_e8 = ENDF8_LINE_RE.match(line)
            if m_e8 and current_isotope and current_reaction:
                indent      = m_e8.group(1)
                old_th_str  = m_e8.group(2).strip()
                old_2p5_str = m_e8.group(3).strip()
                old_14_str  = m_e8.group(4).strip()
                trailing    = m_e8.group(5)  # comma or empty

                rxn_info = lookup.get((current_isotope, current_reaction), {})
                ext_th  = rxn_info.get("sigma_th")
                ext_2p5 = rxn_info.get("sigma_2p5")
                ext_14  = rxn_info.get("sigma_14")

                # Decode existing values from source text
                def _parse_existing(s):
                    s = s.strip()
                    if s == "None":
                        return None
                    try:
                        return float(s)
                    except ValueError:
                        return None

                old_th  = _parse_existing(old_th_str)
                old_2p5 = _parse_existing(old_2p5_str)
                old_14  = _parse_existing(old_14_str)

                # Apply rules
                # sigma_th: use extracted only if non-zero and non-None
                new_th = old_th
                if ext_th is not None and ext_th != 0.0:
                    new_th = ext_th

                # sigma_2p5: always use extracted (was None placeholder)
                new_2p5 = ext_2p5 if ext_2p5 is not None else old_2p5

                # sigma_14: always use extracted if available
                new_14 = ext_14 if ext_14 is not None else old_14

                new_line = (
                    f'{indent}"endf8": {{"sigma_th": {format_sigma(new_th)}, '
                    f'"sigma_2p5": {format_sigma(new_2p5)}, '
                    f'"sigma_14": {format_sigma(new_14)}}}{trailing}'
                )

                # Record actual changes
                for field, old_v, new_v in [
                    ("sigma_th",  old_th,  new_th),
                    ("sigma_2p5", old_2p5, new_2p5),
                    ("sigma_14",  old_14,  new_14),
                ]:
                    if old_v != new_v:
                        changes.append({
                            "isotope":  current_isotope,
                            "reaction": current_reaction,
                            "product":  current_product,
                            "field":    field,
                            "library":  "endf8",
                            "old":      old_v,
                            "new":      new_v,
                            "line":     lno + 1,
                        })

                out_lines.append(new_line)
                continue

        out_lines.append(line)

    return '\n'.join(out_lines), changes


# ---------------------------------------------------------------------------
# Patch: populate sigma_2p5 in endf8 (the normal case)
# ---------------------------------------------------------------------------

def patch_sigma_2p5(source: str, extracted: dict) -> tuple[str, list]:
    """
    Replace `"sigma_2p5": None` with actual values in every endf8 cross_sections block.

    We match based on the surrounding product/reaction context to ensure
    we update the right entry even when multiple reactions produce the same
    energy point value.

    Returns (patched_source, changes) where changes is a list of dicts.
    """
    library   = extracted["library"]
    iso_data  = extracted["isotopes"]

    # Build a flat lookup: (isotope, reaction_str) -> sigma_2p5
    lookup: dict[tuple[str, str], float | None] = {}
    for isotope, iso_info in iso_data.items():
        for reaction_str, rxn_info in iso_info.get("reactions", {}).items():
            lookup[(isotope, reaction_str)] = rxn_info.get("sigma_2p5")

    # We walk through REACTIONS source in file order.
    # Use a regex to find each cross_sections block with its surrounding context.
    #
    # Pattern: find "product": "PRODUCT" ... "sigma_2p5": None within ~400 chars
    # Then match to (isotope, reaction) from REACTIONS dict.
    #
    # Simpler approach: scan for cross_sections blocks and use surrounding
    # product/reaction lines to identify the entry.

    changes = []
    lines = source.split('\n')
    out_lines = []

    # State machine: track isotope and reaction as we scan
    current_isotope  = None
    current_reaction = None
    current_product  = None
    in_reactions     = False

    REACTIONS_START_RE = re.compile(r'^REACTIONS\s*=\s*\{')
    ISOTOPE_KEY_RE     = re.compile(r'^\s+"([A-Z][a-z]?\-\d+)":\s*\[')
    REACTION_KEY_RE    = re.compile(r'\s+"reaction":\s+"([^"]+)"')
    PRODUCT_KEY_RE     = re.compile(r'\s+"product":\s+"([^"]+)"')
    SIGMA_2P5_RE       = re.compile(
        r'("sigma_2p5":\s*)None(\s*(?:,|}))' )
    REACTIONS_END_RE   = re.compile(r'^MATERIALS\s*=\s*\{')

    for lno, line in enumerate(lines):
        if REACTIONS_START_RE.match(line.strip()):
            in_reactions = True
        if REACTIONS_END_RE.match(line.strip()):
            in_reactions = False

        if in_reactions:
            m_iso = ISOTOPE_KEY_RE.match(line)
            if m_iso:
                current_isotope = m_iso.group(1)
                current_reaction = None
                current_product  = None

            m_rxn = REACTION_KEY_RE.search(line)
            if m_rxn:
                current_reaction = m_rxn.group(1)

            m_prod = PRODUCT_KEY_RE.search(line)
            if m_prod:
                current_product = m_prod.group(1)

            # Patch sigma_2p5: None
            m_2p5 = SIGMA_2P5_RE.search(line)
            if m_2p5 and current_isotope and current_reaction:
                new_val = lookup.get((current_isotope, current_reaction))
                if new_val is not None:
                    repl = f'{m_2p5.group(1)}{format_sigma(new_val)}{m_2p5.group(2)}'
                    new_line = line[:m_2p5.start()] + repl + line[m_2p5.end():]
                    changes.append({
                        "isotope":   current_isotope,
                        "reaction":  current_reaction,
                        "product":   current_product,
                        "field":     "sigma_2p5",
                        "library":   library,
                        "old":       None,
                        "new":       new_val,
                        "line":      lno + 1,
                    })
                    out_lines.append(new_line)
                    continue

        out_lines.append(line)

    return '\n'.join(out_lines), changes


# ---------------------------------------------------------------------------
# Patch: add a new library to every cross_sections block
# ---------------------------------------------------------------------------

def patch_add_library(source: str, extracted: dict) -> tuple[str, list]:
    """
    Insert a new '<library>': {...} line inside every cross_sections block.
    Assumes the block currently has only the 'endf8' line.
    """
    library  = extracted["library"]
    iso_data = extracted["isotopes"]

    lookup: dict[tuple[str, str], dict] = {}
    for isotope, iso_info in iso_data.items():
        for reaction_str, rxn_info in iso_info.get("reactions", {}).items():
            lookup[(isotope, reaction_str)] = rxn_info

    changes = []
    lines = source.split('\n')
    out_lines = []

    in_reactions     = False
    current_isotope  = None
    current_reaction = None
    current_product  = None

    REACTIONS_START_RE = re.compile(r'^REACTIONS\s*=\s*\{')
    ISOTOPE_KEY_RE     = re.compile(r'^\s+"([A-Z][a-z]?\-\d+)":\s*\[')
    REACTION_KEY_RE    = re.compile(r'\s+"reaction":\s+"([^"]+)"')
    PRODUCT_KEY_RE     = re.compile(r'\s+"product":\s+"([^"]+)"')
    ENDF8_LINE_RE      = re.compile(
        r'^(\s+)"endf8":\s+\{[^}]+\},?\s*$'
    )
    REACTIONS_END_RE   = re.compile(r'^MATERIALS\s*=\s*\{')

    for lno, line in enumerate(lines):
        if REACTIONS_START_RE.match(line.strip()):
            in_reactions = True
        if REACTIONS_END_RE.match(line.strip()):
            in_reactions = False

        if in_reactions:
            m_iso = ISOTOPE_KEY_RE.match(line)
            if m_iso:
                current_isotope = m_iso.group(1)
                current_reaction = None
                current_product  = None

            m_rxn = REACTION_KEY_RE.search(line)
            if m_rxn:
                current_reaction = m_rxn.group(1)

            m_prod = PRODUCT_KEY_RE.search(line)
            if m_prod:
                current_product = m_prod.group(1)

            m_e8 = ENDF8_LINE_RE.match(line)
            if m_e8 and current_isotope and current_reaction:
                indent = m_e8.group(1)
                rxn_info = lookup.get((current_isotope, current_reaction), {})
                new_lib_line = build_library_line(
                    library,
                    rxn_info.get("sigma_th"),
                    rxn_info.get("sigma_2p5"),
                    rxn_info.get("sigma_14"),
                    indent,
                )
                out_lines.append(line)
                out_lines.append(new_lib_line)
                changes.append({
                    "isotope":   current_isotope,
                    "reaction":  current_reaction,
                    "product":   current_product,
                    "field":     f"new_library:{library}",
                    "library":   library,
                    "old":       None,
                    "new":       rxn_info,
                    "line":      lno + 1,
                })
                continue

        out_lines.append(line)

    return '\n'.join(out_lines), changes


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    args = parse_args()

    extracted = load_extracted(args.json)
    library   = extracted["library"]

    print(f"Library:       {library}")
    print(f"Extracted JSON: {args.json}")
    print(f"Target file:    {DATA_PY}")
    print(f"Mode:           {'add new library' if args.add_library else 'patch sigma_2p5'}")
    print()

    source = DATA_PY.read_text()

    if args.add_library:
        patched, changes = patch_add_library(source, extracted)
    elif args.update_existing:
        # Full endf8 line replacement: sigma_2p5 + sigma_14, sigma_th where MF3 covers thermal
        patched, changes = patch_endf8_full(source, extracted)
    else:
        patched, changes = patch_sigma_2p5(source, extracted)

    # Report changes
    print(f"Changes ({len(changes)}):")
    for c in changes[:50]:
        old_s = repr(c['old']) if c['old'] is not None else "None"
        new_s = repr(c['new']) if isinstance(c['new'], (int, float)) else str(c['new'])
        print(f"  line {c['line']:4d}  {c['isotope']:<12} {c['reaction']:<8}  "
              f"{c['field']}: {old_s} → {new_s}")
    if len(changes) > 50:
        print(f"  ... and {len(changes)-50} more")

    if not changes:
        print("  (nothing to change)")
        return

    # Syntax check patched source
    print("\nRunning syntax check...")
    try:
        ast.parse(patched)
        print("  Syntax OK.")
    except SyntaxError as exc:
        print(f"  SYNTAX ERROR at line {exc.lineno}: {exc.msg}")
        ctx = patched.split('\n')
        start = max(0, exc.lineno - 3)
        end   = min(len(ctx), exc.lineno + 3)
        for i, ln in enumerate(ctx[start:end], start=start+1):
            marker = " >>>" if i == exc.lineno else "    "
            print(f"  {marker} {i:5d}: {ln}")
        print("Aborting — data.py NOT modified.")
        sys.exit(1)

    if args.dry_run:
        print("\nDRY RUN — data.py not modified.")
        return

    # Backup
    backup_path = args.backup or str(DATA_PY) + f".bak-{library}"
    print(f"\nBacking up data.py → {backup_path}")
    Path(backup_path).write_text(source)

    # Write
    DATA_PY.write_text(patched)
    print(f"Wrote patched data.py ({len(changes)} changes).")

    # Write change log
    log_path = DATA_PY.parent / f"data_update_{library}.json"
    with open(log_path, 'w') as f:
        json.dump({"library": library, "changes": changes}, f, indent=2)
    print(f"Change log: {log_path}")


if __name__ == "__main__":
    main()
