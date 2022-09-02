import bpy
import bmesh
from mathutils import Vector
from bmesh.types import BMVert

bl_info = {
    "name": "Extrude Into Object",
    "description": "Extrude selected faces into closed objects.",
    "author": "Jacob Falck",
    "blender": (3, 1, 0),
    "version": (1, 0, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "View 3D"
}

class ExtrudeIntoObject(bpy.types.Operator):
    """Tooltip."""
    bl_idname = "view3d.extrude_into_object"
    bl_label = "Extrude Into Object Addon"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):
        objs = [obj for obj in bpy.context.selected_objects if obj.type == "MESH"]
        # Original list of objects; to filter out new ones down below.
        org_obj_list = {obj.name for obj in objs}
        bpy.ops.object.mode_set(mode="OBJECT")
        sel_objs = {}

        for obj in objs:
            sel_polys = [p for p in obj.data.polygons if p.select]

            if len(sel_polys) > 0:
                sel_objs[obj] = sel_polys

        if len(sel_objs) == 0:
            self.report({"INFO"}, "No face selected, aborting.")
            return {"FINISHED"}
        print(sel_objs)

        for obj in sel_objs:
            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.ops.object.mode_set(mode="OBJECT")

            context.view_layer.objects.active = obj
            # Create new face map and set it as active.
            obj.face_maps.new(name=str(obj.name))
            obj.face_maps.active_index = obj.face_maps[str(obj.name)].index
            # I'M SURE ITS THIS PIECE OF SHIT THAT WONT UPDATE FOR WHATEVER REASON.
            for poly in sel_objs[obj]:
                poly.select = True

            bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.object.face_map_assign()

        for obj in sel_objs:
            context.view_layer.objects.active = obj
            #bpy.ops.object.mode_set(mode="EDIT")
            bpy.ops.mesh.select_all(action = 'DESELECT')
            # Set the face selection face map to active.
            obj.face_maps.active_index = obj.face_maps[str(obj.name)].index
            # Select the faces of the active face map.
            bpy.ops.object.face_map_select()
            
            bm = bmesh.from_edit_mesh(obj.data)
            bm.faces.ensure_lookup_table()

            for f in bm.faces:
                if f.select == True:
                    print(f)

            selected_faces = [f for f in bm.faces if f.select]
            print("sel faces: ", selected_faces)
            selected_verts = [v for v in bm.verts if v.select]

            # extrude_region_move removes internal faces, so we have to create duplicates. 
            # Duplicate #1.
            ret = bmesh.ops.duplicate(bm, geom=selected_faces)
            dupl = ret["geom"]
            del ret
            dupl_src_verts = [ele for ele in dupl if isinstance(ele, bmesh.types.BMVert)]
            # Duplicate #2 to fill the bottom of the new object.
            ret = bmesh.ops.duplicate(bm, geom=selected_faces)
            dupl = ret["geom"]
            del ret
            dupl_new_face = [ele for ele in dupl if isinstance(ele, bmesh.types.BMFace)]
            for f in dupl_new_face:
                f.normal_flip()
            # Sloppy, but it'll have to do for now.
            vector_mean = Vector((0,0,0))
            for f in selected_faces:
                vector_mean += f.normal
            vector_mean /= len(selected_faces)

            bpy.ops.mesh.extrude_region_move(TRANSFORM_OT_translate={"value":vector_mean})
            # extrude_region_move removes the original face, selects the new one.
            top_faces = [f for f in bm.faces if f.select]
            bpy.ops.mesh.select_all(action = 'DESELECT')
            # # Merge duplicate #1 to the original geometry.
            for v in dupl_src_verts:
                v.select = True
            for v in selected_verts:
                v.select = True
            bpy.ops.mesh.remove_doubles()
            bpy.ops.mesh.select_all(action = 'DESELECT')
            # The selection which to separate into new object.
            for f in top_faces:
                f.select = True
            adj_faces = set(v for v in bm.verts if v.select for v in v.link_faces if not v.select)
            for f in adj_faces:
                f.select = True
            for f in dupl_new_face:
                f.select = True
            
            bpy.ops.object.face_map_remove()

            bpy.ops.mesh.separate()
            bpy.ops.mesh.select_all(action = 'DESELECT')

        # To-do:
        # Select top faces in new objects, optionally activate shrink_fatten.
        # Set original active object as the new active object.
        new_objs = []
        # Add new objects to selected objects.
        for obj in context.selected_objects:
            if obj and obj.name not in org_obj_list:
                obj.select_set(True)
                new_objs.append(obj)

        bpy.ops.object.mode_set(mode="OBJECT")
        bpy.ops.object.mode_set(mode="EDIT")

        for obj in new_objs:
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bm = bmesh.from_edit_mesh(obj.data)
            for v in bm.verts:
                v.select = True
            bpy.ops.mesh.remove_doubles()
        # Dunno why I have to do this, but it saves a lot of trouble.
        bpy.ops.object.mode_set(mode="OBJECT")        
        bpy.ops.object.mode_set(mode="EDIT")      

        return {"FINISHED"}

addon_keymaps = []

def register():
    bpy.utils.register_class(ExtrudeIntoObject)

    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(ExtrudeIntoObject.bl_idname, type="E", value="PRESS", ctrl=True, alt=True)
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(ExtrudeIntoObject)

if __name__ == "__main__":
    register()