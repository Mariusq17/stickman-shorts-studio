"""Runs INSIDE Blender (blender -b --python bl_elevator_scene.py -- states.json out_dir [W H samples]).

Builds the elevator scene in real 3D with the same world coordinates as the 2.5D version,
applies the per-frame animation states computed by the narration planner and renders
transparent PNG frames (the sky + overlays are composited later in Python)."""
import json
import math
import os
import sys

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
STATES, OUT = argv[0], argv[1]
W = int(argv[2]) if len(argv) > 2 else 1080
H = int(argv[3]) if len(argv) > 3 else 1920
SAMPLES = int(argv[4]) if len(argv) > 4 else 16
os.makedirs(OUT, exist_ok=True)

FLOORS = (1.0, 4.0, 7.0)
TOP = 10.0
DOOR_X0, DOOR_X1 = 0.75, 1.65
CX = 1.2

bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene


def lin(c):
    return tuple(((v / 255.0) ** 2.2) for v in c) + (1.0,)


_mats = {}


def mat(rgb, rough=0.55, metal=0.0, emit=0.0):
    key = (rgb, rough, metal, emit)
    if key in _mats:
        return _mats[key]
    m = bpy.data.materials.new(f"m{len(_mats)}")
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = lin(rgb)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit:
        b.inputs["Emission Color"].default_value = lin(rgb)
        b.inputs["Emission Strength"].default_value = emit
    _mats[key] = m
    return m


def box(x, y, z, w, d, h, rgb, parent=None, name="box", bevel=0.0, **mk):
    """Axis-aligned box from its min corner (same convention as the 2.5D engine)."""
    bpy.ops.mesh.primitive_cube_add(size=1, location=(x + w / 2, y + d / 2, z + h / 2))
    o = bpy.context.object
    o.name = name
    o.scale = (max(w, 1e-4), max(d, 1e-4), max(h, 1e-4))
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel > 0:
        mod = o.modifiers.new("bev", "BEVEL")
        mod.width = bevel
        mod.segments = 2
    o.data.materials.append(mat(rgb, **mk))
    if parent:
        o.parent = parent
    return o


def empty(name, loc=(0, 0, 0)):
    bpy.ops.object.empty_add(location=loc)
    o = bpy.context.object
    o.name = name
    return o


def cylinder(loc, r, depth, rgb, axis="z", parent=None, verts=32, **mk):
    rot = {"z": (0, 0, 0), "x": (0, math.pi / 2, 0), "y": (math.pi / 2, 0, 0)}[axis]
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=depth, location=loc, rotation=rot, vertices=verts)
    o = bpy.context.object
    o.data.materials.append(mat(rgb, **mk))
    bpy.ops.object.shade_smooth()
    if parent:
        o.parent = parent
    return o


def sphere(loc, r, rgb, parent=None, **mk):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=r, location=loc, segments=24, ring_count=12)
    o = bpy.context.object
    o.data.materials.append(mat(rgb, **mk))
    bpy.ops.object.shade_smooth()
    if parent:
        o.parent = parent
    return o


# ------------------------------------------------------------------ palette
WALL = (205, 212, 224)
FACADE = (238, 228, 212)
CAR = (250, 196, 70)
METAL = (150, 158, 170)
LAWN = (150, 196, 120)
GLASS = (170, 205, 235)

# ------------------------------------------------------------------ static world
lawn = empty("lawn")
for (x, y, w, d) in ((-12, -12, 11.88, 26), (2.2, -12, 12, 26), (-0.12, -12, 2.32, 11.88), (-0.12, 2.0, 2.32, 12)):
    box(x, y, 0.55, w, d, 0.15, LAWN, lawn, rough=0.95)
box(0, 0, -0.1, 2.2, 2.0, 0.1, (150, 155, 168), name="pit")

# shaft walls (scaled in z while "building")
shaft = empty("shaft")
box(-0.12, -0.12, 0, 0.12, 2.12, TOP, WALL, shaft, name="wall_left")
for x0, x1 in ((0.0, DOOR_X0 - 0.08), (DOOR_X1 + 0.08, 2.2)):
    box(x0, -0.12, 0, x1 - x0, 0.12, TOP, WALL, shaft)
zs = [0.0] + [v for fz in FLOORS for v in (fz, fz + 2.18)] + [TOP]
for k in range(0, len(zs), 2):
    box(DOOR_X0 - 0.08, -0.12, zs[k], DOOR_X1 - DOOR_X0 + 0.16, 0.12, zs[k + 1] - zs[k], WALL, shaft)
for i, fz in enumerate(FLOORS):
    box(DOOR_X0 - 0.1, -0.05, fz, 0.08, 0.08, 2.18, (120, 126, 138), shaft, metal=0.3)
    box(DOOR_X1 + 0.02, -0.05, fz, 0.08, 0.08, 2.18, (120, 126, 138), shaft, metal=0.3)
    box(DOOR_X0 - 0.1, -0.05, fz + 2.1, DOOR_X1 - DOOR_X0 + 0.2, 0.08, 0.1, (120, 126, 138), shaft, metal=0.3)
    box(DOOR_X0 - 0.1, -0.05, fz - 0.04, DOOR_X1 - DOOR_X0 + 0.2, 0.2, 0.04, (150, 150, 160), shaft)
    hw = (DOOR_X1 - DOOR_X0) / 2
    box(DOOR_X0, -0.03, fz, hw - 0.005, 0.03, 2.08, (196, 202, 214), shaft, name=f"door{i}_l", metal=0.4, rough=0.35)
    box(DOOR_X0 + hw + 0.005, -0.03, fz, hw - 0.005, 0.03, 2.08, (186, 192, 205), shaft, name=f"door{i}_r",
        metal=0.4, rough=0.35)
    box(DOOR_X1 + 0.2, -0.02, fz + 0.95, 0.12, 0.02, 0.26, (70, 74, 86), shaft)

# facade (rises at the end of the hook)
facade = empty("facade")
box(2.2, -0.3, 0.7, 3.2, 0.3, TOP - 0.7, FACADE, facade, rough=0.8)
box(-0.3, 2.0, 0.7, 0.3, 2.8, TOP - 0.7, FACADE, facade, rough=0.8)
for fz in FLOORS:
    for wx in (2.9, 4.1):
        box(wx, 0.0, fz + 0.7, 0.7, 0.03, 1.1, GLASS, facade, rough=0.15, metal=0.1)
        box(wx - 0.05, 0.0, fz + 0.65, 0.8, 0.06, 0.05, (255, 255, 255), facade)
    for wy in (2.7, 3.7):
        box(0.0, wy, fz + 0.7, 0.03, 0.6, 1.1, GLASS, facade, rough=0.15, metal=0.1)
    box(2.2, 0.0, fz - 0.2, 3.2, 0.05, 0.08, (220, 208, 190), facade)
    box(0.0, 2.0, fz - 0.2, 0.05, 2.8, 0.08, (220, 208, 190), facade)

# ------------------------------------------------------------------ car
car = empty("car", (0, 0, 0))
x0, y0, w, d, h = 0.45, 0.3, 1.5, 1.4, 2.0
box(x0, y0, -0.12, w, d, 0.12, (212, 196, 165), car, name="car_floor")
box(x0, y0, 0, 0.06, d, h, (232, 176, 60), car, name="car_lwall")
box(x0, y0, 0, DOOR_X0 - x0, 0.06, h, (240, 186, 66), car)
box(DOOR_X1, y0, 0, x0 + w - DOOR_X1, 0.06, h, (240, 186, 66), car)
box(DOOR_X0, y0, 1.95, DOOR_X1 - DOOR_X0, 0.06, h - 1.95, (240, 186, 66), car)
box(x0 + w - 0.06, y0 + d - 0.06, 0, 0.06, 0.06, h, CAR, car)
box(x0, y0 + d - 0.06, h - 0.18, w, 0.06, 0.18, CAR, car)
box(x0 + w - 0.06, y0, h - 0.18, 0.06, d, 0.18, CAR, car)
box(x0, y0, h, w, d, 0.12, (240, 190, 70), car, bevel=0.02)
cylinder((x0 + 0.08, y0 + d / 2, 0.95), 0.02, d - 0.2, (200, 200, 210), "y", car, metal=0.8, rough=0.3)

# mascots ("Pegs"): capsule bodies with big eyes, facing the camera
PEG_COLORS = [(255, 170, 60), (90, 170, 255), (120, 210, 130)]
pegs = empty("pegs")
pegs.parent = car
view_dir = Vector((0.62, 0.62, 0.0)).normalized()
for k, (px, py) in enumerate(((0.4, 0.75), (1.0, 0.85), (0.7, 1.3))):
    bx, by = x0 + px, y0 + py
    col = PEG_COLORS[k]
    cylinder((bx, by, 0.55), 0.19, 0.7, col, "z", pegs, rough=0.4)
    sphere((bx, by, 0.90), 0.19, col, pegs, rough=0.4)
    sphere((bx, by, 0.20), 0.19, col, pegs, rough=0.4)
    for s in (-1, 1):
        side = Vector((-view_dir.y, view_dir.x, 0)) * 0.085 * s
        ep = Vector((bx, by, 0.86)) + view_dir * 0.16 + side
        sphere(tuple(ep), 0.07, (255, 255, 255), pegs, rough=0.2)
        sphere(tuple(ep + view_dir * 0.05), 0.032, (25, 25, 35), pegs, rough=0.2)

# ------------------------------------------------------------------ rope + top
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1, location=(0, 0, 0.5), vertices=12)
rope = bpy.context.object
rope.name = "rope"
bpy.ops.object.transform_apply(location=True)
rope.data.materials.append(mat((60, 50, 45), rough=0.7))

top = empty("top")
box(0, 0, TOP, 2.2, 2.0, 0.3, (200, 205, 215), top, bevel=0.02)
sheave = cylinder((0.72, 1.0, TOP + 0.8), 0.48, 0.3, (110, 116, 130), "y", top, verts=48, metal=0.6, rough=0.35)
sheave.name = "sheave"
cylinder((0.72, 1.0, TOP + 0.8), 0.1, 0.36, (70, 74, 86), "y", top, metal=0.5)
box(0.42, 1.25, TOP + 0.3, 0.6, 0.7, 0.8, (70, 120, 200), top, name="motor", bevel=0.04, rough=0.4)
cylinder((0.72, 1.18, TOP + 0.78), 0.06, 0.2, (90, 90, 100), "y", top, metal=0.7)
bpy.ops.mesh.primitive_cylinder_add(radius=0.02, depth=1, location=(0, 0, 0.5), vertices=12)
rope_top = bpy.context.object
bpy.ops.object.transform_apply(location=True)
rope_top.data.materials.append(mat((60, 50, 45), rough=0.7))
rope_top.location = (CX, 1.0, TOP + 0.3)
rope_top.scale = (1, 1, 0.5)
rope_top.parent = top

# ------------------------------------------------------------------ lights, camera, render
bpy.ops.object.light_add(type="SUN", location=(0, 0, 20))
sun = bpy.context.object
sun.data.energy = 2.1
sun.data.angle = math.radians(8)
sun.rotation_euler = (math.radians(42), math.radians(8), math.radians(-28))
world = bpy.data.worlds.new("world")
sc.world = world
world.use_nodes = True
bgn = world.node_tree.nodes["Background"]
bgn.inputs["Color"].default_value = (0.78, 0.86, 1.0, 1)
bgn.inputs["Strength"].default_value = 0.55

bpy.ops.object.camera_add()
cam = bpy.context.object
sc.camera = cam
cam.data.lens = 60
cam.data.sensor_fit = "HORIZONTAL"
cam.data.sensor_width = 36
cam.data.shift_y = 0.06
cam.data.clip_start = 0.05
cam.data.clip_end = 200

sc.render.engine = "BLENDER_EEVEE"
sc.eevee.taa_render_samples = SAMPLES
sc.eevee.use_gtao = True
sc.eevee.gtao_distance = 0.6
sc.eevee.use_soft_shadows = True
sc.eevee.shadow_cube_size = "1024"
sc.eevee.shadow_cascade_size = "2048"
sc.render.film_transparent = True
sc.render.resolution_x, sc.render.resolution_y = W, H
sc.render.image_settings.file_format = "PNG"
sc.render.image_settings.color_mode = "RGBA"
sc.view_settings.view_transform = "Standard"
sc.view_settings.look = "Medium Contrast" if "Medium Contrast" in [
    i.identifier for i in sc.view_settings.bl_rna.properties["look"].enum_items] else "None"

VIEW = Vector((0.62, 0.62, 0.48)).normalized()


def apply(st):
    g = lambda k, dflt=0.0: st.get(k, dflt)
    b = max(1e-3, min(1.0, g("build") * 1.2))
    shaft.scale = (1, 1, b)
    for o in shaft.children_recursive:
        o.hide_render = g("build") < 0.01
    fa = g("facade")
    facade.scale = (1, 1, max(1e-3, fa))
    facade.location = (0, 0, 0.7 * (1 - fa))
    for o in facade.children_recursive:
        o.hide_render = fa < 0.01
    cs = g("car_show")
    car_z = g("car_z", 1.0)
    car.location = (0, 0, car_z + (1 - min(1.0, cs)) * 2.5)
    car.scale = (1, 1, 1)
    for o in car.children_recursive:
        o.hide_render = cs < 0.01
    pi = g("pegs_in")
    pegs.scale = (1, 1, 1) if pi > 0.5 else (1, 1, max(1e-3, pi * 2))
    for o in pegs.children_recursive:
        o.hide_render = pi < 0.01 or cs < 0.01
    rs = g("rope_show")
    z0 = car_z + 2.12
    length = (TOP - z0) * rs
    rope.location = (CX, 1.0, z0)
    rope.scale = (1, 1, max(1e-3, length))
    rope.hide_render = rs < 0.01 or cs < 0.5
    ts = g("top_show")
    top.location = (0, 0, (1 - min(1.0, ts)) * 2.5)
    for o in top.children_recursive:
        o.hide_render = ts < 0.01
    sheave.rotation_euler = (math.pi / 2, -car_z / 0.48, 0)
    # camera: same focus/zoom semantics as the 2.5D builder
    f = Vector(st["cam_f"])
    zoom = st["cam_z"]
    dist = (1080.0 / zoom) * cam.data.lens / 36.0
    cam.location = f + VIEW * dist
    cam.rotation_euler = (-VIEW).to_track_quat("-Z", "Y").to_euler()


with open(STATES) as fh:
    frames = json.load(fh)
for i, st in enumerate(frames):
    apply(st)
    sc.render.filepath = os.path.join(OUT, f"f{i:05d}.png")
    bpy.ops.render.render(write_still=True)
    print(f"FRAME {i + 1}/{len(frames)}", flush=True)
