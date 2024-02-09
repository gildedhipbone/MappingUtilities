import bpy
import bmesh
from mathutils import Vector
from bmesh.types import BMVert

bl_info = {
    "name": "Extrude Into Closed Mesh",
    "description": "Extrude selected faces into closed mesh.",
    "author": "Jacob Falck",
    "blender": (4, 0, 0),
    "version": (1, 0, 1),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "View 3D"
}

# To do:
# Add poll; return only in edit mode.

class ExtrudeIntoClosedMesh(bpy.types.Operator):
    """Tooltip."""
    bl_idname = "view3d.extrude_into_closed_mesh"
    bl_label = "Extrude Into Closed Mesh"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        obj = context.object
        # Helps for some reason.
        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        sel_polys = [p for p in obj.data.polygons if p.select]

        if len(sel_polys) == 0:
            self.report({"INFO"}, "No face selected, aborting.")
            return {"CANCELLED"}

        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()

        selected_faces = [f for f in bm.faces if f.select]
        src_sel_verts = [v for v in bm.verts if v.select]

        # Duplicate source verts and faces.
        ret = bmesh.ops.duplicate(bm, geom=selected_faces)
        dupl = ret["geom"]
        del ret
        dupl_src_verts = [ele for ele in dupl if isinstance(ele, bmesh.types.BMVert)]
        dupl_src_faces = [ele for ele in dupl if isinstance(ele, bmesh.types.BMFace)]
        # Save normals for selection at the end.
        lead_normals = []
        for f in dupl_src_faces:
            lead_normals.append(f.normal)

        # Duplicate for rear faces.
        ret = bmesh.ops.duplicate(bm, geom=selected_faces)
        dupl2 = ret["geom"]
        del ret
        rear_faces = [ele for ele in dupl2 if isinstance(ele, bmesh.types.BMFace)]
        for f in rear_faces:
            f.normal_flip()

        # Get the average normal along which to extrude.
        vector_mean = Vector((0, 0, 0))
        for f in selected_faces:
            vector_mean += f.normal
        vector_mean /= len(selected_faces)

        # This is an ugly hack. But using extrude_region_move rather than bmesh results in fewer 
        # instances of UV stretching. I don't know why. Something to do with Correct Face Attributes?
        bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":vector_mean})

        # Select adjacent faces.
        adj_faces = set(v for v in bm.verts if v.select for v in v.link_faces if not v.select)
        for f in adj_faces:
            f.select = True

        # Split the current selection (lead faces + adjacent faces)
        bpy.ops.mesh.split()
        selected_faces = [f for f in bm.faces if f.select]

        # Merge extruded verts and rear duplicate verts.
        for f in rear_faces:
            f.select = True
        bpy.ops.mesh.remove_doubles()

        bpy.ops.mesh.select_all(action = 'DESELECT')

        # Merge source and duplicate verts.
        for v in src_sel_verts:
            v.select = True
        for v in dupl_src_verts:
            v.select = True    
        bpy.ops.mesh.remove_doubles()

        bpy.ops.mesh.select_all(action = 'DESELECT')
        

        for f in selected_faces:
            for n in lead_normals:
                if (f.normal-n).length < 0.001:
                    f.select = True

        # Move back, but not all the way (if we do, we'll get more UV stretching issues)
        bpy.ops.transform.translate(value=(0,0,-0.999), orient_type="NORMAL", constraint_axis=(False, False, True))
            
        bmesh.update_edit_mesh(obj.data)

        bpy.ops.transform.translate('INVOKE_DEFAULT', orient_type="NORMAL", constraint_axis=(False, False, True))

        return {"FINISHED"}

addon_keymaps = []

def register():
    bpy.utils.register_class(ExtrudeIntoClosedMesh)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(ExtrudeIntoClosedMesh.bl_idname, type="E", value="PRESS", ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(ExtrudeIntoClosedMesh)

if __name__ == "__main__":
    register()