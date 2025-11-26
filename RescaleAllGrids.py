# pyright: reportInvalidTypeForm=false

import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import FloatProperty, StringProperty, BoolProperty

bl_info = {
    "name": "Rescale All Grids",
    "description": "Manually rescale all grids with custom unit scaling",
    "author": "Jacob Falck",
    "blender": (5, 0, 0),
    "version": (2, 0, 0),
    "location": "View3D > Numpad +/- (customizable in preferences)",
    "warning": "",
    "doc_url": "",
    "tracker_url": "",
    "category": "3D View"
}


class RescaleGridsAddonPreferences(AddonPreferences):
    bl_idname = __name__

    custom_multiplier: FloatProperty(
        name="Grid Scale Multiplier",
        description="Multiplier for converting Blender units to custom units",
        default=1.0,
        min=0.001,
        soft_max=1000.0
    )

    custom_unit: StringProperty(
        name="Unit Name",
        description="Custom unit name to display (e.g., 'px', 'm', 'ft')",
        default=""
    )

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        box = layout.box()
        box.label(text="Grid Scale Settings:", icon='GRID')
        box.prop(self, "custom_multiplier")
        box.prop(self, "custom_unit")
        
        layout.separator()
        layout.label(text="Keyboard Shortcuts:", icon='EVENT_SPACEKEY')
        col = layout.column(align=True)
        col.label(text="Numpad + : Scale grid up (2x)")
        col.label(text="Numpad - : Scale grid down (0.5x)")
        col.label(text="Numpad * : Reset scale")


class RescaleGrids(Operator):
    """Rescale viewport grids with custom unit conversion"""
    bl_idname = "view3d.rescale_grids"
    bl_label = "Rescale Grids"
    bl_options = {'REGISTER'}

    grid_scalar: FloatProperty(
        name="Grid Scale",
        default=1.0,
        min=0.001,
        options={'HIDDEN', 'SKIP_SAVE'}
    )

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences
        custom_multiplier = addon_prefs.custom_multiplier
        custom_name = addon_prefs.custom_unit

        grid_scale_value = None
        grid_count = 0

        # Update all 3D viewports
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type != 'VIEW_3D':
                    continue
                
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.grid_scale *= self.grid_scalar
                        grid_scale_value = space.overlay.grid_scale
                        grid_count += 1
                        break

        if grid_scale_value is None:
            self.report({'WARNING'}, "No 3D View found")
            return {'CANCELLED'}

        # Display the actual grid scale
        unit_suffix = f" {custom_name}" if custom_name else " BU"
        
        # Report result showing the grid scale value (not the scalar multiplier)
        self.report(
            {'INFO'},
            f"Grid scale: {grid_scale_value:.3f}{unit_suffix} ({grid_count} viewport{'s' if grid_count > 1 else ''})"
        )

        return {'FINISHED'}


class ResetGrids(Operator):
    """Reset all viewport grids to default scale (1.0)"""
    bl_idname = "view3d.reset_grids"
    bl_label = "Reset Grid Scale"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        grid_count = 0

        # Reset all 3D viewports
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type != 'VIEW_3D':
                    continue
                
                for space in area.spaces:
                    if space.type == 'VIEW_3D':
                        space.overlay.grid_scale = 1.0
                        grid_count += 1
                        break

        if grid_count == 0:
            self.report({'WARNING'}, "No 3D View found")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Reset grid scale to 1.0 ({grid_count} viewport{'s' if grid_count > 1 else ''})")
        return {'FINISHED'}


addon_keymaps = []


def register():
    bpy.utils.register_class(RescaleGridsAddonPreferences)
    bpy.utils.register_class(RescaleGrids)
    bpy.utils.register_class(ResetGrids)

    # Add keymap
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    
    if kc:
        # Scale down (Numpad -)
        km = kc.keymaps.new(name="3D View", space_type='VIEW_3D')
        kmi = km.keymap_items.new(
            RescaleGrids.bl_idname,
            type='NUMPAD_MINUS',
            value='PRESS'
        )
        kmi.properties.grid_scalar = 0.5
        addon_keymaps.append((km, kmi))

        # Scale up (Numpad +)
        kmi = km.keymap_items.new(
            RescaleGrids.bl_idname,
            type='NUMPAD_PLUS',
            value='PRESS'
        )
        kmi.properties.grid_scalar = 2.0
        addon_keymaps.append((km, kmi))

        # Reset (Numpad * - optional)
        kmi = km.keymap_items.new(
            ResetGrids.bl_idname,
            type='NUMPAD_ASTERIX',
            value='PRESS'
        )
        addon_keymaps.append((km, kmi))


def unregister():
    # Remove keymaps
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    # Unregister classes
    bpy.utils.unregister_class(ResetGrids)
    bpy.utils.unregister_class(RescaleGrids)
    bpy.utils.unregister_class(RescaleGridsAddonPreferences)


if __name__ == "__main__":
    register()