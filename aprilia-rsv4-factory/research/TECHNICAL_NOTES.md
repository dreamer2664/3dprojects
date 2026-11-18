# TECHNICAL NOTES — RSV4 Factory 1100 (MY2026)

Source numbers in [brackets] refer to `SOURCE_REGISTER.md`.

## 1. Authoritative 2026 baseline [2] (verified against PDF, 2026-11-18)

| Item | Value |
|---|---|
| Engine | V4 65°, 4 valves/cyl, liquid-cooled, Ride-by-Wire |
| Bore × stroke | 81 × 53.32 mm |
| Displacement | 1,099 cc |
| Max power | 220 HP (161.8 kW) @ 13,000 rpm |
| Max torque | 127 Nm @ 10,800 rpm |
| Gearbox / clutch | 6-speed / multiplate wet, slipper |
| Frame | Twin-spar aluminium |
| Front suspension | Öhlins Ø43 mm EC USD fork, fully adj., 125 mm travel |
| Rear suspension | Öhlins EC monoshock, fully adj., 115 mm travel |
| Front brake | 2 × Ø330 mm floating discs, Brembo **HYPURE** radial calipers |
| Rear brake | Ø220 mm disc, Brembo caliper |
| Wheels | Forged 17×3.5 (F), 17×6 (R), **5 split spokes** |
| Seat height | 840 mm |
| Fuel tank | 18 l |
| Wet weight | 204 kg |
| Std. features relevant to modelling | Full-LED headlight + indicators with light signature; bonded 5" TFT; backlit switch cubes; Öhlins EC steering damper; metal braided brake hoses; passenger seat **and** aero-cover |

Notes: 2025 press [5] stated 220 hp @ 13,100 and 125 Nm; the 2026 sheet states 13,000 rpm / 127 Nm → **2026 sheet wins**.

## 2. Dimensions not on the 2026 sheet (from earlier official / workshop sources)

| Item | Value | Source | Confidence |
|---|---|---|---|
| Wheelbase | 1,435 mm (1435.8) | [10],[11] | High (unchanged chassis) |
| Overall length | 2,055 mm | [10],[11] | High |
| Overall width (bars) | 735 mm | [10],[11] | High |
| Height to fairing top | 1,150 mm | [10] | Medium (2025 screen new) |
| Headstock angle | 24.6° (on-bike) / 26.5° (bare chassis) | [11] / [10] | High |
| Trail | 104.5 mm | [11] | High |
| Tyres | 120/70 ZR17, 200/55 ZR17 (Pirelli Diablo Supercorsa per photos) | [13], photos | High |
| Chain | 525, 110 links | [10] | High |
| Final drive | 16/41 | [10],[11] | High |
| Bare chassis A / B | 655.5 mm / 337.5 mm (headstock ref → swingarm pivot) | [10] p.14 | High |
| Rear shock stroke | 62 mm (progressive linkage) | [10] | Medium (2019–20) |
| Fork offset (derived) | ≈30 mm: trail = (R·sinθ − offset)/cosθ with R = 300 mm, θ = 24.6° → offset = 29.9 mm | derived | Medium |

### Derived tyre geometry
- Front 120/70-17: R = 215.9 + 0.70·120 = **299.9 mm**, width 120 mm.
- Rear 200/55-17: R = 215.9 + 0.55·200 = **325.9 mm** nominal (real Supercorsa SP ≈ 320 mm; model uses 322 mm).

## 3. Engine architecture [8],[10], diagrams
- 65° narrow-V, longitudinal (crank transverse), front bank leaning forward.
- Monobloc upper crankcase with integral cylinder liners, horizontally split lower case (diagram *crankcases-i*).
- DOHC per bank, **chain drives intake cam only**, exhaust cam gear-driven from intake cam → very compact heads.
- Bucket tappets with shims (*valve-tappets-and-shims*), dual valve springs on intake side (*cylinder-head-valves*).
- **Magnesium** cam covers, sump, external covers (2021 press) → modelled as dark-grey satin magnesium casting finish.
- Counter-rotating balance shaft.
- Two twin throttle bodies (front pair, rear pair), 52 mm, each with its own RbW motor housing on the side; secondary injectors in airbox lid (*air-box* items 9–10), variable-length intake trumpets (items 21/24).
- Wet sump, separate oil radiator, spin-on cartridge filter, dual trochoidal pump.
- Exhaust (diagram *silencer*): front bank headers (1) curve down and back; rear bank headers (9, 10) go down behind the engine; all four join an **under-engine collector/catalyst box (6)** with 3 lambda sensors (7); single link pipe up to right-side silencer (11) with end cap (30) and heat guard (12); exhaust valve servo (21) with two cables (28/29).
- Cooling: single curved main radiator (1) with **two fans** (2, 3) on the rear face, expansion tank on the left (31), thermostat (10).

## 4. Chassis findings from 2025 exploded diagrams [6]
- **Frame** (*frame-bodywork*): twin spar of welded cast + pressed elements; steering-head eccentric inserts (2) → adjustable head angle; adjustable swingarm pivot inserts (12/13); engine hangers with spacers; separate **tubular-section bolted rear subframe** (27) with 4 mounting bolts (31) and a seat-lock/tail bracket (29).
- **Swingarm** (*swing-arm*): double-sided banana arm; inverted (upside-down) brace on the upper right side to clear the exhaust; pivot shaft (5) with needle bearings (14); chain slider (2); hugger/mudguard (3) bolted on; chain adjuster blocks (24/25).
- **Shock** (*shock-absorber*): Öhlins TTX with piggy-back reservoir and electronic valve housing on the head; linkage rocker (9) with two dog-bone plates (2).
- **Steering** (*steering*): forged aluminium upper clamp (1) with central nut (9), stem (2) pressed into lower clamp, 2 pinch bolts per side lower; steering damper (3) mounted transversely.
- **Front fairing** (*front-fairing*): nose (1), screen (2) with 4+ screws, side trims (3), lower winglet element (4), mirrors (5,6) fairing-mounted, **upper and lower inner aero elements** (7,8) forming the dual-layer winglets.
- **Side fairing** (*side-fairing*): large upper side panels L/R (1,2), small inserts (3,4,5), lower belly side (6), belly pan (7), inner panels (10).
- **Rear body** (*rear-body*): tail sides L/R (1,2), tail top / aero-cover (5), under-tail (3,4), rear mudguard tray (11).
- **Rear wheel** (*rear-wheel*): sprocket carrier with cush drive (10), 41T sprocket (4) with 5 studs, ABS tone ring (25), 220 mm disc (26).
- **Handlebar** (*handlebar-controls*): forged clip-ons (2,3) clamping above the top clamp? → No: below the top clamp (photos p_19 show clip-ons under top clamp), backlit switch cubes (4,5), throttle with RbW sensor (6), bar ends (1).

## 5. Visual findings from 2026 photographs [1],[3]
- **Colour layout (Shakedown Indigo)**: matte black base; **gloss/matte violet** (~sRGB 105, 40, 210) nose cone, upper wing and lower wing; violet chevron graphics on tank, tank-cover sides and tail top; side fairing with white/grey diagonal stripe field and **red** (≈sRGB 235, 45, 25) chevrons; red + white arrows on tail sides; "aprilia" white logotype on tank sides and nose; Italian tricolour flag under nose logo; "RSV4" logo on upper side fairing.
- Frame: **black** painted (not silver) on MY2026 Factory; swingarm **silver/natural aluminium** (satin), Öhlins fork tubes gold TiN, black fork bottoms, wheels **black**, Brembo Hypure **natural grey anodised** with red logo.
- Silencer: brushed titanium-look sleeve, black end cap and black heat shield; catalyst box under engine shows **bronze/straw heat tint**.
- Seat: black, two-tone texture; passenger aero-cover in photos (tail hump with violet graphic).
- Numberplate holder: long black tail-tidy arm under tail with LED rear light + indicators.
- Mirrors: black on long stalks from fairing; indicator lenses separate on the fairing sides in p_15 (rider-facing amber lenses on fork-level? — the amber discs on fork in side views are **reflectors on fork legs**).
- Clutch-side reservoir and front brake reservoir (smoked, round) on clip-ons; TFT centrally mounted under screen.
