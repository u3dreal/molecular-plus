import bpy
#import sys

def get_object(context, obj):
    depsgraph = context.evaluated_depsgraph_get()
    return obj.evaluated_get(depsgraph)


def destroy_caches(obj):
    for psys in obj.particle_systems:
        # attempt to destroy cache prior to resimulation
        # by provoking an internal RNA update call, this will also update the psys for get_object
        if psys.settings.mol_active:
            step = psys.point_cache.frame_step
            psys.point_cache.frame_step = step
            
            
def update_progress(job_title, progress):
    length = 50 # modify this to change the length
    block = int(round(length*progress))
    msg = "\r{0}: [{1}] {2}%".format(job_title, "*"*block + "-"*(length-block), round(progress*100, 2))
    bpy.context.scene.mol_progress = msg[1:]
    #sys.stdout.write(msg)
