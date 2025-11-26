import bpy

bl_info = {
    "name": "Assign Material Asset to Selection",
    "description": "Assigns material assets to face selection via button in edit mode.",
    "author": "Jacob Falck",
    "blender": (5, 0, 0),
    "version": (2, 0, 0),
    "location": "Asset Browser > Header",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "Material"
}

def assign_material_to_selected_faces(obj, material, selected_faces):
    """Assign material to specific faces of an object"""
    if not obj or not material or not selected_faces:
        return False
    
    # Add material to object if not already present
    if material.name not in obj.data.materials:
        obj.data.materials.append(material)
    
    # Get material slot index
    mat_idx = None
    for i, slot in enumerate(obj.material_slots):
        if slot.material == material:
            mat_idx = i
            break
    
    if mat_idx is None:
        # Material was added but not found in slots, find it
        for i, slot in enumerate(obj.material_slots):
            if slot.material and slot.material.name == material.name:
                mat_idx = i
                break
    
    if mat_idx is None:
        print(f"Could not find material slot for {material.name}")
        return False
    
    # Switch to object mode to assign material
    current_mode = obj.mode
    if current_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Assign material to previously selected faces
    for face_idx in selected_faces:
        if face_idx < len(obj.data.polygons):
            obj.data.polygons[face_idx].material_index = mat_idx
    
    # Return to previous mode
    if current_mode != 'OBJECT':
        bpy.ops.object.mode_set(mode=current_mode)
    
    return True


class AssignMatAssetToSelection(bpy.types.Operator):
    """Assign selected material asset to face selection in edit mode"""
    bl_idname = "asset.assign_mat_asset_to_selection"
    bl_label = "Assign to Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Check if in edit mode and have selected assets
        if context.mode != "EDIT_MESH":
            return False
        
        # Verify we have at least one material asset selected
        if not hasattr(context, 'selected_assets') or not context.selected_assets:
            return False
            
        # Check if first selected asset is a material
        return context.selected_assets[0].id_type == 'MATERIAL'
    
    def execute(self, context):
        asset_representation = context.selected_assets[0]
        obj = context.object
        material_name = asset_representation.name
        
        # Store current face selection
        bpy.ops.object.mode_set(mode='OBJECT')
        selected_faces = [i for i, f in enumerate(obj.data.polygons) if f.select]
        bpy.ops.object.mode_set(mode='EDIT')
        
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}
        
        # Check if object already has the material
        material = None
        if material_name in obj.data.materials:
            material = bpy.data.materials.get(material_name)
        else:
            # Check if material exists in current file
            material = bpy.data.materials.get(material_name)
            
            if material is None:
                # Load the asset from library
                try:
                    blend_path = asset_representation.full_library_path
                    with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
                        if material_name in data_from.materials:
                            data_to.materials = [material_name]
                        else:
                            self.report({'ERROR'}, f"Material '{material_name}' not found in asset file")
                            return {'CANCELLED'}
                    
                    material = bpy.data.materials.get(material_name)
                    if material and material.asset_data:
                        material.asset_clear()
                except Exception as e:
                    self.report({'ERROR'}, f"Failed to load asset: {str(e)}")
                    return {'CANCELLED'}
            
            # Append material to object
            if material:
                obj.data.materials.append(material)
        
        # Assign to selected faces
        success = assign_material_to_selected_faces(obj, material, selected_faces)
        
        if success:
            self.report({'INFO'}, f"Assigned '{material_name}' to {len(selected_faces)} face(s)")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to assign material to selection")
            return {'CANCELLED'}


def display_button(self, context):
    """Draw the operator button in the asset browser header"""
    layout = self.layout
    
    # Only show if we have material assets selected
    if hasattr(context, 'selected_assets') and context.selected_assets:
        if context.selected_assets[0].id_type == 'MATERIAL':
            layout.operator(AssignMatAssetToSelection.bl_idname, icon='MATERIAL')


def register():
    bpy.utils.register_class(AssignMatAssetToSelection)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(display_button)


def unregister():
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(display_button)
    bpy.utils.unregister_class(AssignMatAssetToSelection)


if __name__ == "__main__":
    register()