# Low-Level Radioactive Waste Classification (NRC 10 CFR 61)

## Overview

The United States Nuclear Regulatory Commission (NRC) classifies low-level radioactive waste (LLW) under 10 CFR Part 61 into three disposal classes — A, B, and C — plus a category called Greater Than Class C (GTCC). The classification determines what type of near-surface disposal facility can accept the waste and what engineered barrier requirements apply. Higher classes require progressively more robust containment and longer institutional control periods.

This system is directly relevant to fusion facility decommissioning: activated structural materials, shielding, and concrete must be classified before disposal. The isotopic inventory produced by this tool feeds directly into a 10 CFR 61 classification analysis.

---

## The Three Disposal Classes

### Class A
The least hazardous category. Class A waste can be disposed of at near-surface facilities with minimal engineered barriers. Institutional controls (i.e., site restrictions, monitoring) are required for 100 years post-closure, after which the waste is assumed to be sufficiently decayed to pose no long-term hazard.

Class A limits are set so that, even without engineered barriers beyond the waste container itself, doses to the public remain within acceptable limits over the 100-year control period. Most short-lived activation products (e.g., Mn-56, Al-28, Na-24) fall well within Class A at practical fluences.

### Class B
An intermediate category requiring more robust waste forms — the waste must maintain its physical form for at least 300 years to prevent rapid dispersal as it decays. Class B waste cannot simply be placed in cardboard or steel drums; it typically requires grouting, cement solidification, or equivalent stabilization.

Class B applies to isotopes that are moderately long-lived at concentrations above the Class A threshold but below the Class C threshold. For activated metals, Class B is rarely the binding constraint — the more common situation is that long-lived isotopes (particularly those in Table 2 of 10 CFR 61) push waste directly toward or above Class C.

### Class C
The most restrictive class still eligible for near-surface disposal. Class C waste requires engineered barriers designed to maintain integrity for at least 500 years, plus an intruder barrier capable of preventing inadvertent human intrusion for the same period. Only a small number of licensed facilities in the US accept Class C waste, and disposal costs are substantially higher than for Class A.

The Class C limits — particularly for long-lived isotopes in Table 2 — are the critical design constraint for fusion material selection. Key Class C limits:

| Isotope | Class C Limit | Half-life | Note |
|---------|--------------|-----------|------|
| Nb-94   | 0.2 Ci/m³    | 20,300 y  | Most restrictive activated-metal limit |
| C-14    | 8 Ci/m³      | 5,730 y   | Relevant for concrete, WC, polymers |
| Ni-59   | 220 Ci/m³    | 76,000 y  | Pure EC; waste concern in Ni-bearing alloys |
| Ni-63   | 700 Ci/m³    | 100 y     | Pure β; relevant at high Ni fluence |
| Tc-99   | 3 Ci/m³      | 211,000 y | Downstream of Mo-99; relevant in Mo-bearing SS |

*Source: NRC 10 CFR 61.55, Table 2.*

### Greater Than Class C (GTCC)
Waste exceeding Class C limits is not eligible for near-surface disposal under current US regulations. GTCC waste requires disposal in a geologic repository, which in the US currently has no licensed pathway for LLW-origin GTCC material. In practice, GTCC activated metals from fusion devices would likely require interim storage pending regulatory resolution.

GTCC is the disposal outcome most feared in fusion decommissioning planning, and is the primary driver for reduced-activation material selection (EUROFER97, low-Co/Nb SS grades, LAC concrete).

---

## How Classification Works in Practice: The Sum-of-Fractions Rule

A waste package almost always contains multiple radionuclides. The 10 CFR 61 classification of the package is determined by applying the **sum-of-fractions rule** separately to Table 1 (shorter-lived) and Table 2 (longer-lived) isotopes:

**For Table 2 (long-lived) isotopes — the binding constraint for most fusion materials:**

$$\sum_i \frac{A_i}{L_i^C} \leq 1$$

where $A_i$ is the concentration of isotope $i$ in the waste (Ci/m³) and $L_i^C$ is its Class C limit. If this sum exceeds 1.0, the entire package is GTCC regardless of what else is in it.

**Practical implication:** Nb-94 has a Class C limit of 0.2 Ci/m³. A stainless steel component might have Co-60 well within Class A limits, but even a modest Nb-94 inventory from 50 ppm Nb contamination at high fluence can drive the package into GTCC because the denominator (0.2 Ci/m³) is so small. The sum-of-fractions amplifies the impact of any Table 2 isotope that is present.

This is why the materials with the highest long-term decommissioning risk are not necessarily those with the highest initial dose rates — they are those containing trace amounts of Table 2 isotopes (Nb, Mo→Tc, Ni at high concentration).

---

## Class A Limits for Shorter-Lived Isotopes (Table 1 Selection)

For shorter-lived products that dominate dose in the first years post-shutdown, the binding limit is usually Class A:

| Isotope | Class A Limit | Half-life | Typical activation context |
|---------|--------------|-----------|---------------------------|
| Co-60   | 700 Ci/m³    | 5.27 y    | Dominant 1–10 y dose driver in SS |
| Cs-137  | 1 Ci/m³      | 30.2 y    | Concrete (trace Cs); also fission product |
| Cs-134  | 1 Ci/m³      | 2.07 y    | Concrete activation product (Cs-133(n,γ)) |
| Na-22   | 2.5 Ci/m³    | 2.60 y    | Al and concrete fast-flux product |
| Eu-152  | —            | 13.5 y    | IAEA clearance 0.1 Bq/g applies; not in 10 CFR 61 Table 1 |

*Source: NRC 10 CFR 61.55, Table 1. Co-60 at 700 Ci/m³ is Class A; above this threshold, classification steps up to Class B and then C by concentration.*

---

## IAEA Clearance Levels (RS-G-1.7)

In parallel to the NRC disposal classification system, the IAEA defines **clearance levels** — concentrations below which material can be released from regulatory control entirely (unrestricted release). These are relevant for materials with very low activation that may be cleaner than the LLW threshold.

Key clearance levels from IAEA RS-G-1.7 Table 1:

| Isotope | Clearance level |
|---------|----------------|
| Co-60   | 0.1 Bq/g       |
| Eu-152  | 0.1 Bq/g       |
| Eu-154  | 0.2 Bq/g       |
| Cs-137  | 0.1 Bq/g       |
| Nb-94   | 0.1 Bq/g       |
| Ni-63   | 100 Bq/g       |
| C-14    | 1 Bq/g         |

The IAEA clearance level is often the more relevant threshold for concrete and shielding materials activated at modest fluences — they may fall below clearance rather than requiring formal LLW disposal. The FISPACT-II and IAEA TE-2116 decommissioning guidance uses these values to define the "hands-on" recycling cutoff for structural materials.

---

## Relevance to Fusion Material Selection

The table below summarizes the waste classification risk of the key isotopes produced in this tool, and the material design levers available to control them:

| Product | t½ | Regulatory concern | Primary source in fusion | Mitigation |
|---------|----|--------------------|--------------------------|------------|
| Nb-94   | 20,300 y | NRC Class C — 0.2 Ci/m³ | Nb impurity in SS (50–3000 ppm scrap origin) | Nuclear-grade SS (Nb ≤ 20 ppm); virgin SS; EUROFER97 |
| Co-60   | 5.27 y | NRC Class A — 700 Ci/m³; IAEA clearance 0.1 Bq/g | Co impurity in SS/W; Ni-60(n,p) at 14 MeV | Low-Co grades (≤100 ppm); EUROFER97 (no Co) |
| Ni-63   | 100 y | NRC Class C — 700 Ci/m³ | Ni-62(n,γ) — intrinsic to all Ni-bearing alloys | Minimize Ni content; EUROFER97 (no Ni) |
| Tc-99   | 211,000 y | NRC Class C — 3 Ci/m³ | Mo-99 decay chain; Mo in SS-316 (2–3 wt%) | Avoid Mo-bearing SS where possible |
| C-14    | 5,730 y | NRC Class C — 8 Ci/m³ | N-14(n,p) in concrete, WC, air; O-17(n,α) | Minimize N content in concrete; LAC concrete |
| Eu-152  | 13.5 y | IAEA clearance 0.1 Bq/g | Eu impurity in concrete (0.5–2 ppm) | LAC (limestone aggregate) reduces Eu 3–10× |

EUROFER97 was specifically designed to eliminate Nb, Ni, Mo, and Cu from the composition, making it the only common structural steel that avoids all Table 2 isotope concerns. The long-term decommissioning advantage is significant: EUROFER97 components are expected to reach hands-on recycling levels within 50–100 years, compared to potentially thousands of years for nuclear-grade SS-316 components with Nb contamination.

---

## References

- NRC 10 CFR Part 61: *Licensing Requirements for Land Disposal of Radioactive Waste*, U.S. Nuclear Regulatory Commission.
- IAEA RS-G-1.7: *Application of the Concepts of Exclusion, Exemption and Clearance*, IAEA Safety Standards Series (2004).
- IAEA TE-2116: *Decommissioning and Radioactive Waste Management for Fusion Research Facilities*, IAEA (2026).
- NUREG/CR-6280: *Low-Level Radioactive Waste from Decommissioning of Nuclear Reactors*, NRC (1994) — basis for activated metals LLW classification methodology.
- EPRI TR-112352: *Evaluation of Nb-94 Waste Classification in Activated Structural Steels*, EPRI (1999).
