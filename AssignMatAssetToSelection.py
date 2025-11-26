import bpy
import bmesh

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

def get_selected_face_indices(obj):
    """Get selected face indices using bmesh (more efficient)"""
    if not obj or obj.type != 'MESH':
        return []
    
    bm = bmesh.from_mesh(obj.data)
    bm.faces.ensure_lookup_table()
    selected_faces = [f.index for f in bm.faces if f.select]
    bm.free()
    return selected_faces

def assign_material_to_selected_faces(obj, material, selected_faces):
    """Assign material to specific faces of an object"""
    if not obj or obj.type != 'MESH' or not material or not selected_faces:
        return False
    
    # Add material if not present and get index
    if material.name not in obj.data.materials:
        obj.data.materials.append(material)
        mat_idx = len(obj.data.materials) - 1
    else:
        mat_idx = obj.data.materials.find(material.name)
    
    if mat_idx == -1:
        print(f"Failed to find material slot for {material.name}")
        return False
    
    # Store current mode
    current_mode = obj.mode
    needs_mode_switch = current_mode != 'OBJECT'
    
    if needs_mode_switch:
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # Assign material to faces
    mesh = obj.data
    for face_idx in selected_faces:
        if face_idx < len(mesh.polygons):
            mesh.polygons[face_idx].material_index = mat_idx
    
    # Restore mode
    if needs_mode_switch:
        bpy.ops.object.mode_set(mode=current_mode)
    
    return True

def load_material_from_asset(asset_representation):
    """Load material from asset library"""
    try:
        material_name = asset_representation.name
        blend_path = asset_representation.full_library_path
        
        if not blend_path:
            return None
            
        with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
            if material_name in data_from.materials:
                data_to.materials = [material_name]
            else:
                return None
        
        material = bpy.data.materials.get(material_name)
        if material and material.asset_data:
            material.asset_clear()
            
        return material
        
    except Exception as e:
        print(f"Error loading material from asset: {e}")
        return None

class AssignMatAssetToSelection(bpy.types.Operator):
    """Assign selected material asset to face selection in edit mode"""
    bl_idname = "asset.assign_mat_asset_to_selection"
    bl_label = "Assign to Selection"
    bl_options = {'REGISTER', 'UNDO'}
    
    @classmethod
    def poll(cls, context):
        # Check prerequisites
        if (context.mode != "EDIT_MESH" or 
            not context.object or 
            context.object.type != 'MESH'):
            return False
        
        # Check for selected assets
        if not hasattr(context, 'selected_assets') or not context.selected_assets:
            return False
            
        return context.selected_assets[0].id_type == 'MATERIAL'
    
    def execute(self, context):
        obj = context.object
        asset_representation = context.selected_assets[0]
        material_name = asset_representation.name
        
        # Get selected faces
        selected_faces = get_selected_face_indices(obj)
        if not selected_faces:
            self.report({'WARNING'}, "No faces selected")
            return {'CANCELLED'}
        
        # Find or load material
        material = (bpy.data.materials.get(material_name) or 
                   load_material_from_asset(asset_representation))
        
        if not material:
            self.report({'ERROR'}, f"Failed to load material '{material_name}'")
            return {'CANCELLED'}
        
        # Assign to faces
        success = assign_material_to_selected_faces(obj, material, selected_faces)
        
        if success:
            self.report({'INFO'}, f"Assigned '{material_name}' to {len(selected_faces)} face(s)")
            return {'FINISHED'}
        else:
            self.report({'ERROR'}, "Failed to assign material to selection")
            return {'CANCELLED'}

def display_button(self, context):
    """Draw the operator button in the asset browser header"""
    if (hasattr(context, 'selected_assets') and 
        context.selected_assets and 
        context.selected_assets[0].id_type == 'MATERIAL'):
        self.layout.operator(AssignMatAssetToSelection.bl_idname, icon='MATERIAL')

def register():
    bpy.utils.register_class(AssignMatAssetToSelection)
    bpy.types.ASSETBROWSER_MT_editor_menus.append(display_button)

def unregister():
    bpy.types.ASSETBROWSER_MT_editor_menus.remove(display_button)
    bpy.utils.unregister_class(AssignMatAssetToSelection)

if __name__ == "__main__":
    register()