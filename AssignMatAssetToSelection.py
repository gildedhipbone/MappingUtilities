from asyncio.windows_events import NULL
import bpy

bl_info = {
    "name": "Assign Material Asset to Selection",
    "description": "Assigns the selected material asset to the current face selection.",
    "author": "Jacob Falck",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Material"
}

class AssignMatAssetToSelection(bpy.types.Operator):
    """Tooltip."""
    bl_idname = "asset.assign_mat_asset_to_selection"
    bl_label = "Assign to Selection"
    bl_space_type = 'VIEW_3D'

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def execute(self, context):

        if len(context.selected_assets) > 0 and context.selected_assets[0].id_type == "MATERIAL":
            asset_representation = context.selected_assets[0]
            ob = context.object

            # NOTE: Hooking into asset browser drag and drop won't be possible until
            # https://projects.blender.org/blender/blender/pulls/113658
            # is implemented. Also, context.selected_assets is only available in File context, so we
            # can't use the edit/object context menus. Hence, the ugly button.

            # Does our object have the material?
            if not ob.data.materials.get(asset_representation.name):
                # If our file already contains the material, append it to our object.
                if bpy.data.materials.get(asset_representation.name):
                    ob.data.materials.append(bpy.data.materials.get(asset_representation.name))
                else:
                    # Load the asset file.
                    blendpath = asset_representation.full_library_path
                    with bpy.data.libraries.load(blendpath, link=False) as (data_from, data_to):
                        data_to.materials = [asset_representation.name]
                    # Clear asset mark and append it to our object.
                    bpy.data.materials.get(asset_representation.name).asset_clear()
                    ob.data.materials.append(bpy.data.materials.get(asset_representation.name))
            
            # Get the slot index of our material.        
            mat_idx = None
            for i in ob.material_slots:
                if i.name == asset_representation.name:
                    mat_idx = i.slot_index
                    
            # Can't assign materials in edit mode lol
            bpy.ops.object.mode_set(mode="OBJECT")

            for face in ob.data.polygons:
                if face.select:
                    face.material_index = mat_idx
            
            bpy.ops.object.mode_set(mode="EDIT")

            return {"FINISHED"}
        
        else:
            return {"CANCELLED"}

def display_button(self, context):
    self.layout.operator(AssignMatAssetToSelection.bl_idname)
    #self.layout.enabled = False

def register():
    bpy.utils.register_class(AssignMatAssetToSelection)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(display_button)

def unregister():
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(display_button)
    bpy.utils.unregister_class(AssignMatAssetToSelection)

if __name__ == "__main__":
    register()