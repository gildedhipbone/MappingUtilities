import bpy

bl_info = {
    "name": "Assign Per-Face Materials",
    "description": "Assigns a slot and material to every face in the object.",
    "author": "Jacob Falck",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Material"
}

class AUTOSLOTS_OT_auto_assign_slots(bpy.types.Operator):
    """Tooltip."""
    bl_idname = "facemat.assign_mat_per_face"
    bl_label = "Assign Materials to All Faces"
    bl_space_type = 'VIEW_3D'

    def execute(self, context):

        ob = context.object
        mesh = ob.data

        for face in mesh.polygons:
            if len(ob.material_slots) > 0:
                if ob.material_slots[face.material_index] is not None:
                    mat = ob.material_slots[face.material_index].material
            else:
                mat = bpy.data.materials.new(name="Empty Material")
            
            ob.data.materials.append(mat)
            face.material_index = len(ob.data.materials) - 1 
            
        return {"FINISHED"}

def draw_menu(self, context):
    self.layout.operator("facemat.assign_mat_per_face")

def register():
    bpy.utils.register_class(AUTOSLOTS_OT_auto_assign_slots)
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_menu)

def unregister():
    bpy.types.VIEW3D_MT_object_context_menu.append(draw_menu)
    bpy.utils.unregister_class(AUTOSLOTS_OT_auto_assign_slots)

if __name__ == "__main__":
    register()