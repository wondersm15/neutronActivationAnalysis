"""
Neutron Activation Analysis — Local Web App
Flask backend serving nuclear data from ENDF/B-VIII.0 (bundled).

Run:  python3 app.py
Then open: http://localhost:5050
"""

import os
import json
from flask import Flask, jsonify, render_template, request
from data import MATERIALS, get_material_activation
from physics import compute_activation

app = Flask(__name__)

DATA_SOURCE = "ENDF/B-VIII.0 (NNDC/BNL, 2018) — bundled v1"


@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------------------
# Existing material-info endpoints
# ------------------------------------------------------------------

@app.route("/api/materials")
def api_materials():
    """Return materials grouped by category (dynamic — all categories present in data.py)."""
    from collections import defaultdict
    groups = defaultdict(list)
    for k, v in MATERIALS.items():
        cat = v.get("category", "other")
        groups[cat].append(k)
    return jsonify(dict(groups))


@app.route("/api/material/<path:name>")
def api_material(name):
    if name not in MATERIALS:
        return jsonify({"error": f"Material '{name}' not found"}), 404

    mat = MATERIALS[name]
    activation = get_material_activation(name)

    # All reactions for isotopes in this material — includes stable-product reactions
    # (e.g. Fe-56(n,γ)→Fe-57) that are filtered out of the activation table but
    # are still needed for σ(E) plotting in the Cross Sections tab.
    # Each entry is {reaction, product, stable, t_half} so the UI can badge
    # stable vs. activation products without a separate lookup.
    from data import REACTIONS as _ALL_REACTIONS
    xsec_reactions = {
        iso: [
            {
                "reaction": r.get("reaction"),
                "product":  r.get("product"),
                "stable":   r.get("t_half") == "Stable",
                "t_half":   r.get("t_half") if r.get("t_half") != "Stable" else None,
            }
            for r in _ALL_REACTIONS[iso]
        ]
        for iso in mat.get("isotopes", {})
        if iso in _ALL_REACTIONS
    }

    return jsonify({
        "name":           name,
        "description":    mat["description"],
        "density":        mat["density_g_cc"],
        "isotopes":       mat["isotopes"],
        "impurities":     mat.get("impurities", {}),
        "activation":     activation,
        "xsec_reactions": xsec_reactions,
        "data_source":    DATA_SOURCE,
    })


@app.route("/api/isotope/<isotope>")
def api_isotope(isotope):
    from data import REACTIONS
    if isotope not in REACTIONS:
        return jsonify({"error": f"Isotope '{isotope}' not found"}), 404
    return jsonify({
        "isotope":     isotope,
        "reactions":   REACTIONS[isotope],
        "data_source": DATA_SOURCE,
    })


# ------------------------------------------------------------------
# Activity / dose-rate computation endpoint
# ------------------------------------------------------------------

@app.route("/api/compute", methods=["POST"])
def api_compute():
    """
    Compute activity and dose rate vs. time for one or more materials.

    POST body (JSON):
      {
        "materials":   ["Aluminum (pure)", "Copper (OFHC)"],
        "fluence_th":  0,           // thermal neutron fluence, n/cm^2
        "fluence_2p5": 0,           // 2.5 MeV neutron fluence, n/cm^2 (optional, default 0)
        "fluence_14":  1e12,        // 14.1 MeV neutron fluence, n/cm^2
        "distance_cm": 100,         // optional, default 100 (1 m)
        "library":     "endf8"      // nuclear data library; default "endf8"
      }

    Returns:
      {
        "results": {
          "Aluminum (pure)": { time_s, products, total_activity, ... },
          ...
        },
        "data_source": "..."
      }
    """
    data = request.get_json(force=True)
    materials         = data.get("materials", [])
    fluence_th        = float(data.get("fluence_th", 0))
    fluence_2p5       = float(data.get("fluence_2p5", 0))
    fluence_14        = float(data.get("fluence_14", 1e12))
    distance_cm       = float(data.get("distance_cm", 100))
    library           = data.get("library", "endf8")
    # 1B: optional filtering
    enabled_reactions = data.get("enabled_reactions", None)   # list of "target|reaction|product" or None=all
    sigma_f_min       = float(data.get("sigma_f_min", 0.0))   # min σ·f (b); 0 = no filter

    results = {}
    for mat_name in materials:
        result = compute_activation(
            mat_name, fluence_th, fluence_14,
            fluence_2p5=fluence_2p5,
            distance_cm=distance_cm,
            enabled_reactions=enabled_reactions,
            sigma_f_min=sigma_f_min,
            library=library,
        )
        if result is not None:
            results[mat_name] = result

    return jsonify({
        "results":     results,
        "data_source": DATA_SOURCE,
    })


# ------------------------------------------------------------------
# Literature review endpoints
# ------------------------------------------------------------------

NOTES_DIR = os.path.join(os.path.dirname(__file__), "NotesFromOtherSources")
REFS_FILE  = os.path.join(os.path.dirname(__file__), "references.json")


@app.route("/api/literature")
def api_literature():
    """Return all markdown files from NotesFromOtherSources/ as a list of {filename, title, content}."""
    docs = []
    if not os.path.isdir(NOTES_DIR):
        return jsonify({"docs": [], "error": "NotesFromOtherSources directory not found"}), 200

    for fname in sorted(os.listdir(NOTES_DIR)):
        if not fname.endswith(".md"):
            continue
        fpath = os.path.join(NOTES_DIR, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            # Use first H1 heading as title if present, else prettify filename
            title = fname.replace("-", " ").replace("_", " ").replace(".md", "").title()
            for line in content.splitlines():
                if line.startswith("# "):
                    title = line[2:].strip()
                    break
            docs.append({"filename": fname, "title": title, "content": content})
        except Exception as e:
            docs.append({"filename": fname, "title": fname, "content": f"Error reading file: {e}"})

    return jsonify({"docs": docs})


@app.route("/api/references")
def api_references():
    """Return references.json as structured list."""
    if not os.path.isfile(REFS_FILE):
        return jsonify({"references": [], "error": "references.json not found"}), 200
    try:
        with open(REFS_FILE, "r", encoding="utf-8") as f:
            refs = json.load(f)
        return jsonify({"references": refs})
    except Exception as e:
        return jsonify({"references": [], "error": str(e)}), 500


# ------------------------------------------------------------------
# Cross-section σ(E) endpoint  (Phase 3D)
# ------------------------------------------------------------------

_REACTION_TO_MT = {
    "(n,γ)":     102,
    "(n,p)":     103,
    "(n,α)":     107,
    "(n,2n)":     16,
    "(n,3n)":     17,
    "(n,d)":     104,
    "(n,t)":     105,
    "(n,np)":     28,
    "(n,nα)":     22,
    "(n,total)":   1,
}

_LIBRARY_SUBDIR = {
    "endf8":   "endf8",
    "fendl32c": "fendl32c",
}
_LIBRARY_LABEL = {
    "endf8":   "ENDF/B-VIII.0",
    "fendl32c": "FENDL-3.2c",
}

_POINTWISE_ROOT = os.path.join(os.path.dirname(__file__),
                                "data", "external", "pointwise")


@app.route("/api/xsec/<isotope>")
def api_xsec(isotope):
    """
    Return pointwise σ(E) data for a given isotope + reaction.

    Query params:
      reaction  — e.g. "(n,γ)"   (required)
      library   — default "endf8"

    Response always includes:
      available     bool       — True if pointwise file exists
      three_pt      dict|null  — bundled {sigma_th, sigma_2p5, sigma_14}
      energy/xsec   lists      — present only when available=True
    """
    from data import REACTIONS

    reaction = request.args.get("reaction", "")
    library  = request.args.get("library", "endf8")

    if isotope not in REACTIONS:
        return jsonify({"error": f"Isotope '{isotope}' not found"}), 404

    mt = _REACTION_TO_MT.get(reaction)
    if mt is None:
        return jsonify({"error": f"Unknown reaction '{reaction}'"}), 400

    # Parse "Fe-56" → sym="Fe", A=56
    parts = isotope.split("-")
    if len(parts) != 2:
        return jsonify({"error": "Invalid isotope format (expected e.g. Fe-56)"}), 400
    sym, a_str = parts
    try:
        A = int(a_str)
    except ValueError:
        return jsonify({"error": "Non-integer mass number"}), 400

    # Pull bundled 3-point data from REACTIONS (only for activation reactions, not total XS)
    three_pt = None
    if reaction != "(n,total)":
        for rxn in REACTIONS.get(isotope, []):
            if rxn.get("reaction") == reaction:
                cs = rxn.get("cross_sections", {})
                three_pt = cs.get(library) or cs.get("endf8")
                break

    # Resolve library subdirectory
    subdir = _LIBRARY_SUBDIR.get(library)
    if subdir is None:
        return jsonify({"error": f"Unknown library '{library}'"}), 400

    fname = f"{sym}_{A}_n{mt}.json"
    fpath = os.path.join(_POINTWISE_ROOT, subdir, fname)

    if not os.path.isfile(fpath):
        return jsonify({
            "isotope":   isotope,
            "reaction":  reaction,
            "library":   library,
            "mt":        mt,
            "available": False,
            "three_pt":  three_pt,
            "message":   (
                f"Pointwise file '{fname}' not found for library '{library}'. "
                f"Run: python tools/download_pointwise.py --library {library}"
                + (" --include-total" if mt == 1 else "")
            ),
        })

    with open(fpath) as f:
        pw = json.load(f)

    return jsonify({
        "isotope":   isotope,
        "reaction":  reaction,
        "library":   library,
        "mt":        mt,
        "available": True,
        "energy":    pw["energy"],
        "xsec":      pw["cross section"],
        "three_pt":  three_pt,
    })


if __name__ == "__main__":
    print("=" * 60)
    print("  Neutron Activation Analysis — Local Web App")
    print(f"  Data source: {DATA_SOURCE}")
    print("  Open: http://localhost:5050")
    print("=" * 60)
    app.run(debug=True, port=5050)
