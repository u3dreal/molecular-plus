
import bpy


def is_blender_28():
    return bpy.data.version[0] == 2 and bpy.data.version[1] >= 80
