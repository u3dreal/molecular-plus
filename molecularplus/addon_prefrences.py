import bpy
from os.path import basename, dirname
from bpy.types import AddonPreferences
from bpy.props import IntProperty


class MolecularAddonPreferences(AddonPreferences):
    bl_idname = __package__

    log_size: IntProperty(
        name='Onscreen status size',
        default=25,
        min=1,
        max=200
    )

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "log_size")


pref_classes = (MolecularAddonPreferences)
