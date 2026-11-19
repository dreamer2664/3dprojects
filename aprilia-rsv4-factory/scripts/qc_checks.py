"""Quick workbench checks: rear-shock clearance + winglet framing."""
import bpy, os
from mathutils import Vector
sc = bpy.context.scene
sc.render.engine = 'BLENDER_WORKBENCH'
sc.display.shading.light = 'STUDIO'; sc.display.shading.studio_light = 'rim.sl'
sc.display.shading.color_type = 'TEXTURE' if hasattr(sc.display.shading,'color_type') else 'MATERIAL'
sc.render.resolution_x = 800; sc.render.resolution_y = 500
cam = bpy.data.objects.new('ChkCam', bpy.data.cameras.new('ChkCam')); sc.collection.objects.link(cam); sc.camera = cam
def look(loc, tgt, lens=50):
    cam.location = loc; cam.rotation_euler = (Vector(tgt)-Vector(loc)).to_track_quat('-Z','Y').to_euler(); cam.data.lens = lens
HIDE = ('Fairing_','Tank_','Seat_','Bellypan_','Tail_','Winglet_','Front_fender','Nose_','Screen_','Headlamp','Radiator_','Cowl_')
for o in sc.objects:
    if any(h in o.name for h in HIDE): o.hide_render = True
look((0.95,-1.6,0.75),(0.55,0,0.55),58)
sc.render.filepath='/home/user/work/qc/swarm_chk.png'; bpy.ops.render.render(write_still=True)
for o in sc.objects:
    if any(h in o.name for h in HIDE): o.hide_render = False
look((2.6,2.4,1.02),(1.15,0,0.66),72)
sc.render.filepath='/home/user/work/qc/wing_chk.png'; bpy.ops.render.render(write_still=True)
print('[checks done]')
