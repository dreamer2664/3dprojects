"""
materials.py — procedural materials for the 1890 oak roll-top desk.

All timbers are procedural (no image textures): the sandbox has ~1.9 GB RAM and an 8K
float RGBA image alone would need ~1 GB, so image-based 8K maps are not storable here.
Materials are therefore built from layered noise/wave nodes with real anisotropic grain
direction, plus a set of CLOUDS/MUSGRAVE textures used as actual Displace modifiers so
the grain relief is geometry, not only a bump map.
"""
import bpy


def _clear(mat):
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (900, 0)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.location = (600, 0)
    nt.links.new(b.outputs["BSDF"], out.inputs["Surface"])
    return nt, b


def _coords(nt, scale=(1, 1, 1), rot=(0, 0, 0), obj=True):
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = scale
    mp.inputs["Rotation"].default_value = rot
    nt.links.new(tc.outputs["Object" if obj else "Generated"], mp.inputs["Vector"])
    return mp.outputs["Vector"]


def _ramp(nt, stops, interp='LINEAR'):
    r = nt.nodes.new("ShaderNodeValToRGB")
    r.color_ramp.interpolation = interp
    # rebuild stops
    els = r.color_ramp.elements
    while len(els) > 1:
        els.remove(els[-1])
    els[0].position = stops[0][0]
    els[0].color = (*stops[0][1], 1)
    for pos, col in stops[1:]:
        e = els.new(pos)
        e.color = (*col, 1)
    return r


def wood(name, base, dark, ring_mm=7.0, distortion=1.8, ray_strength=0.10,
         pore_strength=0.22, rough=(0.26, 0.44), grain_axis='X', sheen=0.0,
         ray_scale_mm=6.0, clearcoat=0.22, cathedral=False):
    """Layered timber shader driven by real metric values.

    ring_mm        average growth-ring spacing across the board (English oak ≈ 2-8 mm)
    distortion    0 = perfectly straight rift grain, >6 = wild cathedral figure
    rays          medullary-ray fleck strength (quarter-sawn oak only; 0 for rift)
    Coordinates are Object space in metres, so all scales below are physical.
    """
    mat = bpy.data.materials.new(name)
    nt, bsdf = _clear(mat)
    # stretch coordinates along the grain so features elongate along the board
    axis_vec = {'X': (1.0, 1.0, 1.0), 'Y': (1.0, 1.0, 1.0), 'Z': (1.0, 1.0, 1.0)}[grain_axis]
    vec = _coords(nt, scale=axis_vec)
    bands_dir = {'X': 'Z', 'Y': 'Z', 'Z': 'Y'}[grain_axis]

    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = 'BANDS'
    wave.bands_direction = bands_dir
    wave.wave_profile = 'SIN'
    wave.inputs["Scale"].default_value = 1000.0 / ring_mm
    wave.inputs["Distortion"].default_value = distortion
    wave.inputs["Detail"].default_value = 3.0
    wave.inputs["Detail Scale"].default_value = 0.6
    wave.inputs["Detail Roughness"].default_value = 0.62
    nt.links.new(vec, wave.inputs["Vector"])
    rings = _ramp(nt, [(0.26, dark), (0.54, base), (0.88, dark)], interp='EASE')
    nt.links.new(wave.outputs["Fac"], rings.inputs["Fac"])

    # long board-to-board colour drift
    drift_n = nt.nodes.new("ShaderNodeTexNoise")
    drift_n.inputs["Scale"].default_value = 2.4
    drift_n.inputs["Detail"].default_value = 3.0
    nt.links.new(vec, drift_n.inputs["Vector"])
    drift = _ramp(nt, [(0.30, (0.78, 0.77, 0.76)), (0.70, (1.0, 1.0, 1.0))])
    nt.links.new(drift_n.outputs["Fac"], drift.inputs["Fac"])
    mix_col = nt.nodes.new("ShaderNodeMix")
    mix_col.data_type = 'RGBA'
    mix_col.blend_type = 'MULTIPLY'
    mix_col.inputs["Factor"].default_value = 1.0
    nt.links.new(rings.outputs["Color"], mix_col.inputs[6])
    nt.links.new(drift.outputs["Color"], mix_col.inputs[7])

    # earlywood pores: fine dotted relief that follows the grain
    pore_vec = _coords(nt, scale={'X': (0.05, 60.0, 60.0), 'Y': (60.0, 0.05, 60.0),
                                  'Z': (60.0, 60.0, 0.05)}[grain_axis])
    pores = nt.nodes.new("ShaderNodeTexNoise")
    pores.inputs["Scale"].default_value = 12.0
    pores.inputs["Detail"].default_value = 6.0
    pores.inputs["Roughness"].default_value = 0.68
    nt.links.new(pore_vec, pores.inputs["Vector"])

    # medullary rays (quarter-sawn fleck): very fine lines across the grain, broken
    # into patches by a mask, so they read as ray tissue rather than a crackle network
    ray_wave = nt.nodes.new("ShaderNodeTexWave")
    ray_wave.wave_type = 'BANDS'
    ray_wave.bands_direction = bands_dir
    ray_wave.inputs["Scale"].default_value = 1000.0 / max(ray_scale_mm * 0.28, 0.4)
    ray_wave.inputs["Distortion"].default_value = 0.55
    ray_wave.inputs["Detail"].default_value = 1.0
    nt.links.new(vec, ray_wave.inputs["Vector"])
    ray_mask = nt.nodes.new("ShaderNodeTexNoise")
    ray_mask.inputs["Scale"].default_value = 7.0
    ray_mask.inputs["Detail"].default_value = 2.0
    nt.links.new(vec, ray_mask.inputs["Vector"])
    mask_r = _ramp(nt, [(0.40, (0.0, 0.0, 0.0)), (0.62, (1.0, 1.0, 1.0))], interp='EASE')
    nt.links.new(ray_mask.outputs["Fac"], mask_r.inputs["Fac"])
    ray_r = _ramp(nt, [(0.0, (1.0, 1.0, 1.0)), (0.55, (0.0, 0.0, 0.0))], interp='EASE')
    nt.links.new(ray_wave.outputs["Fac"], ray_r.inputs["Fac"])
    ray_prod = nt.nodes.new("ShaderNodeMath")
    ray_prod.operation = 'MULTIPLY'
    nt.links.new(ray_r.outputs["Color"], ray_prod.inputs[0])
    nt.links.new(mask_r.outputs["Color"], ray_prod.inputs[1])

    final = mix_col
    if ray_strength > 0:
        amt = nt.nodes.new("ShaderNodeMath")
        amt.operation = 'MULTIPLY'
        amt.inputs[1].default_value = ray_strength
        nt.links.new(ray_prod.outputs["Value"], amt.inputs[0])
        ray_mix = nt.nodes.new("ShaderNodeMix")
        ray_mix.data_type = 'RGBA'
        ray_mix.blend_type = 'MIX'
        nt.links.new(amt.outputs["Value"], ray_mix.inputs["Factor"])
        nt.links.new(mix_col.outputs[2], ray_mix.inputs[6])
        ray_mix.inputs[7].default_value = (base[0] * 1.55, base[1] * 1.45,
                                           base[2] * 1.40, 1.0)
        final = ray_mix
    nt.links.new(final.outputs[2] if hasattr(final, 'outputs') else final,
                 bsdf.inputs["Base Color"])

    # roughness: polish varies across the board, slightly glossier on raised grain
    rough_n = nt.nodes.new("ShaderNodeTexNoise")
    rough_n.inputs["Scale"].default_value = 9.0
    rough_n.inputs["Detail"].default_value = 4.0
    nt.links.new(vec, rough_n.inputs["Vector"])
    rr = _ramp(nt, [(0.30, (rough[0],) * 3), (0.72, (rough[1],) * 3)])
    nt.links.new(rough_n.outputs["Fac"], rr.inputs["Fac"])
    nt.links.new(rr.outputs["Color"], bsdf.inputs["Roughness"])

    # relief: pores + ring steps, layered into one normal
    b1 = nt.nodes.new("ShaderNodeBump")
    b1.inputs["Strength"].default_value = pore_strength
    b1.inputs["Distance"].default_value = 0.00035
    nt.links.new(pores.outputs["Fac"], b1.inputs["Height"])
    b2 = nt.nodes.new("ShaderNodeBump")
    b2.inputs["Strength"].default_value = pore_strength * 0.8
    b2.inputs["Distance"].default_value = 0.0006
    nt.links.new(wave.outputs["Fac"], b2.inputs["Height"])
    nt.links.new(b1.outputs["Normal"], b2.inputs["Normal"])
    nt.links.new(b2.outputs["Normal"], bsdf.inputs["Normal"])

    if clearcoat:
        bsdf.inputs["Coat Weight"].default_value = clearcoat
        bsdf.inputs["Coat Roughness"].default_value = 0.18
    if sheen:
        bsdf.inputs["Sheen Weight"].default_value = sheen
    return mat


def metal(name, base, rough=0.28, tarnish=0.0, tarnish_col=(0.22, 0.16, 0.07), aniso=0.0):
    mat = bpy.data.materials.new(name)
    nt, bsdf = _clear(mat)
    vec = _coords(nt, scale=(1, 1, 1))
    n = nt.nodes.new("ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = 18.0
    n.inputs["Detail"].default_value = 6.0
    nt.links.new(vec, n.inputs["Vector"])
    r = _ramp(nt, [(0.35, (rough * 0.7,) * 3), (0.75, (min(rough * 2.1, 0.95),) * 3)])
    nt.links.new(n.outputs["Fac"], r.inputs["Fac"])
    nt.links.new(r.outputs["Color"], bsdf.inputs["Roughness"])
    if tarnish > 0:
        tr = _ramp(nt, [(0.42, (1.0, 1.0, 1.0)), (0.72, (0.0, 0.0, 0.0))], interp='EASE')
        nt.links.new(n.outputs["Fac"], tr.inputs["Fac"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = 'RGBA'
        nt.links.new(tr.outputs["Color"], mix.inputs["Factor"])
        mix.inputs[6].default_value = (*base, 1)
        mix.inputs[7].default_value = (*tarnish_col, 1)
        nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    else:
        bsdf.inputs["Base Color"].default_value = (*base, 1)
    bsdf.inputs["Metallic"].default_value = 1.0
    # fine scratches on polished metal
    scr = nt.nodes.new("ShaderNodeTexNoise")
    scr.inputs["Scale"].default_value = 220.0
    scr.inputs["Detail"].default_value = 1.0
    nt.links.new(vec, scr.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.05
    bump.inputs["Distance"].default_value = 0.0002
    nt.links.new(scr.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def leather(name, base=(0.115, 0.055, 0.030), rough=0.62):
    mat = bpy.data.materials.new(name)
    nt, bsdf = _clear(mat)
    vec = _coords(nt, scale=(1, 1, 1))
    fib = nt.nodes.new("ShaderNodeTexNoise")
    fib.inputs["Scale"].default_value = 340.0
    fib.inputs["Detail"].default_value = 8.0
    fib.inputs["Roughness"].default_value = 0.8
    nt.links.new(vec, fib.inputs["Vector"])
    col = _ramp(nt, [(0.35, tuple(c * 0.78 for c in base)), (0.75, base)])
    nt.links.new(fib.outputs["Fac"], col.inputs["Fac"])
    # wear: large-scale lightening where hands rest
    wear = nt.nodes.new("ShaderNodeTexNoise")
    wear.inputs["Scale"].default_value = 5.0
    nt.links.new(vec, wear.inputs["Vector"])
    wr = _ramp(nt, [(0.45, (0.0, 0.0, 0.0)), (0.8, (0.10, 0.06, 0.035))])
    nt.links.new(wear.outputs["Fac"], wr.inputs["Fac"])
    add = nt.nodes.new("ShaderNodeMix")
    add.data_type = 'RGBA'
    add.blend_type = 'ADD'
    add.inputs["Factor"].default_value = 1.0
    nt.links.new(col.outputs["Color"], add.inputs[6])
    nt.links.new(wr.outputs["Color"], add.inputs[7])
    nt.links.new(add.outputs[2], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = rough
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 0.35
    bump.inputs["Distance"].default_value = 0.0004
    nt.links.new(fib.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return mat


def plain(name, color, rough=0.5, metallic=0.0, spec=0.5):
    mat = bpy.data.materials.new(name)
    nt, bsdf = _clear(mat)
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    return mat


def build_material_library():
    """Named library; every part of the desk references one of these."""
    M = {}
    # English oak, quarter-sawn: golden, bold medullary ray fleck on the radial faces
    M['oak_qsa'] = wood("OAK_QUARTERSAWN_1890", base=(0.168, 0.078, 0.024),
                        dark=(0.108, 0.048, 0.014), ring_mm=4.2, distortion=0.9,
                        ray_strength=0.16, pore_strength=0.30, rough=(0.22, 0.40),
                        grain_axis='X', ray_scale_mm=9.0)
    # rift-sawn: tight, straight grain with almost no ray figure — stiles, slats, rails
    M['oak_rift'] = wood("OAK_RIFTSAWN_1890", base=(0.158, 0.073, 0.022),
                         dark=(0.100, 0.045, 0.013), ring_mm=2.6, distortion=0.18,
                         ray_strength=0.02, pore_strength=0.24, rough=(0.24, 0.42),
                         grain_axis='Y', ray_scale_mm=4.0)
    # plain-sawn solid oak, cathedral figure
    M['oak_cathedral'] = wood("OAK_CATHEDRAL_SOLID", base=(0.172, 0.080, 0.025),
                              dark=(0.110, 0.049, 0.015), ring_mm=5.5, distortion=3.2,
                              ray_strength=0.04, pore_strength=0.30,
                              rough=(0.24, 0.42), grain_axis='X', ray_scale_mm=5.0)
    # the same quarter-sawn timber with the grain running along Y
    M['oak_qsa_y'] = wood("OAK_QUARTERSAWN_Y", base=(0.164, 0.076, 0.023),
                          dark=(0.104, 0.046, 0.014), ring_mm=4.2, distortion=0.9,
                          ray_strength=0.15, pore_strength=0.28, rough=(0.22, 0.40),
                          grain_axis='Y', ray_scale_mm=9.0)
    # end grain: open pores, darker, no ray figure
    M['oak_end'] = wood("OAK_ENDGRAIN", base=(0.115, 0.052, 0.015),
                        dark=(0.032, 0.012, 0.003), ring_mm=2.0, distortion=0.2,
                        ray_strength=0.0, pore_strength=0.60, rough=(0.45, 0.62),
                        grain_axis='Z', clearcoat=0.08)
    # lacewood linings (London plane): pale, bold leopard fleck
    M['lacewood'] = wood("LACEWOOD_LINING", base=(0.230, 0.108, 0.050),
                         dark=(0.150, 0.068, 0.030), ring_mm=5.0, distortion=2.0,
                         ray_strength=0.30, pore_strength=0.16, rough=(0.28, 0.44),
                         grain_axis='Y', ray_scale_mm=16.0)
    # sycamore drawer sides/bottom: pale, closed grain
    M['sycamore'] = wood("SYCAMORE_DRAWER", base=(0.430, 0.320, 0.180),
                         dark=(0.300, 0.212, 0.108), ring_mm=14.0, distortion=0.8,
                         ray_strength=0.04, pore_strength=0.10, rough=(0.34, 0.48),
                         grain_axis='X', ray_scale_mm=10.0, clearcoat=0.12)
    M['sycamore_end'] = wood("SYCAMORE_ENDGRAIN", base=(0.360, 0.262, 0.145),
                             dark=(0.245, 0.170, 0.086), ring_mm=4.0, distortion=0.2,
                             ray_strength=0.0, pore_strength=0.30, rough=(0.44, 0.58),
                             grain_axis='Z', clearcoat=0.08)
    # turned hardwood handles: darker, more polished from handling
    M['oak_turned'] = wood("OAK_TURNED_HANDLE", base=(0.140, 0.062, 0.018),
                           dark=(0.042, 0.016, 0.004), ring_mm=3.0, distortion=0.4,
                           ray_strength=0.10, pore_strength=0.18, rough=(0.18, 0.32),
                           grain_axis='X', clearcoat=0.35)
    # metals
    M['brass'] = metal("BRASS_AGED_POLISH", (0.560, 0.395, 0.148), rough=0.22, tarnish=0.45)
    M['brass_dark'] = metal("BRASS_TARNISHED_RECESS", (0.330, 0.225, 0.085), rough=0.40,
                            tarnish=0.7, tarnish_col=(0.115, 0.078, 0.030))
    M['steel'] = metal("STEEL_DARKENED_CASTORS", (0.130, 0.125, 0.120), rough=0.44,
                       tarnish=0.5, tarnish_col=(0.055, 0.040, 0.028))
    M['iron'] = metal("IRON_CASTORS", (0.085, 0.080, 0.076), rough=0.55)
    # misc
    M['leather'] = leather("LEATHER_WRITING_INSET")
    M['baize'] = plain("BAIZE_GREEN", (0.045, 0.062, 0.040), rough=0.80)
    M['paper'] = plain("LABEL_CARD", (0.700, 0.655, 0.560), rough=0.85)
    M['ink'] = plain("INK_RESIDUE", (0.015, 0.013, 0.016), rough=0.45)
    M['lock_steel'] = metal("LOCK_BRASS_WORN", (0.430, 0.300, 0.115), rough=0.30, tarnish=0.55)
    M['shadow'] = plain("JOINT_SHADOW", (0.010, 0.007, 0.005), rough=0.92)
    M['glass'] = plain("GLASS_THIN", (0.900, 0.930, 0.930), rough=0.05)
    return M


def displacement_textures():
    """Real geometric grain/texture for the Displace modifier (not just bump)."""
    T = {}
    for key, ttype, size, depth in [
        ("grain_fine", 'CLOUDS', 0.004, 2),
        ("grain_wide", 'MUSGRAVE', 0.030, 3),
        ("panel_wear", 'CLOUDS', 0.090, 2),
    ]:
        t = bpy.data.textures.get(key) or bpy.data.textures.new(key, ttype)
        t.noise_scale = size
        if hasattr(t, "noise_depth"):
            t.noise_depth = depth
        T[key] = t
    return T
