"""
Guards against drift between the hardcoded fallback cross_sections values
in ``data.REACTIONS`` (the human-readable reference) and the authoritative
pointwise runtime values in ``data/endf_3pt.json``.

Rationale
---------
``data.py`` carries a hardcoded ``cross_sections`` dict on every reaction
entry. At import, ``_load_extracted_3pt()`` clobbers those values with
runtime values interpolated from the pointwise ENDF/B-VIII.0 and FENDL-3.2c
files — so runtime is always authoritative. But the hardcoded values are
what someone reading ``data.py`` sees, and if they drift from runtime the
file becomes misleading.

This test re-parses ``data.py`` at the source level (bypassing
``_load_extracted_3pt()``) and compares every hardcoded ENDF/B-VIII.0
sigma_* value to the corresponding pointwise value. Anything above the
threshold fails the test.

Scope
-----
- ENDF/B-VIII.0 only. The hardcoded REACTIONS dicts do not carry FENDL-3.2c
  values by convention — FENDL is runtime-only via the pointwise JSON.
- Compares only non-None hardcoded entries. ``None`` means "deliberately
  no value" (e.g., sub-threshold reaction) and is not checked against
  runtime.
- If the pointwise file has no entry for a (isotope, reaction, energy),
  we do not fail — the hardcoded value is the only available reference
  for that cell.
"""

from __future__ import annotations

import ast
import json
import os

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PY = os.path.join(REPO_ROOT, "data.py")
POINTWISE_ENDF = os.path.join(REPO_ROOT, "data", "endf_3pt.json")

# Hardcoded values may be rounded to 3–4 sig figs; runtime is full precision.
# 1% is a generous threshold that catches real data errors without failing
# on normal rounding.
DRIFT_THRESHOLD = 0.01

ENERGY_KEYS = ("sigma_th", "sigma_2p5", "sigma_14")


def _literal(node: ast.AST):
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.UnaryOp) and isinstance(node.operand, ast.Constant):
        if isinstance(node.op, ast.USub) and isinstance(node.operand.value, (int, float)):
            return -node.operand.value
    return None


def _parse_hardcoded() -> list[tuple[str, str, str, float]]:
    """Return list of (isotope, reaction, energy_key, hardcoded_value) for
    every non-None endf8 sigma_* entry in REACTIONS."""
    with open(DATA_PY) as f:
        tree = ast.parse(f.read())
    out: list[tuple[str, str, str, float]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign):
            continue
        targets = [t.id for t in node.targets if isinstance(t, ast.Name)]
        if "REACTIONS" not in targets or not isinstance(node.value, ast.Dict):
            continue
        for iso_key, iso_val in zip(node.value.keys, node.value.values):
            if not isinstance(iso_key, ast.Constant) or not isinstance(iso_val, ast.List):
                continue
            iso = iso_key.value
            for rxn_node in iso_val.elts:
                if not isinstance(rxn_node, ast.Dict):
                    continue
                rxn_name = None
                xsec_node = None
                for k, v in zip(rxn_node.keys, rxn_node.values):
                    if isinstance(k, ast.Constant):
                        if k.value == "reaction":
                            rxn_name = _literal(v)
                        if k.value == "cross_sections" and isinstance(v, ast.Dict):
                            xsec_node = v
                if rxn_name is None or xsec_node is None:
                    continue
                for lib_k, lib_v in zip(xsec_node.keys, xsec_node.values):
                    if not isinstance(lib_k, ast.Constant) or lib_k.value != "endf8":
                        continue
                    if not isinstance(lib_v, ast.Dict):
                        continue
                    for e_k, e_v in zip(lib_v.keys, lib_v.values):
                        if not isinstance(e_k, ast.Constant):
                            continue
                        val = _literal(e_v)
                        if val is None:
                            continue
                        out.append((iso, rxn_name, e_k.value, float(val)))
        break
    return out


@pytest.fixture(scope="module")
def pointwise_endf():
    with open(POINTWISE_ENDF) as f:
        return json.load(f)


@pytest.fixture(scope="module")
def hardcoded_entries():
    return _parse_hardcoded()


def test_hardcoded_covered_by_runtime_within_threshold(hardcoded_entries, pointwise_endf):
    """Every hardcoded ENDF/B-VIII.0 σ value must match the pointwise runtime
    value within DRIFT_THRESHOLD, if the runtime value exists."""
    drifts = []
    for iso, rxn, key, hard_val in hardcoded_entries:
        run_val = (
            pointwise_endf.get(iso, {})
            .get(rxn, {})
            .get(key)
        )
        if run_val is None:
            continue
        if run_val == 0:
            continue  # Skip true zeros — division undefined
        d = abs(hard_val - run_val) / abs(run_val)
        if d > DRIFT_THRESHOLD:
            drifts.append(
                f"{iso} {rxn} endf8 {key}: hardcoded={hard_val:.4g}, "
                f"runtime={run_val:.4g}, Δ={d*100:.1f}%"
            )
    if drifts:
        msg = (
            f"Hardcoded/runtime drift exceeds {DRIFT_THRESHOLD*100:.1f}% "
            f"in {len(drifts)} entries:\n  " + "\n  ".join(drifts)
        )
        pytest.fail(msg)


def test_reactions_parse_cleanly(hardcoded_entries):
    """Sanity: the parser returns a non-trivial list of entries."""
    assert len(hardcoded_entries) > 50, (
        f"Expected >50 hardcoded endf8 entries, parser found {len(hardcoded_entries)}. "
        "Did REACTIONS format change?"
    )
