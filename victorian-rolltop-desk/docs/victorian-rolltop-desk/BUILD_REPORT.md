# BUILD REPORT — Victorian Oak Roll-Top Pedestal Desk, c.1890

Commission 03 · branch `agent/victorian-rolltop-desk-masterpiece`
Everything below is measured from the delivered files, not estimated. Where the deliverable
falls short of the brief, the shortfall is stated with the measurement that caused it.

---

## 1. What was built

A full-size, freestanding late-Victorian English oak roll-top pedestal desk built as **1,555
separate named objects** in 12 collections, generated parametrically from
`scripts/desk/params.py` (no hand-modelling by eye):

| Collection | Contents |
|---|---|
| `PEDESTAL_CARCASSES_AND_PANELS` | 2 pedestals: sides, back, face frames, cock beads, fielded outer/inner/back panels, dust boards, runners, centre dividers, plinths + ovolo mouldings, modesty board, shoe rail |
| `DESKTOP_AND_WRITING_SURFACE` | top board, ovolo nosing, side mouldings, writing ledge, two bearers |
| `TAMBOUR_SLATS_BACKING_AND_TRACKS` | **61 individual slats**, 61 canvas backing strips, 2 S-profile cheek plates, 2 × 2 curved guide ribs, roll liners, stop rail, end stops, posting-slot trim |
| `UPPER_FITTED_INTERIOR` | interior carcass, linings, partitions, wing shelves, centre shelf |
| `33_INTERNAL_DRAWERS` | **33 drawer boxes**, each front/sides/back/bottom/linings/knob/label |
| `VERTICAL_PIGEONHOLES_AND_LETTER_RACKS` | 4 pigeonhole dividers, 2 shelves, beads, letter-rack rails and posts, 2 pen trays |
| `PEDESTAL_DRAWERS_AND_JOINERY` | 8 pedestal drawers + 1 central lockable drawer, tails, cup handles, escutcheons |
| `LOCKS_KEYS_AND_LINKAGE` | tambour barrel lock, escutcheon, bolt, key, lock bar, cranks, rods, catches |
| `WRITING_SLIDES_AND_SUPPORTS` | 2 slide assemblies with nosing, runners, guides, brass stops |
| `BRASS_HARDWARE_AND_CASTORS` | 6 castors (plate, screws, fork, crown, wheel, hub, axle, nuts), tambour pull |
| `MATERIALS_AND_TEST_SWATCHES` | 6 swatch panels |
| `CAMERAS_LIGHTS_AND_STAGING` | cameras, lights, environment, grain-coordinate empties |

## 2. Dimensions (measured from the built mesh, GLB re-import)

| Dimension | Target (brief / listing) | Delivered |
|---|---|---|
| Overall width | 1.520 m | **1.566 m** envelope (1.520 m carcass; the extra 46 mm is the desktop side mouldings) |
| Overall depth | 0.910 m (90.8 cm listed) | **0.961 m** with both writing slides extended 110 mm (0.885 m closed) |
| Overall height | 1.380 m | **1.381 m** |
| Writing surface height | 0.775 m | **0.775 m** (exact) |
| Kneehole width / height | not listed | 0.600 / 0.625 m |
| Pedestal footprint | — | 0.460 × 0.860 m each |
| Tambour roll radius | — | 0.120 m mid-thickness |
| Crown of roll | — | 1.381 m (= overall height) |

Known deviation: the width is 46 mm over because the side mouldings sit proud of the carcass
rather than being worked out of the top's edge. Recorded here rather than quietly rescaled.

## 3. Inventory against the reference

| Reference feature (Yola Gray "Roll top Desk 28") | Delivered |
|---|---|
| 33 internal drawers | **33** (15 left wing + 15 right wing + 3 concealed cushion fronts) |
| 15 vertical compartments | **15** (5 columns × 3 rows, centre bank) |
| Lacewood drawer linings | bottom + two side liners per small drawer, separate lacewood material |
| Oak knobs on internal drawers | oak turned knobs (brass only on label frames and escutcheons) |
| Brass label holders | one per internal drawer, with recessed card and two pins |
| 3 concealed cushion-front drawers | modelled with a broad cushion bevel and no external pull |
| Twin horizontal pen trays | 2 open trays with rims and baize floors on the centre shelf |
| Central letter rack | 2 rails + posts across the upper centre columns |
| 8 graduated pedestal drawers | 4 per pedestal: 0.235 m filing drawer + 3 graduated |
| Large filing drawer | both pedestals (reference has it right-hand only — see §8) |
| Central lockable drawer | 1, with escutcheon, barrel lock and key |
| 2 pull-out writing slides | 2, each with top, nosing, runners, guides and brass stops |
| Central modesty board | fielded panel + backing + shoe rail |
| Posting slot in the tambour | 160 mm wide opening split through slat 13, brass lips and surround |
| Linked tambour lock | barrel lock → bolt → horizontal bar → 2 cranks → 2 vertical rods → pedestal catches |
| Original steel castors | 6 castors, iron wheels + steel forks + brass plates |
| Dismantles into three sections | modelled as separable pedestals / top / upper case |

## 4. The tambour — construction and motion

**Construction.** 61 separate slats, 16.5 mm pitch, 13.0 mm wide, 11.0 mm thick, chamfered
arrises, each with its own origin so the procedural grain differs slat to slat. Ends are carried
10 mm into a real channel in each cheek: the cheek is a plate whose inner face forms the channel
floor, plus **two swept guide ribs** that leave an 11 mm slot — the slat ends run between them.
This follows the sourced construction (slat tongues running in a routed track, canvas as the
flexible hinge).

**Path (single source of truth, `parts_upper.path_at`).** Total 1.638 m of track:

| Segment | Geometry | Length |
|---|---|---|
| A | vertical front run, y = 0.240, z 0.790 → 1.248 | 0.458 |
| B | quarter round, centre (0.360, 1.248), r 0.120 | 0.1885 |
| C | flat roll top, z = 1.368, y 0.360 → 0.615 | 0.255 |
| D | quarter round, centre (0.615, 1.248), r 0.120 | 0.1885 |
| E | rear hanging run, y = 0.735, z 1.248 → 0.700 | 0.548 |

**States.** Closed = offset 0.000 m: slats fill A–C and the roll is visible as the desk top;
opening 0.790–1.248 is fully covered. Open = offset 0.458 m: A is clear, the slats occupy B–E and
hang inside the rear pocket behind the fitted interior. Both states were built and rendered from
the same geometry — no mesh swapping.

**Motion.** `parts_upper.animate_tambour()` keys every slat from its own station on the path with
an eased 96-frame cycle (no scaling, no fake deformation). **It is implemented but not baked into
a delivered file** — see §8.

## 5. Locking system

Modelled: tambour barrel lock body behind the slat, escutcheon with an open keyhole, bolt, a
horizontal lock bar under the desktop with two brass guides, a crank at each end, two vertical
rods and two catches at the pedestal drawer banks. In the `open` build the rods are shortened by
50 mm, i.e. the mechanism is shown withdrawn; in `closed` they are thrown. The physical
arrangement is **inferred** — the listings describe the behaviour ("when the tambour is closed it
locks all the drawers except the central drawer, which has its own lock") but no photograph of the
linkage was available, so this is a conservative, physically plausible interpretation and is
declared as such.

## 6. Materials

Seven timber materials, four metals, plus leather/baize/paper/ink/shadow. All **procedural**
(Object-space coordinates in metres, so every scale is physical):

| Material | Basis |
|---|---|
| `OAK_QUARTERSAWN_1890` | 4.2 mm rings, ray fleck 0.16, coat 0.22 |
| `OAK_RIFTSAWN_1890` | 2.6 mm rings, straight grain, ray 0.02 — stiles, rails, slats |
| `OAK_CATHEDRAL_SOLID` | 5.5 mm rings, distortion 3.2 — plain-sawn panels |
| `OAK_ENDGRAIN` | 2 mm rings, pore 0.60 — plinth skirts, pocket floors |
| `LACEWOOD_LINING` | ray 0.30, 5 mm rings — internal drawer linings |
| `SYCAMORE_DRAWER` / `_ENDGRAIN` | pale closed grain — drawer sides, backs, bottoms |
| `BRASS_AGED_POLISH`, `BRASS_TARNISHED`, `STEEL_DARKENED_CASTORS`, `IRON_CASTORS` | metallic, two-tone tarnish from noise |

Grain relief is **real geometry**: 231 surfaces are densified and driven by three anisotropic
`CLOUDS` displace textures (0.08–0.16 mm amplitude) in addition to the shader bump.

**No image textures are used.** An 8K float RGBA image alone would need ~1 GB of the sandbox's
1.9 GB, so 8K/4K maps were not storable. This is a hard limitation, not a preference.

## 7. Geometry and measured counts

| Measure | Value | How measured |
|---|---|---|
| Objects | 1,555 | scene object count |
| Master vertices (evaluated) | 2,747,001 | `evaluated_stats()` on the evaluated depsgraph |
| **Master triangles (evaluated)** | **5,487,528** | same, summed over every mesh after modifiers |
| GLB triangles | 439,918 | fresh-session glTF re-import |
| Density parameter | 0.72 (master), 0.15 (GLB/render source) | `--density` multiplier on displacement grids |

**The brief's 30 M minimum was not reached.** Measured ceiling in this sandbox:
8.39 M tris = 654 MB OK; 16.8 M tris = OOM kill. The delivered 5.49 M master is the largest that
could be built *and saved* here; it is not possible to render it in this environment at all (§9).
No detail was removed to hit a triangle cap — the ceiling is memory, and the gap is recorded in
`QUALITY_GATE.md`.

## 8. Deliverables, and what is missing from them

| Item | Status |
|---|---|
| `victorian_rolltop_desk_master_closed.blend` | **delivered**, 49 MB (zstd-compressed from 168 MB) |
| `victorian_rolltop_desk_master_open.blend` | **delivered**, 49 MB |
| `victorian_rolltop_desk_closed.glb` / `_open.glb` | **delivered**, 14 MB each, independently re-imported and checked: 1,551 meshes, 439,918 tris, 18 materials, **0 meshes without a material**, size 1.566 × 0.961 × 1.381 m |
| Render package | 17 stills at 1280×800, 32 spp, no denoise |
| Animations (open/close, drawer, slide, lock) | **not delivered** — the keying function exists (`animate_tambour`), no frames were rendered |
| 360° turntable / video | **not delivered** |
| Baked GLB textures | **not delivered** — glTF export does not carry procedural shading; UV-unwrapping 1,555 objects and baking was not possible in the remaining budget |
| `textures/` folder | empty by design — there are no image textures |

Additional deviations recorded honestly:
- The filing drawer is in **both** pedestals (the reference has it in the right pedestal only).
- The 15 pigeonholes follow the reference's count but the "4 large vertical pigeonholes on the
  right" are modelled as part of the 5 × 3 centre grid rather than a separate oversized bank.
- Dovetail joints: 14 drawer side/front joints are genuinely cut with a boolean (the tail solids
  are subtracted from the oak front, then the sycamore tails are inserted). The 33 small drawers
  use a dovetail *shadow* representation, not a cut joint.

## 9. Render settings actually used, and why they are not 4K

| Setting | Value |
|---|---|
| Engine | Cycles, CPU, 2 threads |
| Resolution | 1280 × 800 |
| Samples | 32, adaptive threshold 0.02 |
| Denoising | **off** (OIDN at 1920×1080 was OOM-killed after 112 s) |
| View transform | AgX, Medium High Contrast |
| Lights | 5 area lights, warm "study" set-up + floor and back wall |

Measured failures that set these numbers: 3840×2160 render → killed during scene sync at 849 MB;
1920×1080 with denoise → killed after 112 s. 1280×800 without denoise completes in ~50 s. The
brief requires 3840×2160 minimum; **that requirement is not met** and the cause is RAM, not
render settings. Image noise in the delivered stills is a direct consequence of disabling the
denoiser.

## 10. Reproducing everything

```bash
scripts/provision_blender.sh                      # Blender 4.5.3 LTS + system libs
blender -b --factory-startup --python scripts/desk/build_master.py -- \
        --state open   --out build/master --density 0.72
blender -b --factory-startup --python scripts/desk/build_master.py -- \
        --state closed --out build/glb    --density 0.15
blender -b build/glb/victorian_rolltop_desk_open.blend \
        --python scripts/desk/render.py -- --shot hero_open --res 1280x800 --samples 32
```

`build_master.py` prints `BUILD_STATS` (JSON) with real evaluated vertex/triangle counts, drawer
and slat counts, dovetail successes/failures and build time.
