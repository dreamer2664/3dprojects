#!/usr/bin/env python3
"""Independent inspection of the saved .blend: mesh totals, instances, cameras."""
import bpy
import sys
from collections import Counter

bpy.ops.wm.open_mainfile(filepath=sys.argv[sys.argv.index("--") + 1]
                         if "--" in sys.argv else
                         "/home/user/3dprojects/assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano_master.blend")
scene = bpy.context.scene
dg = bpy.context.evaluated_depsgraph_get()

unique_tri = 0
for me in bpy.data.meshes:
    me.calc_loop_triangles()
    unique_tri += len(me.loop_triangles)

counts = Counter()
seen = 0
for inst in dg.object_instances:
    ob = inst.object
    if ob.type != 'MESH':
        continue
    if ob.hide_render:
        continue
    me = ob.data
    me.calc_loop_triangles()
    n = len(me.loop_triangles)
    counts[ob.name] += 1
    seen += n

print("VALIDATE unique_mesh_triangles", unique_tri)
print("VALIDATE visible_mesh_instances", sum(counts.values()))
print("VALIDATE evaluated_render_triangles", seen)
print("VALIDATE cameras", [o.name for o in bpy.data.objects if o.type == 'CAMERA'])
print("VALIDATE collections", sorted(c.name for c in bpy.data.collections))
for c in bpy.data.collections:
    if c.name == 'TEMPLATES':
        continue
    print("VALIDATE collection", c.name, "objects", len(c.objects))
print("VALIDATE images", [(i.name, i.size[:]) for i in bpy.data.images])
