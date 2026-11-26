#!/usr/bin/env python3
import bpy, os
B='/home/user/3dprojects/assets/1899-bluthner-grand-piano/1899_bluthner_grand_piano_master.blend'
bpy.ops.wm.open_mainfile(filepath=B)
lid=bpy.data.objects['Lid — rosewood with inlaid border']
lid.rotation_euler=(0,0,0)
bpy.context.view_layer.update()
s=bpy.context.scene
s.camera=bpy.data.objects['CAM_PRODUCT_CLOSED']
s.render.resolution_x=1600; s.render.resolution_y=900
s.cycles.samples=40; s.cycles.use_denoising=False
out='/home/user/3dprojects/renders/1899-bluthner-grand-piano/15_closed_lid_product.png'
s.render.filepath=out
os.makedirs(os.path.dirname(out),exist_ok=True)
bpy.ops.render.render(write_still=True)
print('CLOSED_DONE',out,flush=True)
