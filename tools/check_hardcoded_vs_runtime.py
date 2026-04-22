"""
check_hardcoded_vs_runtime.py
------------------------------
Sweep tool: compares the hardcoded ``cross_sections`` dicts in
``data.REACTIONS`` (the human-readable fallback) against the pointwise
runtime values in ``data/endf_3pt.json`` and ``data/fendl_3pt.json``.

Reports:
  * Every (isotope, reaction, library, energy) where |hardcoded − runtime| / runtime
    exceeds a configurable threshold (default 1%).
  * Hardcoded entries with no corresponding runtime value (pointwise not
    available for that reaction/energy).
  * Runtime entries with no hardcoded fallback (new pointwise coverage
    that isn't documented in data.py).

Usage:
    python tools/check_hardcoded_vs_runtime.py [--threshold 0.01] [--json report.json]

Exit status is always 0 — this is a reporting tool, not a gate. For a gate
that fails a test run on drift, see ``tests/test_cross_sections.py``.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import sys
from typing import Any, Iterable

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PY = os.path.join(REPO_ROOT, "data.py")
POINTWISE_FILES = {
    "endf8":    os.path.join(REPO_ROOT, "data", "endf_3pt.json"),
    "fendl32c": os.path.join(REPO_ROOT, "data", "fendl_3pt.json"),
}

ENERGY_KEYS = ("sigma_th", "sigma_2p5", "sigma_14")


# ---------------------------------------------------------------------------
# Parse hardcoded REACTIONS from data.py at the source level.
#
# We parse via AST rather than importing ``data`` because importing triggers
# ``_load_extracted_3pt()``, which clobbers the hardcoded values with the
# pointwise runtime values — exactly the thing we're trying to compare
# against. AST parsing gives us the on-disk literal as written by a human.
# ---------------------------------------------------------------------------

def _literal_or_none(node: ast.AST) -> Any:
    """Return Python value for an ast.Constant, or None for anything else
    (including complex expressions, names, unary ops, etc). We only care
    about numeric literals and ``None`` for cross-section values."""
    if isinstance(node, ast.Constant):
        return node.value
    # Support -1.234 (UnaryOp over Constant) just in case
    if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
        if isinstance(node.op, ast.USub) and isinstance(node.operand.value, (int, float)):
            return -node.operand.value
    return None


def _parse_cross_sections_dict(node: ast.Dict) -> dict[str, dict[str, Any]]:
    """Parse a `cross_sections` dict: {library: {sigma_*: value}}."""
    out: dict[str, dict[str, Any]] = {}
    for k, v in zip(node.keys, node.values):
        if not isinstance(k, ast.Constant) or not isinstance(k.value, str):
            continue
        lib = k.value
        if not isinstance(v, ast.Dict):
            continue
        lib_dict: dict[str, Any] = {}
        for kk, vv in zip(v.keys, v.values):
            if not isinstance(kk, ast.Constant) or not isinstance(kk.value, str):
                continue
            lib_dict[kk.value] = _literal_or_none(vv)
        out[lib] = lib_dict
    return out


def parse_hardcoded_reactions(src_path: str) -> dict[str, list[dict[str, Any]]]:
    """Return {isotope: [{reaction, product, cross_sections}]} from source AST."""
    with open(src_path) as f:
        tree = ast.parse(f.read())

    reactions: dict[str, list[dict[str, Any]]] | None = None
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "REACTIONS" not in targets or not isinstance(node.value, ast.Dict):
            continue
        reactions = {}
        for iso_key, iso_val in zip(node.value.keys, node.value.values):
            if not isinstance(iso_key, ast.Constant) or not isinstance(iso_key.value, str):
                continue
            if not isinstance(iso_val, ast.List):
                continue
            rxn_list = []
            for rxn_node in iso_val.elts:
                if not isinstance(rxn_node, ast.Dict):
                    continue
                rxn_entry: dict[str, Any] = {}
                for k, v in zip(rxn_node.keys, rxn_node.values):
                    if not isinstance(k, ast.Constant) or not isinstance(k.value, str):
                        continue
                    if k.value == "cross_sections" and isinstance(v, ast.Dict):
                        rxn_entry["cross_sections"] = _parse_cross_sections_dict(v)
                    else:
                        rxn_entry[k.value] = _literal_or_none(v)
                if "reaction" in rxn_entry:
                    rxn_list.append(rxn_entry)
            reactions[iso_key.value] = rxn_list
        break

    if reactions is None:
        raise RuntimeError("Could not find REACTIONS dict in data.py")
    return reactions


# ---------------------------------------------------------------------------
# Load pointwise runtime values
# ---------------------------------------------------------------------------

def load_pointwise(path: str) -> dict[str, dict[str, dict[str, float | None]]]:
    with open(path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def pct_diff(hard: float, run: float) -> float:
    """|(hard - run) / run| as a fraction. Undefined if run == 0."""
    if run == 0:
        return float("inf")
    return abs(hard - run) / abs(run)


def compare(
    hardcoded: dict[str, list[dict[str, Any]]],
    pointwise_by_lib: dict[str, dict[str, dict[str, dict[str, float | None]]]],
    threshold: float,
) -> dict[str, list[dict[str, Any]]]:
    """Return categorized report."""
    report: dict[str, list[dict[str, Any]]] = {
        "divergences": [],
        "missing_runtime": [],
        "missing_hardcoded": [],
    }

    # Track every (iso, rxn, lib, key) we've touched via hardcoded
    seen_hardcoded: set[tuple[str, str, str, str]] = set()

    for iso, rxn_list in hardcoded.items():
        for rxn in rxn_list:
            rxn_name = rxn.get("reaction")
            product = rxn.get("product")
            xsec = rxn.get("cross_sections", {})
            for lib, lib_values in xsec.items():
                pw_iso = pointwise_by_lib.get(lib, {}).get(iso, {})
                pw_rxn = pw_iso.get(rxn_name, {}) if isinstance(pw_iso, dict) else {}
                for key in ENERGY_KEYS:
                    hard_val = lib_values.get(key)
                    seen_hardcoded.add((iso, rxn_name, lib, key))
                    if hard_val is None:
                        # Hardcoded deliberately null — skip (means "no thermal rate", etc.)
                        continue
                    run_val = pw_rxn.get(key) if isinstance(pw_rxn, dict) else None
                    if run_val is None:
                        report["missing_runtime"].append({
                            "isotope": iso, "reaction": rxn_name, "product": product,
                            "library": lib, "energy": key, "hardcoded": hard_val,
                        })
                        continue
                    d = pct_diff(hard_val, run_val)
                    if d > threshold:
                        report["divergences"].append({
                            "isotope": iso, "reaction": rxn_name, "product": product,
                            "library": lib, "energy": key,
                            "hardcoded": hard_val, "runtime": run_val,
                            "diff_pct": d * 100.0,
                        })

    # Runtime entries with no hardcoded fallback
    for lib, pw_all in pointwise_by_lib.items():
        for iso, rxn_map in pw_all.items():
            if not isinstance(rxn_map, dict):
                continue
            for rxn_name, energies in rxn_map.items():
                if not isinstance(energies, dict):
                    continue
                for key in ENERGY_KEYS:
                    run_val = energies.get(key)
                    if run_val is None:
                        continue
                    if (iso, rxn_name, lib, key) not in seen_hardcoded:
                        report["missing_hardcoded"].append({
                            "isotope": iso, "reaction": rxn_name,
                            "library": lib, "energy": key, "runtime": run_val,
                        })

    # Stable sort — largest divergence first
    report["divergences"].sort(key=lambda r: r["diff_pct"], reverse=True)
    report["missing_runtime"].sort(key=lambda r: (r["isotope"], r["reaction"], r["library"], r["energy"]))
    report["missing_hardcoded"].sort(key=lambda r: (r["isotope"], r["reaction"], r["library"], r["energy"]))
    return report


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------

def print_report(report: dict[str, list[dict[str, Any]]], threshold: float) -> None:
    divs = report["divergences"]
    mr = report["missing_runtime"]
    mh = report["missing_hardcoded"]

    print(f"\nDivergences > {threshold*100:.1f}%  ({len(divs)}):")
    if not divs:
        print("  (none)")
    else:
        print(f"  {'Isotope':<10} {'Reaction':<8} {'Lib':<10} {'Energy':<10} "
              f"{'Hardcoded':>14} {'Runtime':>14} {'Δ %':>10}")
        for d in divs:
            print(f"  {d['isotope']:<10} {d['reaction']:<8} {d['library']:<10} "
                  f"{d['energy']:<10} {d['hardcoded']:>14.4g} "
                  f"{d['runtime']:>14.4g} {d['diff_pct']:>9.1f}%")

    print(f"\nHardcoded entries with no runtime coverage  ({len(mr)}):")
    if not mr:
        print("  (none)")
    else:
        # Roll up by (isotope, reaction, library) for readability
        seen = set()
        for e in mr:
            key = (e['isotope'], e['reaction'], e['library'])
            if key in seen:
                continue
            seen.add(key)
            energies = [x['energy'] for x in mr if (x['isotope'], x['reaction'], x['library']) == key]
            print(f"  {e['isotope']:<10} {e['reaction']:<8} {e['library']:<10} "
                  f"[{', '.join(energies)}]")

    print(f"\nRuntime entries with no hardcoded fallback  ({len(mh)}):")
    if not mh:
        print("  (none)")
    else:
        seen = set()
        for e in mh:
            key = (e['isotope'], e['reaction'], e['library'])
            if key in seen:
                continue
            seen.add(key)
            print(f"  {e['isotope']:<10} {e['reaction']:<8} {e['library']:<10}")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.strip().splitlines()[0])
    p.add_argument("--threshold", type=float, default=0.01,
                   help="Fractional divergence threshold to flag (default: 0.01 = 1%%)")
    p.add_argument("--json", type=str, default=None,
                   help="If given, write full report as JSON to this path")
    args = p.parse_args()

    hardcoded = parse_hardcoded_reactions(DATA_PY)
    pointwise = {lib: load_pointwise(path) for lib, path in POINTWISE_FILES.items()}
    report = compare(hardcoded, pointwise, args.threshold)
    print_report(report, args.threshold)

    if args.json:
        with open(args.json, "w") as f:
            json.dump(report, f, indent=2)
        print(f"\nWrote JSON report: {args.json}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
