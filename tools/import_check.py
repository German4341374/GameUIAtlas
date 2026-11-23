"""Smoke-test the exported GLBs in a clean Blender scene."""
from pathlib import Path
import bpy

root = Path(__file__).resolve().parents[1]
assets = sorted(root.glob("studies/*/model/prop.glb"))
assert len(assets) == 4
for asset in assets:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    assert bpy.ops.import_scene.gltf(filepath=str(asset)) == {"FINISHED"}
    meshes = [o for o in bpy.context.scene.objects if o.type == "MESH"]
    assert all(o.data.materials and o.data.vertices for o in meshes)
    tris = 0
    for obj in meshes:
        obj.data.calc_loop_triangles()
        tris += len(obj.data.loop_triangles)
    assert len(meshes) > 25 and tris > 1000
    print(f"PASS {asset.parents[1].name}: {len(meshes)} mesh objects, {tris:,} triangles", flush=True)
