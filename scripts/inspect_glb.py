#!/usr/bin/env python3
import bpy, os
from mathutils import Vector
bpy.ops.wm.read_factory_settings(use_empty=True)
p='/home/user/3dprojects/assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano.glb'
bpy.ops.import_scene.gltf(filepath=p)
objs=[o for o in bpy.data.objects if o.type=='MESH']
tri=0
for o in objs:
    o.data.calc_loop_triangles(); tri+=len(o.data.loop_triangles)
pts=[o.matrix_world@Vector(c) for o in objs for c in o.bound_box]
print('GLB_OBJECTS',len(objs),'TRIANGLES',tri,'MATERIALS',len(bpy.data.materials),'IMAGES',len(bpy.data.images))
print('GLB_BOUNDS',tuple(round(min(p[i] for p in pts),3) for i in range(3)),tuple(round(max(p[i] for p in pts),3) for i in range(3)))
keys=[o.name for o in objs if 'key' in o.name.lower()]
strings=[o.name for o in objs if 'string' in o.name.lower()]
legs=[o.name for o in objs if 'leg' in o.name.lower()]
print('GLB_KEYS',len(keys),'GLB_STRINGS',len(strings),'GLB_LEGS',len(legs))
print('GLB_SAMPLE',objs[0].name if objs else 'NONE')
