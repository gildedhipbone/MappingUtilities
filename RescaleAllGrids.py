from distutils.sysconfig import customize_compiler
import bpy
from bpy.types import Operator, AddonPreferences
from bpy.props import FloatProperty, StringProperty

bl_info = {
    "name": "Rescale All Grids",
    "description": "Manually rescale all grids.", 
    "author": "Jacob Falck",
    "blender": (4, 0, 0),
    "version": (1, 0, 0),
    "location": "",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "View 3D"
}

class RescaleGridsAddonPreferences(AddonPreferences):
    bl_idname = __name__

    custom_multiplier: FloatProperty(
        name="Grid Scale Multiplier",
        default=1.0
    )
    custom_unit: StringProperty(
        name="Unit Name",
        default=""
    )

    def draw(self, context):
        layout = self.layout
        #layout.label(text="")
        layout.prop(self, "custom_multiplier")
        layout.prop(self, "custom_unit")

class RescaleGrids(bpy.types.Operator):
    """Tooltip."""
    bl_idname = "view3d.rescale_grids"
    bl_label = "Rescale Grids Addon"
    bl_space_type = 'VIEW_3D'
    
    grid_scalar: FloatProperty(default=1.0)
    grid_scale: FloatProperty()
    # Set to custom multiplier to whatever you want 1 Blender Unit to represent.
    # This should be exposed in the add-on settings. Also add an option to set a custom unit extension, e.g. "px".

    def execute(self, context):
        preferences = context.preferences
        addon_prefs = preferences.addons[__name__].preferences

        custom_multiplier = addon_prefs.custom_multiplier
        custom_name = addon_prefs.custom_unit

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if not area.type == "VIEW_3D":
                    continue

                for s in area.spaces:
                    if s.type == "VIEW_3D":
                        s.overlay.grid_scale *= self.grid_scalar
                        self.grid_scale = s.overlay.grid_scale
                        break
        # This should be drawn in the display port.
        self.report({"INFO"}, f"Grid scale: {(self.grid_scale * custom_multiplier)} {custom_name}")

        return {"FINISHED"}

addon_keymaps = []

def register():
    bpy.utils.register_class(RescaleGridsAddonPreferences)
    bpy.utils.register_class(RescaleGrids)
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(RescaleGrids.bl_idname, type="NUMPAD_MINUS", value="PRESS")
        kmi.properties.grid_scalar = 0.5
        addon_keymaps.append((km, kmi))
        km = wm.keyconfigs.addon.keymaps.new(name="3D View", space_type="VIEW_3D")
        kmi = km.keymap_items.new(RescaleGrids.bl_idname, "NUMPAD_PLUS", "PRESS")
        kmi.properties.grid_scalar = 2.0
        addon_keymaps.append((km, kmi))

def unregister():
    for km, kmi in addon_keymaps:
        km.keymap_items.remove(kmi)
    addon_keymaps.clear()

    bpy.utils.unregister_class(RescaleGrids)
    bpy.utils.register_class(RescaleGridsAddonPreferences)

if __name__ == "__main__":
    register()