# Activation Analysis Tool — Development Activity Log

Chronological record of development sessions, directions from Marc, key decisions, and technical
findings. Complements ROADMAP.md (which tracks planned/completed features) — this log captures
the reasoning and context behind decisions.

---

## Session 1 — Initial Build
**Date:** ~2026-03-28
**Status at start:** New project from scratch.

### Directions
- Build a web-based neutron activation analysis tool for pulsed-power fusion facility design.
- Single-pulse activation model: A(t) = λ·N·σ·Φ·e^{−λt}.
- Bundle all nuclear data (no runtime API calls) from ENDF/B-VIII.0.
- Thermal and 14.1 MeV (fusion) cross-sections.
- ICRP-74 H*(10) ambient dose equivalent for gamma dose rates.

### Work Done
- Flask + single-page HTML/JS/Chart.js/Plotly architecture established.
- `data.py`: bundled ENDF/B-VIII.0 cross-sections, decay data, gamma lines for 5 initial materials.
- `physics.py`: single-pulse activation engine, merged-product handling, ICRP-74 dose rate.
- `app.py`: REST endpoints `/api/materials`, `/api/material/<name>`, `/api/compute`.
- `templates/index.html`: activation product table (sortable), gamma spectrum bar chart, isotopic
  composition chart, flux regime filter, half-life filter, activity and dose rate time plots.
- Initial materials: Aluminum (pure), SS-304, Carbon Steel A36, Copper (OFHC), Tungsten (pure).

---

## Session 2 — Nuclear Data Corrections + Feature Expansion (Phase 1A / 2A)
**Date:** ~2026-04-01

### Directions
- Fix inaccuracies found in the initial composition data.
- Add missing reactions that matter for activation dose.
- Add comparison tab (multi-material overlay).
- Add composition tab (interactive isotope viewer).
- Add activity vs. time plot alongside dose rate.

### Key Findings / Decisions
- SS-304 Cr atom fraction was off by ~4.4× due to incorrect wt%→atom% conversion. Fixed by
  full recomputation from first principles (72 Fe / 18 Cr / 8 Ni / 2 Mn).
- A36 recomputed to (98.5 Fe / 1.5 Mn).
- Critical missing reaction identified: Ni-60(n,p)→Co-60 (σ_14=0.028 b) — was producing zero
  Co-60 from SS matrix despite this being the dominant long-term dose driver for 14 MeV flux.
- Added Ni-60(n,2n)→Ni-59 (t½=76,000 y) for waste classification.
- Added Cr-54(n,γ)→Cr-55, Ni-64(n,γ)→Ni-65, Ni-58(n,α)→Fe-55, Cr-52(n,2n)→Cr-51,
  Mn-55(n,α)→V-52 (very short-lived, V-52 = same product as V-51(n,γ)).
- Additional concrete/soil reactions added: Eu-151, Eu-153, Cs-133, Sc-45, Ba-132/134/136/137/138,
  Na-23(n,γ)→Na-24 (key hard gamma from Al(n,α) product and cement Na).

### Work Done
- Full wt%→atom% recomputation for SS-304 and A36.
- 10+ new REACTIONS entries.
- Comparison tab: multi-material dose rate overlay, snapshot comparison table.
- Composition tab: interactive pie/bar chart, isotope fraction explorer.
- Activity plot added alongside existing dose rate plot.
- noUiSlider for interactive time window control.
- marked.js integrated for markdown rendering (for future Literature tab).

---

## Session 3 — Literature Tab + Impurity Literature Review Part 1
**Date:** 2026-04-03 (session continued from prior context limit)

### Directions
- Implement Literature Review tab in the GUI (markdown file browser + reference cards).
- Conduct a literature review on the impact of impurities in common structural materials —
  emphasis on SS, Cu, W, Al. Use to: (a) populate Literature section, (b) ensure materials
  have all relevant minor constituents, (c) improve activation product notes.
- Make materials available in the ClaudeWorkspace/Projects/Work/WorkNotes/ folder as well.
- Provide variants for materials with highly variable impurity content.
- Confirmed direction on variants: "Add separate Low / High impurity variants" for SS.
  Marc chose Low/High Co for SS-316.

### Key Technical Findings
- **Co-59 was entirely absent from `isotopes` dict for all materials** — Co-60 production was
  computing as zero despite Co being the #1 long-term dose driver in SS at 1–10 y. Critical gap.
- **Ag-110m in OFHC Cu dominates over Zn-65 at ASTM B170 C10100 spec limits:**
  σ·f_th for Ag-110m ≈ 85× higher than Zn-65 at C10100 limits (Ag ≤25 ppm, Zn ≤1 ppm max).
  This inverts the common engineering assumption that Zn-65 dominates copper activation.
  Source: Tanaka et al. 2003 (isomeric cross-section for Ag-109(n,γ)→Ag-110m: σ_th = 4.12 b).
- **Nb-94 waste classification:** Nb-93(n,γ)→Nb-94 (t½=20,300 y, NRC Class C = 0.2 Ci/m³) is
  the most restrictive single activated-metal waste limit. Even 50 ppm Nb in SS at high fluence
  can exceed Class C.
- **Co in commercial SS:** VTT-R-00184-20 measured 1340–2570 ppm in commercial SS-304/316.
  Nuclear-grade: ≤500 ppm (Sandmeyer 304CO); reactor-grade: ≤100 ppm.
- **Ta-182 in W:** Ta-181(n,γ)→Ta-182 (σ_th=20.5 b, t½=114.7 d) is the dominant medium-term
  dose driver in W after the Re/Os chain. ITER spec: Ta ≤50 ppm; industrial W: up to 500 ppm.
- **Mo in SS-316:** Mo-98(n,γ)→Mo-99 (t½=66 h) and Mo-92(n,p)→Nb-92m (t½=10.15 d) now captured.
  Tc-99 (t½=211 ky) downstream from Mo-99 is a long-lived LLW waste concern.

### Work Done (data.py)
- REACTIONS: Added Mo-92/98/100, Nb-93 (×2 reactions), Ag-107, Ag-109, Ta-181.
- MATERIALS:
  - "Stainless Steel 304": Co-59 = 0.00141 (1500 ppm) added to isotopes.
  - NEW "Stainless Steel 316 (commercial)": Co-59=0.00145, Nb-93=3.07e-5, full Mo isotopics.
  - NEW "Stainless Steel 316 (nuclear grade)": Co-59=9.6e-5, Nb-93=1.22e-5.
  - "Copper (OFHC)": Ag-107=7.63e-6, Ag-109=7.07e-6 at ASTM B170 C10100 max (25 ppm Ag).
  - "Tungsten (pure)" REPLACED by "Tungsten (ITER grade)" and "Tungsten (industrial)".
  - Both W variants include Ta-181 and Co-59 at appropriate impurity levels.
- ISOTOPE_MASS: Added Mo-92/94/95/96/97/98/100, Nb-93, Ag-107/109, Ta-181 + light elements.
- Literature tab: `/api/literature` and `/api/references` endpoints, marked.js rendering, file
  selector, reference grid with tags.
- `references.json` created with 11 initial entries (ENDF-VIII, ICRP-74, ORNL-TM-2020/1681, etc.).
- `NotesFromOtherSources/impurity-activation-structural-materials.md`: first literature review,
  SS/Cu/W/Al emphasis, ~300 lines.

### Marc Corrections / Decisions
- "You are saying you already have this information in your training database? You don't need to
  search for additional info?" — confirmed that training knowledge was used; web search only used
  to verify unavailable source documents.

---

## Session 4 — Extended Materials Scope + Full Literature Review
**Date:** 2026-04-03 (this session)

### Directions
- Add SS-304 **baseline** (no impurities — C, Si, P, S, Cr, Mn, Fe, Ni only). Purpose: clean
  lower-bound comparator to isolate impurity contribution.
- Expand material list. Confirmed scope after Marc's review of initial proposal:
  - **Remove from scope**: Inconel 625/718, Beryllium, Vanadium alloy V-4Cr-4Ti.
  - **Keep / add**: EUROFER97, A36 (update), Al-6061, Ti-6Al-4V, Tantalum (pure), Heavymet (90W-7Ni-3Fe), WC-Co, OPC concrete, LAC concrete, Lead, Water, SiO2.
  - **Heavymet spec**: 90W-7Ni-3Fe (generic).
  - **Tantalum**: pure Ta, conservative — note Ta-2.5W is the real structural alloy.
  - **Additional from search**: Marc confirmed adding WC (tungsten carbide).
  - **Borated concrete**: "Kretekast" — Marc provided MCNP material definition m402 (SWX-277).
  - **Skip for now**: CuCrZr, borated polyethylene.
- Conduct more extended literature review covering all 19+ materials.

### Kretekast Composition (from Marc's MCNP m402)
Decoded from MCNP weight fractions, density 1.68 g/cm³:
H-1: 4.9%, O-16: 62.66%, B-10: 0.308%, B-11: 1.297%, N-14: 0.010%, Na-23: 0.13%,
Al-27: 21.45%, S(nat): 0.16%, Si(nat): 1.38%, Ca(nat): 6.56%, C(nat): 0.45%, Fe(nat): 0.27%.
High-alumina borated concrete (Al-aggregate, possibly gibbsite or calcium aluminate based).
Key difference from OPC: very high H (4.9%) and Al (21.45%) → much more Na-24 from Al-27(n,α).

### Key Technical Findings (this session)
- **WC-Co Co binder issue:** Standard WC-6Co (6 wt% Co) puts Co at orders-of-magnitude above
  SS impurity levels (~0.15 wt% vs ~0.15–0.25% max in commercial SS). Co-60 completely dominates
  WC-Co activation. 2025 paper specifically on WC waste implications in fusion confirms.
- **Ti-6Al-4V is genuinely reduced-activation:** Sc-47 (Ni-47(n,p)) and Sc-48 (Ti-48(n,p)) are
  dominant 14 MeV products; Na-24 from 6 wt% Al dominates very early dose. Al-26 (t½=720 ky)
  from Al-27(n,2n) is negligible at practical fusion fluences. Tramp Co/Ni/Nb are the concerns.
- **Heavymet Ni content (7 wt%):** Produces Co-58 from Ni-58(n,p) and Co-60 from Ni-60(n,p)
  at 14 MeV — intrinsic to the alloy, not impurity-level. Ni-63 (100 y) from Ni-62(n,γ) drives
  long-term waste classification; NRC Class C limit = 35 Ci/m³.
- **OPC Concrete impurity dominance:** Eu-152 (13.5 y) from Eu-151(n,γ) dominates OPC dose at
  5–50 y (σ_th ~9200 b Maxwellian; even 0.5–2 ppm Eu is significant). Na-24 from bulk Na
  dominates first 24 h. Co-60 co-dominant 1–10 y. LAC reduces these 3–10× by aggregate choice.
- **EUROFER97 No-Co design:** Eliminating Ni/Mo/Nb/Cu is the key design decision. Ta-182 from
  0.1 wt% alloying Ta is accepted because it decays to acceptable levels in <2 y.
- **SS-304 baseline minor constituents:** C, Si, P, S activation products are all either
  short-lived (Si-31 t½=2.6 h, Al-28 t½=2.2 min), pure beta (P-32, C-14), or negligible
  cross-section. Confirmed they do not meaningfully affect gamma dose.
- **Lead activation is negligible** from bulk Pb: σ_th values are 0.0007–0.699 b. Dominant
  concern is Bi-209(n,γ)→Bi-210→Po-210 (alpha emitter, extreme inhalation radiotoxin).
  Nuclear-grade Pb: Bi <10 ppm. Commercial: 10–10,000 ppm.

### Work Done (this session)
**data.py:**
- REACTIONS added: Ti-47(n,p)→Sc-47, Ti-48(n,p)→Sc-48, Ti-50(n,γ)→Ti-51, V-51(n,γ)→V-52,
  O-16(n,p)→N-16, O-17(n,α)→C-14, Ca-48(n,γ)→Ca-49, K-41(n,γ)→K-42, N-14(n,p)→C-14,
  Si-28(n,p)→Al-28, Si-30(n,γ)→Si-31, Bi-209(n,γ)→Bi-210.
- ISOTOPE_MASS extended: Ca-40/42/43/44/46/48, K-39/40/41, Mg-24/25/26, product nuclides
  (Sc-46/47/48, V-52, K-42, Ca-49, Ti-51, N-16), B-10/11.
- MATERIALS (14 new + 2 updated):
  - NEW: SS-304 (baseline) — bulk only, no Co impurity.
  - UPDATED: Carbon Steel (A36) — now includes Co 2000 ppm, Cu 1000 ppm, Ni 1000 ppm
    (conservative scrap-origin model; was previously only Co ~150 ppm).
  - NEW: EUROFER97 (9Cr-1W-0.2V-0.1Ta-0.4Mn RAFM steel).
  - NEW: Aluminum 6061-T6 (full alloy: Al/Mg/Si/Cu/Cr/Fe/Zn/Ti/Mn).
  - NEW: Titanium Ti-6Al-4V (Ti/Al/V).
  - NEW: Tantalum (pure) — conservative model, note re Ta-2.5W.
  - NEW: Heavymet (90W-7Ni-3Fe).
  - NEW: Tungsten Carbide (WC-Co) — WC-6Co grade.
  - NEW: OPC Concrete — ANSI/ANS-6.4 bulk + Eu/Co/Cs/Sc impurities.
  - NEW: LAC Concrete (Limestone) — reduced-impurity variant.
  - NEW: Borated Concrete (Kretekast) — from MCNP m402 definition.
  - NEW: Lead — Pb isotopics + 50 ppm Bi.
  - NEW: Water (H2O) — H/O isotopics; N-16 dominant prompt product.
  - NEW: Silicon Dioxide (SiO2) — Si/O isotopics; very weak activator.

**references.json:** Expanded from 16 → 25 entries. New: Lindau 2005 (EUROFER97),
OSTI 5171710 (Ti alloys for fusion), ORNL/TM-2008/137 (Ti radiation survey), WC fusion waste 2025,
Royal Society compact tokamak 2018, ANSI/ANS-6.4, Shieldwerx SWX-277 spec, JET Cu activation
2019, NUREG/CR-6280.

**Literature review files:**
- `NotesFromOtherSources/impurity-activation-all-materials.md` — extended review covering all
  19 materials with impurity tables, severity rankings, waste classification summary table. ~430 lines.
- Mirrored to `ClaudeWorkspace/Projects/Work/WorkNotes/`.

**ROADMAP.md:** Phase 2C marked complete (25 materials, 48 reaction targets, 102 isotope masses).

---

## Session 5 — Phase 2D Completion + Category Fix
**Date:** 2026-04-03 (continued from Session 4, which hit context limit)

### Directions
- Complete Phase 2D (impurity annotation system).
- Fix GUI bug: materials with category "concrete", "moderator", "shielding" not appearing in sidebar.
- Add NRC/IAEA waste classification information to the Literature tab.
- Create `decisions-and-feedback.md` context file in ClaudeWorkspace/Context/ for accumulating Marc's decisions and feedback across sessions.
- Marc deprioritized GUI usability items (regulatory lines on plots, time-to-clearance) in favor of Phase 3 (multi-library nuclear data).
- Marc deprioritized GitHub setup — don't push git tasks unless asked.

### Bug Found & Fixed
- **Missing materials in sidebar:** The `/api/materials` endpoint only bucketed `"alloy"` and `"element"` categories. Materials with category `"concrete"`, `"moderator"`, or `"shielding"` had a `category` key (so skipped the `"other"` fallback) but didn't match either named bucket — silently dropped. 5 materials were invisible in the GUI.
- **Fix:** Changed app.py to dynamically collect all categories using `defaultdict`; updated index.html `renderMaterialList()` and `renderComparisonChecklist()` to handle arbitrary category keys with a defined display order.
- **Category rationalization:** Replaced binary alloy/element with 6 categories: steel (6), metal (9), concrete (3), shielding (2), moderator (1), element (4). Carbon Steel A36 needed a manual fix — regex missed it due to long distance between material name and category field.

### Phase 2D Work Done

**data.py:**
- `impurities: {}` added to 4 reference elements (Fe, Cr, Ni, Mn) for consistency.
- `waste_class` dict added to 13 reactions across 10 products: Co-60, Nb-94, Ni-63, Ni-59, C-14, Eu-152, Eu-154, Cs-134, Na-22, Bi-210. Each has `tag` (badge label) and `limit` (exact regulatory limit with source).
- `waste_class` field passed through `get_material_activation()` to frontend.

**app.py:**
- `/api/materials` — dynamic category collection (replaces hardcoded alloy/element).
- `/api/material/<name>` — now returns `impurities` dict.

**index.html:**
- **Activation table**: New "Waste class" column with color-coded badges — NRC Class C (red), NRC Class A (orange), IAEA clearance (blue), Alpha hazard (purple). Badge tooltip shows regulatory limit.
- **Composition tab**: Impurity callout panel below isotope table. Cards with left-border severity coding (CRITICAL=red, high=orange, moderate=yellow), ppm range, and literature note.
- **Sidebar**: 6 category groups with defined display order — Steels and Metals & Alloys open by default; Concrete, Shielding, Moderator, Reference Elements collapsed.
- **Comparison tab**: `renderComparisonChecklist()` fixed to flatten all category arrays via `Object.values(cats).flat()`.

**Literature:**
- New file: `NotesFromOtherSources/llw-waste-classification.md` — comprehensive guide to NRC 10 CFR 61 waste classes (A/B/C/GTCC), sum-of-fractions rule, IAEA clearance levels, and fusion-specific material selection implications.
- `references.json`: expanded to 26 entries (added NRC 10 CFR 61 as formal regulatory citation).

**Context files updated:**
- `ClaudeWorkspace/Context/decisions-and-feedback.md` — new file; accumulated decisions from all sessions.
- `ClaudeWorkspace/Context/project-index.md` — updated Activation Analysis entry with current state.
- `ClaudeWorkspace/Context/working-preferences.md` — added decisions-and-feedback.md to startup list.
- `ClaudeWorkspace/CLAUDE.md` — added decisions-and-feedback.md to startup list.
- `ROADMAP.md` — Phase 2D marked complete.

---

## Session 6 — Phase 3A: Multi-Library Schema Migration
**Date:** 2026-04-04 (continued from Session 5, which hit context limit mid-Phase 3A)

### Directions
- Continue Phase 3A migration that was blocked at end of Session 5.
- Session 5 had written a migration script but it hit a SyntaxError (guard missing for non-REACTIONS uses of `"sigma_th"` string). data.py was intact (script did not write to disk).

### Bug Fixed (from prior session)
- Migration script parsed `"sigma_th"` substring matches in `get_material_activation()` function body (e.g., `rxn["sigma_th"]` in the results dict). Fixed by: (a) scoping the migration to only lines 1–1294 (REACTIONS dict section, before MATERIALS at line 1295); (b) fixing `parse_value()` to strip trailing comma before the `#` comment separator (not after).

### Work Done

**data.py:**
- All 77 REACTIONS entries migrated from flat `sigma_th`/`sigma_14` to nested `cross_sections` dict.
  Format: `"cross_sections": {"endf8": {"sigma_th": V, "sigma_2p5": None, "sigma_14": V}}`.
  `sigma_2p5` is `None` placeholder — will be populated from ENDF files in Phase 3B.
- Three entries had multi-line trailing comments on the sigma_th line (Eu-152, Ag-108m, Ag-110m) — migration handled correctly by consuming comment-continuation lines as part of the sigma_th block.
- `get_material_activation(library="endf8")` updated: extracts `xs = rxn["cross_sections"][library]`; returns `sigma_th`, `sigma_2p5`, `sigma_14`, `sigma_f_th`, `sigma_f_2p5`, `sigma_f_14` in every row.
- Header docstring updated to explain `sigma_2p5` (D-D mean / fission spectrum) and library parameter.
- Syntax verified: `ast.parse()` pass; all 77 cross_sections blocks confirmed.

**physics.py:**
- `compute_activation()` signature extended: added `fluence_2p5=0.0` and `library="endf8"` params.
- `sigma_f_min` threshold filter updated to use `max(sf_th, sf_2p5, sf_14)`.
- Activation sum includes `sigma_2p5 * fluence_2p5` term when both are non-None/non-zero.
- Return dict now includes `fluence_2p5` and `library` fields.

**app.py:**
- `/api/compute` POST body now accepts `fluence_2p5` (default 0) and `library` (default "endf8").
- Both forwarded to `compute_activation()`.
- Docstring updated.

**templates/index.html:**
- Sidebar: new "2.5 MeV fluence" input (`inp-fluence-2p5`, default 0) and "Nuclear data library" `<select>` (`inp-library`; ENDF/B-VIII.0 enabled, 4 others listed as disabled placeholders).
- Activation table: `σ_2.5MeV (b)` column added between σ_th and σ_14 columns. Shows `…` (`.sigma-pending` class, amber italic, cursor:help tooltip) for all current rows where `sigma_2p5 === null`.
- `getIrradParams()`: now returns `fluence_2p5` and `library`.
- `computeForCurrent()` and `computeComparison()` both pass `fluence_2p5` and `library` to `/api/compute`.
- CSS: `.sigma-pending` added (amber italic, `cursor:help`).

### Verification
- `ast.parse()` on all three Python files: PASS.
- Schema validation: 77 reactions checked, 0 errors — all have `cross_sections.endf8` with `sigma_th`, `sigma_2p5`, `sigma_14`.
- `get_material_activation()` rows: all include `sigma_2p5` and `sigma_f_2p5` keys, verified for SS-316 (nuclear grade), Aluminum (pure), Copper (OFHC).
- `compute_activation()` with `fluence_2p5=1e13`: runs correctly, returns correct library/fluence fields.

### Pending Items (Phase 3B onwards)
- **Phase 3B**: Build preprocessing pipeline + download script using `endf-python`. Extract σ(E) from ENDF-6 files for all 5 libraries; populate `sigma_2p5` and additional library entries.
- **Phase 3C**: Cross-validation diff report across all 5 libraries.
- **Phase 3D**: Cross Sections tab with full σ(E) plots, multi-library overlay, EXFOR experimental data overlay.
- **Library selector**: Enable JEFF-3.3/JENDL-5/TENDL-2023/EAF-2010 options once data is populated.
- **Kretekast trace impurities**: OPC-level assumed until Marc provides measured data.
- **GitHub**: Deferred — don't push unless Marc asks.

---

## Current Project State (2026-04-04, updated)

### File Structure
```
ActivationAnalysis/
├── app.py                    (~195 lines) — Flask app; /api/compute accepts fluence_2p5, library
├── data.py                   (~2410 lines) — REACTIONS (77 entries, cross_sections schema),
│                                             MATERIALS (25 entries), ISOTOPE_MASS (102 entries),
│                                             ICRP74_H10, waste_class on 13 reactions,
│                                             impurities on all materials
├── physics.py                (~340 lines) — Single-pulse activation engine; fluence_2p5 + library params
├── templates/
│   └── index.html            (~1360 lines) — Full single-page app (6 tabs) + σ_2.5 column +
│                                             2.5 MeV fluence input + library selector
├── requirements.txt          — flask>=3.0.0
├── references.json           (26 references) — Citable literature database
├── ROADMAP.md                — Phase tracking document
├── ACTIVITY_LOG.md           — This file
├── PHASE3_PLAN.md            — Full Phase 3 architecture plan (3A–3D)
├── .gitignore                — Python/Flask standard exclusions
└── NotesFromOtherSources/
    ├── impurity-activation-structural-materials.md  — SS/Cu/W/Al impurity review
    ├── impurity-activation-all-materials.md          — Full 19-material impurity review
    ├── llw-waste-classification.md                   — NRC 10 CFR 61 waste class guide
    └── low-activation-concrete-review.md             — Concrete/LAC literature review
```

### Materials in Tool (25 total)
**Steels (6):** SS-304 (baseline), SS-304 (commercial), SS-316 (commercial), SS-316 (nuclear grade),
Carbon Steel A36, EUROFER97.
**Non-ferrous metals (8):** Copper (OFHC), Aluminum (pure), Aluminum 6061-T6, Titanium Ti-6Al-4V,
Tantalum (pure), Heavymet (90W-7Ni-3Fe), Tungsten (ITER grade), Tungsten (industrial).
**Carbide/cermet (1):** Tungsten Carbide (WC-Co).
**Shielding/concrete (5):** OPC Concrete, LAC Concrete (Limestone), Borated Concrete (Kretekast),
Lead, Silicon Dioxide (SiO2).
**Reference elements (4):** Iron (natural), Chromium (natural), Nickel (natural), Manganese (natural).
**Moderator (1):** Water (H2O).

### Key Technical Decisions on Record
- Single-pulse model (not multi-pulse) — adequate for pulsed-power regime; simplest correct model.
- All nuclear data bundled in data.py — no runtime API calls; portable, offline-capable.
- Atom fraction convention throughout (not number density); physics.py converts via density.
- Impurity isotopes included directly in `isotopes` dict at modeled concentration — this makes
  the activation calculation explicit and traceable.
- `impurities` metadata dict documents known impurity ranges and significance but does not feed
  the calculation directly (that's done via `isotopes`).
- Co-60 production captured via BOTH Co-59(n,γ) AND Ni-60(n,p) pathways — both are present.
- Literature tab is material-independent; visible before any material is selected.

### Open / Pending Items
- **Phase 3B:** Build preprocessing pipeline + download script using `endf-python`. Extract σ(E) from ENDF-6 files; populate `sigma_2p5` values and additional library dict entries. This is the next priority.
- **Phase 3C:** Cross-library diff report.
- **Phase 3D:** Cross Sections tab with σ(E) plots.
- **Kretekast trace impurities:** OPC-level Eu/Co/Cs/Sc assumed until Marc provides measured data.
- **GitHub setup:** .gitignore created; README and git init pending. Marc deprioritized — don't push unless asked.
- **Regulatory lines on plots / time-to-clearance:** Marc noted as possibly of interest later, not immediate.
- **Formal per-field source tagging (ENDF/measured/estimate):** Partially done via notes text; full structured tagging deferred to Phase 3.

---

## Git / Repository Notes

No git repository initialized as of 2026-04-03. Planned to add to GitHub "soonish" per Marc.

**Files to exclude (.gitignore):**
- `venv/` — Python virtual environment
- `__pycache__/` — Python bytecode
- `*.pyc`
- `.env` (if any secrets added later)

**Files to include in repo root:**
- All .py files, templates/, references.json, requirements.txt
- ROADMAP.md, ACTIVITY_LOG.md
- NotesFromOtherSources/ — literature notes are part of project documentation

**Suggested README content:**
- Project description (single-pulse neutron activation calculator for fusion structural materials)
- Setup: `pip install flask`, `python app.py`, open localhost:5000
- Data sources (ENDF/B-VIII.0 for nuclear data, ICRP-74 for dose conversion)
- Material and reference list
