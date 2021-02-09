import bpy


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
            
def set_substeps():
    parcount = 0
    context = bpy.context
    scene = context.scene
    for obj in bpy.data.objects:
        if obj.particle_systems.active != None:
            psys = get_object(context, obj).particle_systems.active
            parcount += len(psys.particles)
            
    diff = (psys.settings.mol_var3 / psys.settings.mol_var1)
    factor = (parcount**(1/3) / psys.settings.mol_var1**(1/3))
    newsubstep = int(round(factor * psys.settings.mol_var2))
        
    scene.mol_substep = newsubstep
    scene.mol_parnum = parcount
    return 
