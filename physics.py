"""
Physics engine for neutron activation analysis.
Single-pulse irradiation model for pulsed-power applications.

Model:
  For an instantaneous neutron pulse (duration << all half-lives):
    N_activated = (N_A / M_avg) * f_iso * sigma * Phi
    A(t) = lambda * N_activated * exp(-lambda * t)

  where:
    N_A     = Avogadro's number
    M_avg   = average molar mass of the material (g/mol)
    f_iso   = atom fraction of target isotope in material
    sigma   = microscopic cross-section (cm²) at the relevant neutron energy
    Phi     = total neutron fluence (n/cm²)
    lambda  = ln(2) / t_half

Dose rate:
  Point-source approximation at distance d, no self-shielding or buildup.
  H*(10) at d = sum over gamma lines of:
    A(t) * BR_i * h*(E_i) / (4 pi d^2)
  where h*(E) is the ICRP-74 fluence-to-ambient-dose-equivalent coefficient.

Units:
  Activity   : Bq per gram of material
  Dose rate  : uSv/h at specified distance (default 1 m)
"""

import math
from data import MATERIALS, REACTIONS, ISOTOPE_MASS, ICRP74_H10

N_A = 6.02214076e23  # mol^-1


# ---------------------------------------------------------------------------
# ICRP-74 interpolation
# ---------------------------------------------------------------------------

def interpolate_h10(energy_keV):
    """
    Log-log interpolation of ICRP-74 H*(10)/Phi for photons.
    Input:  energy in keV
    Output: h*(10) in pSv*cm^2
    """
    e_MeV = energy_keV / 1000.0

    # Clamp to table bounds
    if e_MeV <= ICRP74_H10[0][0]:
        return ICRP74_H10[0][1]
    if e_MeV >= ICRP74_H10[-1][0]:
        return ICRP74_H10[-1][1]

    for i in range(len(ICRP74_H10) - 1):
        e0, h0 = ICRP74_H10[i]
        e1, h1 = ICRP74_H10[i + 1]
        if e0 <= e_MeV <= e1:
            # Log-log interpolation
            log_frac = (math.log(e_MeV) - math.log(e0)) / (math.log(e1) - math.log(e0))
            return math.exp(math.log(h0) + log_frac * (math.log(h1) - math.log(h0)))

    return ICRP74_H10[-1][1]


# ---------------------------------------------------------------------------
# Average molar mass
# ---------------------------------------------------------------------------

def compute_avg_molar_mass(material_name):
    """Average molar mass (g/mol) from isotopic atom fractions."""
    mat = MATERIALS[material_name]
    return sum(frac * ISOTOPE_MASS[iso] for iso, frac in mat["isotopes"].items()
               if iso in ISOTOPE_MASS)


# ---------------------------------------------------------------------------
# Core computation
# ---------------------------------------------------------------------------

def compute_activation(material_name, fluence_th, fluence_14,
                       fluence_2p5=0.0,
                       t_max_s=None, n_points=250, distance_cm=100.0,
                       enabled_reactions=None, sigma_f_min=0.0,
                       library="endf8"):
    """
    Compute activity and dose rate vs. time for all activation products
    after a single short neutron pulse.

    Products with the same nuclide (produced via different reactions) are
    merged — the measured activity is the total regardless of production path.

    Args:
        material_name      : key into MATERIALS
        fluence_th         : thermal neutron fluence, n/cm^2, at 0.0253 eV
        fluence_14         : 14.1 MeV neutron fluence, n/cm^2
        fluence_2p5        : 2.5 MeV neutron fluence, n/cm^2 (D-D / fission spectrum;
                             default 0 = unused until 2.5 MeV values are populated)
        t_max_s            : max time in seconds (auto-scaled if None)
        n_points           : number of log-spaced time points
        distance_cm        : dose rate distance in cm (default 100 = 1 m)
        enabled_reactions  : set/list of "target|reaction|product" keys to include,
                             or None to include all
        sigma_f_min        : minimum σ·f (barns) threshold; reactions below this
                             in all flux regimes are skipped (0 = no filter)
        library            : nuclear data library key (default "endf8")

    Returns:
        dict with keys: time_s, products, total_activity_Bq_per_g,
        total_dose_rate_uSv_per_h, distance_cm, fluence_th, fluence_2p5, fluence_14
    """
    if material_name not in MATERIALS:
        return None

    mat = MATERIALS[material_name]
    M_avg = compute_avg_molar_mass(material_name)
    if M_avg <= 0:
        return None

    atoms_per_gram = N_A / M_avg

    # ------------------------------------------------------------------
    # Step 1: compute initial activated atoms for each reaction
    # ------------------------------------------------------------------
    raw_products = []

    enabled_set = set(enabled_reactions) if enabled_reactions is not None else None

    for isotope, atom_frac in mat["isotopes"].items():
        if isotope not in REACTIONS:
            continue
        for rxn in REACTIONS[isotope]:
            if rxn["t_half"] == "Stable" or rxn["t_half_s"] is None:
                continue

            # 1A: reaction toggle filter
            rxn_key = f'{isotope}|{rxn["reaction"]}|{rxn["product"]}'
            if enabled_set is not None and rxn_key not in enabled_set:
                continue

            # Extract cross-sections from the selected library
            xs = rxn.get("cross_sections", {}).get(library, {})
            sigma_th  = xs.get("sigma_th")
            sigma_2p5 = xs.get("sigma_2p5")
            sigma_14  = xs.get("sigma_14")

            # 1B: σ·f threshold filter (uses max across all energy points)
            if sigma_f_min > 0:
                sf_th  = (sigma_th  * atom_frac) if sigma_th  is not None else 0.0
                sf_2p5 = (sigma_2p5 * atom_frac) if sigma_2p5 is not None else 0.0
                sf_14  = (sigma_14  * atom_frac) if sigma_14  is not None else 0.0
                if max(sf_th, sf_2p5, sf_14) < sigma_f_min:
                    continue

            n_target = atoms_per_gram * atom_frac

            # Fluence-weighted activation (sigma in barns -> cm^2)
            n_act = 0.0
            if sigma_th  is not None and fluence_th  > 0:
                n_act += n_target * sigma_th  * 1e-24 * fluence_th
            if sigma_2p5 is not None and fluence_2p5 > 0:
                n_act += n_target * sigma_2p5 * 1e-24 * fluence_2p5
            if sigma_14  is not None and fluence_14  > 0:
                n_act += n_target * sigma_14  * 1e-24 * fluence_14

            if n_act <= 0:
                continue

            raw_products.append({
                "product":     rxn["product"],
                "source":      f'{isotope}{rxn["reaction"]}',
                "n_activated": n_act,
                "t_half":      rxn["t_half"],
                "t_half_s":    rxn["t_half_s"],
                "lambda_s":    math.log(2) / rxn["t_half_s"],
                "decay_mode":  rxn["decay_mode"],
                "gammas":      rxn["gammas"],
            })

    # ------------------------------------------------------------------
    # Step 2: merge products with the same nuclide
    # ------------------------------------------------------------------
    merged = {}
    for p in raw_products:
        key = p["product"]
        if key in merged:
            merged[key]["n_activated"] += p["n_activated"]
            merged[key]["sources"].append(p["source"])
        else:
            merged[key] = {
                "product":     p["product"],
                "sources":     [p["source"]],
                "n_activated": p["n_activated"],
                "t_half":      p["t_half"],
                "t_half_s":    p["t_half_s"],
                "lambda_s":    p["lambda_s"],
                "decay_mode":  p["decay_mode"],
                "gammas":      p["gammas"],
            }

    products = list(merged.values())
    if not products:
        return {
            "time_s": [], "products": [], "total_activity_Bq_per_g": [],
            "total_dose_rate_uSv_per_h": [], "distance_cm": distance_cm,
            "fluence_th": fluence_th, "fluence_14": fluence_14,
        }

    # ------------------------------------------------------------------
    # Step 3: pre-compute dose-rate coefficients for each product
    # ------------------------------------------------------------------
    four_pi_d2 = 4.0 * math.pi * distance_cm * distance_cm

    for p in products:
        total_dose_coeff = 0.0
        for energy_keV, intensity_pct in p["gammas"]:
            h10 = interpolate_h10(energy_keV)
            br = intensity_pct / 100.0        # photons per decay
            coeff = h10 * br / four_pi_d2     # pSv/s per Bq
            total_dose_coeff += coeff
        p["dose_coeff_pSv_s_per_Bq"] = total_dose_coeff
        p["initial_activity_Bq_per_g"] = p["lambda_s"] * p["n_activated"]

    # ------------------------------------------------------------------
    # Step 4: generate time array and compute curves
    # ------------------------------------------------------------------
    max_halflife = max(p["t_half_s"] for p in products)
    if t_max_s is None:
        t_max_s = min(10.0 * max_halflife, 50.0 * 365.25 * 86400)
        t_max_s = max(t_max_s, 3600.0)

    log_t_min = 0.0   # log10(1 s)
    log_t_max = math.log10(t_max_s)
    time_s = [10.0 ** (log_t_min + i * (log_t_max - log_t_min) / (n_points - 1))
              for i in range(n_points)]

    total_activity  = [0.0] * n_points
    total_dose_rate = [0.0] * n_points

    PSV_TO_USV_PER_H = 3.6e-3   # pSv/s -> uSv/h

    result_products = []
    for p in products:
        lam = p["lambda_s"]
        n0  = p["n_activated"]
        dc  = p["dose_coeff_pSv_s_per_Bq"]

        activity   = []
        dose_rate  = []

        for i, t in enumerate(time_s):
            a  = lam * n0 * math.exp(-lam * t)          # Bq/g
            dr = a * dc * PSV_TO_USV_PER_H               # uSv/h
            activity.append(a)
            dose_rate.append(dr)
            total_activity[i]  += a
            total_dose_rate[i] += dr

        result_products.append({
            "product":                  p["product"],
            "sources":                  p["sources"],
            "t_half":                   p["t_half"],
            "t_half_s":                 p["t_half_s"],
            "decay_mode":               p["decay_mode"],
            "gammas":                   p["gammas"],
            "initial_activity_Bq_per_g": p["initial_activity_Bq_per_g"],
            "activity_Bq_per_g":        activity,
            "dose_rate_uSv_per_h":      dose_rate,
        })

    # Sort by initial activity descending
    result_products.sort(key=lambda x: -x["initial_activity_Bq_per_g"])

    return {
        "time_s":                    time_s,
        "products":                  result_products,
        "total_activity_Bq_per_g":   total_activity,
        "total_dose_rate_uSv_per_h": total_dose_rate,
        "distance_cm":               distance_cm,
        "fluence_th":                fluence_th,
        "fluence_2p5":               fluence_2p5,
        "fluence_14":                fluence_14,
        "library":                   library,
    }


# ---------------------------------------------------------------------------
# Snapshot at specific cooling times
# ---------------------------------------------------------------------------

SNAPSHOT_TIMES = {
    "1 min":    60,
    "10 min":   600,
    "1 h":      3600,
    "8 h":      28800,
    "1 d":      86400,
    "7 d":      604800,
    "30 d":     2592000,
    "1 y":      31557600,
}

def compute_snapshots(products, fluence_th, fluence_14):
    """
    Compute a table of activity and dose rate at standard cooling times
    for each product. Used for the snapshot/summary table.
    """
    rows = []
    for label, t in SNAPSHOT_TIMES.items():
        row = {"time_label": label, "time_s": t, "products": []}
        total_a  = 0.0
        total_dr = 0.0
        for p in products:
            lam = math.log(2) / p["t_half_s"]
            a = p["initial_activity_Bq_per_g"] * math.exp(-lam * t)
            dr_idx = 0  # we'll compute inline
            # Find dose rate from curve (approximate by nearest time point)
            # or recompute directly
            dc = p.get("dose_coeff_pSv_s_per_Bq", 0)
            dr = a * dc * 3.6e-3
            total_a  += a
            total_dr += dr
            if a > 0:
                row["products"].append({
                    "product":   p["product"],
                    "activity":  a,
                    "dose_rate": dr,
                })
        row["total_activity"]  = total_a
        row["total_dose_rate"] = total_dr
        # Find dominant product
        if row["products"]:
            dom = max(row["products"], key=lambda x: x["activity"])
            row["dominant"] = dom["product"]
        else:
            row["dominant"] = "—"
        rows.append(row)
    return rows
