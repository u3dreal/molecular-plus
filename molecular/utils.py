
import bpy


def is_blender_28():
    return bpy.data.version[0] == 2 and bpy.data.version[1] >= 80

def get_object(context, obj, update=True):
    if is_blender_28():
        if update:
            context.view_layer.update()
        depsgraph = context.evaluated_depsgraph_get()
        return obj.evaluated_get(depsgraph)
    else:
        return obj
