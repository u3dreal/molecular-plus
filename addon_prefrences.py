import bpy
from os.path import basename, dirname
from bpy.types import AddonPreferences
from bpy.props import IntProperty, BoolProperty


class MolecularAddonPreferences(AddonPreferences):
    bl_idname = __package__

    log_size: IntProperty(
        name='Onscreen status size',
        default=25,
        min=1,
        max=200
    ) # type: ignore

    use_retina: BoolProperty(
        name='retina display',
        default=False
    ) # type: ignore

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "log_size")
        row.prop(self, "use_retina")


pref_classes = (MolecularAddonPreferences)
