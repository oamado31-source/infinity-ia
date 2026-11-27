# SPDX-License-Identifier: Apache-2.0
"""ADR-0150: render a scene of ours with the game's camera (runs inside Blender, headless).

  blender -b --factory-startup --python tools/area-author/blender/infai_render.py -- SCENE.json OUT.png

SCENE.json: {"width": px, "height": px, "camera": {"elevation": 45, "px_per_m": 40, "turn": 45,
"u0": px, "v0": px}, "samples": 64, "parts": [...], "lights": [...]}. The camera is the same math as
src/infinity_ai/areas/camera.py: orthographic, looking north, `elevation` degrees above the horizon;
the room (every part) is turned `turn` degrees around the vertical axis. Parts are built here from
primitives with procedural materials; nothing is downloaded.
"""
from __future__ import annotations

import json
import math
import sys

import bpy

KINDS = {}


def part(kind):
    def reg(fn):
        KINDS[kind] = fn
        return fn
    return reg


def material(name, rgb, rough=0.7, metallic=0.0, noise=0.0, stripes=0.0):
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = rough
    bsdf.inputs['Metallic'].default_value = metallic
    base = (*rgb, 1.0)
    if noise or stripes:
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        dark = tuple(c * (1 - max(noise, stripes)) for c in rgb)
        ramp.color_ramp.elements[0].color = (*dark, 1.0)
        ramp.color_ramp.elements[1].color = base
        tex = nt.nodes.new('ShaderNodeTexWave' if stripes else 'ShaderNodeTexNoise')
        if stripes:
            tex.inputs['Scale'].default_value = 6.0
            tex.inputs['Distortion'].default_value = 4.0
        else:
            tex.inputs['Scale'].default_value = 8.0
        nt.links.new(tex.outputs['Fac'] if 'Fac' in tex.outputs else tex.outputs[0], ramp.inputs['Fac'])
        nt.links.new(ramp.outputs['Color'], bsdf.inputs['Base Color'])
    else:
        bsdf.inputs['Base Color'].default_value = base
    return m


def add_box(name, x, y, z, w, d, h, turn, mat, parent):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(x, y, z + h / 2))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (w, d, h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)   # metres in textures
    ob.rotation_euler = (0, 0, math.radians(turn))
    ob.data.materials.append(mat)
    ob.parent = parent
    return ob


@part('checker-floor')
def checker_floor(p, parent):
    n = int(p.get('cells', 10))
    light = material('chk-light', (0.75, 0.75, 0.72), 0.8)
    dark = material('chk-dark', (0.25, 0.25, 0.24), 0.8)
    for i in range(n):
        for j in range(n):
            add_box(f'chk{i}_{j}', p['x'] + i + 0.5, p['y'] + j + 0.5, -0.02, 1, 1, 0.02, 0,
                    light if (i + j) % 2 == 0 else dark, parent)


@part('box')
def box(p, parent):
    mat = material(p.get('material', 'wood'), tuple(p.get('rgb', (0.45, 0.30, 0.17))),
                   p.get('rough', 0.75), noise=p.get('noise', 0.25))
    add_box(p.get('id', 'box'), p['x'], p['y'], p.get('z', 0.0), p['w'], p['d'], p['h'],
            p.get('turn', 0.0), mat, parent)


@part('column')
def column(p, parent):
    bpy.ops.mesh.primitive_cylinder_add(radius=p.get('r', 0.25), depth=p['h'],
                                        location=(p['x'], p['y'], p['h'] / 2))
    ob = bpy.context.object
    ob.name = p.get('id', 'column')
    ob.data.materials.append(material('column', (0.8, 0.2, 0.15), 0.6))
    ob.parent = parent


def _coords(nt, scale=1.0, rot=(0.0, 0.0, 0.0)):
    tc = nt.nodes.new('ShaderNodeTexCoord')
    mp = nt.nodes.new('ShaderNodeMapping')
    mp.inputs['Scale'].default_value = (scale, scale, scale)
    mp.inputs['Rotation'].default_value = tuple(math.radians(a) for a in rot)
    nt.links.new(tc.outputs['Object'], mp.inputs['Vector'])
    return mp.outputs['Vector']


def wood_planks(name, rgb, plank_w=0.3, plank_l=2.4, rot=(0.0, 0.0, 0.0)):
    """Planks from a brick pattern (seams dark), grain from a distorted wave. `rot` turns the
    pattern so a wall gets its planks lying along its length: (90, 0, 0) for a wall along x,
    (90, 90, 0) for one along y."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.8
    vec = _coords(nt, rot=rot)
    brick = nt.nodes.new('ShaderNodeTexBrick')
    brick.inputs['Scale'].default_value = 1.0          # object coordinates are metres
    brick.inputs['Brick Width'].default_value = plank_l
    brick.inputs['Row Height'].default_value = plank_w
    brick.inputs['Mortar Size'].default_value = 0.008
    brick.offset = 0.37
    brick.inputs['Color1'].default_value = (*rgb, 1)
    brick.inputs['Color2'].default_value = (*(c * 0.78 for c in rgb), 1)
    brick.inputs['Mortar'].default_value = (*(c * 0.25 for c in rgb), 1)
    nt.links.new(vec, brick.inputs['Vector'])
    wave = nt.nodes.new('ShaderNodeTexWave')
    wave.bands_direction = 'Y'                         # the grain runs along the plank
    wave.inputs['Scale'].default_value = 2.5
    wave.inputs['Distortion'].default_value = 8.0
    wave.inputs['Detail'].default_value = 3.0
    nt.links.new(vec, wave.inputs['Vector'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 0.25
    nt.links.new(brick.outputs['Color'], mix.inputs['A'])
    nt.links.new(wave.outputs['Color'], mix.inputs['B'])
    nt.links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 40.0
    noise.inputs['Detail'].default_value = 6.0
    nt.links.new(vec, noise.inputs['Vector'])
    relief = nt.nodes.new('ShaderNodeMath')
    relief.operation = 'MULTIPLY'
    nt.links.new(brick.outputs['Fac'], relief.inputs[0])
    nt.links.new(noise.outputs['Fac'], relief.inputs[1])
    bump = nt.nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.35
    bump.inputs['Distance'].default_value = 0.02
    nt.links.new(relief.outputs['Value'], bump.inputs['Height'])
    nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    return m


def add_cyl(name, x, y, z, r, h, mat, parent, axis='Z', verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=(x, y, z))
    ob = bpy.context.object
    ob.name = name
    if axis == 'X':
        ob.rotation_euler = (0, math.pi / 2, 0)
    elif axis == 'Y':
        ob.rotation_euler = (math.pi / 2, 0, 0)
    ob.data.materials.append(mat)
    ob.parent = parent
    return ob


@part('plank-floor')
def plank_floor(p, parent):
    mat = wood_planks('floor-planks', tuple(p.get('rgb', (0.34, 0.17, 0.10))))
    add_box('floor', p['x'] + p['w'] / 2, p['y'] + p['d'] / 2, -0.05, p['w'], p['d'], 0.05, 0,
            mat, parent)


@part('hull-wall')
def hull_wall(p, parent):
    """A wall of horizontal planks with ribs (frames) every `rib` metres, along x or y."""
    along_x = p['axis'] == 'x'
    planks = wood_planks('hull-planks-' + p['axis'], tuple(p.get('rgb', (0.38, 0.17, 0.10))),
                         0.25, 3.0, (90, 0, 0) if along_x else (90, 90, 0))
    ribmat = material('ribs', (0.15, 0.08, 0.05), 0.8, noise=0.3)
    length, h, t = p['length'], p['h'], 0.15
    cx = p['x'] + (length / 2 if along_x else 0)
    cy = p['y'] + (0 if along_x else length / 2)
    wall = add_box(p.get('id', 'hull'), cx, cy, 0, length if along_x else t,
                   t if along_x else length, h, 0, planks, parent)
    wall.rotation_euler[0 if along_x else 1] = math.radians(p.get('lean', 0))
    k = p.get('rib', 1.2)
    n = int(length / k)
    for i in range(1, n):
        rx = p['x'] + (i * k if along_x else 0)
        ry = p['y'] + (0 if along_x else i * k)
        off = -0.12 if p.get('inside', 'minus') == 'minus' else 0.12
        add_box(f'rib{i}', rx + (0 if along_x else off), ry + (off if along_x else 0), 0,
                0.16, 0.16, h + 0.05, 0, ribmat, parent)


def group(name, x, y, z, turn, parent, tilt=(0.0, 0.0)):
    """An empty that holds a part's pieces in its own frame (centre on the ground, turned)."""
    g = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(g)
    g.parent = parent
    g.location = (x, y, z)
    g.rotation_euler = (math.radians(tilt[0]), math.radians(tilt[1]), math.radians(turn))
    return g


def _piece(name, x, y, z, w, d, h, mat, parent, rot=(0.0, 0.0, 0.0)):
    """A box centred at (x, y, z) in the parent's frame (not standing on the ground)."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (w, d, h)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    ob.parent = parent
    ob.location = (x, y, z)
    ob.rotation_euler = rot
    ob.data.materials.append(mat)
    return ob


@part('crate')
def crate(p, parent):
    """A wooden crate as the game draws them: plank sides, an edge frame of battens and a
    diagonal brace on each side."""
    body = wood_planks('crate-planks', (0.42, 0.24, 0.12), 0.16, 1.2, (90, 0, 0))
    batten = material('crate-batten', (0.30, 0.16, 0.08), 0.8, noise=0.3)
    s, h = p.get('s', 1.0), p.get('h', p.get('s', 1.0))
    g = group(p.get('id', 'crate'), p['x'], p['y'], p.get('z', 0.0), p.get('turn', 0.0), parent)
    t, o = 0.07, s / 2
    _piece('body', 0, 0, h / 2, s - 0.03, s - 0.03, h - 0.03, body, g)
    for cx in (-1, 1):                                     # the four standing edges
        for cy in (-1, 1):
            _piece('edge', cx * (o - t / 2), cy * (o - t / 2), h / 2, t, t, h, batten, g)
    for z in (t / 2, h - t / 2):                           # the top and bottom frames
        for c in (-1, 1):
            _piece('edge', 0, c * (o - t / 2), z, s, t, t, batten, g)
            _piece('edge', c * (o - t / 2), 0, z, t, s, t, batten, g)
    span = math.hypot(s - 2 * t, h - 2 * t)
    ang = math.atan2(h - 2 * t, s - 2 * t)
    for c in (-1, 1):                                      # a brace on every side
        _piece('brace', 0, c * (o + 0.005), h / 2, span, 0.03, t * 0.9, batten, g, (0, ang * c, 0))
        _piece('brace', c * (o + 0.005), 0, h / 2, 0.03, span, t * 0.9, batten, g, (ang * c, 0, 0))


@part('bale')
def bale(p, parent):
    """A pale cargo bale wrapped in canvas and tied with rope in a grid."""
    canvas = material('canvas', (0.66, 0.64, 0.58), 0.95, noise=0.25)
    rope = material('rope', (0.30, 0.24, 0.16), 1.0, noise=0.3)
    w, d, h = p.get('w', 0.9), p.get('d', 0.7), p.get('h', 0.6)
    g = group(p.get('id', 'bale'), p['x'], p['y'], p.get('z', 0.0), p.get('turn', 0.0), parent)
    b = _piece('canvas', 0, 0, h / 2, w, d, h, canvas, g)
    bev = b.modifiers.new('round', 'BEVEL')
    bev.width, bev.segments = 0.06, 3
    for f in (-0.25, 0.25):
        _piece('rope', f * w, 0, h / 2, 0.03, d + 0.02, h + 0.02, rope, g)
        _piece('rope', 0, f * d, h / 2, w + 0.02, 0.03, h + 0.02, rope, g)


def _barrel_mesh(name, r_end, r_mid, h, segs=28, rings=10):
    import bmesh
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    loops = []
    for i in range(rings + 1):
        z = h * i / rings
        r = r_end + (r_mid - r_end) * (1 - (2 * z / h - 1) ** 2)
        loops.append([bm.verts.new((r * math.cos(2 * math.pi * k / segs),
                                    r * math.sin(2 * math.pi * k / segs), z))
                      for k in range(segs)])
    for a, b in zip(loops, loops[1:]):
        for k in range(segs):
            bm.faces.new((a[k], a[(k + 1) % segs], b[(k + 1) % segs], b[k]))
    bm.faces.new(loops[-1])
    bm.faces.new(list(reversed(loops[0])))
    bm.to_mesh(me)
    bm.free()
    return me


def staves(name, rgb, n=18):
    """Barrel wood: vertical staves around the axis (dark seams), grain along them."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.7
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])
    ang = nt.nodes.new('ShaderNodeMath')
    ang.operation = 'ARCTAN2'
    nt.links.new(sep.outputs['Y'], ang.inputs[0])
    nt.links.new(sep.outputs['X'], ang.inputs[1])
    mul = nt.nodes.new('ShaderNodeMath')
    mul.operation = 'MULTIPLY'
    mul.inputs[1].default_value = n / (2 * math.pi)
    nt.links.new(ang.outputs['Value'], mul.inputs[0])
    frac = nt.nodes.new('ShaderNodeMath')
    frac.operation = 'FRACT'
    nt.links.new(mul.outputs['Value'], frac.inputs[0])
    seam = nt.nodes.new('ShaderNodeMath')
    seam.operation = 'LESS_THAN'
    seam.inputs[1].default_value = 0.07
    nt.links.new(frac.outputs['Value'], seam.inputs[0])
    noise = nt.nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 6.0
    nt.links.new(tc.outputs['Object'], noise.inputs['Vector'])
    tone = nt.nodes.new('ShaderNodeValToRGB')
    tone.color_ramp.elements[0].color = (*(c * 0.75 for c in rgb), 1)
    tone.color_ramp.elements[1].color = (*rgb, 1)
    nt.links.new(noise.outputs['Fac'], tone.inputs['Fac'])
    mix = nt.nodes.new('ShaderNodeMix')
    mix.data_type = 'RGBA'
    nt.links.new(seam.outputs['Value'], mix.inputs['Factor'])
    nt.links.new(tone.outputs['Color'], mix.inputs['A'])
    mix.inputs['B'].default_value = (*(c * 0.3 for c in rgb), 1)
    nt.links.new(mix.outputs['Result'], bsdf.inputs['Base Color'])
    return m


@part('barrel')
def barrel(p, parent):
    """A barrel as the game draws them: bulging staves, dark iron hoops, a lid; standing, or
    lying on its side (`lying`: true)."""
    wood = staves('barrel-staves', (0.46, 0.25, 0.11))
    lid = material('barrel-lid', (0.33, 0.18, 0.08), 0.8, noise=0.3)
    hoop = material('hoop', (0.10, 0.09, 0.09), 0.45, metallic=0.7)
    r, h = p.get('r', 0.30), p.get('h', 0.9)
    r_mid = r * 1.12
    lying = p.get('lying', False)
    g = group(p.get('id', 'barrel'), p['x'], p['y'], p.get('z', 0.0) + (r_mid if lying else 0.0),
              p.get('turn', 0.0), parent, (90.0, 0.0) if lying else (0.0, 0.0))
    me = _barrel_mesh('barrel', r, r_mid, h)
    ob = bpy.data.objects.new('barrel', me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = g
    if lying:
        ob.location = (0, 0, -h / 2)
    ob.data.materials.append(wood)
    for poly in ob.data.polygons:
        poly.use_smooth = True
    base = -h / 2 if lying else 0.0
    for f in (0.08, 0.26, 0.74, 0.92):
        z = h * f
        rz = r + (r_mid - r) * (1 - (2 * z / h - 1) ** 2) + 0.012
        bpy.ops.mesh.primitive_cylinder_add(radius=rz, depth=0.05, vertices=28,
                                            location=(0, 0, 0))
        ring = bpy.context.object
        ring.parent = g
        ring.location = (0, 0, base + z)
        ring.data.materials.append(hoop)
    bpy.ops.mesh.primitive_cylinder_add(radius=r * 0.93, depth=0.02, vertices=28,
                                        location=(0, 0, 0))
    top = bpy.context.object
    top.parent = g
    top.location = (0, 0, base + h - 0.005)
    top.data.materials.append(lid)


def net_material(name, see_through=True):
    """Rope mesh: a grid of cords (mesh 10 cm); hung, it is a see-through cloth (a cord is under a
    pixel at the game's scale); in a heap, the dark holes give its texture."""
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    out = nt.nodes['Material Output']
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 1.0
    rope = (0.40, 0.37, 0.22)
    bsdf.inputs['Base Color'].default_value = (*rope, 1)
    vec = _coords(nt, rot=(90, 0, 0))
    grid = nt.nodes.new('ShaderNodeTexBrick')
    grid.offset = 0.0
    grid.inputs['Scale'].default_value = 1.0
    grid.inputs['Brick Width'].default_value = 0.10
    grid.inputs['Row Height'].default_value = 0.10
    grid.inputs['Mortar Size'].default_value = 0.025
    nt.links.new(vec, grid.inputs['Vector'])
    if see_through:
        hole = nt.nodes.new('ShaderNodeBsdfTransparent')
        mix = nt.nodes.new('ShaderNodeMixShader')
        # at the game's scale a cord is under a pixel: the net reads as a see-through cloth
        cover = nt.nodes.new('ShaderNodeMapRange')
        cover.inputs['To Min'].default_value = 0.6
        cover.inputs['To Max'].default_value = 1.0
        nt.links.new(grid.outputs['Fac'], cover.inputs['Value'])   # 1 on the cords
        nt.links.new(cover.outputs['Result'], mix.inputs['Fac'])
        nt.links.new(hole.outputs['BSDF'], mix.inputs[1])
        nt.links.new(bsdf.outputs['BSDF'], mix.inputs[2])
        nt.links.new(mix.outputs['Shader'], out.inputs['Surface'])
    else:
        tone = nt.nodes.new('ShaderNodeValToRGB')
        tone.color_ramp.elements[0].color = (*(c * 0.35 for c in rope), 1)
        tone.color_ramp.elements[1].color = (*rope, 1)
        nt.links.new(grid.outputs['Fac'], tone.inputs['Fac'])
        nt.links.new(tone.outputs['Color'], bsdf.inputs['Base Color'])
    return m


def _hanging_net(name, width, drop, parent, x, y, z):
    """A net hung from a bar: gathered towards the bottom, bulging a little."""
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=14, y_subdivisions=18, size=1.0)
    ob = bpy.context.object
    ob.name = name
    for v in ob.data.vertices:
        u, t = v.co.x + 0.5, 0.5 - v.co.y            # u across, t from the top (0) down (1)
        v.co.x = (u - 0.5) * width * (1 - 0.45 * t)
        v.co.z = -t * drop
        v.co.y = 0.07 * math.sin(math.pi * u) * math.sin(math.pi * t)
    ob.parent = parent
    ob.location = (x, y, z)
    ob.data.materials.append(net_material('net'))
    return ob


@part('net-rack')
def net_rack(p, parent):
    """Fishing nets hung to dry: two posts, a bar and two nets, as in the game's docks."""
    pole = material('rack-pole', (0.30, 0.16, 0.08), 0.7, noise=0.3)
    length, h = p.get('length', 1.6), p.get('h', 1.9)
    g = group(p.get('id', 'net-rack'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    for c in (-1, 1):
        _piece('post', c * length / 2, 0, h / 2, 0.07, 0.07, h, pole, g)
    _piece('bar', 0, 0, h - 0.04, length + 0.1, 0.05, 0.05, pole, g)
    for k, off in enumerate((-length / 4, length / 4)):
        _hanging_net(f'net{k}', length * 0.42, h * 0.62, g, off, 0, h - 0.06)


@part('net-pile')
def net_pile(p, parent):
    """A heap of net on the floor."""
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=4, radius=p.get('r', 0.45),
                                          location=(p['x'], p['y'], 0.0))
    ob = bpy.context.object
    ob.scale = (1.0, 0.8, 0.32)
    tex = bpy.data.textures.new('heap', 'CLOUDS')
    tex.noise_scale = 0.25
    disp = ob.modifiers.new('heap', 'DISPLACE')
    disp.texture = tex
    disp.strength = 0.12
    ob.data.materials.append(net_material('net-heap', see_through=False))
    ob.parent = parent
    bpy.ops.object.shade_smooth()


@part('sack')
def sack(p, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.35, location=(p['x'], p['y'], 0.22))
    ob = bpy.context.object
    ob.scale = (1.0, 0.8, 0.6)
    ob.data.materials.append(material('sack', (0.44, 0.37, 0.26), 0.95, noise=0.2))
    ob.parent = parent
    bpy.ops.object.shade_smooth()


@part('post')
def post(p, parent):
    mat = material('post', (0.25, 0.15, 0.08), 0.8, noise=0.3)
    add_box(p.get('id', 'post'), p['x'], p['y'], 0, p.get('s', 0.3), p.get('s', 0.3), p['h'], 0,
            mat, parent)


@part('mast')
def mast(p, parent):
    mat = material('mast', (0.33, 0.21, 0.11), 0.75, stripes=0.25)
    add_cyl(p.get('id', 'mast'), p['x'], p['y'], p['h'] / 2, p.get('r', 0.3), p['h'], mat,
            parent, verts=24)


@part('ladder')
def ladder(p, parent):
    mat = material('ladder', (0.40, 0.26, 0.14), 0.8, noise=0.25)
    h, w = p['h'], p.get('w', 0.6)
    lean = p.get('lean', 0.35)                       # metres the top is pushed towards +x
    for side in (-1, 1):
        rail = add_box('rail', p['x'] + lean / 2, p['y'] + side * w / 2, 0, 0.07, 0.07,
                       math.hypot(h, lean), 0, mat, parent)
        rail.rotation_euler = (0, math.atan2(lean, h), 0)
    steps = int(h / 0.3)
    for i in range(1, steps):
        z = i * 0.3
        add_box('rung', p['x'] + lean * z / h, p['y'], z, 0.06, w, 0.04, 0, mat, parent)


@part('cage')
def cage(p, parent):
    """Iron bars on the open sides of a corner cell: `sides` lists 'x' (the side at y=y0, along
    x) and/or 'y' (the side at x=x1, along y)."""
    iron = material('iron', (0.12, 0.12, 0.13), 0.45, metallic=0.85)
    x0, y0, x1, y1, h = p['x0'], p['y0'], p['x1'], p['y1'], p.get('h', 2.2)
    gap = p.get('gap', 0.18)
    if 'x' in p.get('sides', 'xy'):
        n = int((x1 - x0) / gap)
        for i in range(n + 1):
            add_cyl('bar', x0 + i * gap, y0, h / 2, 0.02, h, iron, parent, verts=8)
        add_box('beam', (x0 + x1) / 2, y0, h - 0.06, x1 - x0, 0.08, 0.1, 0, iron, parent)
    if 'y' in p.get('sides', 'xy'):
        n = int((y1 - y0) / gap)
        for i in range(n + 1):
            add_cyl('bar', x1, y0 + i * gap, h / 2, 0.02, h, iron, parent, verts=8)
        add_box('beam', x1, (y0 + y1) / 2, h - 0.06, 0.08, y1 - y0, 0.1, 0, iron, parent)
    straw = material('straw', (0.45, 0.37, 0.19), 1.0, noise=0.5)
    add_box('straw', (x0 + x1) / 2, (y0 + y1) / 2, 0, (x1 - x0) * 0.8, (y1 - y0) * 0.6, 0.04, 0,
            straw, parent)


def glow():
    glass = bpy.data.materials.get('lantern-glow')
    if glass:
        return glass
    glass = bpy.data.materials.new('lantern-glow')
    glass.use_nodes = True
    em = glass.node_tree.nodes.new('ShaderNodeEmission')
    em.inputs['Color'].default_value = (1.0, 0.62, 0.28, 1)
    em.inputs['Strength'].default_value = 5.0
    glass.node_tree.links.new(em.outputs['Emission'],
                              glass.node_tree.nodes['Material Output'].inputs['Surface'])
    return glass


@part('lantern')
def lantern(p, parent):
    """A wall lantern: an iron arm out of the wall (`wall`: the side the wall is on, 'x+' or
    'y+'), a dark iron cage with glowing panes hanging from it, and a cap."""
    iron = material('iron', (0.12, 0.12, 0.13), 0.45, metallic=0.85)
    x, y, z = p['x'], p['y'], p['z']
    dx, dy = (-1, 0) if p.get('wall', 'y+') == 'x+' else (0, -1)
    reach = 0.32
    ax, ay = x + dx * reach / 2, y + dy * reach / 2
    add_box('arm', ax, ay, z + 0.18, reach if dx else 0.04, reach if dy else 0.04, 0.04, 0,
            iron, parent)
    add_box('plate', x, y, z + 0.05, 0.04 if dx else 0.12, 0.12 if dx else 0.04, 0.26, 0, iron,
            parent)
    lx, ly = x + dx * reach, y + dy * reach
    add_box('panes', lx, ly, z - 0.22, 0.13, 0.13, 0.22, 0, glow(), parent)
    for ox in (-0.07, 0.07):
        for oy in (-0.07, 0.07):
            add_box('frame', lx + ox, ly + oy, z - 0.24, 0.02, 0.02, 0.27, 0, iron, parent)
    add_box('cap', lx, ly, z + 0.02, 0.18, 0.18, 0.05, 0, iron, parent)
    add_box('hook', lx, ly, z + 0.07, 0.02, 0.02, 0.13, 0, iron, parent)


def camera(spec, width, height):
    e = math.radians(spec['elevation'])
    s = spec['px_per_m']
    cam_data = bpy.data.cameras.new('cam')
    cam_data.type = 'ORTHO'
    cam_data.ortho_scale = max(width, height) / s
    cam = bpy.data.objects.new('cam', cam_data)
    bpy.context.scene.collection.objects.link(cam)
    a = math.pi / 2 - e
    cam.rotation_euler = (a, 0.0, 0.0)
    right = (1.0, 0.0, 0.0)
    up = (0.0, math.cos(a), math.sin(a))
    back = (0.0, -math.sin(a), math.cos(a))
    # the world origin must land at (u0, v0): shift the frame centre accordingly
    dx = (width / 2 - spec.get('u0', width / 2)) / s
    dy = (spec.get('v0', height / 2) - height / 2) / s
    dist = 80.0
    cam.location = tuple(right[k] * dx + up[k] * dy + back[k] * dist for k in range(3))
    cam_data.clip_end = 400.0
    bpy.context.scene.camera = cam


def lights(specs, parent):
    if not specs:
        specs = [{'kind': 'sun', 'angle': [50, 0, 30], 'energy': 3.0, 'rgb': [1.0, 0.92, 0.8]}]
    for i, l in enumerate(specs):
        if l['kind'] == 'sun':
            data = bpy.data.lights.new(f'sun{i}', 'SUN')
            data.energy = l.get('energy', 3.0)
            data.angle = math.radians(l.get('soft', 8))
            ob = bpy.data.objects.new(f'sun{i}', data)
            ob.rotation_euler = tuple(math.radians(v) for v in l['angle'])
        else:
            data = bpy.data.lights.new(f'lamp{i}', 'POINT')
            data.energy = l.get('energy', 80.0)
            data.shadow_soft_size = l.get('radius', 0.15)
            ob = bpy.data.objects.new(f'lamp{i}', data)
            ob.location = tuple(l['at'])
            ob.parent = parent
        data.color = tuple(l.get('rgb', (1.0, 0.85, 0.6)))
        bpy.context.scene.collection.objects.link(ob)


def render(scene_path, out_path):
    with open(scene_path, encoding='utf-8') as f:
        spec = json.load(f)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    w, h = spec['width'], spec['height']
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.resolution_percentage = 100
    sc.render.engine = 'CYCLES'
    prefs = bpy.context.preferences.addons['cycles'].preferences
    try:
        prefs.compute_device_type = 'METAL'
        prefs.get_devices()
        for d in prefs.devices:
            d.use = True
        sc.cycles.device = 'GPU'
    except Exception:                                   # noqa: BLE001 - CPU is fine
        sc.cycles.device = 'CPU'
    sc.cycles.samples = int(spec.get('samples', 64))
    sc.cycles.use_denoising = True
    sc.view_settings.view_transform = 'Standard'
    sc.render.image_settings.file_format = 'PNG'
    sc.render.image_settings.color_mode = 'RGB'
    world = bpy.data.worlds.new('void')
    world.use_nodes = True
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (0, 0, 0, 1)
    world.node_tree.nodes['Background'].inputs['Strength'].default_value = spec.get('ambient', 0.0)
    sc.world = world
    room = bpy.data.objects.new('room', None)
    sc.collection.objects.link(room)
    room.rotation_euler = (0, 0, math.radians(spec['camera'].get('turn', 0.0)))
    for p in spec.get('parts', []):
        KINDS[p['kind']](p, room)
    lights(spec.get('lights'), room)
    camera(spec['camera'], w, h)
    sc.render.filepath = out_path
    bpy.ops.render.render(write_still=True)


if __name__ == '__main__':
    argv = sys.argv[sys.argv.index('--') + 1:]
    render(argv[0], argv[1])
