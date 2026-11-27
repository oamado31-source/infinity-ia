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


def net_material(name, see_through=True, mesh=0.10, cord=0.025, cover=0.6):
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
    grid.inputs['Brick Width'].default_value = mesh
    grid.inputs['Row Height'].default_value = mesh
    grid.inputs['Mortar Size'].default_value = cord
    nt.links.new(vec, grid.inputs['Vector'])
    if see_through:
        hole = nt.nodes.new('ShaderNodeBsdfTransparent')
        mix = nt.nodes.new('ShaderNodeMixShader')
        # at the game's scale a cord is under a pixel: the net reads as a see-through cloth
        opacity = nt.nodes.new('ShaderNodeMapRange')
        opacity.inputs['To Min'].default_value = cover
        opacity.inputs['To Max'].default_value = 1.0
        nt.links.new(grid.outputs['Fac'], opacity.inputs['Value'])   # 1 on the cords
        nt.links.new(opacity.outputs['Result'], mix.inputs['Fac'])
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


@part('hammock')
def hammock(p, parent):
    """A sailor's hammock: canvas sagging between two hooks, hung by ropes from the beams
    (cut away above the walls). `length` runs along its own turn."""
    canvas = material('hammock', (0.42, 0.37, 0.28), 0.95, noise=0.3)
    rope = material('rope', (0.30, 0.24, 0.16), 1.0, noise=0.3)
    L, wid, z, sag = p.get('length', 2.0), p.get('w', 0.8), p.get('z', 1.3), p.get('sag', 0.35)
    g = group(p.get('id', 'hammock'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=16, y_subdivisions=6, size=1.0)
    ob = bpy.context.object
    for v in ob.data.vertices:
        u, t = v.co.x + 0.5, v.co.y + 0.5
        v.co.x = (u - 0.5) * L
        v.co.y = (t - 0.5) * wid * (0.35 + 0.65 * math.sin(math.pi * u))
        v.co.z = z - sag * math.sin(math.pi * u) - 0.12 * math.sin(math.pi * t)
    ob.parent = g
    ob.data.materials.append(canvas)
    sol = ob.modifiers.new('cloth', 'SOLIDIFY')
    sol.thickness = 0.02
    for c in (-1, 1):
        _piece('rope', c * (L / 2 + 0.05), 0, (z + 2.75) / 2, 0.025, 0.025, 2.75 - z, rope, g)


@part('table')
def table(p, parent):
    """A plank table on four legs."""
    top = wood_planks('table-top', (0.40, 0.21, 0.11), 0.25, 1.5)
    leg = material('table-leg', (0.28, 0.15, 0.08), 0.8, noise=0.3)
    w, d, h = p.get('w', 3.0), p.get('d', 0.9), p.get('h', 0.75)
    g = group(p.get('id', 'table'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    _piece('top', 0, 0, h - 0.03, w, d, 0.06, top, g)
    for cx in (-1, 1):
        for cy in (-1, 1):
            _piece('leg', cx * (w / 2 - 0.1), cy * (d / 2 - 0.1), (h - 0.06) / 2, 0.08, 0.08,
                   h - 0.06, leg, g)


@part('bench')
def bench(p, parent):
    seat = material('table-leg', (0.28, 0.15, 0.08), 0.8, noise=0.3)
    w, d, h = p.get('w', 2.8), p.get('d', 0.3), p.get('h', 0.45)
    g = group(p.get('id', 'bench'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    _piece('seat', 0, 0, h - 0.03, w, d, 0.06, seat, g)
    for c in (-1, 1):
        _piece('leg', c * (w / 2 - 0.15), 0, (h - 0.06) / 2, 0.08, d - 0.04, h - 0.06, seat, g)


def _blob(name, x, y, z, sx, sy, sz, mat, parent):
    bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=16, ring_count=8,
                                         location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.scale = (sx, sy, sz)
    ob.parent = parent
    ob.location = (x, y, z)
    ob.data.materials.append(mat)
    bpy.ops.object.shade_smooth()
    return ob


def _cyl(name, x, y, z, r, h, mat, parent, verts=16):
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=h, vertices=verts, location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.parent = parent
    ob.location = (x, y, z + h / 2)
    ob.data.materials.append(mat)
    return ob


@part('table-setting')
def table_setting(p, parent):
    """A laid table, as the game's tables: a platter with a roast, plates with food, loaves of
    bread, pewter tankards, dark bottles, a fruit bowl and a candle. `h` is the table's height;
    the setting runs along the table's length `w`."""
    pewter = material('pewter', (0.42, 0.40, 0.37), 0.35, metallic=0.8)
    ceramic = material('ceramic', (0.44, 0.39, 0.31), 0.5)
    roast = material('roast', (0.42, 0.18, 0.07), 0.35)
    bread = material('bread', (0.62, 0.40, 0.17), 0.8, noise=0.2)
    glass = material('bottle', (0.04, 0.16, 0.07), 0.12)
    red = material('apple', (0.55, 0.08, 0.05), 0.4)
    green = material('pear', (0.40, 0.48, 0.12), 0.5)
    stew = material('stew', (0.35, 0.22, 0.10), 0.4)
    wax = material('wax', (0.85, 0.80, 0.62), 0.6)
    z = p.get('h', 0.75)                 # the layout is set for a table about 3 m long
    g = group(p.get('id', 'setting'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    # the platter with the roast, in the middle
    pl = _cyl('platter', 0, 0, z, 0.24, 0.02, pewter, g, 24)
    pl.scale = (1.5, 1.0, 1.0)
    for k, (dx, dy) in enumerate(((-0.13, 0.02), (0.0, -0.03), (0.13, 0.03))):
        _blob('roast', dx, dy, z + 0.05, 0.09, 0.06, 0.045, roast, g)
    # plates with food, along both sides
    for i, dx in enumerate((-1.1, -0.5, 0.55, 1.1)):
        for side in (-1, 1):
            if (i + (side > 0)) % 3 == 2:
                continue
            _cyl('plate', dx, side * 0.27, z, 0.11, 0.015, ceramic, g, 20)
            _blob('food', dx + 0.01, side * 0.27, z + 0.03, 0.06, 0.05, 0.025, stew, g)
    # loaves of bread
    for dx, dy, t in ((-0.75, 0.05, 20), (0.8, -0.06, -15), (0.35, 0.18, 70)):
        b = _blob('loaf', dx, dy, z + 0.04, 0.13, 0.05, 0.045, bread, g)
        b.rotation_euler = (0, 0, math.radians(t))
    # tankards
    for dx, dy in ((-0.85, -0.2), (-0.25, 0.22), (0.3, -0.24), (1.25, 0.2), (0.95, -0.18)):
        _cyl('tankard', dx, dy, z, 0.045, 0.11, pewter, g)
        _piece('handle', dx + 0.06, dy, z + 0.06, 0.03, 0.012, 0.06, pewter, g)
    # bottles
    for dx, dy in ((-0.4, -0.12), (0.62, 0.1)):
        _cyl('bottle', dx, dy, z, 0.04, 0.17, glass, g)
        _cyl('neck', dx, dy, z + 0.17, 0.015, 0.07, glass, g)
    # a fruit bowl
    _cyl('bowl', -1.35, -0.02, z, 0.12, 0.05, ceramic, g, 20)
    for k, (dx, dy) in enumerate(((-0.04, 0.0), (0.04, 0.03), (0.0, -0.05), (0.02, 0.06))):
        _blob('fruit', -1.35 + dx, -0.02 + dy, z + 0.07, 0.045, 0.045, 0.045,
              red if k % 2 == 0 else green, g)
    # a candle, burning
    _cyl('candle', 0.15, 0.25, z, 0.025, 0.12, wax, g)
    flame = _blob('flame', 0.15, 0.25, z + 0.14, 0.012, 0.012, 0.025, glow(), g)
    light = bpy.data.lights.new('candle', 'POINT')
    light.energy = p.get('candle', 5.0)
    light.color = (1.0, 0.7, 0.4)
    light.shadow_soft_size = 0.05
    lo = bpy.data.objects.new('candle', light)
    bpy.context.scene.collection.objects.link(lo)
    lo.parent = g
    lo.location = (0.15, 0.25, z + 0.2)
    return flame


@part('partition')
def partition(p, parent):
    """An inner wall of planks along x or y, from (x, y), `length` long, with door gaps
    ([start, end] along it) and a lintel over each gap."""
    along_x = p['axis'] == 'x'
    planks = wood_planks('partition-' + p['axis'], tuple(p.get('rgb', (0.36, 0.16, 0.09))),
                         0.2, 2.0, (90, 0, 0) if along_x else (90, 90, 0))
    frame = material('ribs', (0.15, 0.08, 0.05), 0.8, noise=0.3)
    L, h, t = p['length'], p.get('h', 2.4), 0.12
    cuts = sorted(tuple(g) for g in p.get('gaps', []))
    edges, start = [], 0.0
    for a, b in cuts:
        edges.append((start, a))
        start = b
    edges.append((start, L))

    def seg(a, b, z0, z1, mat):
        if b - a < 0.01:
            return
        m = (a + b) / 2
        x, y = (p['x'] + m, p['y']) if along_x else (p['x'], p['y'] + m)
        add_box('wall', x, y, z0, (b - a) if along_x else t, t if along_x else (b - a), z1 - z0, 0,
                mat, parent)

    for a, b in edges:
        seg(a, b, 0.0, h, planks)
    for a, b in cuts:
        seg(a, b, 2.05, h, planks)                       # over the door
        for c in (a, b):                                 # the door posts
            seg(c - 0.05, c + 0.05, 0.0, 2.1, frame)


def rug_material(w, d):
    """A rug as the game's (AR0515): a dark outer edge, a wide golden border woven like a
    braid, a thin red line and a thin golden line, and a mottled rust-red field. Bands follow
    the distance to the nearest edge, in metres (object coordinates)."""
    name = 'rug-%.2f-%.2f' % (w, d)
    m = bpy.data.materials.get(name)
    if m:
        return m
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes['Principled BSDF']
    bsdf.inputs['Roughness'].default_value = 0.95
    tc = nt.nodes.new('ShaderNodeTexCoord')
    sep = nt.nodes.new('ShaderNodeSeparateXYZ')
    nt.links.new(tc.outputs['Object'], sep.inputs['Vector'])

    def math(op, a, b=None):
        n = nt.nodes.new('ShaderNodeMath')
        n.operation = op
        for i, v in enumerate((a, b)):
            if v is None:
                continue
            if isinstance(v, (int, float)):
                n.inputs[i].default_value = v
            else:
                nt.links.new(v, n.inputs[i])
        return n.outputs['Value']

    dx = math('SUBTRACT', w / 2, math('ABSOLUTE', sep.outputs['X']))
    dy = math('SUBTRACT', d / 2, math('ABSOLUTE', sep.outputs['Y']))
    edge = math('MINIMUM', dx, dy)

    def ramp(fac, c0, c1):
        r = nt.nodes.new('ShaderNodeValToRGB')
        r.color_ramp.elements[0].color = (*c0, 1)
        r.color_ramp.elements[1].color = (*c1, 1)
        nt.links.new(fac, r.inputs['Fac'])
        return r.outputs['Color']

    mottle = nt.nodes.new('ShaderNodeTexNoise')
    mottle.inputs['Scale'].default_value = 7.0
    mottle.inputs['Detail'].default_value = 5.0
    nt.links.new(tc.outputs['Object'], mottle.inputs['Vector'])
    field = ramp(mottle.outputs['Fac'], (0.30, 0.07, 0.035), (0.46, 0.12, 0.06))
    braid = nt.nodes.new('ShaderNodeTexWave')
    braid.bands_direction = 'DIAGONAL'
    braid.inputs['Scale'].default_value = 7.0          # a twist every ~12 cm (5 px)
    braid.inputs['Distortion'].default_value = 0.8
    nt.links.new(tc.outputs['Object'], braid.inputs['Vector'])
    gold = ramp(braid.outputs['Fac'], (0.24, 0.15, 0.05), (0.58, 0.45, 0.21))
    dots = nt.nodes.new('ShaderNodeTexVoronoi')
    dots.inputs['Scale'].default_value = 2.6           # a dark knot every ~40 cm
    dots.inputs['Randomness'].default_value = 0.0
    nt.links.new(tc.outputs['Object'], dots.inputs['Vector'])
    knot = nt.nodes.new('ShaderNodeMix')
    knot.data_type = 'RGBA'
    nt.links.new(math('LESS_THAN', dots.outputs['Distance'], 0.14), knot.inputs['Factor'])
    nt.links.new(gold, knot.inputs['A'])
    knot.inputs['B'].default_value = (0.10, 0.05, 0.03, 1)
    gold = knot.outputs['Result']
    color = field
    for limit, layer in ((0.32, (0.50, 0.37, 0.15)), (0.29, (0.40, 0.09, 0.05)),
                         (0.24, gold), (0.025, (0.12, 0.05, 0.03))):
        mix = nt.nodes.new('ShaderNodeMix')
        mix.data_type = 'RGBA'
        nt.links.new(math('LESS_THAN', edge, limit), mix.inputs['Factor'])
        nt.links.new(color, mix.inputs['A'])
        if isinstance(layer, tuple):
            mix.inputs['B'].default_value = (*layer, 1)
        else:
            nt.links.new(layer, mix.inputs['B'])
        color = mix.outputs['Result']
    nt.links.new(color, bsdf.inputs['Base Color'])
    return m


@part('rug')
def rug(p, parent):
    """A rug in the game's style (see rug_material)."""
    w, d = p['w'], p['d']
    add_box('rug', p['x'], p['y'], 0.0, w, d, 0.008, p.get('turn', 0.0), rug_material(w, d),
            parent)


@part('bed')
def bed(p, parent):
    """A four-poster bed: wooden frame and posts, mattress, blanket and pillow."""
    wood = material('chest', (0.33, 0.17, 0.09), 0.8, noise=0.3)
    linen = material('linen', (0.62, 0.57, 0.46), 0.95, noise=0.2)
    rgb = tuple(p.get('rgb', (0.16, 0.22, 0.09)))
    blanket = material('blanket-%.2f-%.2f-%.2f' % rgb, rgb, 0.95, noise=0.35)
    L, W = p.get('length', 2.0), p.get('w', 1.0)
    g = group(p.get('id', 'bed'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    _piece('frame', 0, 0, 0.2, L, W, 0.3, wood, g)
    _piece('mattress', 0, 0, 0.42, L - 0.1, W - 0.1, 0.14, linen, g)
    _piece('blanket', 0.25, 0, 0.5, L * 0.62, W - 0.04, 0.05, blanket, g)
    _blob('pillow', -L / 2 + 0.3, 0, 0.53, 0.16, W * 0.38, 0.06, linen, g)
    _piece('head', -L / 2 - 0.04, 0, 0.6, 0.08, W, 0.8, wood, g)
    for cx in (-1, 1):
        for cy in (-1, 1):
            _piece('post', cx * (L / 2 + 0.02), cy * (W / 2 - 0.03), 0.7, 0.08, 0.08, 1.4, wood, g)


@part('chair')
def chair(p, parent):
    wood = material('chest', (0.33, 0.17, 0.09), 0.8, noise=0.3)
    g = group(p.get('id', 'chair'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    _piece('seat', 0, 0, 0.45, 0.45, 0.45, 0.05, wood, g)
    _piece('back', -0.2, 0, 0.75, 0.05, 0.45, 0.6, wood, g)
    for cx in (-1, 1):
        for cy in (-1, 1):
            _piece('leg', cx * 0.19, cy * 0.19, 0.22, 0.05, 0.05, 0.44, wood, g)


@part('wardrobe')
def wardrobe(p, parent):
    wood = material('chest', (0.33, 0.17, 0.09), 0.8, noise=0.3)
    seam = material('ribs', (0.15, 0.08, 0.05), 0.8, noise=0.3)
    w, d, h = p.get('w', 1.0), p.get('d', 0.5), p.get('h', 1.9)
    g = group(p.get('id', 'wardrobe'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    _piece('body', 0, 0, h / 2, w, d, h, wood, g)
    _piece('cornice', 0, 0, h + 0.03, w + 0.08, d + 0.08, 0.06, seam, g)
    _piece('seam', 0, -d / 2 - 0.005, h / 2, 0.02, 0.01, h - 0.1, seam, g)


@part('window')
def window(p, parent):
    """A stern window on a wall (`wall`: 'x+' or 'y+'): a dark frame, mullions and moonlit
    glass."""
    frame = material('ribs', (0.15, 0.08, 0.05), 0.8, noise=0.3)
    moon = bpy.data.materials.get('moon-glass')
    if moon is None:
        moon = bpy.data.materials.new('moon-glass')
        moon.use_nodes = True
        em = moon.node_tree.nodes.new('ShaderNodeEmission')
        em.inputs['Color'].default_value = (0.45, 0.58, 0.8, 1)
        em.inputs['Strength'].default_value = 1.2
        moon.node_tree.links.new(em.outputs['Emission'],
                                 moon.node_tree.nodes['Material Output'].inputs['Surface'])
    on_x = p.get('wall', 'x+') == 'x+'
    w, h, z = p.get('w', 0.8), p.get('h', 0.9), p.get('z', 1.1)
    x, y = p['x'], p['y']
    gw, gd = (0.02, w) if on_x else (w, 0.02)
    add_box('glass', x, y, z, gw, gd, h, 0, moon, parent)
    for k in (-1, 0, 1):
        o = k * w / 2
        add_box('mullion', x, y + (o if on_x else 0), z, 0.05, 0.05, h, 0, frame, parent) if on_x \
            else add_box('mullion', x + o, y, z, 0.05, 0.05, h, 0, frame, parent)
    for zz in (z - 0.03, z + h / 2 - 0.02, z + h - 0.03):
        add_box('rail', x, y, zz, 0.06 if on_x else w + 0.06, w + 0.06 if on_x else 0.06, 0.06, 0,
                frame, parent)


def _prism(name, top_pts, z0, z1, mat, parent, bottom_scale=1.0):
    """A solid from a polygon (room metres): its top at z1 and its bottom at z0, the bottom
    shrunk towards the centre by `bottom_scale` (a hull narrowing to the keel)."""
    import bmesh
    cx = sum(x for x, _y in top_pts) / len(top_pts)
    cy = sum(y for _x, y in top_pts) / len(top_pts)
    me = bpy.data.meshes.new(name)
    bm = bmesh.new()
    top = [bm.verts.new((x, y, z1)) for x, y in top_pts]
    bot = [bm.verts.new((cx + (x - cx) * bottom_scale, cy + (y - cy) * bottom_scale, z0))
           for x, y in top_pts]
    n = len(top_pts)
    bm.faces.new(top)
    bm.faces.new(list(reversed(bot)))
    for k in range(n):
        bm.faces.new((bot[k], bot[(k + 1) % n], top[(k + 1) % n], top[k]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.parent = parent
    ob.data.materials.append(mat)
    return ob


def _beam(name, a, b, r, mat, parent, verts=8):
    """A thin round piece (a rope, a spar) from point a to point b (room metres)."""
    ax, ay, az = a
    bx, by, bz = b
    dx, dy, dz = bx - ax, by - ay, bz - az
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    bpy.ops.mesh.primitive_cylinder_add(radius=r, depth=length, vertices=verts,
                                        location=(0, 0, 0))
    ob = bpy.context.object
    ob.name = name
    ob.parent = parent
    ob.location = ((ax + bx) / 2, (ay + by) / 2, (az + bz) / 2)
    ob.rotation_euler = (0.0, math.acos(max(-1.0, min(1.0, dz / length))), math.atan2(dy, dx))
    ob.data.materials.append(mat)
    return ob


@part('water')
def water(p, parent):
    """The sea at night: dark, with a gentle swell catching the moon."""
    m = bpy.data.materials.get('sea')
    if m is None:
        m = bpy.data.materials.new('sea')
        m.use_nodes = True
        nt = m.node_tree
        bsdf = nt.nodes['Principled BSDF']
        bsdf.inputs['Roughness'].default_value = 0.22
        swell = nt.nodes.new('ShaderNodeTexNoise')
        swell.inputs['Scale'].default_value = 0.25
        tone = nt.nodes.new('ShaderNodeValToRGB')
        tone.color_ramp.elements[0].color = (0.008, 0.028, 0.030, 1)   # the docks' teal, at night
        tone.color_ramp.elements[1].color = (0.020, 0.060, 0.062, 1)
        nt.links.new(swell.outputs['Fac'], tone.inputs['Fac'])
        nt.links.new(tone.outputs['Color'], bsdf.inputs['Base Color'])
        tc = nt.nodes.new('ShaderNodeTexCoord')
        nt.links.new(tc.outputs['Object'], swell.inputs['Vector'])
        waves = nt.nodes.new('ShaderNodeTexNoise')
        waves.inputs['Scale'].default_value = 0.9
        waves.inputs['Detail'].default_value = 8.0
        nt.links.new(tc.outputs['Object'], waves.inputs['Vector'])
        bump = nt.nodes.new('ShaderNodeBump')
        bump.inputs['Strength'].default_value = 0.45
        nt.links.new(waves.outputs['Fac'], bump.inputs['Height'])
        nt.links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    bpy.ops.mesh.primitive_plane_add(size=p.get('size', 120.0), location=(0, 0, p.get('z', -2.4)))
    ob = bpy.context.object
    ob.data.materials.append(m)
    ob.parent = parent


@part('ship-deck')
def ship_deck(p, parent):
    """The ship seen from above: the deck inside its outline, the hull going down to the sea
    and a bulwark (a low wall with a rail) around."""
    outline = [tuple(q) for q in p['outline']]
    deck = wood_planks('deck-planks', (0.34, 0.17, 0.10), 0.22, 3.0)
    hull = wood_planks('hull-outer', (0.24, 0.11, 0.06), 0.3, 4.0, (90, 0, 0))
    rail = material('rail', (0.20, 0.10, 0.05), 0.75, noise=0.3)
    _prism('deck', outline, -0.12, 0.0, deck, parent)
    _prism('hull', outline, p.get('waterline', -2.4) - 0.6, -0.12, hull, parent,
           bottom_scale=p.get('keel', 0.82))
    h, t = p.get('bulwark', 0.9), 0.14
    for k, (a, b) in enumerate(zip(outline, outline[1:] + outline[:1])):
        length = math.dist(a, b)
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        add_box(f'bulwark{k}', mx, my, 0.0, length + t, t, h, ang, hull, parent)
        add_box(f'cap{k}', mx, my, h, length + t + 0.05, t + 0.08, 0.07, ang, rail, parent)


@part('raised-deck')
def raised_deck(p, parent):
    """A raised deck (the quarterdeck): a planked top `h` above the deck, its front faces
    panelled, and a railing on its edges with a gap for the stairs on the front."""
    x0, x1, y0, y1, h = p['x0'], p['x1'], p['y0'], p['y1'], p['h']
    top = wood_planks('deck-planks', (0.34, 0.17, 0.10), 0.22, 3.0)
    face = wood_planks('partition-x', (0.36, 0.16, 0.09), 0.2, 2.0, (90, 0, 0))
    rail = material('rail', (0.20, 0.10, 0.05), 0.75, noise=0.3)
    add_box('qd-body', (x0 + x1) / 2, (y0 + y1) / 2, 0.0, x1 - x0, y1 - y0, h - 0.06, 0, face,
            parent)
    add_box('qd-top', (x0 + x1) / 2, (y0 + y1) / 2, h - 0.06, x1 - x0 + 0.1, y1 - y0 + 0.1,
            0.06, 0, top, parent)
    g0, g1 = p.get('gap', (0.0, 0.0))
    rh = 0.9
    segments = [((x0, y0), (x1, y0)), ((x0, y1), (x1, y1)), ((x1, y0), (x1, y1))]
    if g1 > g0:
        segments += [((x0, y0), (x0, g0)), ((x0, g1), (x0, y1))]
    else:
        segments.append(((x0, y0), (x0, y1)))
    for k, (a, b) in enumerate(segments):
        length = math.dist(a, b)
        if length < 0.05:
            continue
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        add_box(f'qrail{k}', mx, my, h + rh - 0.05, length + 0.06, 0.1, 0.06, ang, rail, parent)
        steps = max(2, int(length / 0.35))
        for i in range(steps + 1):
            f = i / steps
            add_box('baluster', a[0] + (b[0] - a[0]) * f, a[1] + (b[1] - a[1]) * f, h, 0.05, 0.05,
                    rh - 0.06, 0, rail, parent)


@part('stairs')
def stairs(p, parent):
    """Wooden stairs rising along +x from x0 (on the deck) to x1 (at height h), `w` wide."""
    wood = material('table-leg', (0.28, 0.15, 0.08), 0.8, noise=0.3)
    x0, x1, y, w, h = p['x0'], p['x1'], p['y'], p.get('w', 1.0), p['h']
    n = max(3, int(h / 0.22))
    run = (x1 - x0) / n
    for i in range(n):
        add_box('step', x0 + run * (i + 0.5), y, h * i / n, run + 0.02, w, h / n, 0, wood, parent)
    for c in (-1, 1):
        a = (x0, y + c * (w / 2 + 0.04), 0.9)
        b = (x1, y + c * (w / 2 + 0.04), h + 0.9)
        _beam('handrail', a, b, 0.03, wood, parent)


@part('door')
def door(p, parent):
    """A double door in a face looking towards -x (the raised deck's front), with its frame."""
    wood = material('chest', (0.33, 0.17, 0.09), 0.8, noise=0.3)
    frame = material('ribs', (0.15, 0.08, 0.05), 0.8, noise=0.3)
    iron = material('iron', (0.12, 0.12, 0.13), 0.45, metallic=0.85)
    x, y, w, h = p['x'], p['y'], p.get('w', 1.3), p.get('h', 1.7)
    add_box('door-frame', x - 0.02, y, 0.0, 0.08, w + 0.2, h + 0.12, 0, frame, parent)
    for c in (-1, 1):
        add_box('leaf', x - 0.06, y + c * w / 4, 0.0, 0.05, w / 2 - 0.03, h, 0, wood, parent)
        add_box('ring', x - 0.1, y + c * 0.12, h * 0.5, 0.03, 0.06, 0.06, 0, iron, parent)


@part('rigging')
def rigging(p, parent):
    """The mast's ropes (shrouds) from its top down to the bulwarks, and a yard with its sail
    furled. `top` and `anchors` are room points (x, y, z)."""
    rope = material('rope', (0.30, 0.24, 0.16), 1.0, noise=0.3)
    sail = material('sail', (0.55, 0.50, 0.40), 0.95, noise=0.3)
    spar = material('mast', (0.33, 0.21, 0.11), 0.75, stripes=0.25)
    top = tuple(p['top'])
    for k, a in enumerate(p.get('anchors', [])):
        _beam(f'shroud{k}', tuple(a), top, 0.022, rope, parent, 6)
    if 'yard' in p:
        y = p['yard']
        a, b = (y['x'], y['y0'], y['z']), (y['x'], y['y1'], y['z'])
        _beam('yard', a, b, 0.12, spar, parent, 12)
        _beam('furled', (a[0], a[1] + 0.4, a[2] - 0.18), (b[0], b[1] - 0.4, b[2] - 0.18), 0.17,
              sail, parent, 12)


@part('wheel')
def wheel(p, parent):
    """The ship's wheel on its post, facing along x."""
    wood = material('chest', (0.33, 0.17, 0.09), 0.8, noise=0.3)
    x, y, z = p['x'], p['y'], p.get('floor', 0.0)
    add_box('helm-post', x, y, z, 0.25, 0.3, 1.0, 0, wood, parent)
    c = (x - 0.18, y, z + 1.15)
    bpy.ops.mesh.primitive_torus_add(major_radius=0.42, minor_radius=0.035, location=c,
                                     rotation=(0, math.pi / 2, 0))
    ring = bpy.context.object
    ring.parent = parent
    ring.data.materials.append(wood)
    for k in range(8):
        a = 2 * math.pi * k / 8
        _beam('spoke', c, (c[0], c[1] + 0.58 * math.cos(a), c[2] + 0.58 * math.sin(a)), 0.02,
              wood, parent, 6)


@part('capstan')
def capstan(p, parent):
    wood = material('mast', (0.33, 0.21, 0.11), 0.75, stripes=0.25)
    x, y = p['x'], p['y']
    _cyl('drum', x, y, 0.0, 0.35, 0.8, wood, parent, 16)
    _cyl('cap', x, y, 0.8, 0.45, 0.12, wood, parent, 16)
    for k in range(4):
        a = math.pi * k / 4
        _beam('bar', (x - 0.9 * math.cos(a), y - 0.9 * math.sin(a), 0.86),
              (x + 0.9 * math.cos(a), y + 0.9 * math.sin(a), 0.86), 0.03, wood, parent, 6)


@part('rope-coil')
def rope_coil(p, parent):
    rope = material('rope', (0.30, 0.24, 0.16), 1.0, noise=0.3)
    for k in range(3):
        bpy.ops.mesh.primitive_torus_add(major_radius=p.get('r', 0.35) - 0.06 * k,
                                         minor_radius=0.04,
                                         location=(p['x'], p['y'], p.get('floor', 0.0) + 0.04 + 0.07 * k))
        t = bpy.context.object
        t.parent = parent
        t.data.materials.append(rope)


@part('lantern-post')
def lantern_post(p, parent):
    """A post with an arm and a hanging lantern (the deck's lanterns)."""
    wood = material('post', (0.25, 0.15, 0.08), 0.8, noise=0.3)
    iron = material('iron', (0.12, 0.12, 0.13), 0.45, metallic=0.85)
    x, y, f, h = p['x'], p['y'], p.get('floor', 0.0), p.get('h', 2.4)
    add_box('lpost', x, y, f, 0.14, 0.14, h, 0, wood, parent)
    add_box('larm', x + 0.2, y, f + h - 0.1, 0.45, 0.05, 0.05, 0, iron, parent)
    lx = x + 0.4
    add_box('panes', lx, y, f + h - 0.5, 0.14, 0.14, 0.24, 0, glow(), parent)
    add_box('lcap', lx, y, f + h - 0.24, 0.19, 0.19, 0.05, 0, iron, parent)
    add_box('lhook', lx, y, f + h - 0.2, 0.02, 0.02, 0.12, 0, iron, parent)


@part('grating-hatch')
def grating_hatch(p, parent):
    """A deck hatch: a raised frame with a wooden grating over a dark opening."""
    frame = material('crate-batten', (0.30, 0.16, 0.08), 0.8, noise=0.3)
    hole = material('hole', (0.0, 0.0, 0.0), 1.0)
    x, y, w, d = p['x'], p['y'], p.get('w', 1.6), p.get('d', 1.4)
    add_box('coaming', x, y, 0.0, w + 0.24, d + 0.24, 0.25, 0, frame, parent)
    add_box('dark', x, y, 0.25, w, d, 0.005, 0, hole, parent)
    for k in range(int(w / 0.2) + 1):
        add_box('slat', x - w / 2 + k * 0.2, y, 0.25, 0.05, d, 0.04, 0, frame, parent)
    for k in range(int(d / 0.2) + 1):
        add_box('slat', x, y - d / 2 + k * 0.2, 0.27, w, 0.05, 0.03, 0, frame, parent)


@part('rope-ladder')
def rope_ladder(p, parent):
    """A rope ladder hanging over the side (at y = `y`, the side facing -y) down to the sea."""
    rope = material('rope', (0.30, 0.24, 0.16), 1.0, noise=0.3)
    rung = material('ladder', (0.40, 0.26, 0.14), 0.8, noise=0.25)
    x, y, top, bottom = p['x'], p['y'], p.get('top', 0.95), p.get('bottom', -2.3)
    out, half = p.get('out', 0.35), p.get('half', 0.3)
    for c in (-half, half):                 # as wide as the way up the search map gives
        _beam('lrope', (x + c, y, top), (x + c, y - out, bottom), 0.025, rope, parent, 6)
    n = int((top - bottom) / 0.3)
    for i in range(1, n):
        f = i / n
        z = top + (bottom - top) * f
        add_box('lrung', x, y - out * f, z, 2 * half, 0.05, 0.04, 0, rung, parent)


@part('boarding-net')
def boarding_net(p, parent):
    """A boarding net hung over the side (the side facing -y at `y`), from the rail down to the
    water, `w` wide, sagging a little, with a few loose ropes: the party climbs it beside the
    ladder."""
    x, y, w = p['x'], p['y'], p.get('w', 3.0)
    top, bottom, out = p.get('top', 0.95), p.get('bottom', -2.2), p.get('out', 0.4)
    bpy.ops.mesh.primitive_grid_add(x_subdivisions=24, y_subdivisions=20, size=1.0)
    ob = bpy.context.object
    for v in ob.data.vertices:
        u, t = v.co.x + 0.5, 0.5 - v.co.y               # u across, t from the rail (0) down (1)
        v.co.x = x + (u - 0.5) * w
        v.co.z = top + (bottom - top) * t
        v.co.y = y - out * t - 0.06 * math.sin(math.pi * u) * math.sin(math.pi * t)
    ob.parent = parent
    # a coarse cargo net (20 cm mesh): its cords read on the dark hull
    ob.data.materials.append(net_material('boarding-net', mesh=0.2, cord=0.04, cover=0.15))
    rope = material('rope', (0.30, 0.24, 0.16), 1.0, noise=0.3)
    for k, dx in enumerate(p.get('ropes', (-0.5, 0.5))):
        ex = x + (w / 2 + 0.35) * (1 if dx > 0 else -1) + dx * 0.4
        _beam(f'loose{k}', (ex, y, top), (ex + 0.1, y - out * 0.9, bottom + 0.4), 0.025, rope,
              parent, 6)
    for c in (-1, 1):                                  # the net's edge ropes
        _beam('edge', (x + c * w / 2, y, top), (x + c * w / 2, y - out, bottom), 0.03, rope,
              parent, 6)


@part('rowboat')
def rowboat(p, parent):
    """A rowboat as the ones moored at the game's docks: weathered grey-green planks, a pointed
    bow (towards +x of its own turn), a square stern, thwarts and a pair of oars. `floor` is the
    height of its bottom boards; `length` and `beam` its size."""
    L, B, f = p.get('length', 6.0), p.get('beam', 2.0), p.get('floor', -2.15)
    planks = wood_planks('boat-planks', (0.20, 0.22, 0.17), 0.18, 1.6)
    rim = material('boat-rim', (0.15, 0.14, 0.11), 0.8, noise=0.3)
    g = group(p.get('id', 'rowboat'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    outline = [(-L / 2, -B / 2 * 0.85), (L * 0.18, -B / 2), (L / 2, 0.0), (L * 0.18, B / 2),
               (-L / 2, B / 2 * 0.85)]
    _prism('boat-hull', outline, f - 0.55, f, planks, g, bottom_scale=0.55)
    sides = wood_planks('boat-sides', (0.20, 0.22, 0.17), 0.15, 2.0, (90, 0, 0))
    for k, (a, b) in enumerate(zip(outline, outline[1:] + outline[:1])):
        length = math.dist(a, b)
        ang = math.degrees(math.atan2(b[1] - a[1], b[0] - a[0]))
        mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
        _piece(f'strake{k}', mx, my, f + 0.22, length + 0.06, 0.07, 0.44, sides, g,
               (0, 0, math.radians(ang)))
        _piece(f'gunwale{k}', mx, my, f + 0.46, length + 0.08, 0.11, 0.05, rim, g,
               (0, 0, math.radians(ang)))
    for k, x in enumerate((-L * 0.3, -L * 0.05, L * 0.2)):
        width = B * (0.84 if x < L * 0.18 else 0.7)
        _piece(f'thwart{k}', x, 0, f + 0.3, 0.28, width, 0.05, rim, g)
    oar = material('oar', (0.38, 0.30, 0.18), 0.8, noise=0.2)
    for c in (-1, 1):
        _beam('oar', (-L * 0.35, c * 0.25, f + 0.38), (L * 0.25, c * 0.55, f + 0.4), 0.03, oar, g, 8)
        _piece('blade', L * 0.27, c * 0.57, f + 0.4, 0.5, 0.16, 0.02, oar, g)


@part('chest')
def chest(p, parent):
    """A sea chest: dark wood with iron bands and a lid."""
    wood = material('chest', (0.33, 0.17, 0.09), 0.8, noise=0.3)
    iron = material('iron', (0.12, 0.12, 0.13), 0.45, metallic=0.85)
    w, d, h = p.get('w', 0.8), p.get('d', 0.5), p.get('h', 0.5)
    g = group(p.get('id', 'chest'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    _piece('body', 0, 0, h / 2, w, d, h, wood, g)
    _piece('lid', 0, 0, h + 0.03, w + 0.02, d + 0.02, 0.06, wood, g)
    for c in (-0.3, 0.3):
        _piece('band', c * w, 0, h / 2 + 0.03, 0.05, d + 0.03, h + 0.07, iron, g)


@part('floor-hatch')
def floor_hatch(p, parent):
    """An opening in the floor with a raised frame and the top of a ladder going down."""
    frame = material('crate-batten', (0.30, 0.16, 0.08), 0.8, noise=0.3)
    hole = material('hole', (0.0, 0.0, 0.0), 1.0)
    w, d = p.get('w', 1.1), p.get('d', 1.1)
    g = group(p.get('id', 'hatch'), p['x'], p['y'], 0.0, p.get('turn', 0.0), parent)
    _piece('dark', 0, 0, 0.005, w, d, 0.01, hole, g)
    t = 0.12
    for c in (-1, 1):
        _piece('frame', 0, c * (d / 2 + t / 2), 0.08, w + 2 * t, t, 0.16, frame, g)
        _piece('frame', c * (w / 2 + t / 2), 0, 0.08, t, d, 0.16, frame, g)
    ladder = material('ladder', (0.40, 0.26, 0.14), 0.8, noise=0.25)
    for side in (-1, 1):
        _piece('rail', -w / 2 + 0.15, side * 0.28, 0.1, 0.07, 0.07, 0.4, ladder, g)


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
    """A ladder whose top leans `lean` metres towards +x (or +y with `axis`: 'y'); a negative
    lean leans the other way."""
    mat = material('ladder', (0.40, 0.26, 0.14), 0.8, noise=0.25)
    h, w, lean = p['h'], p.get('w', 0.6), p.get('lean', 0.35)
    turn = 90.0 if p.get('axis', 'x') == 'y' else 0.0
    g = group(p.get('id', 'ladder'), p['x'], p['y'], 0.0, turn, parent)
    for side in (-1, 1):
        rail = _piece('rail', lean / 2, side * w / 2, h / 2, 0.07, 0.07, math.hypot(h, lean), mat,
                      g)
        rail.rotation_euler = (0, math.atan2(lean, h), 0)
    for i in range(1, int(h / 0.3)):
        z = i * 0.3
        _piece('rung', lean * z / h, 0, z, 0.06, w, 0.04, mat, g)


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
    world.node_tree.nodes['Background'].inputs['Color'].default_value = (
        *spec.get('ambient_rgb', (0.0, 0.0, 0.0)), 1)
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
