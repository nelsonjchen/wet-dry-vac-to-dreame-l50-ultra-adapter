"""Render the checked-in CAD meshes with Blender.

Run: blender --background --python cad/render_models.py
Outputs: cad/exports/blog/ (ignored).
"""
import bpy
from mathutils import Vector
from pathlib import Path
from math import radians

root=Path(__file__).resolve().parents[1]
out=root/'cad/exports/blog'
out.mkdir(parents=True, exist_ok=True)

def material(name, color):
    m=bpy.data.materials.new(name)
    m.diffuse_color=(*color,1)
    m.use_nodes=True
    shader=m.node_tree.nodes.get('Principled BSDF')
    shader.inputs['Base Color'].default_value=(*color,1)
    shader.inputs['Roughness'].default_value=.36
    return m

def render(kind,adapter,elbow,color):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    scene=bpy.context.scene
    scene.render.engine='CYCLES'
    scene.cycles.samples=40
    scene.cycles.use_denoising=True
    scene.render.resolution_x=1600
    scene.render.resolution_y=1000
    scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG'
    scene.view_settings.view_transform='AgX'
    scene.world.color=(.28,.28,.28)
    plastic=material(kind,color)
    pieces=[]
    for filename,x in [(adapter,-62),(elbow,76)]:
        bpy.ops.wm.stl_import(filepath=str(root/'models'/filename))
        obj=bpy.context.object
        obj.data.materials.append(plastic)
        points=[obj.matrix_world@Vector(v) for v in obj.bound_box]
        middle=(min(p.x for p in points)+max(p.x for p in points))/2
        center_y=(min(p.y for p in points)+max(p.y for p in points))/2
        obj.location+=Vector((x-middle,-center_y,-min(p.z for p in points)))
        for face in obj.data.polygons: face.use_smooth=True
        obj.data.set_sharp_from_angle(angle=radians(35))
        pieces.append(obj)
    bpy.context.view_layer.update()
    pts=[o.matrix_world@Vector(v) for o in pieces for v in o.bound_box]
    target=Vector(((min(p.x for p in pts)+max(p.x for p in pts))/2,0,25))
    bpy.ops.object.camera_add(location=target+Vector((160,-235,220)))
    camera=bpy.context.object
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler()
    camera.data.type='ORTHO'
    rotation=camera.rotation_euler.to_matrix().transposed()
    projected=[rotation@(p-target) for p in pts]
    width=max(p.x for p in projected)-min(p.x for p in projected)
    height=max(p.y for p in projected)-min(p.y for p in projected)
    # Blender's ortho scale is horizontal at this landscape aspect.
    camera.data.ortho_scale=max(width,height*1.6)*1.16
    scene.camera=camera
    bpy.ops.mesh.primitive_plane_add(size=2000,location=(0,0,-.5))
    bpy.context.object.data.materials.append(material('Background',(.88,.9,.9)))
    for location,power,size in [((-120,-160,280),1500000,180),((200,80,220),1100000,150),((-100,150,100),550000,120)]:
        bpy.ops.object.light_add(type='AREA',location=location)
        light=bpy.context.object
        light.data.energy=power
        light.data.shape='DISK'
        light.data.size=size
        light.rotation_euler=(target-light.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(out/f'{kind}-adapter-and-elbow.png')
    bpy.ops.render.render(write_still=True)

render('stanley','hose-adapter-rev5.stl','stanley-to-stanley-90-elbow.stl',(.02,.45,.27))
render('dewalt','hose-adapter-rev5-dewalt-measured.stl','dewalt-to-dewalt-90-elbow.stl',(.88,.48,.025))
