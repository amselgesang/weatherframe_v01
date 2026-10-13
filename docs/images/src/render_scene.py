"""Blender (bpy) scene: the weather frame on a woodchip-papered wall, warm light, USB-C cable down.

  /tmp/bvenv/bin/python render_scene.py <screen.png> <out.png> [samples] [res_x res_y]

Geometry: the real bezel.stl / back.stl from hardware/mechanical/export (mm -> m).
Frame coordinates as in frame_geom.py: X right, Y up, Z toward the viewer, wall at Z = -24.5 mm.
"""
import math
import sys

import bpy
from mathutils import Vector

screen, out = sys.argv[sys.argv.index("--") + 1:][:2] if "--" in sys.argv else sys.argv[1:3]
rest = (sys.argv[sys.argv.index("--") + 3:] if "--" in sys.argv else sys.argv[3:])
samples = int(rest[0]) if rest else 128
rx, ry = (int(rest[1]), int(rest[2])) if len(rest) >= 3 else (1600, 1200)
EXPORT = "/home/claude/mech/out/"
MM = 0.001

bpy.ops.wm.read_factory_settings(use_empty=True)
scn = bpy.context.scene


# ------------------------------------------------------------------ materials
def mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    return m, m.node_tree.nodes, m.node_tree.links, m.node_tree.nodes["Principled BSDF"]


# woodchip wallpaper (Raufaser), warm off-white paint
wall_m, n, l, bsdf = mat("woodchip")
bsdf.inputs["Base Color"].default_value = (0.80, 0.72, 0.60, 1)
bsdf.inputs["Roughness"].default_value = 0.92
tc = n.new("ShaderNodeTexCoord")
mp = n.new("ShaderNodeMapping"); mp.inputs["Scale"].default_value = (1, 1, 1)
l.new(tc.outputs["Object"], mp.inputs["Vector"])
# chips: two Voronoi layers, distorted by noise so they look like irregular wood fibres
noise = n.new("ShaderNodeTexNoise"); noise.inputs["Scale"].default_value = 180; noise.inputs["Detail"].default_value = 4
mix = n.new("ShaderNodeMix"); mix.data_type = "VECTOR"; mix.inputs["Factor"].default_value = 0.012
l.new(mp.outputs["Vector"], mix.inputs[4]); l.new(noise.outputs["Color"], mix.inputs[5])
vor1 = n.new("ShaderNodeTexVoronoi"); vor1.feature = "F1"; vor1.inputs["Scale"].default_value = 520
vor2 = n.new("ShaderNodeTexVoronoi"); vor2.feature = "SMOOTH_F1"; vor2.inputs["Scale"].default_value = 260
l.new(mix.outputs[1], vor1.inputs["Vector"]); l.new(mix.outputs[1], vor2.inputs["Vector"])
r1 = n.new("ShaderNodeValToRGB")
r1.color_ramp.elements[0].position = 0.0; r1.color_ramp.elements[0].color = (1, 1, 1, 1)
r1.color_ramp.elements[1].position = 0.35; r1.color_ramp.elements[1].color = (0, 0, 0, 1)
l.new(vor1.outputs["Distance"], r1.inputs["Fac"])
r2 = n.new("ShaderNodeValToRGB")
r2.color_ramp.elements[0].position = 0.05; r2.color_ramp.elements[1].position = 0.45
l.new(vor2.outputs["Distance"], r2.inputs["Fac"])
add = n.new("ShaderNodeMath"); add.operation = "MAXIMUM"
l.new(r1.outputs["Color"], add.inputs[0])
inv = n.new("ShaderNodeMath"); inv.operation = "SUBTRACT"; inv.inputs[0].default_value = 1.0
l.new(r2.outputs["Color"], inv.inputs[1])
mul = n.new("ShaderNodeMath"); mul.operation = "MULTIPLY"; mul.inputs[1].default_value = 0.55
l.new(inv.outputs[0], mul.inputs[0])
add2 = n.new("ShaderNodeMath"); add2.operation = "ADD"
l.new(add.outputs[0], add2.inputs[0]); l.new(mul.outputs[0], add2.inputs[1])
bump = n.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 1.0; bump.inputs["Distance"].default_value = 0.0012
l.new(add2.outputs[0], bump.inputs["Height"])
l.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
# slight colour variation in the chips (paint pooling)
cr = n.new("ShaderNodeValToRGB")
cr.color_ramp.elements[0].color = (0.70, 0.62, 0.50, 1); cr.color_ramp.elements[1].color = (0.84, 0.77, 0.65, 1)
l.new(add2.outputs[0], cr.inputs["Fac"])
l.new(cr.outputs["Color"], bsdf.inputs["Base Color"])

# MJF nylon, dyed black: matte with a fine sintered grain
frame_m, n, l, bsdf = mat("frame_white")
bsdf.inputs["Base Color"].default_value = (0.86, 0.85, 0.82, 1)   # white MJF / SLA white
bsdf.inputs["Roughness"].default_value = 0.55
bsdf.inputs["Subsurface Weight"].default_value = 0.05
g = n.new("ShaderNodeTexNoise"); g.inputs["Scale"].default_value = 2500; g.inputs["Detail"].default_value = 2
b = n.new("ShaderNodeBump"); b.inputs["Strength"].default_value = 0.25; b.inputs["Distance"].default_value = 0.0001
l.new(g.outputs["Fac"], b.inputs["Height"]); l.new(b.outputs["Normal"], bsdf.inputs["Normal"])

# e-paper: matte, slightly warm grey "paper" white, ink from the screen image
epd_m, n, l, bsdf = mat("epaper")
bsdf.inputs["Roughness"].default_value = 0.55
bsdf.inputs["Specular IOR Level"].default_value = 0.35
img = n.new("ShaderNodeTexImage"); img.image = bpy.data.images.load(screen); img.interpolation = "Cubic"
ramp = n.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].color = (0.035, 0.035, 0.038, 1)      # ink
ramp.color_ramp.elements[1].color = (0.62, 0.61, 0.57, 1)         # e-paper white (not paper white)
l.new(img.outputs["Color"], ramp.inputs["Fac"])
l.new(ramp.outputs["Color"], bsdf.inputs["Base Color"])

border_m, n, l, bsdf = mat("epaper_border")
bsdf.inputs["Base Color"].default_value = (0.58, 0.57, 0.53, 1); bsdf.inputs["Roughness"].default_value = 0.55

cable_m, n, l, bsdf = mat("cable")
bsdf.inputs["Base Color"].default_value = (0.86, 0.84, 0.80, 1); bsdf.inputs["Roughness"].default_value = 0.45

# ------------------------------------------------------------------ geometry
def stl(name):
    bpy.ops.wm.stl_import(filepath=EXPORT + name + ".stl", global_scale=MM)
    o = bpy.context.selected_objects[0]
    o.data.materials.append(frame_m)
    for p in o.data.polygons:
        p.use_smooth = False
    return o


bezel = stl("bezel")
back = stl("back")

# wall
bpy.ops.mesh.primitive_plane_add(size=3, location=(0, 0, -0.0245))
wall = bpy.context.object; wall.data.materials.append(wall_m)

# e-paper active area (image) + panel border, front of the glass at z = -2.5 mm
aa_w, aa_h = 0.1632, 0.09792
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, 0, -0.00249))
aa = bpy.context.object; aa.scale = (aa_w, aa_h, 1); aa.data.materials.append(epd_m)
bpy.ops.mesh.primitive_plane_add(size=1, location=(0, -0.00314, -0.00252))
pb = bpy.context.object; pb.scale = (0.1702, 0.1112, 1); pb.data.materials.append(border_m)

# USB-C plug: overmold 12 x 6.5 x 24 mm, entering the right wall at y = -14 mm, z = -17.6 mm
px0, py, pz = 0.0949, -0.0140, -0.0176
bpy.ops.mesh.primitive_cube_add(size=1, location=(px0 + 0.012 + 0.003, py, pz))
plug = bpy.context.object; plug.scale = (0.024, 0.012, 0.0065)
bv = plug.modifiers.new("bevel", "BEVEL"); bv.width = 0.0022; bv.segments = 6
plug.data.materials.append(cable_m)
bpy.ops.object.shade_smooth()
# strain relief
bpy.ops.mesh.primitive_cylinder_add(radius=0.0028, depth=0.010, location=(px0 + 0.027 + 0.005 + 0.003, py, pz),
                                    rotation=(0, math.pi / 2, 0))
relief = bpy.context.object; relief.data.materials.append(cable_m); bpy.ops.object.shade_smooth()

# cable: out of the plug, curving down against the wall and out of the picture
cd = bpy.data.curves.new("cable", "CURVE"); cd.dimensions = "3D"
cd.bevel_depth = 0.0018; cd.bevel_resolution = 6; cd.resolution_u = 32
sp = cd.splines.new("BEZIER")
pts = [(px0 + 0.040, py, pz), (px0 + 0.056, py - 0.012, -0.0205), (px0 + 0.060, py - 0.045, -0.0226),
       (px0 + 0.054, -0.16, -0.0226), (px0 + 0.060, -0.32, -0.0226), (px0 + 0.052, -0.6, -0.0226)]
sp.bezier_points.add(len(pts) - 1)
for bp, p in zip(sp.bezier_points, pts):
    bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
cable = bpy.data.objects.new("cable", cd); scn.collection.objects.link(cable)
cable.data.materials.append(cable_m)

# ------------------------------------------------------------------ light, camera, world
world = bpy.data.worlds.new("w"); scn.world = world; world.use_nodes = True
bg = world.node_tree.nodes["Background"]
bg.inputs["Color"].default_value = (0.32, 0.24, 0.17, 1); bg.inputs["Strength"].default_value = 0.35

# warm late-afternoon sun from the upper left, raking across the woodchip
bpy.ops.object.light_add(type="SUN")
sun = bpy.context.object
sun.data.energy = 5.0; sun.data.angle = math.radians(2.5); sun.data.color = (1.0, 0.68, 0.40)
d = Vector((0.80, -0.50, -0.33)).normalized()          # direction the light travels
sun.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

# soft warm fill from the room (large area light, right/front)
bpy.ops.object.light_add(type="AREA", location=(0.45, 0.10, 0.75))
fill = bpy.context.object
fill.data.energy = 6; fill.data.size = 0.8; fill.data.color = (1.0, 0.85, 0.68)
fill.rotation_euler = (Vector((0.02, -0.05, -0.02)) - fill.location).to_track_quat("-Z", "Y").to_euler()

bpy.ops.object.camera_add(location=(0.23, 0.07, 0.58))
cam = bpy.context.object; scn.camera = cam
cam.data.lens = 50; cam.data.dof.use_dof = True; cam.data.dof.aperture_fstop = 4.0
target = Vector((0.03, -0.045, -0.012))
from mathutils import Matrix
f = (target - cam.location).normalized()
right = f.cross(Vector((0, 1, 0))).normalized()
up = right.cross(f)
cam.rotation_euler = Matrix((right, up, -f)).transposed().to_euler()
cam.data.dof.focus_distance = (Vector((0.0, -0.005, -0.003)) - cam.location).length

# ------------------------------------------------------------------ render
scn.render.engine = "CYCLES"
scn.cycles.device = "CPU"
scn.cycles.samples = samples
scn.cycles.use_denoising = True
scn.cycles.max_bounces = 6
scn.render.resolution_x, scn.render.resolution_y = rx, ry
scn.render.film_transparent = False
try:
    scn.view_settings.view_transform = "AgX"
    scn.view_settings.look = "AgX - Medium High Contrast"
except Exception:
    pass
scn.view_settings.exposure = 0.15
scn.render.image_settings.file_format = "PNG"
scn.render.filepath = out
bpy.ops.render.render(write_still=True)
print("rendered", out)
