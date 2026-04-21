# Neutron Activation Impurity Reference — All Structural Materials

**Scope:** Impurity content and activation significance for 19 structural/shielding materials
relevant to fusion device design and facility radiation management. Covers steels, non-ferrous
metals, shielding materials, and moderators. Emphasis on impurities that produce long-lived
gamma emitters or drive waste classification.

**Last updated:** 2026-04-03
**Author:** Literature synthesis (training data + targeted search)

---

## Background: Why Impurities Dominate Activation

For most structural materials, bulk isotopes activate predictably and cool relatively fast
(Fe-55 t½=2.7 y, Mn-54 t½=312 d, Ni-63 t½=100 y). The impurities — present at tens to
thousands of ppm — frequently produce isotopes that (a) have much higher thermal cross-sections,
(b) have longer half-lives, or (c) emit harder gammas than the bulk products. The result is that
trace impurities at 10–2000 ppm often set the contact dose rate at 1–10 year cooling times and
determine waste classification. Systematic impurity control at procurement is the single most
effective low-activation design lever for non-RAFM steels.

Key references for this section:
- ORNL/TM-2020/1681 — best practices for activated metals characterization at DOE facilities
- EPRI TR-112352 — waste classification guidance for nuclear facility decommissioning
- IAEA TECDOC-2116 (2023) — fusion facility decommissioning and waste management
- NRC 10 CFR Part 61 — Class A/B/C activity concentration limits

---

## 1. Stainless Steel 304 (baseline) and SS-304 (commercial)

**Bulk composition:** Fe (~72 wt%), Cr (~18 wt%), Ni (~8 wt%), Mn (~2 wt%), with C ≤0.08%, Si ≤1%, P ≤0.045%, S ≤0.030%.

**Bulk activation products (in decreasing dose importance at 1–5 y cooling):**

| Isotope | Reaction | t½ | Eγ (keV) | Note |
|---------|----------|----|----------|------|
| Fe-55   | Fe-54(n,γ) | 2.73 y | none (EC) | Dominant contact dose at >5 y; NRC Class C 40,000 Ci/m³ |
| Mn-54   | Fe-54(n,p), Mn-55(n,2n) | 312 d | 835 (100%) | Strong 835 keV gamma; fast flux dependent |
| Co-60   | Co-59(n,γ) | 5.27 y | 1173+1332 | **From impurity only** — see below |
| Ni-63   | Ni-62(n,γ) | 100 y | none (β) | Long-term waste classification driver; Class C 35 Ci/m³ |
| Cr-51   | Cr-50(n,γ) | 27.7 d | 320 (9.9%) | Short-lived; important early |
| Fe-59   | Fe-58(n,γ) | 44.5 d | 1099+1292 | Medium-lived |

**Minor spec constituents — activation significance:**

| Element | Reaction | Product | t½ | σ_th (b) | Significance |
|---------|----------|---------|-----|---------|--------------|
| P-31    | P-31(n,γ) | P-32   | 14.3 d | 0.172 | Pure β emitter; no external dose contribution; negligible |
| S-32    | S-32(n,p) | P-32   | 14.3 d | ~0.54 mb (fast) | Fast only, very small cross-section |
| Si-28   | Si-28(n,p) | Al-28 | 2.24 min | fast only | Prompt/very short-lived; irrelevant for structural dose |
| Si-30   | Si-30(n,γ) | Si-31 | 2.62 h | 0.107 | Short-lived; some early shutdown dose |
| C-12    | C-12(n,γ) | C-13  | stable | 3.5 mb | Negligible activation |
| C-13    | C-13(n,γ) | C-14  | 5730 y | 1.37 mb | C-14 in steel is a long-term waste concern at ppm levels; however at ≤0.08 wt% C in SS, atom fraction is ~0.36% → C-14 production is small but non-zero; primary concern in concrete and graphite |

**Conclusion for SS-304 baseline:** Minor spec constituents (C, Si, P, S) contribute negligibly to external gamma dose. Their inclusion in the baseline composition is correct for completeness but the activation products are either pure beta, very short-lived, or have negligible cross-sections. The baseline entry is a valid lower-bound comparator.

**Critical impurities in SS-304 commercial:**

| Impurity | Typical ppm | Reaction | Product | t½ | Significance |
|----------|-------------|----------|---------|-----|--------------|
| Co | 1340–2570 ppm (commercial); ≤500 ppm nuclear grade; ≤100 ppm reactor grade | Co-59(n,γ) | Co-60 | 5.27 y | **CRITICAL** — 60–95% of external dose at 2–5 y (ORNL/TM-2020/1681). Hard 1173/1332 keV gammas. VTT-R-00184-20 measured 1340–2570 ppm range in commercial 304/316. |
| Nb | 0–3000 ppm (scrap-fed heats) | Nb-93(n,γ) | Nb-94 | 20,300 y | **HIGH** — Class C limit = 0.2 Ci/m³ (most restrictive for metals, EPRI TR-112352). Even 50 ppm Nb at high fluence can exceed Class C. |
| Mo | 0–7500 ppm (some heats) | Mo-98(n,γ); Mo-92(n,p) | Mo-99 (66 h); Nb-92m (10 d) | — | Moderate. Tc-99 (t½=211 ky) downstream waste concern. |

**References:** ORNL/TM-2020/1681; VTT-R-00184-20; EPRI TR-112352; ENDF/B-VIII.0.

---

## 2. Stainless Steel 316 (commercial and nuclear grade)

Identical bulk activation discussion to SS-304. Key difference: 2.5 wt% Mo adds meaningful Mo activation products. Co impurity modeled at 1500 ppm (commercial) and 100 ppm (nuclear grade).

**Additional bulk activation from Mo (2.5 wt%):**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) |
|----------|---------|----|----------|---------|
| Mo-98(n,γ) | Mo-99 | 65.9 h | 739 (12%), 181 (6%) | 0.130 |
| Mo-92(n,p) | Nb-92m | 10.15 d | 934 (99%) | 0.068 (14 MeV) |
| Mo-100(n,γ) | Mo-101 | 14.6 min | 590, 1012 | 0.199 |

Tc-99 (t½=211,000 y, pure β) from Mo-99 decay chain: long-term groundwater/waste concern.

**Nb impurity (50 ppm commercial, 20 ppm nuclear grade):** Same Nb-94 waste classification concern as SS-304. Nuclear-grade procurement specifications (per Sandmeyer 304CO) typically limit Nb to <100 ppm and Co to <500 ppm.

**References:** VTT-R-00184-20; ORNL/TM-2020/1681; ENDF/B-VIII.0; EPRI TR-112352.

---

## 3. A36 Carbon Steel

**Bulk composition:** Fe (~98.5 wt%), Mn (≤1.2 wt%), C (≤0.26 wt%), Si (≤0.40 wt%), P (≤0.04 wt%), S (≤0.05 wt%), Cu (≤0.2 wt% in some grades).

**Key point:** A36 is typically produced from scrap steel with no controlled composition beyond mechanical properties. This makes it the worst-case steel for activation impurities among common structural grades.

**Bulk activation products:** Same Fe/Mn/Cr products as SS-304 minus Cr and Ni (A36 has little Cr or Ni). Fe-55 and Mn-54 dominate.

**Critical impurities — uncontrolled in A36:**

| Impurity | Typical range | Reaction | Product | t½ | Significance |
|----------|--------------|----------|---------|-----|--------------|
| Co | 50–5000 ppm (scrap-origin, highly variable) | Co-59(n,γ) | Co-60 | 5.27 y | **CRITICAL** — highest uncertainty of any common steel. Scrap-origin A36 from mixed recycled steel can carry 1000–5000 ppm Co depending on source composition. |
| Cu | 500–2000 ppm | Cu-63(n,γ), Cu-65(n,γ) | Cu-64 (12.7 h), Zn-65 (244 d) | — | Moderate — Cu residual in scrap steel is common; Zn-65 from Cu-64 decay is an early-to-mid dose contributor |
| Ni | 500–3000 ppm | Ni-58(n,p), Ni-62(n,γ) | Co-58 (70.9 d), Ni-63 (100 y) | — | Moderate — Co-58 from Ni-58(n,p) significant at 14 MeV; Ni-63 long-lived waste |
| Nb | 0–500 ppm (scrap) | Nb-93(n,γ) | Nb-94 | 20,300 y | High — same waste classification concern as SS-304 |
| Mo | 0–2000 ppm | Mo-98(n,γ) | Mo-99 | 66 h | Low-moderate |

**Recommendation:** A36 should be treated as the worst-case activation scenario for carbon steel structural elements. For any fusion facility application, measured elemental analysis (ICP-OES or XRF) before irradiation is strongly recommended. Modeled in data.py with nominal Co at 2000 ppm, Cu at 1000 ppm, Ni at 1000 ppm as conservative representative values.

**References:** ORNL/TM-2020/1681; EPRI TR-112352; NRC NUREG/CR-6280.

---

## 4. EUROFER97 (Reduced Activation Ferritic-Martensitic Steel)

**Bulk composition:** 8.7 wt% Cr, 1.0 wt% W, 0.2 wt% V, 0.1 wt% Ta, 0.4 wt% Mn, balance Fe.

**Design philosophy:** EUROFER97 was specifically engineered for low activation by eliminating or minimizing elements with problematic activation products. Ni, Mo, Nb, Cu are all intentionally excluded or held to extremely low residual levels (<100 ppm each). The result is that the dominant long-term products are all within the reduced-activation category.

**Bulk activation products:**

| Isotope | Reaction | t½ | Eγ (keV) | Note |
|---------|----------|----|----------|------|
| Fe-55   | Fe-54(n,γ) | 2.73 y | none | Dominant at >5 y |
| Mn-54   | Fe-54(n,p), Mn-55(n,2n) | 312 d | 835 | |
| Cr-51   | Cr-50(n,γ) | 27.7 d | 320 | Short-lived |
| W-185   | W-184(n,γ) | 75.1 d | 125 | Moderate |
| W-187   | W-186(n,γ) | 23.7 h | 686, 772 | Short-lived |
| Re-186  | W-186(n,γ)→W-187→Re-187→... | chain | — | Re/Os transmutation chain (see W section) |
| Ta-182  | Ta-181(n,γ) | 114.7 d | 1221, 1231 | From 0.1 wt% Ta (intentional alloying element) |
| V-52    | V-51(n,γ) | 3.75 min | 1434 | Very short-lived; prompt dose only |

**Key advantage:** Because Ni, Mo, Nb, Cu are absent, EUROFER97 lacks Co-60, Ni-63, Nb-94, Mo-99, Zn-65. This dramatically reduces long-term dose. Lindau et al. (2005) showed EUROFER97-activated material reaches hands-on contact dose within 50–100 years post-shutdown, vs. thousands of years for standard 316SS.

**Residual impurity concerns in EUROFER97:**

| Impurity | Spec limit | Reaction | Product | t½ | Significance |
|----------|-----------|----------|---------|-----|--------------|
| Ni | <100 ppm | Ni-58(n,p) | Co-58 | 70.9 d | Low; sub-ppm production |
| Mo | <100 ppm | Mo-98(n,γ) | Mo-99 | 66 h | Low |
| Nb | <10 ppm | Nb-93(n,γ) | Nb-94 | 20,300 y | Marginal; very low Nb spec is critical |
| Co | <50 ppm | Co-59(n,γ) | Co-60 | 5.27 y | Low — see spec; negligible vs. bulk products |

**References:** Lindau et al. 2005 (Fusion Eng. Design); EUROfusion EUROFER spec sheet; IAEA TECDOC-2116.

---

## 5. Copper (OFHC, C10100)

**Bulk composition:** ≥99.99% Cu. Two stable isotopes: Cu-63 (69.17%), Cu-65 (30.83%).

**Bulk activation:**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) |
|----------|---------|----|----------|---------|
| Cu-63(n,γ) | Cu-64 | 12.7 h | 511 (β+, 38%) | 4.50 |
| Cu-65(n,γ) | Cu-66 | 5.12 min | 1039 | 2.17 |
| Cu-63(n,2n) | Cu-62 | 9.67 min | 511 | fast only |
| Zn-64(n,γ) | Zn-65* | 243.9 d | 1116 (50.2%) | 0.47 b on Zn-64 | *From Zn impurity only in C10100 |

**Critical finding — Ag dominates over Zn in C10100 OFE copper:**

ASTM B170 (C10100 OFE copper specification): Ag ≤25 ppm total, Zn ≤1 ppm max. At these limits, Ag-110m from Ag-109(n,γ) is the primary medium-term dose driver, not Zn-65.

σ·f comparison at C10100 specification limits (thermal activation):
- Zn-65 (Zn ≤1 ppm): σ·f_th ≈ 0.47 × 9.5×10⁻⁷ = 4.5×10⁻⁷ b·atom⁻¹ (negligible)
- Ag-110m (Ag ≤25 ppm): σ·f_th ≈ 4.12 × 1.42×10⁻⁵ = 5.8×10⁻⁵ b·atom⁻¹ (~130× higher)

This is a critical correction to the common engineering assumption that Zn-65 dominates Cu activation. For commercial-grade OFHC with relaxed Ag limits, the ranking may differ.

**Impurity table for Cu (OFHC):**

| Impurity | ASTM C10100 limit | Reaction | Product | t½ | Eγ (keV) | Significance |
|----------|------------------|----------|---------|-----|----------|--------------|
| Ag (total) | ≤25 ppm | Ag-109(n,γ) → Ag-110m | Ag-110m | 249.8 d | 658, 885, 937 | **CRITICAL** — dominates medium-term dose at C10100 spec. σ_th (isomeric) = 4.12 b (Tanaka et al. 2003). |
| Ag (total) | ≤25 ppm | Ag-107(n,γ) → Ag-108m | Ag-108m | 438 y | 434, 614, 723, 879 | **HIGH** — long-lived waste concern. σ_th = 35 b (93% isomeric fraction). |
| Zn | ≤1 ppm | Zn-64(n,γ) | Zn-65 | 244 d | 1116 | **LOW** at C10100 spec (negligible vs. Ag). Significant only in commercial OFHC (C10200) where Zn may reach 10–100 ppm. |
| Co | ≤5 ppm (typical) | Co-59(n,γ) | Co-60 | 5.27 y | 1173, 1332 | Low at typical Cu purity levels |
| Ni | ≤5 ppm | Ni-58(n,p) | Co-58 | 70.9 d | 811 | Low |

**References:** ASTM B170; Tanaka et al. 2003 (JNST 40:831); ORNL/TM-2020/1681; JET dose rate paper (Sci. Reports 2019); NNDC NuDat3.

---

## 6. Aluminum 6061

**Bulk composition (ASTM B209, T6):** Al ≥95.8 wt%, Mg 0.8–1.2 wt%, Si 0.4–0.8 wt%, Cu 0.15–0.40 wt%, Cr 0.04–0.35 wt%, Fe ≤0.7 wt%, Zn ≤0.25 wt%, Ti ≤0.15 wt%, Mn ≤0.15 wt%.

This is substantially different from pure aluminum. Al-27 dominates, but Mg, Si, Cu, Cr, Fe, and Zn are bulk components with their own activation.

**Bulk activation products:**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) | Note |
|----------|---------|----|----------|---------|------|
| Al-27(n,γ) | Al-28 | 2.24 min | 1779 (100%) | 0.231 | Short-lived; prompt dose |
| Al-27(n,α) | Na-24 | 14.96 h | 1369+2754 | 0.725 mb (thermal); large at 14 MeV | Hard gammas; 14 MeV flux dependent |
| Mg-26(n,γ) | Mg-27 | 9.46 min | 844, 1015 | 0.038 | Short-lived |
| Si-28(n,p) | Al-28 | 2.24 min | 1779 | fast only | Short-lived |
| Si-30(n,γ) | Si-31 | 2.62 h | 1266 | 0.107 | Short-lived |
| Cu-63(n,γ) | Cu-64 | 12.7 h | 511 | 4.50 | From 0.15–0.40 wt% Cu |
| Fe-56(n,γ) | Fe-57m | prompt | — | — | Stable product |
| Fe-58(n,γ) | Fe-59 | 44.5 d | 1099, 1292 | 1.31 | From ≤0.7 wt% Fe |
| Cr-50(n,γ) | Cr-51 | 27.7 d | 320 | 15.9 | From Cr content |
| Zn-64(n,γ) | Zn-65 | 244 d | 1116 | 0.47 | From ≤0.25 wt% Zn |

**Key Al-6061 observation:** Unlike pure Al, this alloy has meaningful Cr (up to 0.35 wt%), Cu, and Zn as bulk components. Cr-51 and Zn-65 production are not trace-level. Na-24 from Al-27(n,α) dominates the short-term dose.

**Impurity concerns specific to 6061:**

| Impurity | Content | Reaction | Product | t½ | Significance |
|----------|---------|----------|---------|-----|--------------|
| Fe | ≤0.7 wt% (bulk) | Fe-58(n,γ) | Fe-59 | 44.5 d | Moderate — Fe-59 is a 1.1/1.3 MeV gamma emitter; significant in first few months |
| Co | trace (uncontrolled) | Co-59(n,γ) | Co-60 | 5.27 y | Depends on scrap origin; often 10–100 ppm in commercial Al alloys |
| Eu | trace (~0.1–1 ppm) | Eu-151(n,γ) | Eu-152 | 13.5 y | Low at these levels but Eu-152 is a hard gamma emitter |

**Al-26 from Al-27(n,2n):** Long-lived product (t½=720,000 y) but very small 14 MeV cross-section (~0.07 b). At fusion neutron fluences relevant to structural Al, Al-26 production is negligible for short-to-medium term activation but is noted as the very long-term residual isotope in reduced-activation Al assessments (OSTI Ti assessment uses this as comparator).

**References:** ASTM B209; ORNL/TM-2020/1681; ENDF/B-VIII.0; NNDC NuDat3.

---

## 7. Tungsten — ITER Grade and Industrial

**Bulk composition:** W-180 (0.12%), W-182 (26.50%), W-183 (14.31%), W-184 (30.64%), W-186 (28.43%).

**Bulk activation (Re/Os transmutation chain):**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) |
|----------|---------|----|----------|---------|
| W-184(n,γ) | W-185 | 75.1 d | 125 | 1.72 |
| W-186(n,γ) | W-187 | 23.7 h | 686 (26%), 772 (4%), 685 | 37.9 |
| W-186→Re-187 | Re-187 | 4.35×10¹⁰ y | stable essentially | — |
| Re-187(n,γ) | Re-188 | 17.0 h | 155 (15%) | 76.4 |
| Re-185(n,γ) | Re-186 | 3.72 d | 137 (9%) | 112 |
| Re-186→Os-186 | Os-186 | stable | — | — |
| W-183(n,γ) | W-184 | stable | — | 10.1 |

The Re/Os transmutation chain is the dominant long-term activation concern in W. Re builds up at high fluence; Re-188 (t½=17 h) and Re-186 (t½=3.7 d) provide post-shutdown dose. At very high fluence, Os and Ir isotopes accumulate.

**Impurity table — ITER grade vs. industrial:**

| Impurity | ITER grade (ppm) | Industrial (ppm) | Reaction | Product | t½ | Significance |
|----------|-----------------|-----------------|----------|---------|-----|--------------|
| Ta | ≤50 | ≤500 | Ta-181(n,γ) | Ta-182 | 114.7 d | **HIGH** — σ_th=20.5 b; strong 1221/1231 keV gammas. Ta-182 is the dominant medium-term dose driver in W (after the Re chain settles). |
| Co | ≤5–10 | ≤30 | Co-59(n,γ) | Co-60 | 5.27 y | Moderate in ITER grade; significant in industrial at >30 ppm |
| Fe | ≤30 | ≤300 | Fe-58(n,γ) | Fe-59 | 44.5 d | Moderate — Fe impurity in industrial W is non-trivial |
| Ni | ≤20 | ≤100 | Ni-62(n,γ) | Ni-63 | 100 y | Long-term waste classification concern at higher levels |
| Mo | ≤100 | ≤500 | Mo-98(n,γ) | Mo-99 | 66 h | Moderate in industrial grade |
| K | ≤100 | ≤500 | K-41(n,γ) | K-42 | 12.4 h | Short-lived; minor |

**References:** Rieth et al. 2015 (IOP MSE); ITER Material Properties Handbook (IAEA); ENDF/B-VIII.0; Leblond et al. — W activation in DEMO (Fusion Eng. Design 2023).

---

## 8. Titanium Alloy Ti-6Al-4V

**Bulk composition:** Ti (89–91 wt%), Al (5.5–6.75 wt%), V (3.5–4.5 wt%), Fe ≤0.40 wt%, O ≤0.20 wt%, C ≤0.10 wt%, N ≤0.05 wt%, H ≤0.015 wt%.

Ti-6Al-4V is considered a **reduced-activation** structural material in the fusion literature. It was used for the TPX (Tokamak Physics Experiment) vacuum vessel specifically for its low residual radioactivity at 10–100 year timescales.

**Bulk activation products:**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) | Note |
|----------|---------|----|----------|---------|------|
| Ti-46(n,γ) | Ti-47 | stable | — | 0.59 | |
| Ti-48(n,γ) | Ti-49 | stable | — | 7.93 | |
| Ti-50(n,γ) | Ti-51 | 5.76 min | 320, 928 | 0.179 | Short-lived |
| Ti-47(n,p) | Sc-47 | 3.35 d | 159 (68%) | 1.5 mb (fast) | Fast flux |
| Ti-48(n,p) | Sc-48 | 43.7 h | 984, 1037, 1312 | 0.037 (fast) | Fast flux; hard gammas |
| Ti-46(n,2n) | Ti-45 | 3.08 h | 511 | fast | Short-lived |
| Al-27(n,α) | Na-24 | 14.96 h | 1369+2754 | 0.725 mb | From 6 wt% Al; large Na-24 source; dominant early shutdown dose |
| Al-27(n,γ) | Al-28 | 2.24 min | 1779 | 0.231 | Very short-lived |
| V-51(n,γ) | V-52 | 3.75 min | 1434 | 4.90 | Very short-lived; prompt dose |
| V-51(n,p) | Ti-51 | 5.76 min | 320, 928 | fast | |
| Al-27(n,2n) | **Al-26** | **720,000 y** | 1809 (100%) | ~0.07 b at 14 MeV | **Long-term residual** — very low production rate, but essentially permanent. Pure γ emitter (1809 keV). Identified as the dominant very-long-term activation product in Ti alloys (OSTI assessment). |

**Key finding:** Ti-6Al-4V is genuinely low-activation at 1–100 year timescales compared to SS or W. The only long-term concern is Al-26 from Al-27(n,2n) at 14 MeV. Practical doses from Al-26 are negligible at fusion-device fluences on human timescales, but it is the dominant residual at >1000 year cooling.

**Tramp impurity concerns:**

| Impurity | Typical range | Reaction | Product | t½ | Significance |
|----------|--------------|----------|---------|-----|--------------|
| Co | 10–100 ppm (depends on source) | Co-59(n,γ) | Co-60 | 5.27 y | Moderate — identified as a detrimental tramp impurity in Ti (OSTI 5171710) |
| Ni | 50–300 ppm | Ni-58(n,p) | Co-58 | 70.9 d | Moderate — especially at 14 MeV |
| Ag | trace | Ag-109(n,γ) | Ag-110m | 250 d | Minor |
| Nb | 0–500 ppm | Nb-93(n,γ) | Nb-94 | 20,300 y | High if present — same waste classification concern |

**Note on application:** Ti-6Al-4V is the dominant high-strength titanium alloy used in aerospace and vacuum system structures. In a fusion device context it is used for vacuum vessel components, cryostat supports, and RF system hardware where its combination of strength, low activation, and non-magnetic properties are all valuable.

**References:** OSTI 5171710 (Assessment of Ti alloys for fusion, ORNL); OSTI ORNL/TM-2008/137 (Survey of radiation effects in Ti alloys); Zinkle & Snead 1995 (Use of Ti in fusion, Fusion Eng. Design); ENDF/B-VIII.0.

---

## 9. Tantalum (Pure)

**Bulk composition:** Ta-181 (99.988%), Ta-180m (0.012%, nearly stable t½ >> 10¹⁵ y). Density 16.65 g/cm³.

**Note on conservatism:** Pure Ta is modeled here as a conservative upper bound. Structural Ta applications most commonly use Ta-2.5W alloy (2.5 wt% W for improved strength), which has lower Ta atom fraction and therefore proportionally lower Ta-182 production. Pure Ta is noted in data.py accordingly.

**Bulk activation:**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) | Note |
|----------|---------|----|----------|---------|------|
| Ta-181(n,γ) | Ta-182 | 114.74 d | 1221 (27%), 1231 (12%), 68 (35%), 100 (14%), 1189 (17%) | 20.5 | **DOMINANT** — very high σ_th; Ta-182 is the primary activation product. Hard gammas drive contact dose. |
| Ta-181(n,2n) | Ta-180 | 8.15 h | 93 (37%) | fast | Short-lived |
| Ta-180m(n,γ) | Ta-181 | stable | — | large | Absorption into stable product; sink not source |

**Ta-182 is essentially the only significant activation product for pure Ta.** Ta-182 has a 1221 keV gamma that is strong and penetrating; contact dose rates will be high immediately post-irradiation, but the 115 day half-life means significant decay within 1–2 years. No very-long-lived products from bulk Ta activation.

**Impurity concerns:**

| Impurity | Typical ppm | Reaction | Product | t½ | Significance |
|----------|------------|----------|---------|-----|--------------|
| W | 10–100 ppm (major impurity in Ta) | W-186(n,γ) | W-187 | 23.7 h | Minor at trace levels; short-lived |
| Nb | 10–100 ppm | Nb-93(n,γ) | Nb-94 | 20,300 y | **Moderate** — Nb is the main concern in Ta; if present at >50 ppm, Nb-94 waste classification applies |
| Fe | 10–100 ppm | Fe-58(n,γ) | Fe-59 | 44.5 d | Minor |

**Note on Ta-2.5W alloy:** The W addition produces W-187 (t½=23.7 h, short-lived) and the longer Re chain products. At 2.5 wt% W, W-185 (t½=75 d) production is not negligible. For longer cooling times, the alloy version is actually slightly worse than pure Ta for dose. Pure Ta is conservative for the initial 1–2 years; for >2 years the W alloy is comparable due to W-185.

**References:** ENDF/B-VIII.0; NNDC NuDat3; Rieth et al. 2015 (W/Ta properties in fusion); IAEA TECDOC-2116.

---

## 10. Heavymet (90W-7Ni-3Fe)

**Bulk composition (by weight):** W 90 wt%, Ni 7 wt%, Fe 3 wt%. Density ~17.0 g/cm³. Produced by liquid-phase sintering.

**Application context:** Used as radiation shielding, collimators, and counterweights in experimental and fusion facilities. The high density provides excellent gamma and fast neutron attenuation in compact form factors. Preferred over pure W where machinability is required.

**Bulk activation — three-component system:**

*Tungsten component (90 wt%):* Same W isotopic activation as pure W (W-185, W-187, Re chain). See §7.

*Nickel component (7 wt%):*

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) |
|----------|---------|----|----------|---------|
| Ni-58(n,γ) | Ni-59 | 76,000 y | none (EC) | 4.61 | Long-lived waste concern; Class B/C threshold |
| Ni-62(n,γ) | Ni-63 | 100 y | none (β) | 14.5 | **Most restrictive** — NRC Class C 35 Ci/m³ |
| Ni-58(n,p) | Co-58 | 70.9 d | 811 (99%) | fast | Significant at 14 MeV; Co-58 hard gamma |
| Ni-60(n,p) | Co-60 | 5.27 y | 1173+1332 | fast | Co-60 production from Ni-60 at 14 MeV |

*Iron component (3 wt%):* Fe-55 (t½=2.73 y), Fe-59 (t½=44.5 d), Mn-54 from Fe-54(n,p). See SS-304 §1.

**Critical concern:** The Ni content in Heavymet is 7 wt% — far higher than the trace impurity levels in SS or W. Ni-63 (t½=100 y) at this level will dominate long-term waste classification. NRC Class C limit for Ni-63 is 35 Ci/m³ for activated metal. Heavily irradiated Heavymet will likely require careful waste classification analysis.

**Co production in Heavymet:** Co-58 is produced from Ni-58(n,p) at 14 MeV and Co-60 from Ni-60(n,p) — these are intrinsic products of the 7 wt% Ni, not just impurity-level. This is distinct from the Co *impurity* in SS.

**Impurity concerns:**

| Impurity | Typical ppm | Reaction | Product | t½ | Significance |
|----------|------------|----------|---------|-----|--------------|
| Co | 10–100 ppm (sintering impurity) | Co-59(n,γ) | Co-60 | 5.27 y | Moderate — on top of Co produced from Ni(n,p) |
| Mn | trace | Mn-55(n,γ) | Mn-56 | 2.58 h; also Mn-54 via (n,2n) | Mn-54 (312 d) significant if Mn >100 ppm |
| Ta | trace | Ta-181(n,γ) | Ta-182 | 114.7 d | Minor; depends on Ta in W feedstock |

**References:** ENDF/B-VIII.0; NNDC NuDat3; Royal Society Phil Trans 2018 (shielding in compact tokamak); ORNL/TM-2020/1681.

---

## 11. Tungsten Carbide — WC-Co Grade

**Bulk composition (typical WC-6Co grade):** WC 94 wt% (W 94 × 15.63/15.63 — see below), Co binder ~6 wt%. Stoichiometric WC: W = 97.79 wt% of WC, C = 12.01/195.85 = 6.13 wt% of WC.

Effective bulk weight fractions: W ≈ 88.1 wt%, C ≈ 5.78 wt%, Co ≈ 6 wt%.

**Application context in fusion:** WC is studied as an inboard neutron shielding material for compact spherical tokamaks (STEP, ST40 designs) and as collimator/diagnostic insert material. The combination of high-Z W (fast neutron/gamma attenuation) and C (neutron moderation) makes WC more compact than either pure W or SS for combined neutron+gamma shielding. Recent work (ScienceDirect 2025) specifically analyzes WC waste implications under fusion neutron spectra.

**Key activation issue:** Standard WC uses a **Co binder at 3–6 wt%** for sintering and toughness. This Co content is orders of magnitude higher than the Co impurity in SS (1500 ppm = 0.15 wt%). Co-60 production from the binder dominates activation completely and makes standard WC-Co a poor choice for any structural element with post-irradiation handling requirements.

**Activation breakdown:**

| Component | Dominant product | t½ | Significance |
|-----------|-----------------|-----|--------------|
| W (bulk) | W-185, W-187, Re chain | 75 d, 23.7 h, chain | Same as pure W. Long-lived Re/Os at high fluence. |
| C (6 wt%) | C-14 from N-14 impurity (n,p); minimal from C-12 | 5730 y | C-14 from trace N in WC feedstock (typically 50–200 ppm N). Long-lived waste. |
| Co binder (6 wt%) | Co-60 from Co-59(n,γ) | **5.27 y** | **COMPLETELY DOMINATES** all other activation products for the first 10–20 years. Contact dose from WC-Co after irradiation will be dominated by Co-60. |

**Comparison — WC-Co vs WC with Fe binder:**
Low-activation Fe-based binders (FeNi, FeCr, FeCo alternatives) are under development specifically to address this problem. Fe binders produce Fe-55 and Fe-59 instead of Co-60, reducing long-term dose and improving waste classification.

**Impurity concerns for WC feedstock:**

| Impurity | Typical ppm | Reaction | Product | t½ | Significance |
|----------|------------|----------|---------|-----|--------------|
| N in WC | 50–200 ppm | N-14(n,p) | C-14 | 5730 y | Cumulative waste concern; C-14 Class B limit 80 Ci/m³ |
| Ta | 50–200 ppm | Ta-181(n,γ) | Ta-182 | 114.7 d | Moderate in WC feedstock |
| Fe (residual) | 100–500 ppm | Fe-58(n,γ) | Fe-59 | 44.5 d | Minor |

**References:** ScienceDirect 2025 (WC waste implications in fusion); Royal Society Phil Trans 2018 (compact tokamak shielding); ResearchGate (W carbides and borides neutron shields); ENDF/B-VIII.0.

---

## 12. OPC Concrete (Ordinary Portland Cement)

**Typical bulk composition (ANSI/ANS-6.4-2006 standard mix):**
O (~52 wt%), Si (~21 wt%), Ca (~16 wt%), Al (~4 wt%), Fe (~2 wt%), H (~1 wt%), Na (~0.8 wt%), K (~0.6 wt%), Mg (~0.3 wt%), trace elements.

**Key long-term activation impurities in OPC concrete:**

| Impurity | Typical range | Reaction | Product | t½ | Significance |
|----------|--------------|----------|---------|-----|--------------|
| Eu | 0.5–2 ppm | Eu-151(n,γ) | Eu-152 | 13.5 y | **CRITICAL** — σ_th ≈ 5900 b (MACS). Eu-152 dominates OPC activation dose at 5–50 y in neutron environments (SCK-CEN bioshield study, JET). Hard gammas 344/1408 keV. |
| Co | 5–30 ppm | Co-59(n,γ) | Co-60 | 5.27 y | **HIGH** — even at 5 ppm, Co-60 contribution is significant. |
| Cs | 1–15 ppm | Cs-133(n,γ) | Cs-134 | 2.07 y | High — 605/796 keV gammas. Large σ_th = 29.0 b for Cs-133. |
| Na | ~8000 ppm (bulk cement) | Na-23(n,γ) | Na-24 | 14.96 h | Moderate — short-lived but hard gammas (1369, 2754 keV); dominates prompt post-shutdown dose |
| Ba | 100–500 ppm | Ba-130(n,γ) | Ba-131 | 11.5 d; Ba-137m | Low-moderate |
| Sc | 5–20 ppm | Sc-45(n,γ) | Sc-46 | 83.8 d | Moderate — σ_th = 27.2 b; 889/1121 keV gammas |
| K | ~5000 ppm (bulk) | K-41(n,γ) | K-42 | 12.4 h | Short-lived; moderate |
| Fe | ~20,000 ppm (bulk) | Fe-54(n,p), Fe-58(n,γ) | Mn-54, Fe-59 | 312 d, 44.5 d | Significant from bulk Fe content |

**Dominant activation sequence at different cooling times:**
- 0–24 h: Na-24 (hard 1369/2754 keV gammas from bulk Na)
- 1 d – 3 mo: Mn-54 (Fe bulk), Cs-134 (Cs impurity), Co-60 onset
- 3 mo – 10 y: Co-60 and Eu-152 co-dominant
- 10–50 y: Eu-152 dominant; Co-60 decays away
- >50 y: Eu-154 (8.6 y), Ba-133 (10.5 y), Sc-46, then approach clearance

**References:** SCK-CEN ITER bioshield study (OSTI 20902507); Kinno et al. 2007 (LAC development); IAEA TECDOC-2116; ORNL/TM-2020/1681; ENDF/B-VIII.0; Scientific Reports 2024 (natural radionuclides in building materials).

---

## 13. Limestone / Low-Activation Concrete (LAC)

**Composition design philosophy:** Replace siliceous (andesite/basalt) aggregate with limestone (CaCO₃-based) aggregate and use low-alkali cement. This reduces Na, K, Co, and Eu contents, addressing the dominant activation impurities in OPC concrete.

**Key compositional differences vs. OPC:**
- Lower Na (~0.1–0.3 wt% vs ~0.8 wt%): Na-24 production reduced 3–8×
- Lower K: K-42 reduced similarly
- Co reduced by selection of low-Co aggregate (limestone typically 1–5 ppm Co vs 15–30 ppm for basalt)
- Eu reduced (limestone 0.1–0.5 ppm vs OPC 0.5–2 ppm)
- Higher Ca content: Ca-48(n,γ)→Ca-49 (8.72 min) short-lived; no long-lived Ca product of concern
- Higher C content: C-14 concern from N impurity in binder

**Remaining activation concerns in LAC:**

| Impurity | LAC range | OPC range | Reduction factor | Significance |
|----------|----------|----------|-----------------|--------------|
| Eu | 0.1–0.5 ppm | 0.5–2 ppm | 3–10× | **Still dominant at >5 y** — Eu cannot be fully eliminated from aggregate |
| Co | 1–5 ppm | 5–30 ppm | 3–6× | Significant improvement |
| Na | 1000–3000 ppm | ~8000 ppm | 3–8× | Good improvement for early shutdown dose |
| Cs | 0.5–5 ppm | 1–15 ppm | 2–3× | Moderate improvement |

Kinno et al. (2007) reported LAC dose rate reduction of 1/300–1/400 vs. andesite aggregate for 14 MeV neutron irradiation at 1 year cooling, primarily driven by Co and Eu reduction.

**References:** Kinno et al. 2007 (Fujita LAC report); SCK-CEN bioshield study; IAEA TECDOC-2116; Maiorov et al. 2016 (ITER bio-shield).

---

## 14. Lead

**Bulk composition:** Pb-204 (1.4%), Pb-206 (24.1%), Pb-207 (22.1%), Pb-208 (52.4%). Density 11.35 g/cm³.

**Lead is a weak activator under thermal/epithermal neutron flux** — cross-sections are small for all Pb isotopes (Pb-208 σ_th = 0.00070 b; Pb-207 σ_th = 0.699 b; Pb-206 σ_th = 0.030 b). However under fast/14 MeV flux, (n,2n) and (n,3n) reactions become significant.

**Activation products:**

| Reaction | Product | t½ | Eγ (keV) | σ_th/14MeV |
|----------|---------|----|----------|----------|
| Pb-207(n,γ) | Pb-208 | stable | — | 0.699 b th |
| Pb-206(n,γ) | Pb-207m | 0.80 s | 570 | 0.030 b th |
| Pb-208(n,2n) | Pb-207m | 0.80 s | 570 | large (fast) |
| Pb-208(n,2n) | Pb-207 | stable | — | — |
| Pb-207(n,n') | Pb-207m | 0.80 s | 570 | fast | Short-lived |
| Pb-204(n,γ) | Pb-205 | **1.51×10⁷ y** | 975 (IC; low γ) | 0.65 b | **LONG-LIVED** — Pb-205 is a long-lived concern in Pb shielding; pure EC, very low dose rate but long-term waste |
| Pb-206(n,2n) | Pb-205 | 1.51×10⁷ y | — | significant at 14 MeV | Same long-term concern |

**Bismuth impurity** is the critical concern in lead:

| Impurity | Typical ppm | Reaction | Product | t½ | Significance |
|----------|------------|----------|---------|-----|--------------|
| Bi | 10–10,000 ppm (commercial Pb); <10 ppm nuclear grade | Bi-209(n,γ) | Bi-210 | 5.01 d | then → Po-210 (5.1 MeV α, t½=138 d) — **CRITICAL** — Po-210 is an extreme radiotoxic inhalation hazard. Not a gamma concern but a criticality contamination hazard if Pb becomes hot. Nuclear-grade Pb specifies Bi <10 ppm. |

**Note on Pb shielding application:** Lead is highly effective for gamma shielding (high Z, photoelectric dominance) but poor for fast neutrons (low inelastic cross-section without hydrogenous material). In fusion contexts, Pb is typically combined with polyethylene or concrete for combined n+γ shielding. Po-210 hazard from Bi impurity is the dominant decommissioning concern for activated Pb.

**References:** ENDF/B-VIII.0; NNDC NuDat3; IAEA TECDOC-2116; NRC NUREG/CR-6280.

---

## 15. Water (H₂O)

**Bulk composition (natural water):** H-1 (99.985%), H-2 (0.015%), O-16 (99.757%), O-17 (0.038%), O-18 (0.205%).

**Relevant activation products:**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) | Note |
|----------|---------|----|----------|---------|------|
| H-1(n,γ) | H-2 | stable | 2223 (capture γ) | 0.332 | Dominant thermal neutron capture; H-2 is stable, no activation |
| O-16(n,p) | N-16 | **7.13 s** | **6130 (67%), 7115 (5%)** | fast (threshold) | **VERY HIGH ENERGY** hard gammas; dominates prompt dose in water-cooled systems during operation. Activated coolant in water-cooled facilities. Short-lived — gone within 2 minutes. |
| O-17(n,α) | C-14 | 5730 y | none (β) | 0.235 | Low production rate but C-14 is a long-term tritiated water / waste concern |
| H-1(n,γ) | H-2 → T(n,γ) from D₂O | — | — | — | Tritium from D-T fusion is a separate contamination topic |
| O-18(n,γ) | O-19 | 26.9 s | 197 | 0.00016 | Negligible |
| H-2(n,γ) | H-3 (tritium) | 12.3 y | none (β) | 0.000519 | Very low production from deuterium in natural water; tritium waste concern |

**Key conclusion for water:** No significant long-lived gamma emitters from pure water activation. N-16 is the only significant activation product and it is gone within 2 minutes of shutdown. The primary activation concern in water coolant circuits is **activation of dissolved and suspended solids** — corrosion products (Fe, Ni, Co, Cr particles) that circulate and deposit in pipes/heat exchangers. This out-of-core activated corrosion product (OACP) problem is a major dose driver in water-cooled facilities and is separate from water chemistry activation itself.

**Tritium in D-T fusion facilities:** H-3 contamination of cooling water from tritium permeation through first-wall components is a design concern, but is managed as a tritium inventory issue rather than an activation/decay problem.

**References:** ENDF/B-VIII.0; NNDC NuDat3; IAEA Safety Standards (water chemistry and OACPs).

---

## 16. Silicon Dioxide (SiO₂)

**Bulk composition:** Si-28 (92.23%), Si-29 (4.67%), Si-30 (3.10%); O-16 (99.757%), O-17 (0.038%), O-18 (0.205%). Density 2.65 g/cm³ (quartz).

**Application context:** SiO₂ appears as: quartz aggregate in concrete, fused silica optics windows/viewports, ceramic insulators, and quartz vessel components.

**Activation products:**

| Reaction | Product | t½ | Eγ (keV) | σ_th (b) | Note |
|----------|---------|----|----------|---------|------|
| Si-30(n,γ) | Si-31 | 2.62 h | 1266 (0.07%) | 0.107 | Short-lived; minimal gamma |
| Si-28(n,p) | Al-28 | 2.24 min | 1779 (100%) | fast only | Very short-lived; fast flux |
| Si-29(n,p) | Al-29 | 6.56 min | 1273 (91%) | fast | Short-lived |
| Si-28(n,α) | Mg-25 | stable | — | fast | Stable product |
| O-16(n,p) | N-16 | 7.13 s | 6130 | fast | Same as water; negligible at shutdown |
| Al-28 decay → Mg-28 | Mg-28 | 20.9 h | 400, 1780 | — | Indirect chain; minor |

**Key conclusion:** SiO₂ is a very weak activator. All significant activation products are either short-lived (Al-28, Si-31, N-16) or produced only under fast flux conditions. No long-lived gamma emitters from the bulk Si-O system. SiO₂ components can be handled rapidly after shutdown.

**Impurity concerns in SiO₂:**

| Impurity | Typical range | Reaction | Product | t½ | Significance |
|----------|--------------|----------|---------|-----|--------------|
| Al | 100–10,000 ppm (natural quartz) | Al-27(n,γ) | Al-28 | 2.24 min | Negligible |
| Fe | 10–1000 ppm | Fe-58(n,γ) | Fe-59 | 44.5 d | Low-moderate in impure quartz |
| Na | 10–500 ppm | Na-23(n,γ) | Na-24 | 14.96 h | Moderate at higher Na levels; hard gammas |
| Co | 0.1–5 ppm | Co-59(n,γ) | Co-60 | 5.27 y | Minor; still worth noting for long-term dose |
| Eu | 0.01–1 ppm | Eu-151(n,γ) | Eu-152 | 13.5 y | Low but nonzero; same concern as in concrete |

High-purity fused silica (as used for optical components and viewports) can be as low as 1–10 ppm total metallic impurities and is essentially non-activating beyond the Al-28/Si-31 short-lived products.

**References:** ENDF/B-VIII.0; NNDC NuDat3; ANSI/ANS concrete composition standard; SCK-CEN bioshield study.

---

## Summary Severity Rankings

### Long-term dose (1–10 y cooling)

| Rank | Material | Driver | Half-life |
|------|----------|--------|-----------|
| 1 | WC-Co (standard) | Co-60 from 6 wt% Co binder | 5.27 y |
| 2 | Heavymet (WC-Ni-Fe) | Co-60 (Ni(n,p) + Co impurity) + Ni-63 | 5.27 y / 100 y |
| 3 | SS-304/316 commercial | Co-60 from ~1500 ppm Co impurity | 5.27 y |
| 4 | A36 carbon steel | Co-60 (uncontrolled Co in scrap) | 5.27 y |
| 5 | OPC concrete | Eu-152 (0.5–2 ppm Eu, σ_th ~9200 b) | 13.5 y |
| 6 | Tungsten (industrial) | Ta-182 + Re chain | 115 d + chain |
| 7 | Cu OFHC | Ag-110m (25 ppm Ag) | 250 d |
| 8 | Ta (pure) | Ta-182 | 115 d |
| 9 | Tungsten (ITER grade) | Re chain → Re-186/188 | days |
| 10 | SS-316 nuclear grade | Co-60 (100 ppm Co) — much reduced | 5.27 y |
| 11 | EUROFER97 | Fe-55, Ta-182 | 2.73 y, 115 d |
| 12 | Al 6061 | Na-24 (short), Zn-65, Fe-59 | 15 h, 244 d, 45 d |
| 13 | Ti-6Al-4V | Na-24 (short), Sc-47/48 | 15 h, 3–44 d |
| 14 | LAC concrete | Eu-152 (reduced), Co-60 | 13.5 y |
| 15 | Lead | Pb-205 (negligible γ), Bi→Po-210 concern | long |
| 16 | SiO₂ (pure) | Al-28, Si-31 (both very short) | minutes |
| 17 | Water | N-16 (shutdown only) | 7 s |

### Waste classification concern (long-lived isotopes, NRC 10 CFR 61)

| Isotope | t½ | NRC Class C limit | Primary material concern |
|---------|----|------------------|------------------------|
| Nb-94 | 20,300 y | 0.2 Ci/m³ | SS-316 commercial, A36, Inconel (scrap Nb) |
| Ni-63 | 100 y | 35 Ci/m³ | Heavymet (7 wt% Ni), SS, any Ni-bearing alloy |
| Co-60 | 5.27 y | 700 Ci/m³ | All commercial steels, WC-Co, Heavymet |
| Ag-108m | 438 y | no published limit | Cu OFHC at high fluence |
| Al-26 | 720,000 y | — | Ti-6Al-4V, Al-6061 at 14 MeV |
| Pb-205 | 1.51×10⁷ y | — | Pb shielding |
| C-14 | 5730 y | 80 Ci/m³ (Class B) | WC (N impurity), concrete, graphite |

---

## Material Variants Recommended in data.py

Based on this review, the following variants capture meaningful activation differences:

| Material | Variants | Differentiator |
|----------|----------|---------------|
| SS-304 | Baseline (no impurities), Commercial (Co 1500 ppm) | Co impurity drives all long-term dose |
| SS-316 | Commercial (Co 1500 ppm, Nb 50 ppm), Nuclear grade (Co 100 ppm, Nb 20 ppm) | Co + Nb impurity control |
| A36 | Single entry with conservative Co/Cu/Ni impurity estimates | Scrap-origin variability |
| Tungsten | ITER grade, Industrial | Ta/Co impurity levels |
| WC | WC-Co standard (6 wt% Co binder) | Co binder completely dominates |
| Concrete | OPC, LAC/Limestone | Eu/Co/Na reduction in LAC |
| Cu | OFHC C10100 only (Ag at 25 ppm max) | Ag-110m dominates over Zn |
| Ti-6Al-4V | Single entry (genuinely low-activation bulk) | Al-26 only very long-term concern |
| Ta | Pure Ta (conservative — note Ta-2.5W in real applications) | Ta-182 only significant product |
| Heavymet | Single 90W-7Ni-3Fe | Ni-63 dominant long-term waste driver |

---

## References

1. **ORNL/TM-2020/1681** — Best Practices for Characterization of Activated Metals at DOE Nuclear Facilities. ORNL, 2020. https://doi.org/10.2172/1760244
2. **VTT-R-00184-20** — Cobalt Content of Stainless Steels Used in Nuclear Power Plants. VTT Technical Research Centre of Finland, 2020.
3. **EPRI TR-112352** — Radioactive Waste Management Guide for Nuclear Power Plant Decommissioning. EPRI, 1999.
4. **ASTM B170** — Standard Specification for Oxygen-Free Electrolytic Copper — Refinery Shapes. ASTM International, 2021.
5. **Tanaka et al. 2003** — Isomeric Cross Section Ratio for the (n,γ) Reaction on ¹⁰⁹Ag. JNST 40:831–836.
6. **Lindau et al. 2005** — EUROFER97: A Low Activation Ferritic-Martensitic Steel for Fusion Applications. Fusion Eng. Design. doi:10.1016/j.fusengdes.2005.06.033
7. **Rieth et al. 2015** — Tungsten as a Structural Divertor Material. IOP Conf. Series MSE.
8. **Kinno et al. 2007** — Development of Low-Activation Concrete for Fusion Reactor. Fujita Technical Research Report.
9. **OSTI 5171710** — Assessment of Titanium Alloys for Fusion Reactor First-Wall and Blanket Applications. ORNL.
10. **ORNL/TM-2008/137** — Survey of Radiation Effects in Titanium Alloys. ORNL, 2008.
11. **SCK-CEN OSTI 20902507** — Activation and Dose Rate Calculations for the ITER Bioshield. SCK-CEN, 2006.
12. **ScienceDirect 2025** — Performance characteristics and waste implications of WC materials used as neutron shielding materials in fusion. doi:10.1016/j.bulsci.2025.002458
13. **Royal Society Phil Trans A 2018** — Shielding materials in the compact spherical tokamak. doi:10.1098/rsta.2017.0443
14. **IAEA TECDOC-2116** — Decommissioning and Radioactive Waste Management for Fusion Facilities. IAEA, 2023.
15. **NRC 10 CFR Part 61** — Licensing Requirements for Land Disposal of Radioactive Waste.
16. **ENDF/B-VIII.0** — Brown et al. Nuclear Data Sheets 148:1–142 (2018). doi:10.1016/j.nds.2018.02.001
17. **NNDC NuDat3** — Nuclear Structure and Decay Data. NNDC/BNL, 2023. https://www.nndc.bnl.gov/nudat3/
18. **Zinkle & Snead 1995** — Use of titanium in fusion components. Fusion Eng. Design 29:445–452.
19. **ANSI/ANS-6.4-2006** — Nuclear Analysis and Design of Concrete Radiation Shielding for Nuclear Power Plants.
20. **NRC NUREG/CR-6280** — Technology, Safety, and Costs of Decommissioning a Reference PWR. NRC, 1997.
