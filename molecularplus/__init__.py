# ====================== BEGIN GPL LICENSE BLOCK ======================
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ======================= END GPL LICENSE BLOCK ========================
bl_info = {
    "name": "Molecular+",
    "author":
        "Jean-Francois Gallant (PyroEvil), "
        "Pavel_Blend, "
        "Martin Felke (scorpion81), "
        "Gregor Quade (u3dreal)",
    "version": (1, 1, 10),
    "blender": (2, 80, 0),
    "location": "Properties editor > Physics Tab",
    "description":
        "Addon for calculating collisions "
        "and for creating links between particles",
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "http://q3de.com/research/molecular/",
    "tracker_url": "https://discord.gg/tAwvNEAfA3",
    "category": "Physics"
}


def register():

    import bpy
    from . import properties, ui, operators, creators, addon_prefrences

    properties.define_props()

    for operator in operators.operator_classes:
        bpy.utils.register_class(operator)

    for panel in ui.panel_classes:
        bpy.utils.register_class(panel)

    for panel in creators.create_classes:
        bpy.utils.register_class(panel)

    bpy.utils.register_class(addon_prefrences.pref_classes)

    bpy.types.PHYSICS_PT_add.append(ui.append_to_PHYSICS_PT_add_panel)


def unregister():

    import bpy
    from . import ui, operators, creators, addon_prefrences

    bpy.types.PHYSICS_PT_add.remove(ui.append_to_PHYSICS_PT_add_panel)

    for operator in reversed(operators.operator_classes):
        bpy.utils.unregister_class(operator)

    for panel in reversed(ui.panel_classes):
        bpy.utils.unregister_class(panel)

    for panel in reversed(creators.create_classes):
        bpy.utils.unregister_class(panel)

    bpy.utils.unregister_class(addon_prefrences.pref_classes)

if __name__ == "__main__":
    register()
