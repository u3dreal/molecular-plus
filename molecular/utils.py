
import bpy


def is_blender_28():
    return bpy.data.version[0] == 2 and bpy.data.version[1] >= 80

def get_object(context, obj):
    if is_blender_28():
        depsgraph = context.evaluated_depsgraph_get()
        return obj.evaluated_get(depsgraph)
    else:
        return obj

def destroy_caches(obj):
    for psys in obj.particle_systems:
        #attempt to destroy cache prior to resimulation
        #by provoking an internal RNA update call, this will also update the psys for get_object
        if psys.settings.mol_active:
            step = psys.point_cache.frame_step
            psys.point_cache.frame_step = step
