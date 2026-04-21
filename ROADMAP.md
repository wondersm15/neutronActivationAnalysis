# Neutron Activation Analysis Tool — Roadmap

Tracking document for implemented features, in-progress work, and planned development.
Maintained alongside the codebase. Each entry records what was done, why, and any open issues.

---

## Completed Work

### Phase 0 — Initial Build (2026-03-28)
- Flask + single-page HTML/JS/Chart.js/Plotly architecture
- `data.py`: bundled ENDF/B-VIII.0 thermal and 14.1 MeV cross-sections, decay data, gamma lines
- `physics.py`: single-pulse activation model A(t) = λ·N₀·σ·Φ·exp(−λt), merged-product handling, ICRP-74 H*(10) dose rate
- `app.py`: REST API endpoints `/api/materials`, `/api/material/<name>`, `/api/compute`
- 5 materials: Aluminum (pure), SS304, Carbon Steel A36, Copper (OFHC), Tungsten (pure)
- Activation product table (sortable), gamma spectrum bar chart, isotopic composition chart
- Flux regime filter (thermal / 14 MeV), half-life filter, activity & dose rate plots
- Material comparison tab with multi-material overlay plots and snapshot tables

### Phase 1A — Nuclear Data Corrections & Expansion (2026-04-01)
- **SS304 composition fix**: Full recomputation of wt% → atom% conversion from first principles (72 Fe / 18 Cr / 8 Ni / 2 Mn). Old data had Cr fraction off by ~4.4×.
- **A36 composition fix**: Recomputed (98.5 Fe / 1.5 Mn).
- **Missing reactions added**:
  - Cr-54(n,γ)→Cr-55: σ_th=0.36 b, t½=3.497 min (near-pure β⁻ emitter, 1528 keV γ only 0.04%)
  - Ni-60(n,p)→Co-60: σ_14=0.028 b, t½=5.27 y — **critical missing reaction** (dominant long-term SS dose driver)
  - Ni-60(n,2n)→Ni-59: σ_14≈0.50 b, t½=75,000 y (waste classification)
  - Ni-64(n,γ)→Ni-65: σ_th=1.52 b, t½=2.52 h
  - Ni-58(n,α)→Fe-55: σ_14≈0.016 b (same product as Fe-54(n,γ))
  - Cr-52(n,2n)→Cr-51: σ_14=0.32 b (same product as Cr-50(n,γ))
  - Mn-55(n,α)→V-52: σ_14≈0.025 b
  - Cu-65(n,p)→Ni-65: σ_14≈0.018 b
  - W-180(n,γ)→W-181: σ_th=21.7 b, t½=121.2 d (EC, weak gammas)
  - W-182(n,2n)→W-181: σ_14=2.0 b (dominant 14 MeV W-181 path)
- **σ·f production proxy**: Added σ_th×f and σ_14×f columns, default sort by σ·f
- **Ni-61 mass** added to ISOTOPE_MASS
- **7 pure-element materials** added: Iron, Chromium, Nickel, Manganese (new), plus Al/Cu/W reclassified
- **Material categories**: `"alloy"` vs `"element"` field on all MATERIALS entries

### Phase 1B — Reaction Toggle & Threshold Filter (2026-04-01)
- Per-reaction checkbox column in activation table; header checkbox toggles all
- Disabled reactions dimmed (35% opacity) and excluded from compute calls
- `disabledReactions` Set maintained in JS, passed as `enabled_reactions` to backend
- Min σ·f threshold input in sidebar; filters both table display and backend compute
- `physics.py` accepts `enabled_reactions` and `sigma_f_min` parameters

### Phase 1C — Sidebar & UI Improvements (2026-04-01)
- Sidebar material list split into collapsible "Alloys" and "Elements" accordion groups
- `/api/materials` returns `{alloys: [...], elements: [...]}` instead of flat list
- Half-life filter upgraded from dropdown to dual-handle logarithmic noUiSlider (1 s → 317 y)
- Half-life filter now affects activity/dose rate plots (not just the table)
- "Atom frac" column renamed to "Nuclide frac"
- Activity and dose rate y-axes floored at 1e-10 (range:[-10, null] in log10)
- Gamma spectrum bar width fixed (barThickness:10)
- Notes column widened (min 320px, max 480px)

---

## Current Phase: Phase 2 — Literature Integration & Data Expansion

### Phase 2A — Literature Review Tab & Reference Tracking
**Status: Complete (2026-04-01)**

- [x] Created `references.json` — 11 structured entries covering ENDF/B-VIII.0, ICRP-74, JAEA-FNS, Kinno LAC, ORNL/TM-2020/1681, SCK-CEN ITER bioshield, IAEA TE-2116, NRC 10 CFR 61, IAEA RS-G-1.7, EUROfusion EUROFER, NNDC NuDat3
- [x] Added "Literature" tab to the GUI — always accessible (does not require material selection); renders markdown from `NotesFromOtherSources/` via marked.js with dark-themed CSS
- [x] `/api/literature` Flask endpoint: reads all `.md` files from `NotesFromOtherSources/`, extracts H1 title, returns list of `{filename, title, content}`
- [x] `/api/references` Flask endpoint: serves `references.json` as structured JSON
- [x] References sub-view in Literature tab with card-based grid layout
- [ ] Each activation product note in data.py should cite its source (ENDF eval, literature measurement, estimate) — ongoing; partially done via notes field

### Phase 2B — Critical Missing Nuclear Data
**Status: Tier 1 + Tier 2 complete (2026-04-01). Tier 3 not started.**

Priority isotopes/reactions identified from literature review. Confidence tiers noted.

**Tier 1 — Must-have (dominant dose or waste drivers):**
- [x] Co-59(n,γ)→Co-60: σ_th=37.2 b — also added (n,2n)→Co-58 σ_14=0.708 b, (n,p)→Fe-59
- [x] Ni-62(n,γ)→Ni-63: σ_th=14.5 b — already present from Phase 1A
- [x] Fe-54(n,p)→Mn-54: σ_14=0.080 b — already present from Phase 1A
- [x] Na-23(n,γ)→Na-24: σ_th=0.529 b — also added (n,2n)→Na-22 σ_14=0.0085 b
- [x] Eu-151(n,γ)→Eu-152: σ_th=5900 b (ENDF 2200 m/s; note: Maxwellian avg quoted as ~9200 b in literature — needs JEFF-3.3 cross-check) — also added (n,2n)→Eu-150
- [x] Eu-153(n,γ)→Eu-154: σ_th=312 b

**Tier 2 — Important (significant contributors or waste concerns):**
- [x] Cs-133(n,γ)→Cs-134: σ_th=29.0 b
- [x] Sc-45(n,γ)→Sc-46: σ_th=27.2 b
- [x] Ba-132(n,γ)→Ba-133: σ_th=7.0 b
- [x] Zn-64(n,γ)→Zn-65: σ_th=0.793 b — also added (n,p)→Cu-64 σ_14=0.052 b
- [x] Ni-58(n,p)→Co-58: σ_14≈0.30 b — already present from Phase 1A
- [ ] Al-27(n,2n+α)→Na-22: high-energy channel, σ very small, t½=2.60 y — long-term trace in Al (low priority)

**Tier 3 — Completeness (systematic channel coverage):**
- [ ] Audit all targets for missing (n,3n) channels — relevant at 14.1 MeV for heavy nuclei (W, Pb, Ba)
  - W-184(n,3n)→W-182 (stable, but threshold check needed)
  - W-186(n,3n)→W-184 (stable)
  - Pb isotopes: (n,3n) thresholds vs 14.1 MeV availability
- [ ] Audit for missing (n,d), (n,t), (n,nα) channels with non-negligible cross-sections at 14 MeV
- [ ] Add (n,2n) for all heavy targets where threshold < 14.1 MeV and product is radioactive
- [ ] Systematic check: for every target isotope in REACTIONS, verify all channels with σ > 1 mb at 14 MeV are included

### Phase 2C — New Materials
**Status: COMPLETE (2026-04-03)**

Total: 25 materials across 5 categories. 48 reaction targets, 102 isotope masses.

Completed this session:
- [x] **SS-304 (baseline)**: Bulk composition only — Fe/Cr/Ni/Mn/C/Si/P/S. No impurities. Clean lower-bound reference.
- [x] **SS-316 (commercial)**: Co ~1500 ppm, Nb ~50 ppm, full Mo isotopics. (prev. session)
- [x] **SS-316 (nuclear grade)**: Co ≤100 ppm, Nb ≤20 ppm. (prev. session)
- [x] **Tungsten (ITER grade / industrial)**: Ta and Co impurities at spec levels. (prev. session)
- [x] **EUROFER97**: 9Cr-1W-0.2V-0.1Ta-0.4Mn RAFM steel. No Co/Ni/Mo/Nb. Reduced-activation.
- [x] **Carbon Steel (A36)**: Updated with conservative impurity model — Co 2000 ppm, Cu 1000 ppm, Ni 1000 ppm, scrap-origin basis.
- [x] **Aluminum 6061-T6**: Full alloy (Al/Mg/Si/Cu/Cr/Fe/Zn/Ti/Mn) replacing "Aluminum (pure)" placeholder.
- [x] **Titanium Ti-6Al-4V**: Ti/Al/V. Reduced-activation; Na-24 dominant early; Al-26 very long-term.
- [x] **Tantalum (pure)**: Pure Ta — conservative model. Ta-182 only significant product.
- [x] **Heavymet (90W-7Ni-3Fe)**: W/Ni/Fe alloy. 7 wt% Ni → Co-58 at 14 MeV + Ni-63 waste concern.
- [x] **Tungsten Carbide (WC-Co)**: 94 wt% WC + 6 wt% Co binder. Co-60 completely dominates.
- [x] **OPC Concrete**: ANSI/ANS-6.4 bulk + Eu/Co/Cs/Sc impurities modeled. Eu-152 dominant >5 y.
- [x] **LAC Concrete (Limestone)**: Limestone aggregate. Reduced Eu/Co/Na/K vs. OPC.
- [x] **Borated Concrete (Kretekast)**: SWX-277 from MCNP m402 definition. Density 1.68 g/cm³.
- [x] **Lead**: Pb isotopics + 50 ppm Bi (→ Po-210 alpha hazard).
- [x] **Water (H2O)**: H/O isotopics. N-16 dominant prompt; essentially no long-lived γ products.
- [x] **Silicon Dioxide (SiO2)**: Si/O isotopics. Very weak activator; all products short-lived.

New REACTIONS added: Ti-47/48/50, V-51, O-16, O-17, Ca-48, K-41, N-14, Si-28, Si-30, Bi-209.
New ISOTOPE_MASS entries: Ca isotopes, K isotopes, Mg isotopes, product nuclides (Sc-46/47/48, V-52, K-42, Ca-49, Ti-51, N-16), B-10/11.

### Phase 2D — Impurity & Annotation System
**Status: COMPLETE (2026-04-03)**

- [x] `"impurities"` field populated for all 25 MATERIALS (empty `{}` for pure reference elements; structured entries with `ppm_range`, `significance`, `note` for all others)
- [x] `"impurities"` exposed in `/api/material` endpoint response
- [x] **Composition tab — Impurity callout panel**: renders below isotope table; shows each known impurity as a card with significance badge (CRITICAL/high/moderate/low), ppm range, and literature note. Left-border color coded by severity.
- [x] **Activation table — Waste Class column**: `waste_class` field added to 13 reactions across 10 products (Co-60, Nb-94, Ni-63, Ni-59, C-14, Eu-152, Eu-154, Cs-134, Na-22, Bi-210). Displayed as color-coded badges: NRC Class C (red), NRC Class A (orange), IAEA clearance (blue), Alpha hazard (purple). Badge tooltip shows the exact regulatory limit and source.
- [x] `waste_class` passed through `get_material_activation()` to frontend
- [x] Material categories rationalized: steel/metal/concrete/shielding/moderator/element replacing alloy/element binary split — all 25 materials now appear correctly grouped in sidebar and comparison tab
- [ ] Literature-sourced source tags per reaction (ENDF/measured/estimate) — partially done via notes text; formal per-field source tagging deferred to Phase 3

---

## Phase 3 — Nuclear Data API Integration (Planned)

### Phase 3A — Multi-Database Architecture
**Status: COMPLETE (2026-04-04)**

**Target databases (in priority order):**
1. **ENDF/B-VIII.0** (current, bundled) — US evaluation, primary reference
2. **JEFF-3.3** (Joint Evaluated Fission and Fusion, EU) — preferred for fusion activation by EUROfusion/FISPACT-II
3. **JENDL-5** (Japan, 2021) — excellent for shielding and activation, validated at JAEA FNS
4. **TENDL-2023** (TALYS-based) — broadest isotope coverage, useful for filling gaps
5. **EAF-2010** (European Activation File) — activation-specific library used with FISPACT-II

**Completed:**
- [x] **REACTIONS schema migration**: All 77 reaction entries migrated from flat `sigma_th`/`sigma_14` keys to nested `cross_sections` dict: `{"endf8": {"sigma_th": V, "sigma_2p5": None, "sigma_14": V}}`. `sigma_2p5` placeholder is `None` until raw ENDF files are processed (Phase 3B).
- [x] **`get_material_activation(library="endf8")`**: Updated to extract cross-sections from `cross_sections[library]`. Returns `sigma_2p5` and `sigma_f_2p5` in every row.
- [x] **`compute_activation(fluence_2p5=0, library="endf8")`**: Added 2.5 MeV fluence parameter; σ_2p5 included in activation sum when non-zero; `library` passed through.
- [x] **`/api/compute`** endpoint: Accepts `fluence_2p5` and `library` in POST body.
- [x] **Frontend**: 2.5 MeV fluence input added to sidebar; library selector (ENDF/B-VIII.0 default; JEFF-3.3/JENDL-5/TENDL-2023/EAF-2010 listed as disabled placeholders); σ_2.5MeV column added to activation table (shows `…` pending indicator for all current rows); `getIrradParams()` passes both params to API; comparison tab updated to send both.

**Remaining for Phase 3A (blocked on ENDF files):**
- [ ] Populate `sigma_2p5` values once raw ENDF-6 files are available (Phase 3B)
- [ ] Populate additional library entries (`jeff33`, `jendl5`, `tendl23`, `eaf10`) once files downloaded
- [ ] Enable library selector options as data becomes available

### Phase 3B — Energy-Dependent Cross-Section Plots
**Goal**: Full σ(E) curves from threshold to 20 MeV, selectable by database, overlaid for comparison.

- [ ] New "Cross Sections" tab in the GUI
- [ ] For each reaction in the current material, plot σ(E) from the selected database(s)
- [ ] Overlay multiple databases on the same plot for comparison (ENDF vs JEFF vs JENDL)
- [ ] Mark the thermal (0.0253 eV) and 14.1 MeV evaluation points used in our activation calculations
- [ ] Include resonance region detail (log-log axes, zoom capability)
- [ ] Option to overlay EXFOR experimental data points on evaluated curves
- [ ] Consider using Plotly for interactive zoom/pan on dense resonance data

### Phase 3C — Redundancy & Validation
- [ ] For every reaction in data.py, record which library the current values come from and flag where libraries disagree significantly
- [ ] Automated comparison: when a new library is added, generate a diff report of cross-section values vs current bundled data
- [ ] Validation against JAEA FNS benchmark measurements (the premier concrete/steel activation benchmark for DT neutrons, per literature review)
- [ ] Flag reactions where ENDF/B-VIII.0, JEFF-3.3, and JENDL-5 disagree by >20% at thermal or 14.1 MeV

---

## Phase 4 — Advanced Features (Future)

### Physics Model Enhancements
- [ ] Multi-pulse irradiation model (campaign accumulation with inter-pulse decay)
- [ ] Pulsed irradiation schedule definition (pulse width, rep rate, campaign phases) — per ALARA/FISPACT-II methodology
- [ ] Activation chain handling (A→B→C sequential decays, e.g., W→Re→Os transmutation chain)
- [ ] Burnup/depletion correction for high-fluence scenarios
- [ ] Self-shielding corrections for high-σ resonance absorbers (Eu-151 at 9200 b)

### Waste Classification & Regulatory
- [ ] IAEA RS-G-1.7 clearance level lines on activity plots (0.1 Bq/g for Co-60, Eu-152)
- [ ] NRC 10 CFR 61 Class A/B/C limits on activity plots
- [ ] ΣDi/Ci clearance ratio calculation (sum of activity/clearance-limit across all isotopes)
- [ ] Time-to-clearance estimator: for a given material and fluence, when does it drop below clearance?

### UI & Export
- [ ] Export activation table and plots as PDF report
- [ ] Save/load irradiation scenarios
- [ ] URL-encoded state sharing (material + fluence + filters in URL params)
- [ ] Dark/light theme toggle

### Deployment
- [ ] Possible migration from local Flask to hosted deployment
- [ ] Consider Electron wrapper for desktop app distribution

---

## Data Confidence Convention

All nuclear data in `data.py` should be tagged with confidence level in notes:

| Tag | Meaning |
|-----|---------|
| **ENDF** | Value from ENDF/B-VIII.0 evaluation |
| **JEFF** | Value from JEFF-3.3 evaluation |
| **JENDL** | Value from JENDL-5 evaluation |
| **measured** | Published experimental measurement (cite) |
| **estimate** | Order-of-magnitude estimate, not from evaluation |
| **literature** | Value cited in review paper (not primary source) |

---

## References

See `references.json` for the full structured reference list. Key sources:

- ENDF/B-VIII.0: Brown et al., Nuclear Data Sheets 148 (2018) 1–142
- JAEA FNS shielding benchmarks: Sato et al., J. Nucl. Sci. Tech. (2018)
- JAEA/Fujita LAC program: Kinno et al., Fujita Technical Research Report (2007)
- ORNL activated metals best practices: ORNL/TM-2020/1681
- SCK-CEN ITER bioshield study: OSTI 20902507
- ICRP-74 dose conversion coefficients: ICRP Publication 74 (1996)
- NRC fusion device guidance: activation products licensing and decommissioning
- IAEA TE-2116: decommissioning and waste management for fusion (2026)
