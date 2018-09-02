
import multiprocessing

import bpy


def define_props():
    parset = bpy.types.ParticleSettings
    parset.mol_active = bpy.props.BoolProperty(name = "mol_active", description = "Activate molecular script for this particles system",default = False)
    parset.mol_refresh = bpy.props.BoolProperty(name = "mol_refresh", description = "Simple property used to refresh data in the process",default = True)
    parset.mol_density_active = bpy.props.BoolProperty(name="mol_density_active", description="Control particle weight by density",default = False)
    item = [("-1","custom","put your parameter below"),("1555","sand","1555kg per meter cu"),("1000","water","1000kg per meter cu"),("7800","iron","7800kg per meter cu")]
    parset.mol_matter = bpy.props.EnumProperty(items = item, description = "Choose a matter preset for density")
    parset.mol_density = bpy.props.FloatProperty(name = "mol_density", description = "Density of the matter kg/cube meter", default = 1000, min = 0.001)

    parset.mol_selfcollision_active = bpy.props.BoolProperty(name = "mol_selfcollision_active", description = "Activate self collsion between particles in the system",default = False)
    parset.mol_othercollision_active = bpy.props.BoolProperty(name = "mol_othercollision_active", description = "Activate collision with particles from others systems",default = False)
    parset.mol_friction = bpy.props.FloatProperty(name = "mol_friction", description = "Friction between particles at collision 0 = no friction , 1 = full friction",default = 0.005 , min = 0 , max = 1, precision=6, subtype='FACTOR')
    parset.mol_collision_damp = bpy.props.FloatProperty(name = "mol_collision_damp", description = "Damping between particles at collision 0 = bouncy , 1 = no collision",default = 0.005 , min = 0 , max = 1, precision=6, subtype='FACTOR')
    item = []
    for i in range(1,12):
        item.append((str(i),"Collision Group " + str(i),"collide only with group " + str(i) ))
    parset.mol_collision_group = bpy.props.EnumProperty(items = item, description = "Choose a collision group you want to collide with")

    parset.mol_links_active = bpy.props.BoolProperty(name = "mol_links_active", description = "Activate links between particles of this system",default = False)
    parset.mol_link_rellength = bpy.props.BoolProperty(name = "mol_link_rellength", description = "Activate search distance relative to particles radius",default = True)
    parset.mol_link_friction = bpy.props.FloatProperty(name = "mol_link_friction", description = "Friction in links , a kind of viscosity. Slow down tangent velocity. 0 = no friction , 1.0 = full of friction",min = 0,max = 1, default = 0.005, precision=6, subtype='FACTOR')
    parset.mol_link_length = bpy.props.FloatProperty(name = "mol_link_length", description = "Searching range to make a link between particles",min = 0, precision = 6, default = 1)
    parset.mol_link_tension = bpy.props.FloatProperty(name = "mol_link_tension", description = "Make link bigger or smaller than it's created (1 = normal , 0.9 = 10% smaller , 1.15 = 15% bigger)",min = 0, precision = 6, default = 1)
    parset.mol_link_tensionrand = bpy.props.FloatProperty(name = "mol_link_tensionrand", description = "Tension random",min = 0,max = 1, precision = 6, default = 0, subtype='FACTOR')
    parset.mol_link_max = bpy.props.IntProperty(name = "mol_link_max", description = "Maximum of links per particles",min = 0,default = 16)
    parset.mol_link_stiff = bpy.props.FloatProperty(name = "mol_link_stiff", description = "Stiffness of links between particles",min = 0,max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_link_stiffrand = bpy.props.FloatProperty(name = "mol_link_stiffrand", description = "Random variation for stiffness",min = 0 ,max = 1 ,default = 0, precision=6, subtype='FACTOR')
    parset.mol_link_stiffexp = bpy.props.IntProperty(name = "mol_link_stiffexp", description = "Give a exponent force to the spring links", default = 1, min = 1 , max = 10)
    parset.mol_link_damp = bpy.props.FloatProperty(name = "mol_link_damp", description = "Damping effect on spring links",min = 0,max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_link_damprand = bpy.props.FloatProperty(name = "mol_link_damprand", description = "Random variation on damping",min = 0 ,max = 1, default = 0, precision=6, subtype='FACTOR')
    parset.mol_link_broken = bpy.props.FloatProperty(name = "mol_link_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 6)
    parset.mol_link_brokenrand = bpy.props.FloatProperty(name = "mol_link_brokenrand", description = "Give a random variation to the stretch limit",min = 0 ,max = 1, default = 0, precision=6, subtype='FACTOR')

    parset.mol_link_samevalue = bpy.props.BoolProperty(name = "mol_link_samevalue", description = "When active , expansion and compression of the spring have same value",default = True)

    parset.mol_link_estiff = bpy.props.FloatProperty(name = "mol_link_estiff", description = "Expension stiffness of links between particles",min = 0,max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_link_estiffrand = bpy.props.FloatProperty(name = "mol_link_estiffrand", description = "Random variation for expansion stiffness",min = 0 ,max = 1 ,default = 0, precision=6, subtype='FACTOR')
    parset.mol_link_estiffexp = bpy.props.IntProperty(name = "mol_link_estiffexp", description = "Give a exponent force to the expension spring links", default = 1, min = 1 , max = 10)
    parset.mol_link_edamp = bpy.props.FloatProperty(name = "mol_link_edamp", description = "Damping effect on expension spring links",min = 0,max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_link_edamprand = bpy.props.FloatProperty(name = "mol_link_edamprand", description = "Random variation on expension damping",min = 0 ,max = 1, default = 0, precision=6, subtype='FACTOR')
    parset.mol_link_ebroken = bpy.props.FloatProperty(name = "mol_link_ebroken", description = "How much link can expand before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 6)
    parset.mol_link_ebrokenrand = bpy.props.FloatProperty(name = "mol_link_ebrokenrand", description = "Give a random variation to the expension stretch limit",min = 0 ,max = 1, default = 0, precision=6, subtype='FACTOR')

    item = []
    for i in range(1,12):
        item.append((str(i),"Relink Group " + str(i),"Relink only with group " + str(i) ))
    parset.mol_relink_group = bpy.props.EnumProperty(items = item, description = "Choose a group that new link are possible")        
    parset.mol_relink_chance = bpy.props.FloatProperty(name = "mol_relink_chance", description = "Chance of a new link are created on collision. 0 = off , 100 = 100% of chance",min = 0, max = 100, default = 0, precision=6)
    parset.mol_relink_chancerand = bpy.props.FloatProperty(name = "mol_relink_chancerand", description = "Give a random variation to the chance of new link", default = 0, min=0, max=1, precision=6, subtype='FACTOR')
    parset.mol_relink_tension = bpy.props.FloatProperty(name = "mol_relink_tension", description = "Make link bigger or smaller than it's created (1 = normal , 0.9 = 10% smaller , 1.15 = 15% bigger)",min = 0, precision = 6, default = 1)
    parset.mol_relink_tensionrand = bpy.props.FloatProperty(name = "mol_relink_tensionrand", description = "Tension random",min = 0,max = 1, default = 0, precision=6, subtype='FACTOR')
    parset.mol_relink_max = bpy.props.IntProperty(name = "mol_relink_max", description = "Maximum of links per particles",min = 0,default = 16)
    parset.mol_relink_stiff = bpy.props.FloatProperty(name = "mol_relink_stiff", description = "Stiffness of links between particles",min = 0,max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_relink_stiffrand = bpy.props.FloatProperty(name = "mol_relink_stiffrand", description = "Random variation for stiffness",min = 0, max = 1 ,default = 0, precision=6, subtype='FACTOR')
    parset.mol_relink_stiffexp = bpy.props.IntProperty(name = "mol_relink_stiffexp", description = "Give a exponent force to the spring links",min = 1, max = 10, default = 1)
    parset.mol_relink_damp = bpy.props.FloatProperty(name = "mol_relink_damp", description = "Damping effect on spring links",min = 0, max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_relink_damprand = bpy.props.FloatProperty(name = "mol_relink_damprand", description = "Random variation on damping",min = 0 , max = 1, default = 0, precision=6, subtype='FACTOR')
    parset.mol_relink_broken = bpy.props.FloatProperty(name = "mol_relink_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 6)
    parset.mol_relink_brokenrand = bpy.props.FloatProperty(name = "mol_relink_brokenrand", description = "Give a random variation to the stretch limit",min = 0, max = 1, default = 0, precision=6, subtype='FACTOR')

    parset.mol_relink_samevalue = bpy.props.BoolProperty(name = "mol_relink_samevalue", description = "When active , expansion and compression of the spring have same value",default = True)

    parset.mol_relink_estiff = bpy.props.FloatProperty(name = "mol_relink_estiff", description = "Stiffness of links expension between particles",min = 0,max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_relink_estiffrand = bpy.props.FloatProperty(name = "mol_relink_estiffrand", description = "Random variation for expension stiffness",min = 0, max = 1 ,default = 0, precision=6, subtype='FACTOR')
    parset.mol_relink_estiffexp = bpy.props.IntProperty(name = "mol_relink_estiffexp", description = "Give a exponent force to the spring links",min = 1, max = 10, default = 1)
    parset.mol_relink_edamp = bpy.props.FloatProperty(name = "mol_relink_edamp", description = "Damping effect on expension spring links",min = 0, max = 1, default = 1, precision=6, subtype='FACTOR')
    parset.mol_relink_edamprand = bpy.props.FloatProperty(name = "mol_relink_deamprand", description = "Random variation on damping",min = 0 , max = 1, default = 0, precision=6, subtype='FACTOR')
    parset.mol_relink_ebroken = bpy.props.FloatProperty(name = "mol_relink_ebroken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 6)
    parset.mol_relink_ebrokenrand = bpy.props.FloatProperty(name = "mol_relink_ebrokenrand", description = "Give a random variation to the stretch limit",min = 0, max = 1, default = 0, precision=6, subtype='FACTOR')

    parset.mol_var1 = bpy.props.IntProperty(name = "mol_var1", description = "Current number of particles to calculate substep",min = 1, default = 1000)
    parset.mol_var2 = bpy.props.IntProperty(name = "mol_var2", description = "Current substep",min = 1, default = 4)
    parset.mol_var3 = bpy.props.IntProperty(name = "mol_var3", description = "Targeted number of particles you want to increase or decrease from current system to calculate substep you need to achieve similar effect",min = 1, default = 1000)
    parset.mol_bakeuv = bpy.props.BoolProperty(name = "mol_bakeuv", description = "Bake uv when finish",default = False)

    bpy.types.Scene.mol_timescale_active = bpy.props.BoolProperty(name = "mol_timescale_active", description = "Activate TimeScaling",default = False)
    bpy.types.Scene.timescale = bpy.props.FloatProperty(name = "timescale", description = "SpeedUp or Slow down the simulation with this multiplier", default = 1)
    bpy.types.Scene.mol_substep = bpy.props.IntProperty(name = "mol_substep", description = "mol_substep. Higher equal more stable and accurate but more slower",min = 0, max = 900, default = 4)
    bpy.types.Scene.mol_bake = bpy.props.BoolProperty(name = "mol_bake", description = "Bake simulation when finish",default = True)
    bpy.types.Scene.mol_render = bpy.props.BoolProperty(name = "mol_render", description = "Start rendering animation when simulation is finish. WARNING: It's freeze blender until render is finish.",default = False)
    bpy.types.Scene.mol_cpu = bpy.props.IntProperty(name = "mol_cpu", description = "Numbers of cpu's included for process the simulation", default = multiprocessing.cpu_count(),min = 1,max =multiprocessing.cpu_count())

    bpy.types.Scene.mol_exportdata = []
    bpy.types.Scene.mol_minsize = bpy.props.FloatProperty()
    bpy.types.Scene.mol_simrun = bpy.props.BoolProperty(default=False)
    bpy.types.Scene.mol_timeremain = bpy.props.StringProperty()
    bpy.types.Scene.mol_old_endframe = bpy.props.IntProperty()
    bpy.types.Scene.mol_newlink = bpy.props.IntProperty()
    bpy.types.Scene.mol_deadlink = bpy.props.IntProperty()
    bpy.types.Scene.mol_totallink = bpy.props.IntProperty()
    bpy.types.Scene.mol_totaldeadlink = bpy.props.IntProperty()
    bpy.types.Scene.mol_objuvbake = bpy.props.StringProperty()
    bpy.types.Scene.mol_psysuvbake = bpy.props.StringProperty()
    bpy.types.Scene.mol_stime = bpy.props.FloatProperty()
