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
    mol = bpy.context.scene
    length = 50 # modify this to change the length
    block = int(round(length*progress))
    mol.mol_progress = "|" + (">"*block) + ("--"*(length-block)) + str(round(progress*100, 2)) + "%" + "|" + "\n" + "Time remain : " + str(mol.mol_timeremain) + "\n" + "Total links : " + str(mol.mol_totallink) + "\n" + "Dead links : " + str(mol.mol_deadlink) + "\n" + "New links : " + str(mol.mol_newlink) + "\n" + "Total dead links : " + str(mol.mol_totaldeadlink) + "\n" + "Status : " + job_title