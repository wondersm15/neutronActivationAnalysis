# Nuclear Data Libraries: A Comparison

## What Nuclear Data Libraries Are

A nuclear data library is a curated, evaluated compilation of nuclear reaction cross sections, angular distributions, fission product yields, decay data, and other nuclear quantities. "Evaluated" means that raw experimental data from EXFOR (the international experimental nuclear reaction database) and other sources have been reviewed, resolved for inconsistencies, and supplemented with nuclear model calculations to fill gaps where measurements are sparse or absent. The result is a complete, self-consistent set of recommended values across all energies and reaction channels for each isotope.

Libraries differ because the evaluation process involves judgment: weighting conflicting experiments, choosing nuclear models, deciding how to handle poorly-measured reactions. These choices reflect the priorities of the evaluating organization and the available experimental database at the time of evaluation. Comparing multiple libraries is one of the primary validation methods in neutronics — but as discussed below, this comparison is far less independent than it appears.

---

## The Library Independence Problem

**This is the most important thing to understand about multi-library comparisons, and it is routinely underappreciated.**

When ENDF/B-VIII.0 and FENDL-3.2c agree on a cross section value, that agreement does not constitute independent validation. It often means both libraries evaluated the same handful of measurements and arrived at similar fits. When they disagree, it does not necessarily mean one is wrong — it may mean they weighted the same experimental data differently. The provenance tree of nuclear data evaluations is deeply interconnected.

### FENDL-3.2c Is Largely JEFF-3.3

The FENDL development process (documented in IAEA TECDOC-1628 and the FENDL-3.2 release notes) is explicit about this: for the majority of neutron-induced reactions on structural isotopes, FENDL-3.2c takes its evaluations directly from JEFF-3.3. The FENDL team's contribution is (a) selecting which source library to use for each isotope, (b) applying targeted modifications where fusion benchmark experiments showed systematic discrepancy, and (c) assembling the library for distribution through the IAEA.

For the isotopes in this tool, the following are taken from JEFF-3.3 with minimal or no modification in FENDL-3.2c:
- Fe-54, Fe-56, Fe-57, Fe-58 (radiative capture)
- Cr-50, Cr-52, Cr-53, Cr-54
- Ni-58, Ni-60, Ni-62, Ni-64 (capture; (n,p) was modified)
- Al-27, Si-28, Si-30
- W-180, W-182, W-183, W-184, W-186 (largely JEFF-3.3)
- Cu-63, Cu-65

**Practical consequence:** An ENDF/B-VIII.0 vs. FENDL-3.2c comparison for Fe-56(n,γ) is approximately equivalent to an ENDF/B-VIII.0 vs. JEFF-3.3 comparison. It is not a cross-check between two independent US and European evaluations — it is a cross-check between one US evaluation and one CEA/IRMM evaluation wrapped in the FENDL package.

### All Libraries Share the Same Experimental Foundation

The primary high-quality neutron cross section measurements for structural isotopes (Fe, Cr, Ni, W, Cu, Co) were produced by a small number of facilities:

- **IRMM Geel (Belgium):** Time-of-flight measurements of Fe, Cr, Ni, W, Co, Cu in the resolved resonance region (eV–keV). These are the highest-resolution data available. They are in EXFOR and were used by ENDF/B-VIII.0, JEFF-3.3, and JENDL-4.0. Agreement between libraries in the resolved resonance region (1 eV–100 keV) in most cases reflects different R-matrix fits (SAMMY, REFIT, or FITACS) to the same IRMM data.

- **ORELA (Oak Ridge):** Wide-range TOF data for Fe, Ni, Cr. Incorporated into ENDF/B evaluations. Some of this data also appears in JEFF via the IRMM comparisons.

- **LANL (Los Alamos):** 14 MeV differential cross section measurements for many threshold reactions. Primary input for ENDF/B-VIII.0 fast-neutron evaluations. Not directly used by JEFF-3.3 or FENDL.

- **OKTAVIAN (Osaka):** 14 MeV integral activation benchmarks for Fe, Ni, Cu, Al, Si. Used by the FENDL team to validate and modify evaluations. Not directly incorporated into ENDF/B-VIII.0.

- **FNG (Frascati):** 14 MeV streaming and activation benchmarks for ITER-specific material assemblies (FNG-ITER, FNG-Cu, FNG-W, FNG-SS, FNG-SiC). Drove FENDL modifications. Not used in ENDF/B.

- **BNL Sigma Center / Atlas of Neutron Resonances:** The definitive compilation of thermal and resonance integral values, used as anchoring points by all libraries. Agreement at thermal energies between libraries is almost entirely a consequence of all libraries referencing the same BNL Atlas values.

### Where Libraries Are Genuinely Independent

Despite the shared foundations, there are energy ranges and reactions where ENDF/B-VIII.0 and FENDL-3.2c are meaningfully independent:

**1. Threshold reactions at 14 MeV (most important for this tool)**

For (n,p), (n,α), and (n,2n) reactions, the 14 MeV experimental databases used by ENDF/B and FENDL are substantially different:
- ENDF/B-VIII.0 threshold evaluations draw heavily on LANL 14 MeV measurements, Ohio University activation data, and INIS/EXFOR literature compilations
- FENDL modifications at 14 MeV come primarily from OKTAVIAN integral benchmarks and FNG activation measurements

These are different experiments, different geometries, different irradiation and counting approaches. Agreement between ENDF/B-VIII.0 and FENDL-3.2c for a threshold reaction at 14 MeV is genuinely informative — it means two distinct experimental programs support the same value.

Disagreement is equally informative and should be understood as a physics uncertainty rather than a data quality issue. Observed disagreements of 10–30% for Ni-58(n,p), Fe-56(n,p), and Cu-63(n,2n) at 14 MeV fall within this category.

**2. Nuclear model parameterization in the unresolved resonance and fast regions**

Above the resolved resonance region (~100 keV–1 MeV), both libraries switch from R-matrix fits to statistical model (Hauser-Feshbach) calculations. Different groups use different optical model potentials, level density parameters, and pre-equilibrium treatments. Even if both libraries process the same EXFOR data, their model parameterizations are independently derived and can lead to genuine differences in the 0.1–10 MeV range.

**3. Isotopes with sparse measurement data**

For rare earth impurities (Eu-151, Eu-153) and some trace elements, experimental data is limited and the evaluations rely more heavily on nuclear models. Here, different codes (EMPIRE, TALYS, GNASH) can give genuinely different results even with the same input data.

### The WPEC/IAEA Coordination Effect

The OECD/NEA Working Party on International Nuclear Data Evaluation Co-operation (WPEC) produces Subgroup reports that recommend specific evaluations and methodologies. These recommendations are typically adopted by multiple libraries in their next release cycle. When WPEC Subgroup 26 (High-Priority Request List) identifies a discrepancy and recommends an updated cross section, ENDF/B, JEFF, and JENDL all tend to update in the same direction in their subsequent releases. This convergence is beneficial for reliability but reduces the independence of inter-library comparisons.

**Net assessment for this tool:** When ENDF/B-VIII.0 and FENDL-3.2c agree on σ_th or in the resolved resonance region, treat it as a consistency check, not independent validation. When they agree at 14 MeV for a threshold reaction, treat it as meaningful confirmation from different experimental programs. When they disagree at 14 MeV, the uncertainty is real and both values should be retained as the credible range for that cross section.

---

## ENDF/B-VIII.0 (2018)

**Origin:** Brookhaven National Laboratory / NNDC, US Nuclear Data Program  
**Primary application:** Thermal and fast fission reactors, criticality safety, shielding, general-purpose neutronics  
**Energy range:** 10⁻⁵ eV → 20 MeV (neutron incident)  
**Isotope coverage:** ~557 incident-neutron isotopes

ENDF/B-VIII.0 is the current US standard and the primary library in this tool. It incorporates updated evaluations for Fe, Cr, Ni, and W using improved R-matrix analysis (SAMMY code) of IRMM and ORELA time-of-flight data, better thermal scattering law treatment, and updated 14 MeV cross sections from LANL measurements. It is the most comprehensively reviewed library and the safe default for any isotope not covered by a more application-specific alternative.

**Coverage for this tool:** Complete — every isotope in REACTIONS has an ENDF/B-VIII.0 entry.

**Limitations for 14 MeV fusion:** Not specifically benchmarked against 14 MeV integral experiments. Some threshold reaction evaluations at 14 MeV are model-based with limited experimental constraint from the fusion-specific measurement programs (FNG, OKTAVIAN).

---

## FENDL-3.2c (2018, updated 2021)

**Origin:** IAEA Nuclear Data Section — assembled primarily from JEFF-3.3 evaluations with fusion-driven modifications  
**Primary application:** Fusion reactor design, activation, shielding, dose rate assessment for ITER/DEMO  
**Energy range:** 10⁻⁵ eV → 20 MeV  
**Isotope coverage:** ~180 isotopes (fusion-relevant structural and shielding materials)

FENDL is the standard nuclear data library for ITER design calculations and is used by the major European fusion institutions (CEA, EUROfusion, ENEA, CCFE/UKAEA). Its evaluations for structural isotopes are taken from JEFF-3.3 and modified using feedback from the FNG streaming benchmarks and OKTAVIAN activation experiments — the most directly fusion-relevant experimental validation available.

**Why FENDL-3.2c is the right second library for this tool:**

For a 14 MeV D-T source at Pacific Fusion, the FNG and OKTAVIAN benchmark experiments are the closest analogs to your actual irradiation conditions. FENDL modifications are derived from measuring discrepancies between calculated and experimental activation in configurations very similar to your use case. This gives FENDL a genuine advantage over ENDF/B-VIII.0 for threshold reactions at 14 MeV in the materials common to both this tool and ITER (Fe, Ni, Cr, W, Cu, Co, Al, Ta).

Key reactions where FENDL is better constrained than ENDF/B-VIII.0 for fusion applications:
- **Ni-58(n,p) → Co-58:** Modified from JEFF-3.3 baseline based on OKTAVIAN Ni benchmark. Co-58 is a primary dose-rate contributor in Ni-containing steels at short-to-medium cooling times. FENDL and ENDF/B-VIII.0 disagree by ~10% at 14.1 MeV.
- **Fe-56(n,p) → Mn-56 and Fe-56(n,2n) → Fe-55:** FNG-Fe benchmark drove FENDL parameter adjustments. Fe-55 (t½ = 2.74 y) is the dominant long-term dose contributor in iron and steel.
- **W isotopes (n,γ):** FENDL uses JEFF-3.3 W evaluations from IRMM Geel; ENDF/B-VIII.0 used independent IRMM data but with different R-matrix analysis. Agreement in the resonance region reflects different fits to the same data.
- **Ta-181(n,γ) → Ta-182:** Ta-182 (t½ = 114.7 d) is the primary concern for pure tantalum components. FENDL has dedicated evaluation for fusion first-wall material studies.

**What FENDL-3.2c does NOT have:**

FENDL excludes isotopes outside the fusion structural materials scope:
- **Eu-151, Eu-153:** Rare earth trace impurities in Kretekast concrete. Not in FENDL scope. Use ENDF/B-VIII.0 only for these.
- **General light element / biological shielding isotopes at trace levels**
- Actinides, fission products, medical isotopes

---

## JEFF-3.3 (2017)

**Origin:** NEA/OECD — Joint European Fission and Fusion File, consortium of European national laboratories  
**Primary application:** European thermal and fast reactor analysis, fission safety calculations  
**Isotope coverage:** ~562 incident-neutron isotopes

JEFF-3.3 is the parent library for most FENDL-3.2c structural isotope evaluations. For isotopes where FENDL has not modified the JEFF-3.3 baseline, comparing ENDF/B-VIII.0 vs. FENDL-3.2c is equivalent to comparing ENDF/B-VIII.0 vs. JEFF-3.3 — see the independence discussion above. JEFF-3.3 is the standard for reactor calculations in France, UK, and other European countries. Its Fe and W evaluations were led by IRMM Geel and CEA, using the same experimental facility that produced the highest-quality resonance data used by ENDF/B.

Not currently available in this tool as a selectable library (no JSON distribution in the openmc-data-storage format).

---

## JENDL-5 (2021)

**Origin:** Japan Atomic Energy Agency (JAEA)  
**Energy range:** 10⁻¹¹ eV → 200 MeV (the broadest of any library — unique for high-energy applications)  
**Notable strengths:** Very high energy neutrons (spallation, proton activation), actinides, and isotopes with limited Western measurement data

JENDL evaluations for structural isotopes are more independent from the ENDF/JEFF tradition than FENDL: JAEA conducted its own differential cross section measurements (for some isotopes) and uses its own set of nuclear reaction codes (CCONE code system vs. EMPIRE/TALYS used in the West). JENDL-4.0 contributed some isotope evaluations to FENDL-3.2c where JEFF-3.3 data was considered less reliable.

For 14 MeV activation in the materials covered by this tool, JENDL-5 would be a genuinely more independent comparison than FENDL-3.2c vs. ENDF/B-VIII.0 — particularly for isotopes where JAEA conducted independent 14 MeV measurements. Not currently available in this tool.

---

## TENDL-2023

**Origin:** Paul Scherrer Institute (PSI) / NRG Petten — Talys Evaluated Nuclear Data Library  
**Method:** Fully automated — cross sections generated by the TALYS nuclear reaction code without manual evaluation

TENDL's distinctive feature is near-complete isotopic coverage (thousands of isotopes), making it invaluable for activation calculations involving exotic or rarely-measured nuclides. The evaluations are model-based with limited experimental constraint for most isotopes. For well-measured structural isotopes (Fe, Ni, Cr, W, Co, Cu, Al), TENDL is generally less reliable than ENDF/B-VIII.0, JEFF-3.3, or FENDL — the automated evaluation cannot replicate the careful weighing of experiments by domain experts. It is most useful as a cross-check for threshold reactions in exotic isotopes, or where no experimental data exists at all.

---

## Interpreting Library Disagreements

| Pattern | Likely interpretation |
|---|---|
| < 5% everywhere | Libraries agree; either is reliable |
| 5–20% at 14 MeV only | Threshold region with different 14 MeV data sources; FENDL likely more reliable for D-T |
| 5–20% in resolved resonance region | Different R-matrix fits to same IRMM data; low physical significance for 14 MeV activation |
| Factor 2–10 at 14 MeV | Significant evaluation difference; check EXFOR for measurements |
| Agreement at thermal, disagreement at 14 MeV | Both anchored to same thermal measurements; 14 MeV difference is real physics uncertainty |
| Disagreement everywhere | Suspect one evaluation has a systematic issue; check against JENDL-5 or TENDL as tie-breaker |

**The 51 discrepancies found during ENDF/B-VIII.0 preprocessing** fell into two categories: clear data entry errors (Mn-55 n,2n factor-of-1000 wrong, Fe-56 n,2n factor-of-700 wrong, both corrected in data.py) where the original values were transcription errors unrelated to library differences, and genuine library-level differences of 10–200% for threshold reactions at 14 MeV. The FENDL-3.2c overlay in the Cross Sections tab allows visual inspection of where the two libraries agree and disagree across the full energy range, which is more informative than the three-point comparison in data.py.

---

## Recommended Library Strategy

| Situation | Recommended library |
|---|---|
| Default activation calculations | ENDF/B-VIII.0 (complete coverage) |
| 14 MeV D-T activation validation | FENDL-3.2c (fusion benchmarked, independent 14 MeV data) |
| Cross-library σ(E) comparison | ENDF/B-VIII.0 + FENDL-3.2c overlay |
| Rare earth impurities (Eu, Gd, Sm) | ENDF/B-VIII.0 only (FENDL lacks these) |
| Concrete, biological shielding | ENDF/B-VIII.0 (broader light element coverage) |
| True independent check on threshold reactions | Add JENDL-5 (independent Japanese measurements, different nuclear codes) |
| Unknown or exotic isotopes | TENDL-2023 as fallback only |
| Agreement at thermal as validation | Treat with caution — all libraries share same thermal anchor data |
