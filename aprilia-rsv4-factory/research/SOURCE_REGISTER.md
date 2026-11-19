# SOURCE REGISTER — Aprilia RSV4 Factory 1100 (MY2026, Shakedown Indigo)

All access dates: **2026-11-18** (UTC, sandbox clock). "Archived" = a local copy exists in this repository.
Status key: ✅ opened & examined · ⚠️ partially accessible · ❌ inaccessible

## A. Primary official Aprilia sources

| # | Source | URL | Model year | Status | Local archive | What was learned | Informs |
|---|---|---|---|---|---|---|---|
| 1 | Official RSV4 Factory 1100 product page | https://www.aprilia.com/en_EN/models/rsv4/rsv4-factory-1100-4s4v-2026/ | 2026 | ✅ (chunks 1–2 of 3 read; chunk 3 is accessories/footer) | `research/photos/official_*` (16 images incl. 7× 3840×2560 premium gallery) | 220 hp @ 13,000 / 127 Nm @ 10,800; 52 mm throttle bodies; **dual-layer winglets under the windscreen**, aero surfaces on fairing + tail; "nolder" on upper fairing; inverted-brace swingarm; 5" TFT; backlit switch cubes; full-LED headlight with DRL; rear light integrated in removable numberplate holder; fans optimise heat extraction; Öhlins Smart EC 2.0 w/ TiN fork | Overall styling, livery, aero, lights, cockpit, all exterior checks |
| 2 | Official 2026 Factory tech spec PDF | https://wlassets.aprilia.com/wlassets/aprilia/master/tech_spec/RSV4/RSV4_Factory_tech_spec_EN/original/RSV4_Factory_tech_spec_EN.pdf | 2026 | ✅ (needed browser UA; first plain request was "Access Denied") | `research/pdf/RSV4_Factory_tech_spec_EN_2026.pdf`, text in `research/text/` | Authoritative baseline (see TECHNICAL_NOTES §1). Adds: wheels 17×3.5 / 17×6, **5 split spokes**; metal braided hoses; Öhlins EC steering damper; passenger seat + aero-cover standard | Every dimensioned component |
| 3 | Press release "Aprilia Factory range: new graphic variants" + gallery | https://press.piaggiogroup.com/en_EN/post/show/336555/aprilia-factory-range-new-grap.html | 2026 | ✅ text read in full; all **9** RSV4 Factory images downloaded at max served res (1920 px long edge — server refuses larger) | `research/photos/p_11.jpg … p_19.jpg` | Livery concept: arrows along sides (hot-air flow, fading to tail) + CFD-flow-indicator lines; gloss/matte intersections give 3 apparent depth levels; colours purple/white/red. Photos: 3/4 front R (p_11, p_12 "acc"), 3/4 front L (p_13), 3/4 rear R (p_14), front (p_15, p_16 "acc"), right side (p_17), left side (p_18), cockpit top (p_19) | Livery, proportions, orthographic QC overlays |
| 4 | 2026 Aprilia range brochure PDF | https://www.aprilia.com/wlassets/EICMA/EICMA-2025/Aprilia/brochure/EN-DIGITAL-Aprilia-Range-11-2025/original/EN-DIGITAL-Aprilia-Range-11-2025.pdf | 2026 | ❌ **Inaccessible** — Akamai "Access Denied" (HTTP 403 body) for plain and browser user agents | none | — | — |
| 5 | Press release "New Aprilia RSV4 and RSV4 Factory" (2025 evolution) | https://press.piaggiogroup.com/en_EN/post/show/308733/new-aprilia-rsv4-and-rsv4-fact.html | 2025 | ✅ text chunks 1–2 read (remaining chunks are image index lists) | text notes only | Two stacked wing surfaces beneath windshield; Cx −6 %, wheelie tendency −8 %; new side panels + tail; minimalist rear light in numberplate holder, indicators carry lighting functions; new lighter aluminium upper triple clamp; **Hypure** replaces Stylema; 52 mm TBs, **catalyst repositioned** (under-engine box seen in photos); bending lights in headlight housings | Aero, top clamp, brakes, exhaust layout, lights |

## B. OEM parts catalogues / exploded diagrams

| # | Source | URL | Model year | Status | Local archive | What was learned | Informs |
|---|---|---|---|---|---|---|---|
| 6 | aprilia-parts.nl — RSV4 1100 Factory E5+ (EU) | https://aprilia-parts.nl/en/parts-catalog/aprilia-rsv4-1100-factory-e5-eu-1100-2025 | 2025 | ✅ index read; **all 58 diagrams downloaded at full resolution** (subpages return empty body to curl; full-size image URL derived from index thumbnail hash and verified against `fetch_page` of the Öhlins fork subpage) | `research/parts_diagrams/aprilia-rsv4-1100-factory-e5-eu-1100-2025/*.webp`, `diagram_index.json` | See TECHNICAL_NOTES §4 for per-diagram findings. Examined in detail: frame-bodywork, swing-arm, silencer, crankcases-i, front-fairing, side-fairing, cooling-system, air-box, rear-body, steering, cylinder-head-valves, throttle-body, shock-absorber, rear-wheel, handlebar-controls, front-fork-ohlins (parts list) | Frame, swingarm, exhaust, engine, bodywork split lines, cooling, intake, steering, cockpit |
| 7 | aprilia-parts.nl — RSV4 1100 Factory (EU) | https://aprilia-parts.nl/en/parts-catalog/aprilia-rsv4-1100-factory-eu-1100-2024 | 2024 | ✅ all 58 diagrams downloaded | `research/parts_diagrams/aprilia-rsv4-1100-factory-eu-1100-2024/` | Used for cross-checking which parts changed for 2025 (different hashes on: air-box, clutch-cover, cooling-system, crankshaft, decal, frame-bodywork, front-electrical, fuel-tank, lubrication, rear-body, side-fairing, silencer, steering…) → those are 2025+ specific and the 2025 version is used | Change detection 2024→2025 |

## C. Additional technical & visual references

| # | Source | URL | Model year | Status | Local archive | What was learned | Informs |
|---|---|---|---|---|---|---|---|
| 8 | Press release "APRILIA RSV4" (2021 generation) | https://press.piaggiogroup.com/en_EN/post/show/205020/aprilia-rsv4.html | 2021 | ✅ chunks 1–2 of 14 read (design, chassis, engine) | text notes only | Cast + pressed aluminium elements welded; adjustable engine height, headstock angle, swingarm pivot; swingarm with **lower reinforcing brace**, 3 welded elements; extended axle adjustment slot; **magnesium** cam covers, sump and external covers; chain drives intake cam only, intake→exhaust cam via gear; monobloc crankcase with integral liners; counter-shaft; stroke 52.3→53.3 mm | Engine construction, materials, swingarm |
| 9 | Same URL as #5 (user listed it twice as "older gallery") | https://press.piaggiogroup.com/en_EN/post/show/308733/new-aprilia-rsv4-and-rsv4-fact.html | 2025 | ✅ (gallery lists 89 images: 44 dynamic, statics). Dark Kraken livery — **used for mechanics only, never livery** | — | Confirms 2025 hardware is same as 2026 apart from graphics (2026 release says "technical features remain unchanged") | Mechanics |
| 10 | Aprilia **Service Station Manual 2Q000401 — RSV4 1100 Factory** (dealer manual, 549 pp.) | https://cdn.webshopapp.com/shops/233369/files/369289182/aprilia-rsv4-1100-factory-service-station-manual-2.pdf | 2019–2020 (1077 cc) | ✅ downloaded; characteristics chapter read in full; pages rendered | `research/pdf/RSV4_1100_Factory_Service_Station_Manual_2Q000401.pdf`, `research/manual_pages/` | Chassis "A" 655.5 mm, "B" 337.5 mm, head angle 26.5° (bare frame); chain **525, 110 links (Regina)**; final drive 16/41, primary 44/73; gear ratios; wet sump + oil cooler; dual trochoidal pump; 3-way thermostat; Bosch Li battery; NGK plugs; stick coils; rear shock stroke 62 mm, progressive linkage. Engine-removal photo sequence shows real frame finish (cast silver aluminium), hose routing | Frame geometry, drivetrain, cooling, wiring |
| 11 | Official RSV4 Factory tech spec 2022 | https://wlassets.aprilia.com/wlassets/aprilia/master/tech_spec/2022/aprilia_RSV4_factory_en_2022/original/aprilia_RSV4_factory_en_2022.pdf | 2022 | ✅ | `research/pdf/RSV4_Factory_tech_spec_EN_2022.pdf` | Wheelbase 1435.8 mm; length 2055; width 735; headstock 24.6°; trail 104.5 mm; 330 mm disc with **6-pin** aluminium flange; rear Brembo 2×32 mm; compression 13.6:1; Öhlins NIX fork, TTX shock piggy-back | Geometry, brakes |
| 12 | Official RSV4 1100 Factory tech spec MY20 | https://storeusa.aprilia.com/files/technical/RSV4_1100_factory_my20.pdf | 2020 | ✅ | `research/pdf/RSV4_1100_Factory_tech_spec_MY20.pdf` | Wheels "fully machined, 5 double spokes"; rear 2-piston isolated caliper | Wheels |
| 13 | motorcycle.com spec page 2025 RSV4 Factory | https://www.motorcycle.com/specs/aprilia/sport/2025/rsv4/factory-1100/detail.html | 2025 | ⚠️ search snippet only (third-party) | — | Length 2055, width 735, height 1148, wheelbase 1435, tyres 120/70 ZR17 + 200/55 ZR17 (Pirelli) | Cross-check only |
| 14 | International Motorsports dealer spec | https://www.internationalmotorsports.com/new-models/2025-aprilia-rsv4-factory-1100-29255165b | 2025 | ⚠️ snippet (third-party) | — | Rake 26.5°, trail 103.8 mm | Cross-check only |
| 15 | Brembo Hypure product data (FC-Moto listing of Brembo text; OPPRacing; Brook Suspension) | https://www.fc-moto.com/en-gb/p/brembo-s.p.a.-hypure-caliper-right-BI-1152480006 | 2025 | ⚠️ snippet | — | Asymmetric monobloc, 3-bridge gravity-cast aluminium; 4×30 mm pistons; 100 mm radial mount; discs 290–340 × 5 mm; OE finish **grey natural anodised**; patented spring/pad/pin | Front calipers |
| 16 | Öhlins TTX36 owner's manual (motowheels mirror) | https://motowheels.com/pdf/327288 | — | ⚠️ snippet | — | Concentric twin-tube TTX36, piggy-back reservoir, adjusters on cylinder head | Rear shock |

## D. Searched for but NOT obtained (explicitly)

- Official CAD / STEP data — not public. ❌
- Frame / swingarm engineering drawings — not public; only the bare-chassis A/B/C dimension drawing (#10). ❌
- 2025/2026 workshop manual — not found publicly; the 2019–20 manual (#10) is used for architecture only. ❌
- Wiring diagram for MY2025+ — not obtained (2019–20 manual contains one; not yet transcribed). ⚠️
- Homologation documents / patents — not searched in depth yet (TODO).
- Range brochure (#4) — blocked. ❌

**No engineering drawings were fabricated.** All internal dimensions not covered above are documented as assumptions in `DECISIONS.md`.

## CC0 environment assets (Poly Haven, licence CC0)
| # | Source | Date | Used for |
|---|--------|------|----------|
| 17 | polyhaven.com/a/studio_small_09 (2k HDR) | 2026-11-18 | Studio lighting/environment for hero + technical renders |
| 18 | polyhaven.com/a/brown_photostudio_02 (2k HDR) | 2026-11-18 | Dark studio environment (rear hero, details, final) |
| 19 | polyhaven.com/a/kloofendal_48d_partly_cloudy_puresky (2k HDR) | 2026-11-18 | Outdoor/racetrack lighting (low front shot) |
| 20 | polyhaven.com/a/asphalt_02 (diff/rough/nor_gl 2k) | 2026-11-18 | Ground texture for outdoor shot |
