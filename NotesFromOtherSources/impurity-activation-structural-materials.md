# Impurity-Driven Neutron Activation in Common Structural Materials

**Prepared for:** Pacific Fusion — Neutron Activation Analysis Project
**Date:** April 2026
**Status:** Living document — Phase 2 implementation reference

---

## 1. Why Impurities Dominate Long-Term Activation

In single-pulse neutron irradiation, the activity of a product nuclide at time *t* after the pulse is:

```
A(t) = λ · N₀ · σ · Φ · exp(−λt)
```

For long-lived products (large λ⁻¹), the exponential decay is slow — so activity persists. The term N₀·σ·Φ determines the *production*. For a trace impurity at atom fraction f and cross-section σ:

```
Production proxy: σ · f
```

The critical insight: a trace element can have σ·f *equal to or exceeding* a bulk constituent if its cross-section is sufficiently large. Below are the key examples that are routinely underestimated or missed in activation models.

---

## 2. Stainless Steel (SS-304, SS-316)

### 2.1 Cobalt — The Primary Long-Term Dose Driver

SS-304 and SS-316 do not specify a cobalt content in the base ASTM standard (A276/A240/A312). Cobalt enters as a tramp element through:
- Raw nickel feed materials (Ni ores naturally contain Co at ~0.1–1 wt%)
- Ferroalloy additions
- Scrap re-melt (cobalt redistribution from Co-bearing alloys)

**Measured ranges:**

| Category | Co concentration | Notes |
|---|---|---|
| Commercial SS-316, typical | 1,340–1,630 ppm | Measured; literature range 90–2,570 ppm [ORNL/TM-2020/1681] |
| Commercial SS, Ni-rich grades | ~2,000 ppm (0.2 wt%) | Springer 2023 decommissioning study |
| Nuclear-grade low-Co (304CO, Sandmeyer) | ≤500 ppm max | Sandmeyer Steel / [EPRI TR-112352] |
| Reactor-grade low-Co (special melt) | ≤100 ppm | Special order; higher cost; vendor specification |
| Ultra-low Co (scrap-free melt) | 20–50 ppm | Available from select suppliers |

**Activation implications — Co-59(n,γ)→Co-60:**

σ_th = 37.2 b; t½ = 5.2714 y; gammas: 1173.2 keV (99.85%), 1332.5 keV (99.98%)

σ·f comparison in SS-316 at 14.1 MeV flux (thermal σ·f values):

| Co content | f_Co59 | σ·f_th (b) | vs. Fe-56 bulk (0.62 × σ_th≈2.5e-3 b) |
|---|---|---|---|
| 2,000 ppm | 2.02×10⁻³ | 0.075 | **30× larger** |
| 500 ppm | 5.0×10⁻⁴ | 0.019 | 7.5× larger |
| 100 ppm | 1.0×10⁻⁴ | 0.0037 | 1.5× larger |
| 50 ppm | 5.0×10⁻⁵ | 0.0019 | comparable |

(Note: f_Co59 ≈ Co_ppm × 10⁻⁶ × (55.85/58.93) / sum_over_all_elements; tabulated as approximate.)

ORNL/EPRI analyses consistently show Co-60 responsible for **60–95% of external gamma dose** from activated SS-316 at 2–5 years cooling for typical fluence conditions. At 10+ years, Co-60 remains dominant until it decays away, followed by Ni-63 as the long-lived waste concern.

**Implications for this tool:** The tool must include Co-59 in the isotopic composition of all SS materials to produce meaningful long-term results. Two variants are required:
- **SS-316 (commercial):** Co at ~1500 ppm
- **SS-316 (nuclear grade):** Co at ≤100 ppm

### 2.2 Niobium — Critical Long-Lived Waste Driver

Niobium enters SS via:
- Contamination from Nb-stabilized grades during scrap re-melt (SS-347 = 18/8 + Nb; SS-321 + Nb variants)
- Ferroniobium additions to the melt bath
- Nb present in Inconel alloys often mixed with SS scrap

**Typical Nb levels:**
- Virgin SS-316 (scrap-free): <100 ppm, often <50 ppm
- Commercial SS-316 from mixed scrap: 200–3,000 ppm
- Inconel X-750: up to ~1 wt% Nb (deliberate addition)

**Activation: Nb-93(n,γ)→Nb-94**

σ_th = 1.15 b; t½ = 20,300 y; gammas: 702.63 keV (99.97%), 871.10 keV (99.89%)

NRC 10 CFR 61 Class C limit for Nb-94: **0.2 Ci/m³** — the most restrictive single limit in the Class C table for activated metals. A 2023 Springer study found that Nb-94 concentrations exceeded the Class C limit in Inconel X-750 reactor internals, requiring deep geological disposal or indefinite storage.

For SS-316 with 500 ppm Nb at a pulsed fusion fluence of 10¹³ n/cm²:
- Very small Nb-94 activity at single-pulse scale, but accumulates dramatically under repeated-pulse or long-burst operation.

**Implication:** For characterization of activated SS structural components (e.g. near the pulsed power load), Nb should be analytically characterized if scrap-source material is used. Single-pulse activity is modest, but cumulative activation over a fusion facility lifetime makes Nb-94 a potential deep-disposal driver.

### 2.3 Nickel — High-Fluence Waste Classification

SS-316 bulk Ni: 10–14 wt%. Ni is not an "impurity" but a bulk constituent. However, its activation products are critical for waste classification at high fluences.

**Ni-58(n,γ)→Ni-59:** σ_th = 4.6 b; t½ = 76,000 y
**Ni-62(n,γ)→Ni-63:** σ_th = 14.5 b; t½ = 100.1 y

Both are pure beta emitters (no gamma) but drive waste classification:
- NRC 10 CFR 61: Ni-63 Class C limit = 70 Ci/m³ (LLW)
- Ni-59 does have a soft X-ray from K-capture but is not a significant dose-to-person contributor in the same way Co-60 is

For bulk SS-316 at 12% Ni:
- f_Ni62 ≈ 0.12 × (58.69/55.85) / 1 × 0.03634 ≈ 0.00232
- σ·f_th (Ni-63) = 14.5 × 0.00232 ≈ 0.0336 b — significant

At a pulsed fusion facility with high time-integrated fluence, Ni-63 + Ni-59 can accumulate to dominate the Class C compliance problem even though they don't produce a dose-rate issue (no gammas).

### 2.4 Manganese (≤2 wt% bulk)

Mn is a bulk alloying element in SS-316 (not trace), but its activation products are notable:

- **Mn-55(n,γ)→Mn-56:** σ_th=13.3 b, t½=2.578 h — dominant short-term dose source (847.77 keV, 98.9% intensity; 1810.73 keV, 26.9%)
- **Fe-54(n,p)→Mn-54:** σ_14=0.080 b, t½=312.2 d — significant medium-term dose at 14 MeV flux

With 2% Mn in SS-316, f_Mn55 ≈ 0.0214; σ·f_th(Mn-56) ≈ 0.285 b — dominant short-term product.

### 2.5 Silver — Often-Missed Medium-Term Contributor in SS

Ag enters SS as a trace impurity from raw Ni feed and from Ag-bearing alloys in mixed scrap. Typical: <10 ppm in virgin SS; up to 50 ppm in commercial grades.

**Ag-109(n,γ)→Ag-110m:** σ_th(→Ag-110m) = 4.49 b (isomeric cross-section only; total Ag-109 σ_th ≈ 91 b but ~95% goes to short-lived Ag-110g), t½=249.8 d
Gammas: 657.76 keV (94.7%), 884.68 keV (72.7%), 937.49 keV (34.3%), 1384.29 keV (24.3%), 763.94 keV (22.3%), 1505.04 keV (13.1%)

**Ag-107(n,γ)→Ag-108m:** σ_th ≈ 35 b (→Ag-108m isomeric state); t½ = **438 y** — extremely long-lived waste concern
Gammas: 434.00 keV (90.7%), 614.28 keV (89.8%), 722.91 keV (91.0%)

Even at 10 ppm total Ag (split ~52% Ag-107, 48% Ag-109), the Ag-108m contribution can appear in waste characterization analyses for activated SS over decades of operation. This nuclide appears in the decommissioning radionuclide list for several LWR studies.

---

## 3. OFHC Copper (C10100 / C10200, ASTM B170)

ASTM B170 covers two grades of oxygen-free electrolytic copper:
- **C10100 (OFE):** 99.99% minimum Cu; strictly controlled impurity limits
- **C10200 (OFHC):** slightly looser purity

### C10100 (OFE) Impurity Limits (ASTM B170)

| Impurity | Max (ppm) | Key activation product | σ_th (b) |
|---|---|---|---|
| Ag | **25** | Ag-110m (249.8 d), Ag-108m (438 y) | 4.49 / ~35 |
| Fe | 10 | Mn-54 (312.2 d) via (n,p), Fe-59 (44.5 d) | minor |
| Ni | 10 | Co-58 (70.8 d) via (n,p), Ni-63 (100.1 y) | 4.6/14.5 |
| Pb | 5 | Bi isotopes (threshold) | variable |
| Zn | **1** | Zn-65 (243.9 d) | 0.793 |
| Cd | 1 | Ag via daughters | — |
| As | 5 | — | — |
| Sb | 4 | Sb-124 (60.2 d) | significant |
| Co | not listed | Co-60 (5.27 y) | 37.2 |

**Co in OFE/OFHC Cu:** Co is not formally limited in ASTM B170 but is typically <5 ppm in high-purity electrolytic copper. At 5 ppm Co, the Co-60 σ·f contribution (~1.6×10⁻⁴ b thermal) is small but non-negligible relative to Ag.

### 3.1 Silver — Primary Medium-Term Dose Driver in OFE Copper

Silver is the highest-specified impurity in C10100 at ≤25 ppm. This makes Ag-110m (249.8 d) the **primary medium-term activation concern** in true OFE/OFHC copper under thermal neutron irradiation, not Zn-65.

**σ·f comparison at ASTM B170 maximum limits:**

For a thermal flux:
- Ag-109 at 25 ppm: f_Ag109 ≈ 25×10⁻⁶ × (63.55/107.87) × 0.4816 ≈ 7.1×10⁻⁶; σ·f = 4.49 × 7.1×10⁻⁶ = **3.2×10⁻⁵ b**
- Zn-64 at 1 ppm: f_Zn64 ≈ 1×10⁻⁶ × (63.55/65.38) × 0.4863 ≈ 4.7×10⁻⁷; σ·f = 0.793 × 4.7×10⁻⁷ = **3.7×10⁻⁷ b**
- Zn-64 at 50 ppm (commercial "OFHC"): σ·f ≈ **1.8×10⁻⁵ b**

At the ASTM B170 limits: Ag-110m production exceeds Zn-65 by ~85×. Even when Zn is 50 ppm (commercial grade), Ag-110m remains comparable if Ag is near the 25 ppm limit.

**Key practical point:** Activation analyses of copper that include Zn but not Ag are missing the larger contributor for thermal-spectrum exposures.

Ag-108m (438-year half-life) additionally becomes a waste classification concern for repeated-pulse operation or high time-averaged fluences. With Ag-107 at ~52% abundance and σ_th(→Ag-108m) ≈ 35 b:
- f_Ag107 ≈ 25×10⁻⁶ × (63.55/107.87) × 0.5184 ≈ 7.6×10⁻⁶
- σ·f = 35 × 7.6×10⁻⁶ = **2.7×10⁻⁴ b** — larger still, but the product is very long-lived, so activity per pulse is very small

### 3.2 Zinc — Relevant Primarily for Commercial-Grade or C10200 Copper

For true C10100 (OFE, Zn ≤1 ppm), Zn-65 is a minor concern dominated by Ag-110m. For commercial "OFHC" copper (C10200, C11000) with 10–100 ppm Zn, Zn-65 becomes comparable to or exceeds Ag-110m:
- C10200 Zn spec: not in ASTM B170 — manufacturer-dependent; can be 5–50 ppm
- ETP copper (C11000): 99.9% Cu, Zn up to 500 ppm in some lots

**Recommendation:** Always clarify which copper grade (C10100, C10200, C11000) when specifying materials for activation analysis. The difference in Zn and Ag content between grades dramatically changes the medium-term dose picture.

### 3.3 Material Variants for This Tool

Two Cu variants recommended:
- **Cu (OFE, ASTM B170 C10100):** Ag=25 ppm, Zn=1 ppm, Ni=10 ppm, Fe=10 ppm
- **Cu (OFHC/commercial, C10200):** Ag=10 ppm, Zn=50 ppm, Ni=10 ppm, Fe=10 ppm

Current "Copper (OFHC)" entry should be updated to explicitly include Ag-109 and Ag-107 in the isotopic composition.

---

## 4. Pure Tungsten (W > 99.95%)

### 4.1 Intrinsic Activation — W→Re→Os Chain

This is not impurity-driven; it occurs in pure W under any neutron flux:

| Reaction | σ_th (b) | t½ | Notes |
|---|---|---|---|
| W-186(n,γ)→W-187 | 37.9 | 23.9 h | Short-term dominant; 685.7 keV (27.3%), 479.5 keV (21.6%) |
| W-184(n,γ)→W-185 | 1.70 | 75.1 d | Medium-term; 125.4 keV (0.019%) — weak gamma, mainly β⁻ |
| W-182(n,γ)→W-183m | ~20 | 5.15 s | Very short-lived, unimportant |
| Re-185(n,γ)→Re-186 | 112 | 3.718 d | Re builds up from W-186 β⁻ decay; 137.2 keV (9.47%) |

Re-186 and Re-187 accumulate as transmutation products. Over long exposures the Re inventory grows significantly; ITER DEMO analyses project 0.2 at.% Re after 14 operating years.

### 4.2 Tantalum Impurity

Ta is the most significant impurity in pure W from an activation standpoint.

- **ITER W specification:** Ta ≤50 µg/g (50 ppm) typical; some fusion-grade W < 10 ppm
- **Commercial/industrial W:** Ta can range from 50–500 ppm (Ta and W often co-processed)
- **W metallurgical note:** Ta is deliberately added to some W alloys (W-La₂O₃, W-Re, W-ThO₂), so composition documentation is critical

**Ta-181(n,γ)→Ta-182:** σ_th = 20.5 b; t½ = 114.74 d
Gammas: 1221.41 keV (27.3%), 1231.02 keV (11.6%), 68.41 keV (34.7%), 100.11 keV (14.2%)

At 100 ppm Ta in W:
- f_Ta181 ≈ 100×10⁻⁶ × (183.84/180.95) ≈ 1.016×10⁻⁴
- σ·f_th = 20.5 × 1.016×10⁻⁴ ≈ **0.00208 b**

Compare to bulk W-186: f_W186 ≈ 0.2843; σ·f_th = 37.9 × 0.2843 ≈ **10.77 b** (dominant short-term)

Ta-182 production is ~200× smaller than W-187 production in pure W, but Ta-182's half-life of 114 d means it persists well beyond W-187 (23.9 h). At 1–3 months post-pulse, Ta-182 may contribute comparably to or dominate over W-185 in the dose picture for heavily irradiated W with Ta content.

### 4.3 ITER W Specification Impurity Limits

From the ScienceDirect ITER tungsten paper (2015), maximum impurity contents:

| Impurity | Max (µg/g, ppm) | Typical (µg/g) |
|---|---|---|
| C | 30 | 6 |
| O | 20 | 2 |
| N | 5 | 1 |
| Fe | 30 | 8 |
| Ni | 20 | 2 |
| Si | 20 | 1 |
| Co | 5 | <1 |
| Ta | 50 | — |
| Mo | 100 | — |

**Cobalt in W:** 5 ppm max in ITER spec, typically <1 ppm.
- f_Co59 ≈ 5×10⁻⁶ × (183.84/58.93) ≈ 1.56×10⁻⁵
- σ·f_th_Co60 = 37.2 × 1.56×10⁻⁵ = **5.8×10⁻⁴ b**
- This is non-trivial for a long-term dose contributor even in pure W — at 5 ppm Co, Co-60 production in W components can exceed 10% of the W-185 production rate in terms of long-term (year-scale) dose

### 4.4 Material Variants for This Tool

Two W variants:
- **W (ITER/fusion grade):** Co ≤5 ppm, Ta ≤50 ppm, Ni ≤20 ppm, Fe ≤30 ppm
- **W (industrial grade):** Co ≤50 ppm, Ta ≤500 ppm, Ni ≤100 ppm, Mo ≤500 ppm

The current "Tungsten (pure)" entry should include Ta-181 in the isotopic composition.

---

## 5. Aluminum Alloys

### 5.1 Al-6061-T6 — Most Common Structural Grade

Nominal composition per ASTM B308 (6061):

| Element | Range (wt%) | Status | Primary activation product |
|---|---|---|---|
| Al | balance (~97%) | bulk | Na-24 via Al-27(n,α) — short-term |
| Mg | 0.80–1.20% | alloying | Na-24 via Mg-26(n,p)? Minor |
| Si | 0.40–0.80% | alloying | P-32? Negligible. Al-28 short-lived |
| Fe | ≤0.70% | residual | Mn-54 (via Fe-54(n,p)), Fe-59 |
| Cu | 0.15–0.40% | alloying | Cu-64 (12.7 h), short-term dose |
| Cr | 0.04–0.35% | alloying | Cr-51 (27.7 d), 320 keV gamma |
| **Zn** | **≤0.25%** | alloying | **Zn-65 (243.9 d) — medium-term** |
| **Mn** | **≤0.15%** | alloying | **Mn-56 (2.578 h) — dominant short-term** |
| Ti | ≤0.15% | trace | Sc-46 via Ti-46(n,p); minor |

**Manganese:** At ≤0.15% Mn (up to 1500 ppm), Mn-56 from Mn-55(n,γ) is the dominant short-term dose source in Al-6061:
- f_Mn55 ≈ 0.0015 × (26.98/54.94) ≈ 7.4×10⁻⁴
- σ·f_th = 13.3 × 7.4×10⁻⁴ = **0.0098 b** — significant

**Zinc:** At ≤0.25% Zn, Zn-65 is a significant medium-term contributor in Al-6061:
- f_Zn64 ≈ 0.0025 × (26.98/65.38) × 0.4863 ≈ 5.0×10⁻⁴
- σ·f_th = 0.793 × 5.0×10⁻⁴ = **3.97×10⁻⁴ b** — notable

**Chromium:** At 0.1% Cr, Cr-50(n,γ)→Cr-51 (27.7 d, 320 keV, 9.91%):
- f_Cr50 ≈ 0.001 × (26.98/51.996) × 0.04345 ≈ 2.25×10⁻⁵
- σ·f_th = 15.9 × 2.25×10⁻⁵ = **3.6×10⁻⁴ b** — comparable to Zn

### 5.2 Al-1100 vs. Al-6061 vs. Al-5052

For pulsed power applications, material choice matters:

| Grade | Mn (%) | Zn (%) | Cu (%) | Mg (%) | Activation concern |
|---|---|---|---|---|---|
| Al-1100 | ≤0.05 | ≤0.10 | 0.05–0.20 | — | Low Mn → less short-term dose |
| Al-6061 | ≤0.15 | ≤0.25 | 0.15–0.40 | 0.8–1.2 | Moderate |
| Al-5052 | ≤0.10 | ≤0.10 | ≤0.10 | 2.2–2.8 | Low Mn/Zn |
| Al-7075 | ≤0.30 | 5.1–6.1 | 1.2–2.0 | 2.1–2.9 | High Zn! Zn-65 dominant |

**Al-7075 warning:** With 5–6% Zn, Al-7075 has dramatically higher Zn-65 activation than 6061. For applications near the neutron source, 7075 should be evaluated carefully or replaced with lower-Zn grades if medium-term personnel access is required.

### 5.3 Sodium Trace in Aluminum

Na-23 is not a specified impurity in ASTM aluminum specifications but enters from:
- Hall-Héroult process electrolyte (NaF/AlF₃/cryolite) — can leave Na contamination
- Sodium-based flux used during casting
- Typical levels: 1–20 ppm Na in commercial Al alloys

At even 10 ppm Na: f_Na23 ≈ 10×10⁻⁶ × (26.98/22.99) ≈ 1.17×10⁻⁵
σ·f_th(Na-24) = 0.529 × 1.17×10⁻⁵ = **6.2×10⁻⁶ b** — small.

However, Na-24 emits a penetrating 2.754 MeV gamma (99.9%) and at short cooling times (< 1 day) even small quantities are noticeable. For concrete and Al-containing systems this is well-documented.

---

## 6. A36 Structural Steel

A36 is a low-carbon structural steel (ASTM A36). It is not specified for nuclear applications and impurity levels are relatively uncontrolled.

**Nominal composition ranges:**

| Element | Range (wt%) | Activation concern |
|---|---|---|
| Fe | balance (~98%) | Fe-59 (44.5 d), Fe-55 (2.73 y) via Ni(n,p)? No — Fe-54(n,p)→Mn-54 |
| Mn | 0.80–1.20% | Mn-56 (2.578 h) dominant short-term; Mn-54 (312 d) medium |
| C | ≤0.26% | Low activation; C-14 from N-14(n,p) if N impurities |
| Si | 0.15–0.40% | Low |
| Cu | ≤0.20% | Cu-64 short-term |
| Co | **not specified** | **Co-60 highly variable — major concern** |
| Nb | **not specified** | **Nb-94 — possible from scrap** |

A36 is typically made from scrap and can have Co content ranging from 500–3000 ppm with no specification requirement. This makes it a **poor choice for components that may see significant neutron flux**, both because Co-60 activation is unpredictable and because it cannot be reliably characterized without elemental analysis.

**Key recommendation:** A36 used in structural applications near the primary neutron source should be characterized (ICP-MS or OES) for Co and Nb content. If dose rates at 1–5 years cooling are a concern, low-Co or pre-characterized steel should be specified.

---

## 7. Material Database Recommendations

### 7.1 Priority Additions to This Tool

The following impurity-bearing isotopes should be added to material isotopic compositions in `data.py`:

| Material | Isotope to add | Atom fraction (approx.) | Why |
|---|---|---|---|
| SS-316 (commercial) | Co-59 | 1.5×10⁻³ | Co-60: dominant long-term dose |
| SS-316 (nuclear grade) | Co-59 | 1.0×10⁻⁴ | Co-60: still significant |
| Cu (all grades) | Ag-109 | 7.1×10⁻⁶ (25 ppm Ag) | Ag-110m: primary medium-term contributor |
| Cu (all grades) | Ag-107 | 7.6×10⁻⁶ (25 ppm Ag) | Ag-108m: 438 y waste concern |
| W (ITER grade) | Ta-181 | 1.0×10⁻⁴ (50 ppm Ta) | Ta-182: medium-term contributor |
| W (industrial) | Ta-181 | 5.1×10⁻⁴ (100 ppm Ta) | Ta-182: significant |
| Al-6061 | — | already has Mn, Zn, Cu as bulk | Add Cr-50 explicitly |

### 7.2 New REACTIONS Entries Needed

| Target | Reaction | Product | σ_th (b) | t½ | Priority |
|---|---|---|---|---|---|
| Ag-109 | (n,γ) | Ag-110m | 4.49 | 249.8 d | HIGH |
| Ag-107 | (n,γ) | Ag-108m | ~35 | 438 y | HIGH |
| Nb-93 | (n,γ) | Nb-94 | 1.15 | 20,300 y | HIGH |
| Ta-181 | (n,γ) | Ta-182 | 20.5 | 114.74 d | HIGH |
| Cr-50 | (n,γ) | Cr-51 | 15.9 | 27.7 d | MEDIUM |
| Mn-55 | (n,γ) | Mn-56 | 13.3 | 2.578 h | MEDIUM |
| Cu-63 | (n,γ) | Cu-64 | 4.5 | 12.701 h | MEDIUM |
| Fe-58 | (n,γ) | Fe-59 | 1.31 | 44.495 d | MEDIUM |
| Sb-121 | (n,γ) | Sb-122 | 5.8 | 2.724 d | LOW |
| Sb-123 | (n,γ) | Sb-124 | 4.0 | 60.20 d | LOW |

### 7.3 Material Variants — Recommended Entries

**SS-316 (commercial, ~1500 ppm Co)**
- Add to existing SS-316 or create new entry
- Co-59 atom fraction: ~1.5×10⁻³
- Nb-93: ~5×10⁻⁵ (representing ~50 ppm Nb in virgin material)

**SS-316 (nuclear grade, ≤100 ppm Co)**
- New entry as "SS-316 (nuclear grade)"
- Co-59 atom fraction: ~1.0×10⁻⁴
- Nb-93: ~2×10⁻⁵ (representing ~20 ppm Nb, scrap-free melt)

**Copper (OFE, ASTM B170 C10100)**
- Update current OFHC Cu entry or rename
- Add Ag-109: 7.1×10⁻⁶, Ag-107: 7.6×10⁻⁶ (25 ppm total Ag, 52/48 natural abundance)
- Keep Zn-64 at 1 ppm equivalent

**Copper (commercial OFHC, C10200)**
- New entry "Copper (commercial OFHC)"
- Add Zn-64: ~4.7×10⁻⁶ (50 ppm Zn)
- Add Ag-109: 2.8×10⁻⁶ (10 ppm Ag)

**Tungsten (ITER fusion grade)**
- Update current W (pure) to add Ta-181: 1.0×10⁻⁴
- Co-59: 1.56×10⁻⁵ (5 ppm)

---

## 8. Summary: Impurity Activation Severity Ranking

Ranked by severity of impact on long-term (>1 year) dose or waste classification for a typical pulsed power fusion facility:

| Rank | Impurity | Host material | Long-term concern | Severity |
|---|---|---|---|---|
| 1 | Co-59 | SS-316 (commercial) | Co-60 dose driver (5.27 y) | Critical |
| 2 | Ag-109 | OFE/OFHC Cu | Ag-110m dose (250 d), Ag-108m waste (438 y) | High |
| 3 | Nb-93 | SS-316 (scrap) | Nb-94 waste classification violation (20,300 y) | High |
| 4 | Co-59 | W (>5 ppm Co) | Co-60 in W components | Moderate |
| 5 | Ta-181 | W (>50 ppm Ta) | Ta-182 medium-term (115 d) | Moderate |
| 6 | Zn-64 | Cu (commercial) | Zn-65 medium-term (244 d) | Moderate |
| 7 | Ag-107 | OFE/OFHC Cu | Ag-108m long-lived waste (438 y) | Moderate |
| 8 | Co-59 | Al-6061 (trace) | Co-60 trace (if Co impurity present) | Low-Moderate |
| 9 | Zn-64 | Al-7075 | Zn-65 — major for this alloy at 5-6% Zn | High for 7075 |
| 10 | Nb-93 | Inconel | Nb-94 in high-Nb Inconel alloys | Very High |

---

## 9. References

1. **[ORNL/TM-2020/1681]** Oak Ridge National Laboratory, "Best Practices for Shielding Analyses of Activated Metals at DOE Nuclear Facilities," ORNL/TM-2020/1681, 2020. DOI: 10.2172/1760244. Primary source for Co ranges in commercial SS, dose driver rankings, and activation analysis best practices.

2. **[Springer-2023-Decom]** Rönn A., et al., "Sampling, characterization, method validation, and lessons learned in analysis of highly activated stainless steel from reactor decommissioning," *Journal of Radioanalytical and Nuclear Chemistry*, 2023. DOI: 10.1007/s10967-023-09182-y. Source for Nb-94 exceeding Class C limits in Inconel X-750 and SS components.

3. **[EPRI-TR-112352]** Electric Power Research Institute, TR-112352, "Radiation Source Term — Materials Control: Cobalt Reduction in PWRs." Cited for low-cobalt SS specifications and EPRI methodology. https://restservice.epri.com/publicdownload/TR-112352/0/Product

4. **[Sandmeyer-304CO]** Sandmeyer Steel Company, "304CO Cobalt-Restricted Stainless Steel Plate," product specification. Co ≤500 ppm. https://www.sandmeyersteel.com/alloy-304co/

5. **[ASTM-B170]** ASTM International, "B170 Standard Specification for Oxygen-Free Electrolytic Copper — Refinery Shapes," current edition. Impurity limits: Ag ≤25 ppm, Zn ≤1 ppm (C10100). https://www.astm.org/Standards/B170.htm

6. **[Tanaka-2003-Ag]** Tanaka T. et al., "Measurement of the Thermal Neutron Capture Cross Section and the Resonance Integral of the ¹⁰⁹Ag(n,γ)¹¹⁰ᵐAg Reaction," *Journal of Nuclear Science and Technology*, 40(3), 2003. σ_th(→Ag-110m) = 4.12±0.10 b, RI = 67.9±3.1 b. DOI: 10.1080/18811248.2003.9715341

7. **[Rieth-2015-W]** Rieth M. et al., "Use of tungsten material for the ITER divertor," *Nuclear Materials and Energy*, 2015. ITER W specification: Co <5 ppm, Ta <50 ppm, Fe <30 ppm, Ni <20 ppm. DOI: 10.1016/j.nme.2015.xx (ScienceDirect)

8. **[OSTI-Nb94]** National Low-Level Waste Management Program, "Radionuclide Report Series, Volume 2: Niobium-94," DOE/LLW-107, 1995. UNT Digital Library. Key reference for Nb-94 classification limits and decommissioning hazard ranking. https://digital.library.unt.edu/ark:/67531/metadc624288/

9. **[OSTI-Decom-Waste]** Aarrestad T.K. et al., "Radionuclide characterization of reactor decommissioning waste and neutron-activated metals," OSTI Technical Report, 1994. OSTI 10170334. https://www.osti.gov/biblio/10170334

10. **[ENDF-VIII]** Brown D.A. et al., "ENDF/B-VIII.0," *Nuclear Data Sheets*, 148, 1–142, 2018. DOI: 10.1016/j.nds.2018.02.001. Source for all cross-section values cited (σ_th, σ_14MeV).

11. **[NNDC-NuDat3]** National Nuclear Data Center, NuDat 3, 2023. https://www.nndc.bnl.gov/nudat3/. Source for half-lives, decay modes, and gamma intensities.

12. **[VTT-R-00184-20]** VTT Technical Research Centre of Finland, "Impurities in LWR Fuel and Structural Materials," VTT-R-00184-20, 2020. Cobalt ranges 1340–1630 ppm in commercial SS-316 samples analyzed. https://kyt2022.vtt.fi/pdf/raportit2019/KARAHDE_Impurities_in_LWR_fuel_and_structural_materials.pdf (requires institutional access)

---

*This document should be cross-referenced with the companion review: `low-activation-concrete-review.md` which covers concrete trace elements (Eu, Cs, Sc, Ba) in detail.*
