import bpy
import bmesh
from mathutils import Vector
from bmesh.types import BMVert

bl_info = {
    "name": "Extrude Into Closed Mesh",
    "description": "Extrude selected faces into closed mesh.",
    "author": "Jacob Falck",
    "blender": (5, 0, 0),
    "version": (1, 1, 0),
    "location": "View3D > Mesh > Extrude Into Closed Mesh",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Mesh"
}


class ExtrudeIntoClosedMesh(bpy.types.Operator):
    """Extrude selected faces into a closed mesh with proper topology"""
    bl_idname = "mesh.extrude_into_closed_mesh"
    bl_label = "Extrude Into Closed Mesh"
    bl_options = {'REGISTER', 'UNDO'}

    @classmethod
    def poll(cls, context):
        """Only allow in edit mode with mesh object"""
        return (context.mode == 'EDIT_MESH' and 
                context.object is not None and 
                context.object.type == 'MESH')

    def execute(self, context):
        obj = context.object
        
        # Ensure we're in edit mode
        if context.mode != 'EDIT_MESH':
            self.report({'WARNING'}, "Must be in Edit Mode")
            return {'CANCELLED'}

        # Get BMesh from edit mode (this is the correct selection state)
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        # Check for selected faces using BMesh (not obj.data.polygons)
        selected_faces = [f for f in bm.faces if f.select]
        if len(selected_faces) == 0:
            self.report({'INFO'}, "No faces selected")
            return {'CANCELLED'}
        src_sel_verts = [v for v in bm.verts if v.select]

        # Duplicate source verts and faces
        ret = bmesh.ops.duplicate(bm, geom=selected_faces)
        dupl = ret["geom"]
        dupl_src_verts = [ele for ele in dupl if isinstance(ele, bmesh.types.BMVert)]
        dupl_src_faces = [ele for ele in dupl if isinstance(ele, bmesh.types.BMFace)]
        
        # Save normals for selection at the end
        lead_normals = [f.normal.copy() for f in dupl_src_faces]

        # Duplicate for rear faces
        ret = bmesh.ops.duplicate(bm, geom=selected_faces)
        dupl2 = ret["geom"]
        rear_faces = [ele for ele in dupl2 if isinstance(ele, bmesh.types.BMFace)]
        
        # Flip rear face normals
        for f in rear_faces:
            f.normal_flip()

        # Calculate average normal for extrusion direction
        vector_mean = Vector((0, 0, 0))
        for f in selected_faces:
            vector_mean += f.normal
        vector_mean.normalize()

        # Update mesh before operator call
        bmesh.update_edit_mesh(obj.data)

        # Extrude using operator for better UV handling
        bpy.ops.mesh.extrude_region_move(
            TRANSFORM_OT_translate={"value": vector_mean}
        )

        # Refresh BMesh reference after operator
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()

        # Select adjacent faces
        selected_verts = [v for v in bm.verts if v.select]
        adj_faces = set()
        for v in selected_verts:
            for f in v.link_faces:
                if not f.select:
                    adj_faces.add(f)
        
        for f in adj_faces:
            f.select = True

        # Update and split
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.split()

        # Refresh BMesh
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        
        selected_faces = [f for f in bm.faces if f.select]

        # Merge extruded verts with rear duplicate verts
        for f in rear_faces:
            if f.is_valid:
                f.select = True
        
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.remove_doubles()

        # Deselect all
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bm.verts.ensure_lookup_table()
        
        bpy.ops.mesh.select_all(action='DESELECT')

        # Merge source and duplicate verts
        for v in src_sel_verts:
            if v.is_valid:
                v.select = True
        for v in dupl_src_verts:
            if v.is_valid:
                v.select = True
        
        bmesh.update_edit_mesh(obj.data)
        bpy.ops.mesh.remove_doubles()

        # Deselect all
        bm = bmesh.from_edit_mesh(obj.data)
        bm.faces.ensure_lookup_table()
        bpy.ops.mesh.select_all(action='DESELECT')

        # Select lead faces based on normal comparison
        for f in selected_faces:
            if f.is_valid:
                for n in lead_normals:
                    if (f.normal - n).length < 0.001:
                        f.select = True
                        break

        bmesh.update_edit_mesh(obj.data)

        # Move back slightly to avoid UV stretching
        bpy.ops.transform.translate(
            value=(0, 0, -0.999),
            orient_type='NORMAL',
            constraint_axis=(False, False, True)
        )

        # Invoke interactive transform
        bpy.ops.transform.translate(
            'INVOKE_DEFAULT',
            orient_type='NORMAL',
            constraint_axis=(False, False, True)
        )

        return {'FINISHED'}


def menu_func(self, context):
    """Add menu entry"""
    self.layout.operator(ExtrudeIntoClosedMesh.bl_idname, text="Extrude Into Closed Mesh")


addon_keymaps = []


def register():
    bpy.utils.register_class(ExtrudeIntoClosedMesh)
    bpy.types.VIEW3D_MT_edit_mesh_extrude.append(menu_func)

    # Add keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = kc.keymaps.new(name='Mesh', space_type='EMPTY')
        kmi = km.keymap_items.new(
            ExtrudeIntoClosedMesh.bl_idname,
            type='E',
            value='PRESS',
            ctrl=True,
            alt=True
        )
        addon_keymaps.append((km, kmi))


def unregister():
    # Remove keymap
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.types.VIEW3D_MT_edit_mesh_extrude.remove(menu_func)
    bpy.utils.unregister_class(ExtrudeIntoClosedMesh)


if __name__ == "__main__":
    register()