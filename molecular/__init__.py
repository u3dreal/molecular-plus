#====================== BEGIN GPL LICENSE BLOCK ======================
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
#======================= END GPL LICENSE BLOCK ========================

bl_info = {
    "name": "Molecular script",
    "author": "Jean-Francois Gallant(PyroEvil)",
    "version": (1, 0, 1),
    "blender": (2, 6, 8),
    "location": "Properties editor > Particles Tabs",
    "description": ("Molecular script"),
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "http://pyroevil.com/molecular-script-docs/",
    "tracker_url": "http://pyroevil.com/contact/" ,
    "category": "Object"}
    
import bpy
try:
    from molecular import cmolcore
except:
    print("cmolcore not working")
from random import random
from math import pi
from mathutils import Vector
from mathutils.geometry import barycentric_transform as barycentric
import imp
from time import clock,sleep,strftime,gmtime
import pstats, cProfile
import multiprocessing

mol_simrun = False

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
    parset.mol_friction = bpy.props.FloatProperty(name = "mol_friction", description = "Friction between particles at collision 0 = no friction , 1 = full friction",default = 0.005 , min = 0 , max = 1)
    parset.mol_collision_damp = bpy.props.FloatProperty(name = "mol_collision_damp", description = "Damping between particles at collision 0 = bouncy , 1 = no collision",default = 0.005 , min = 0 , max = 1)
    item = []
    for i in range(1,12):
        item.append((str(i),"Collision Group " + str(i),"collide only with group " + str(i) ))
    parset.mol_collision_group = bpy.props.EnumProperty(items = item, description = "Choose a collision group you want to collide with")
    
    parset.mol_links_active = bpy.props.BoolProperty(name = "mol_links_active", description = "Activate links between particles of this system",default = False)
    parset.mol_link_rellength = bpy.props.BoolProperty(name = "mol_link_rellength", description = "Activate search distance relative to particles radius",default = True)
    parset.mol_link_friction = bpy.props.FloatProperty(name = "mol_link_friction", description = "Friction in links , a kind of viscosity. Slow down tangent velocity. 0 = no friction , 1.0 = full of friction",min = 0,max = 1, default = 0.005)
    parset.mol_link_length = bpy.props.FloatProperty(name = "mol_link_length", description = "Searching range to make a link between particles",min = 0, precision = 6, default = 1)
    parset.mol_link_tension = bpy.props.FloatProperty(name = "mol_link_tension", description = "Make link bigger or smaller than it's created (1 = normal , 0.9 = 10% smaller , 1.15 = 15% bigger)",min = 0, precision = 3, default = 1)
    parset.mol_link_tensionrand = bpy.props.FloatProperty(name = "mol_link_tensionrand", description = "Tension random",min = 0,max = 1, precision = 3, default = 0)
    parset.mol_link_max = bpy.props.IntProperty(name = "mol_link_max", description = "Maximum of links per particles",min = 0,default = 16)
    parset.mol_link_stiff = bpy.props.FloatProperty(name = "mol_link_stiff", description = "Stiffness of links between particles",min = 0,max = 1, default = 1)
    parset.mol_link_stiffrand = bpy.props.FloatProperty(name = "mol_link_stiffrand", description = "Random variation for stiffness",min = 0 ,max = 1 ,default = 0)
    parset.mol_link_stiffexp = bpy.props.IntProperty(name = "mol_link_stiffexp", description = "Give a exponent force to the spring links", default = 1, min = 1 , max = 10)
    parset.mol_link_damp = bpy.props.FloatProperty(name = "mol_link_damp", description = "Damping effect on spring links",min = 0,max = 1, default = 1)
    parset.mol_link_damprand = bpy.props.FloatProperty(name = "mol_link_damprand", description = "Random variation on damping",min = 0 ,max = 1, default = 0)
    parset.mol_link_broken = bpy.props.FloatProperty(name = "mol_link_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 3)
    parset.mol_link_brokenrand = bpy.props.FloatProperty(name = "mol_link_brokenrand", description = "Give a random variation to the stretch limit",min = 0 ,max = 1, default = 0)
    
    parset.mol_link_samevalue = bpy.props.BoolProperty(name = "mol_link_samevalue", description = "When active , expansion and compression of the spring have same value",default = True)
    
    parset.mol_link_estiff = bpy.props.FloatProperty(name = "mol_link_estiff", description = "Expension stiffness of links between particles",min = 0,max = 1, default = 1)
    parset.mol_link_estiffrand = bpy.props.FloatProperty(name = "mol_link_estiffrand", description = "Random variation for expansion stiffness",min = 0 ,max = 1 ,default = 0)
    parset.mol_link_estiffexp = bpy.props.IntProperty(name = "mol_link_estiffexp", description = "Give a exponent force to the expension spring links", default = 1, min = 1 , max = 10)
    parset.mol_link_edamp = bpy.props.FloatProperty(name = "mol_link_edamp", description = "Damping effect on expension spring links",min = 0,max = 1, default = 1)
    parset.mol_link_edamprand = bpy.props.FloatProperty(name = "mol_link_edamprand", description = "Random variation on expension damping",min = 0 ,max = 1, default = 0)
    parset.mol_link_ebroken = bpy.props.FloatProperty(name = "mol_link_ebroken", description = "How much link can expand before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 3)
    parset.mol_link_ebrokenrand = bpy.props.FloatProperty(name = "mol_link_ebrokenrand", description = "Give a random variation to the expension stretch limit",min = 0 ,max = 1, default = 0)
    
    
    item = []
    for i in range(1,12):
        item.append((str(i),"Relink Group " + str(i),"Relink only with group " + str(i) ))
    parset.mol_relink_group = bpy.props.EnumProperty(items = item, description = "Choose a group that new link are possible")        
    parset.mol_relink_chance = bpy.props.FloatProperty(name = "mol_relink_chance", description = "Chance of a new link are created on collision. 0 = off , 100 = 100% of chance",min = 0, max = 100, default = 0)
    parset.mol_relink_chancerand = bpy.props.FloatProperty(name = "mol_relink_chancerand", description = "Give a random variation to the chance of new link", default = 0)
    parset.mol_relink_tension = bpy.props.FloatProperty(name = "mol_relink_tension", description = "Make link bigger or smaller than it's created (1 = normal , 0.9 = 10% smaller , 1.15 = 15% bigger)",min = 0, precision = 3, default = 1)
    parset.mol_relink_tensionrand = bpy.props.FloatProperty(name = "mol_relink_tensionrand", description = "Tension random",min = 0,max = 1, precision = 3, default = 0)
    parset.mol_relink_max = bpy.props.IntProperty(name = "mol_relink_max", description = "Maximum of links per particles",min = 0,default = 16)
    parset.mol_relink_stiff = bpy.props.FloatProperty(name = "mol_relink_stiff", description = "Stiffness of links between particles",min = 0,max = 1, default = 1)
    parset.mol_relink_stiffrand = bpy.props.FloatProperty(name = "mol_relink_stiffrand", description = "Random variation for stiffness",min = 0, max = 1 ,default = 0)
    parset.mol_relink_stiffexp = bpy.props.IntProperty(name = "mol_relink_stiffexp", description = "Give a exponent force to the spring links",min = 1, max = 10, default = 1)
    parset.mol_relink_damp = bpy.props.FloatProperty(name = "mol_relink_damp", description = "Damping effect on spring links",min = 0, max = 1, default = 1)
    parset.mol_relink_damprand = bpy.props.FloatProperty(name = "mol_relink_damprand", description = "Random variation on damping",min = 0 , max = 1, default = 0)
    parset.mol_relink_broken = bpy.props.FloatProperty(name = "mol_relink_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 3)
    parset.mol_relink_brokenrand = bpy.props.FloatProperty(name = "mol_relink_brokenrand", description = "Give a random variation to the stretch limit",min = 0, max = 1, default = 0)

    parset.mol_relink_samevalue = bpy.props.BoolProperty(name = "mol_relink_samevalue", description = "When active , expansion and compression of the spring have same value",default = True)

    parset.mol_relink_estiff = bpy.props.FloatProperty(name = "mol_relink_estiff", description = "Stiffness of links expension between particles",min = 0,max = 1, default = 1)
    parset.mol_relink_estiffrand = bpy.props.FloatProperty(name = "mol_relink_estiffrand", description = "Random variation for expension stiffness",min = 0, max = 1 ,default = 0)
    parset.mol_relink_estiffexp = bpy.props.IntProperty(name = "mol_relink_estiffexp", description = "Give a exponent force to the spring links",min = 1, max = 10, default = 1)
    parset.mol_relink_edamp = bpy.props.FloatProperty(name = "mol_relink_edamp", description = "Damping effect on expension spring links",min = 0, max = 1, default = 1)
    parset.mol_relink_edamprand = bpy.props.FloatProperty(name = "mol_relink_deamprand", description = "Random variation on damping",min = 0 , max = 0, default = 0)
    parset.mol_relink_ebroken = bpy.props.FloatProperty(name = "mol_relink_ebroken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5, precision = 3)
    parset.mol_relink_ebrokenrand = bpy.props.FloatProperty(name = "mol_relink_ebrokenrand", description = "Give a random variation to the stretch limit",min = 0, max = 1, default = 0)
    
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

def pack_data(initiate):
    global mol_exportdata
    global mol_minsize
    global mol_simrun
    psyslen = 0
    parnum = 0
    scene = bpy.context.scene
    for obj in bpy.data.objects:
        for psys in obj.particle_systems:           
            if psys.settings.mol_matter != "-1":
                psys.settings.mol_density = float(psys.settings.mol_matter)
            if psys.settings.mol_active == True and len(psys.particles) > 0:
                parlen = len(psys.particles)
                par_loc = [0,0,0] * parlen
                par_vel = [0,0,0] * parlen
                par_size = [0] * parlen
                par_alive = []
                for par in psys.particles:
                    parnum += 1
                    if par.alive_state == "UNBORN":
                        par_alive.append(2)
                    if par.alive_state == "ALIVE":
                        par_alive.append(0)
                    if par.alive_state == "DEAD":
                        par_alive.append(3)
                        
                psys.particles.foreach_get('location',par_loc)
                psys.particles.foreach_get('velocity',par_vel)
                
                if initiate:
                    par_mass = []
                    
                    if psys.settings.mol_density_active:
                        for par in psys.particles:
                            par_mass.append(psys.settings.mol_density * (4/3*pi*((par.size/2)**3)))
                    else:
                        for par in psys.particles:
                            par_mass.append(psys.settings.mass)
                    """
                    if scene.mol_timescale_active == True:
                        psys.settings.timestep = 1 / (scene.render.fps / scene.timescale)
                    else:
                        psys.settings.timestep = 1 / scene.render.fps 
                    """
                    #psys.settings.count = psys.settings.count
                    psys.point_cache.frame_step = psys.point_cache.frame_step
                    psyslen += 1
                    psys.particles.foreach_get('size',par_size)
                    if mol_minsize > min(par_size):
                        mol_minsize = min(par_size)
                    
                    if psys.settings.mol_link_samevalue:
                        psys.settings.mol_link_estiff = psys.settings.mol_link_stiff
                        psys.settings.mol_link_estiffrand = psys.settings.mol_link_stiffrand
                        psys.settings.mol_link_estiffexp = psys.settings.mol_link_stiffexp
                        psys.settings.mol_link_edamp = psys.settings.mol_link_damp
                        psys.settings.mol_link_edamprand = psys.settings.mol_link_damprand
                        psys.settings.mol_link_ebroken = psys.settings.mol_link_broken
                        psys.settings.mol_link_ebrokenrand = psys.settings.mol_link_brokenrand
                        
                    if psys.settings.mol_relink_samevalue:
                        psys.settings.mol_relink_estiff = psys.settings.mol_relink_stiff
                        psys.settings.mol_relink_estiffrand = psys.settings.mol_relink_stiffrand
                        psys.settings.mol_relink_estiffexp = psys.settings.mol_relink_stiffexp
                        psys.settings.mol_relink_edamp = psys.settings.mol_relink_damp
                        psys.settings.mol_relink_edamprand = psys.settings.mol_relink_damprand
                        psys.settings.mol_relink_ebroken = psys.settings.mol_relink_broken
                        psys.settings.mol_relink_ebrokenrand = psys.settings.mol_relink_brokenrand
                    
                    params = [0] * 45
                    params[0] = psys.settings.mol_selfcollision_active
                    params[1] = psys.settings.mol_othercollision_active
                    params[2] = psys.settings.mol_collision_group
                    params[3] = psys.settings.mol_friction
                    params[4] = psys.settings.mol_collision_damp
                    params[5] = psys.settings.mol_links_active
                    if psys.settings.mol_link_rellength == True:
                        params[6] = psys.settings.particle_size * psys.settings.mol_link_length
                    else:
                        params[6] = psys.settings.mol_link_length
                    params[7] = psys.settings.mol_link_max
                    params[8] = psys.settings.mol_link_tension
                    params[9] = psys.settings.mol_link_tensionrand
                    params[10] = psys.settings.mol_link_stiff
                    params[11] = psys.settings.mol_link_stiffrand
                    params[12] = psys.settings.mol_link_stiffexp
                    params[13] = psys.settings.mol_link_damp
                    params[14] = psys.settings.mol_link_damprand
                    params[15] = psys.settings.mol_link_broken
                    params[16] = psys.settings.mol_link_brokenrand
                    params[17] = psys.settings.mol_link_estiff
                    params[18] = psys.settings.mol_link_estiffrand
                    params[19] = psys.settings.mol_link_estiffexp
                    params[20] = psys.settings.mol_link_edamp
                    params[21] = psys.settings.mol_link_edamprand
                    params[22] = psys.settings.mol_link_ebroken
                    params[23] = psys.settings.mol_link_ebrokenrand
                    params[24] = psys.settings.mol_relink_group
                    params[25] = psys.settings.mol_relink_chance
                    params[26] = psys.settings.mol_relink_chancerand
                    params[27] = psys.settings.mol_relink_max
                    params[28] = psys.settings.mol_relink_tension
                    params[29] = psys.settings.mol_relink_tensionrand
                    params[30] = psys.settings.mol_relink_stiff
                    params[31] = psys.settings.mol_relink_stiffexp
                    params[32] = psys.settings.mol_relink_stiffrand
                    params[33] = psys.settings.mol_relink_damp
                    params[34] = psys.settings.mol_relink_damprand
                    params[35] = psys.settings.mol_relink_broken
                    params[36] = psys.settings.mol_relink_brokenrand
                    params[37] = psys.settings.mol_relink_estiff
                    params[38] = psys.settings.mol_relink_estiffexp
                    params[39] = psys.settings.mol_relink_estiffrand
                    params[40] = psys.settings.mol_relink_edamp
                    params[41] = psys.settings.mol_relink_edamprand
                    params[42] = psys.settings.mol_relink_ebroken
                    params[43] = psys.settings.mol_relink_ebrokenrand
                    params[44] = psys.settings.mol_link_friction                   
    
                if initiate:
                    mol_exportdata[0][2] = psyslen
                    mol_exportdata[0][3] = parnum
                    #print(par_loc)
                    mol_exportdata.append((parlen,par_loc,par_vel,par_size,par_mass,par_alive,params))
                    pass
                else:
                    #print(par_loc)
                    mol_exportdata.append((par_loc,par_vel,par_alive))     
                    pass  
    


class MolecularPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Molecular script"
    bl_idname = "OBJECT_PT_molecular"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"
    
    def draw_header(self, context):
        layout = self.layout
        obj = context.object
        psys = obj.particle_systems.active
        row = layout.row()
        if psys != None:
            row.prop(psys.settings,"mol_active", text = "")

    def draw(self, context):
        global mol_simrun
        global mol_timeremain
        global mol_objuvbake
        global mol_psysuvbake
        
        layout = self.layout
        scn = bpy.context.scene
        obj = context.object
        psys = obj.particle_systems.active
        if psys != None:
            layout.enabled = psys.settings.mol_active
            row = layout.row()
            row.label(text = "Density:")
            box = layout.box()
            box.prop(psys.settings,"mol_density_active", text = "Calculate particles weight by density")
            subbox = box.box()
            subbox.enabled  = psys.settings.mol_density_active
            row = subbox.row()
            row.prop(psys.settings,"mol_matter",text = "Preset:")
            row = subbox.row()
            if int(psys.settings.mol_matter) == 0:
                row.enabled = True
            elif int(psys.settings.mol_matter) >= 1:
                row.enabled = False
            row.prop(psys.settings, "mol_density", text = "Kg per CubeMeter:")
            #subsubbox = subbox.box()
            #row = subsubbox.row()
            #row.label(text = "Particle info:")
            #row = subsubbox.row()
            #row.label(icon = "INFO",text = "size: " + str(round(psys.settings.particle_size,5)) + " m")
            #row.label(icon = "INFO",text = "volume: " + str(round(psys.settings.particle_size**3,5)) + " m3")
            #row = subsubbox.row()
            pmass = (psys.settings.particle_size**3) * psys.settings.mol_density
            #row.label(icon = "INFO",text = "mass: " + str(round(pmass,5)) + " kg")
            row = subbox.row()
            row.label(icon = "INFO",text = "Total system approx weight: " + str(round(len(psys.particles) * pmass,4)) + " kg") 
            row = layout.row()
            row.label(text = "Collision:")
            box = layout.box()
            box.prop(psys.settings,"mol_selfcollision_active", text = "Activate Self Collision")
            box.prop(psys.settings,"mol_othercollision_active", text = "Activate Collision with others")
            box.prop(psys.settings,"mol_collision_group",text = " Collide only with:")
            box.prop(psys.settings,"mol_friction",text = " Friction:")
            box.prop(psys.settings,"mol_collision_damp",text = " Damping:")

            row = layout.row()
            row.label(text = "Links:")
            box = layout.box()
            box.prop(psys.settings,"mol_links_active", text = "Activate Particles linking")
            
            subbox = box.box()
            subbox.enabled  = psys.settings.mol_links_active
            subbox.label(text = "Initial Linking (at bird):")
            row = subbox.row()
            row.prop(psys.settings,"mol_link_length",text = "search length")
            row.prop(psys.settings,"mol_link_rellength",text = "Relative")
            row = subbox.row()
            row.prop(psys.settings,"mol_link_max",text = "Max links")
            row = subbox.row()
            row.prop(psys.settings,"mol_link_friction",text = "Link friction")
            layout.separator()
            row = subbox.row()
            row.prop(psys.settings,"mol_link_tension",text = "Tension")
            row.prop(psys.settings,"mol_link_tensionrand",text = "Rand Tension")
            row = subbox.row()
            row.prop(psys.settings,"mol_link_stiff",text = "Stiff")
            row.prop(psys.settings,"mol_link_stiffrand",text = "Rand Stiff")
            #row = subbox.row()
            #row.prop(psys.settings,"mol_link_stiffexp",text = "Exponent")
            #row.label(text = "")
            row = subbox.row()
            row.prop(psys.settings,"mol_link_damp",text = "Damping")
            row.prop(psys.settings,"mol_link_damprand",text = "Rand Damping")
            row = subbox.row()
            row.prop(psys.settings,"mol_link_broken",text = "broken")
            row.prop(psys.settings,"mol_link_brokenrand",text = "Rand Broken")
            row = subbox.row()
            layout.separator()
            row = subbox.row()
            row.prop(psys.settings,"mol_link_samevalue", text = "Same values for compression/expansion")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_link_samevalue
            row.prop(psys.settings,"mol_link_estiff",text = "E Stiff")
            row.prop(psys.settings,"mol_link_estiffrand",text = "Rand E Stiff")
            #row = subbox.row()
            #row.enabled  = not psys.settings.mol_link_samevalue
            #row.prop(psys.settings,"mol_link_estiffexp",text = "E Exponent")
            #row.label(text = "")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_link_samevalue
            row.prop(psys.settings,"mol_link_edamp",text = "E Damping")
            row.prop(psys.settings,"mol_link_edamprand",text = "Rand E Damping")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_link_samevalue
            row.prop(psys.settings,"mol_link_ebroken",text = "E broken")
            row.prop(psys.settings,"mol_link_ebrokenrand",text = "Rand E Broken")

            
            subbox = box.box()
            subbox.active = psys.settings.mol_links_active
            subbox.label(text = "New Linking (at collision):")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_group",text = "Only links with:")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_chance",text = "% linking")
            row.prop(psys.settings,"mol_relink_chancerand",text = "Rand % linking")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_max",text = "Max links")
            row = subbox.row()
            layout.separator()
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_tension",text = "Tension")
            row.prop(psys.settings,"mol_relink_tensionrand",text = "Rand Tension")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_stiff",text = "Stiff")
            row.prop(psys.settings,"mol_relink_stiffrand",text = "Rand Stiff")
            #row = subbox.row()
            #row.prop(psys.settings,"mol_relink_stiffexp",text = "Exp")
            #row.label(text = "")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_damp",text = "Damping")
            row.prop(psys.settings,"mol_relink_damprand",text = "Rand Damping")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_broken",text = "broken")
            row.prop(psys.settings,"mol_relink_brokenrand",text = "Rand broken")
            row = subbox.row()
            layout.separator()
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_samevalue", text = "Same values for compression/expansion")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_relink_samevalue
            row.prop(psys.settings,"mol_relink_estiff",text = "E Stiff")
            row.prop(psys.settings,"mol_relink_estiffrand",text = "Rand E Stiff")
            #row = subbox.row()
            #row.enabled  = not psys.settings.mol_relink_samevalue
            #row.prop(psys.settings,"mol_relink_estiffexp",text = "Exp")
            #row.label(text = "")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_relink_samevalue
            row.prop(psys.settings,"mol_relink_edamp",text = "E Damping")
            row.prop(psys.settings,"mol_relink_edamprand",text = "Rand E Damping")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_relink_samevalue
            row.prop(psys.settings,"mol_relink_ebroken",text = "E broken")
            row.prop(psys.settings,"mol_relink_ebrokenrand",text = "Rand E broken")
            
            row = layout.row()
            row.label(text = "UV's:")
            box = layout.box()
            row = box.row()
            if obj.data.uv_layers.active != None:
                row.prop(psys.settings,"mol_bakeuv",text = "Bake UV at ending (current: " + str(obj.data.uv_textures.active.name) + ")" )
            else:
                row.active = False
                row.prop(psys.settings,"mol_bakeuv",text = "Bake UV at ending (current: None)" )
                
            row = layout.row()
            row.label(text = "")
            row = layout.row()
            row.label(text = "Simulate")
            row = layout.row()
            row.prop(scn,"frame_start",text = "Start Frame")
            row.prop(scn,"frame_end",text = "End Frame")
            #row = layout.row()
            #row.prop(scn,"mol_timescale_active",text = "Activate TimeScaling")
            #row = layout.row()
            #row.enabled = scn.mol_timescale_active
            #row.prop(scn,"timescale",text = "TimeScale")
            #row.label(text = "")
            row = layout.row()
            row.prop(scn,"mol_substep",text = "mol_substep")
            row.label(text = "")
            row = layout.row()
            row.label(text = "CPU used:")
            row.prop(scn,"mol_cpu",text = "CPU")
            row = layout.row()
            row.prop(scn,"mol_bake",text = "Bake all at ending")
            row.prop(scn,"mol_render",text = "Render at ending")
            row = layout.row()
            if mol_simrun == False and psys.point_cache.is_baked == False:
                row.enabled = True
                row.operator("object.mol_simulate",icon = 'RADIO',text = "Start Molecular Simulation")
                row = layout.row()
                row.enabled = False
                row.operator("ptcache.free_bake_all", text="Free All Bakes")
            if psys.point_cache.is_baked == True and mol_simrun == False:
                row.enabled = False
                row.operator("object.mol_simulate",icon = 'RADIO',text = "Simulation baked")
                row = layout.row()
                row.enabled = True
                row.operator("ptcache.free_bake_all", text="Free All Bakes")
            if mol_simrun == True:
                row.enabled = False
                row.operator("object.mol_simulate",icon = 'RADIO',text = "Process: " + mol_timeremain + " left")
                row = layout.row()
                row.enabled = False
                row.operator("ptcache.free_bake_all", text="Free All Bakes")
            
            box = layout.box()
            row = box.row()
            box.enabled = True
            row.label(text = "Molecular Tools:",icon = 'MODIFIER')
            subbox = box.box()
            row = subbox.row()
            row.label(text = "Particle UV:")
            row = subbox.row()
            row.alignment = 'CENTER'
            row.label(icon = 'INFO',text = "Set current particles position  ")
            row = subbox.row()
            row.alignment = 'CENTER'
            row.label(text = "has global or current uv in angular velocity.")
            row = subbox.row()
            row.alignment = 'CENTER'
            row.label(text = " Retrieve it with Cycles particle info node")
            row = subbox.row()
            row.operator("object.mol_set_global_uv",icon = 'GROUP_UVS',text = "Set Global UV")
            row = subbox.row()
            if obj.data.uv_layers.active != None:
                mol_objuvbake = context.object
                mol_psysuvbake = context.object.particle_systems.active
                row.operator("object.mol_set_active_uv",icon = 'GROUP_UVS',text = "Set Active UV (current: " + str(obj.data.uv_textures.active.name) + ")" )
            else:
                row.active = False
                row.operator("object.mol_set_active_uv",icon = 'GROUP_UVS',text = "Set Active UV ( no uvs found)")
            subbox = box.box()
            row = subbox.row()
            row.label(text = "SUBSTEPS CALCULATOR:")
            row = subbox.row()
            row.label(icon = 'INFO',text = "Current systems have: " + str(len(psys.particles)) + " particles")
            row = subbox.row()
            row.prop(psys.settings,"mol_var1",text = "Current numbers of particles")
            row = subbox.row()
            row.prop(psys.settings,"mol_var2",text = "Current substep")
            row = subbox.row()
            row.prop(psys.settings,"mol_var3",text = "Targeted numbers of particles")
            diff = (psys.settings.mol_var3 / psys.settings.mol_var1)
            factor = (psys.settings.mol_var3**(1/3) / psys.settings.mol_var1**(1/3))
            newsubstep = int(round(factor * psys.settings.mol_var2))
            row = subbox.row()
            row.label(icon = 'FORWARD',text = "You must set new substep to:   " + str(newsubstep))
            row = subbox.row()
            row.label(icon = 'ERROR',text = "Multiply particles size by: " + str(round(1/factor,5)))
            row = subbox.row()
            row.label(icon = 'ERROR',text = "Multiply others sys particle number by: " + str(round(diff,5)))
            
            
            box = layout.box()
            row = box.row()
            box.active = False
            box.alert = False
            row.alignment = 'CENTER'
            row.label(text = "THANKS TO ALL DONATORS !")
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text = "If you want donate to support my work")
            row = box.row()
            row.alignment = 'CENTER'
            row.operator("wm.url_open", text=" click here to Donate ", icon='URL').url = "www.pyroevil.com/donate/"
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text = "or visit: ")
            row = box.row()
            row.alignment = 'CENTER'
            row.label(text = "www.pyroevil.com/donate/")



class MolSimulate(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.mol_simulate"
    bl_label = "Mol Simulate"


    def execute(self, context):
        global mol_substep
        global mol_old_endframe
        global mol_exportdata
        global mol_report
        global mol_minsize
        global mol_newlink
        global mol_deadlink
        global mol_totallink
        global mol_totaldeadlink
        global mol_simrun
        global mol_timeremain
        
        mol_simrun = True
        mol_timeremain = "...Simulating..."
        
        mol_minsize = 1000000000
        
        mol_newlink = 0
        mol_deadlink = 0
        mol_totallink = 0
        mol_totaldeadlink = 0
        
        print("Molecular Sim start--------------------------------------------------")
        mol_stime = clock()
        scene = bpy.context.scene
        object = bpy.context.object
        scene.frame_set(frame = scene.frame_start)
        mol_old_endframe = scene.frame_end
        mol_substep = scene.mol_substep
        scene.render.frame_map_old = 1
        scene.render.frame_map_new = mol_substep + 1
        scene.frame_end *= mol_substep + 1
        
        if scene.mol_timescale_active == True:
            fps = scene.render.fps / scene.timescale
        else:
            fps = scene.render.fps
        cpu = scene.mol_cpu
        mol_exportdata = []
        mol_exportdata = [[fps,mol_substep,0,0,cpu]]
        mol_stime = clock()
        pack_data(True)
        #print("sys number",mol_exportdata[0][2])
        etime = clock()
        print("  " + "PackData take " + str(round(etime - mol_stime,3)) + "sec")
        mol_stime = clock()
        mol_report = cmolcore.init(mol_exportdata)
        etime = clock()
        print("  " + "Export time take " + str(round(etime - mol_stime,3)) + "sec")
        print("  total numbers of particles: " + str(mol_report))
        print("  start processing:")
        bpy.ops.wm.mol_simulate_modal()
        return {'FINISHED'}
        
class MolSetGlobalUV(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.mol_set_global_uv"
    bl_label = "Mol Set UV"


    def execute(self, context):
        global mol_substep
        global mol_old_endframe
        global mol_exportdata
        global mol_report
        global mol_minsize
        global mol_newlink
        global mol_deadlink
        global mol_totallink
        global mol_totaldeadlink
        global mol_simrun
        global mol_timeremain
        scene = bpy.context.scene
        object = bpy.context.object
        psys = object.particle_systems.active
        coord = [0,0,0] * len(psys.particles)
        psys.particles.foreach_get("location",coord)
        psys.particles.foreach_set("angular_velocity",coord)
        
        return {'FINISHED'}
    
    
class MolSetActiveUV(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.mol_set_active_uv"
    bl_label = "Mol Set Active UV"


    def execute(self, context):
        global mol_substep
        global mol_old_endframe
        global mol_exportdata
        global mol_report
        global mol_minsize
        global mol_newlink
        global mol_deadlink
        global mol_totallink
        global mol_totaldeadlink
        global mol_simrun
        global mol_timeremain
        global mol_objuvbake
        global mol_psysuvbake
        
        scene = context.scene
        object = mol_objuvbake
        
        print('  start bake uv from:',object.name)
        #object2 = object.copy()
        
        obdata = object.data.copy()
        object2 = bpy.data.objects.new(name="mol_uv_temp",object_data = obdata)
        object2.matrix_world = object.matrix_world
        
        context.scene.objects.link(object2)
        mod = object2.modifiers.new("tri_for_uv","TRIANGULATE")
        mod.use_beauty = False
        newmesh = object2.to_mesh(bpy.context.scene,True,"RENDER",True,False)
        object2.data = newmesh
        context.scene.update()
        """
        oldmesh = object.data
        newmesh = object.data.copy()
        object.data = newmesh
        mod = object.modifiers.new("tri_for_uv","TRIANGULATE")
        mod.use_beauty = False
        bpy.ops.object.modifier_apply(apply_as='DATA', modifier=mod.name)
        """
        psys = mol_psysuvbake
        #print('-------------start------------')
        for par in psys.particles:
            parloc = (par.location * object2.matrix_world) - object2.location
            point = object2.closest_point_on_mesh(parloc)
            #print('closest:',par.location,point[0],point[2])
            vindex1 = object2.data.polygons[point[2]].vertices[0]
            vindex2 = object2.data.polygons[point[2]].vertices[1]
            vindex3 = object2.data.polygons[point[2]].vertices[2]
            v1 = (object2.matrix_world * object2.data.vertices[vindex1].co).to_tuple()
            v2 = (object2.matrix_world * object2.data.vertices[vindex2].co).to_tuple()
            v3 = (object2.matrix_world * object2.data.vertices[vindex3].co).to_tuple()
            uvindex1 = object2.data.polygons[point[2]].loop_start + 0
            uvindex2 = object2.data.polygons[point[2]].loop_start + 1
            uvindex3 = object2.data.polygons[point[2]].loop_start + 2
            uv1 = object2.data.uv_layers.active.data[uvindex1].uv.to_3d()
            uv2 = object2.data.uv_layers.active.data[uvindex2].uv.to_3d()
            uv3 = object2.data.uv_layers.active.data[uvindex3].uv.to_3d()
            #print(vertices1.co,vertices2.co,vertices3.co)
            #print(uv1,uv2,uv3)
            p = object2.matrix_world * point[0]
            v1 = Vector(v1)
            v2 = Vector(v2)
            v3 = Vector(v3)
            uv1 = Vector(uv1)
            uv2 = Vector(uv2)
            uv3 = Vector(uv3)
            #print(a,b,c,uv1,uv2,uv3,p)
            newuv = barycentric(p,v1,v2,v3,uv1,uv2,uv3)
            #print('New UVs:',newuv)
            parloc = par.location * object2.matrix_world
            dist = (Vector((parloc[0] - p[0],parloc[1] - p[1],parloc[2] - p[2]))).length
            newuv[2] = dist
            newuv = newuv.to_tuple()
            par.angular_velocity = newuv
        scene.objects.unlink(object2)
        bpy.data.objects.remove(object2)
        bpy.data.meshes.remove(newmesh)
        print('         uv baked on:',psys.settings.name)
        
        return {'FINISHED'}

class MolSimulateModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.mol_simulate_modal"
    bl_label = "Simulate Molecular"
    _timer = None

    def modal(self, context, event):
        global mol_substep
        global mol_old_endframe
        global mol_exportdata
        global mol_stime
        global mol_importdata
        global mol_minsize
        global mol_newlink
        global mol_deadlink
        global mol_totallink
        global mol_totaldeadlink
        global mol_timeremain
        global mol_simrun
        global mol_objuvbake
        global mol_psysuvbake
        
        #mol_stime = clock()
        scene = bpy.context.scene
        frame_end = scene.frame_end
        frame_current = scene.frame_current
        if event.type == 'ESC' or frame_current == frame_end:
            if frame_current == frame_end and scene.mol_bake == True:
                fake_context = bpy.context.copy()
                for obj in bpy.data.objects:
                    for psys in obj.particle_systems:
                        if psys.settings.mol_active == True  and len(psys.particles) > 0:
                            fake_context["point_cache"] = psys.point_cache
                            bpy.ops.ptcache.bake_from_cache(fake_context)
            scene.render.frame_map_new = 1
            scene.frame_end = mol_old_endframe
            
            for obj in bpy.data.objects:
                for psys in obj.particle_systems:
                    for psys in obj.particle_systems:
                        if psys.settings.mol_bakeuv == True:
                            mol_objuvbake = obj
                            mol_psysuvbake = psys
                            bpy.context.scene.update()
                            scene.frame_set(frame = psys.settings.frame_start)
                            bpy.context.scene.update()
                            bpy.ops.object.mol_set_active_uv()
            
            if frame_current == frame_end and scene.mol_render == True:
                bpy.ops.render.render(animation=True)
                
            scene.frame_set(frame = scene.frame_start)

            cmolcore.memfree()
            mol_simrun = False
            print("--------------------------------------------------Molecular Sim end")
            return self.cancel(context)

        if event.type == 'TIMER':
            if frame_current == scene.frame_start:            
                mol_stime = clock()
            mol_exportdata = []
            #stimex = clock()
            pack_data(False)
            #print("packdata time",clock() - stimex,"sec")
            mol_importdata = cmolcore.simulate(mol_exportdata)
            i = 0
            #stimex = clock()
            for obj in bpy.data.objects:
                for psys in obj.particle_systems:
                    if psys.settings.mol_active == True  and len(psys.particles) > 0:
                        #print(len(mol_importdata[i][1]))
                        #print(len(psys.particles))
                        psys.particles.foreach_set('velocity',mol_importdata[1][i])
                        i += 1
            #print("inject new velocity time",clock() - stimex,"sec")
            framesubstep = frame_current/(mol_substep+1)        
            if framesubstep == int(framesubstep):
                etime = clock()
                print("    frame " + str(framesubstep + 1) + ":")
                print("      links created:",mol_newlink)
                if mol_totallink != 0:
                    print("      links broked :",mol_deadlink)
                    print("      total links:",mol_totallink - mol_totaldeadlink ,"/",mol_totallink," (",round((((mol_totallink - mol_totaldeadlink) / mol_totallink) * 100),2),"%)")
                print("      Molecular Script: " + str(round(etime - mol_stime,3)) + " sec")
                remain = (((etime - mol_stime) * (mol_old_endframe - framesubstep - 1)))
                days = int(strftime('%d',gmtime(remain))) - 1
                mol_timeremain = strftime(str(days) + ' days %H hours %M mins %S secs', gmtime(remain))
                print("      Remaining estimated:",mol_timeremain)
                mol_newlink = 0
                mol_deadlink = 0
                mol_stime = clock()
                stime2 = clock()
            mol_newlink += mol_importdata[2]
            mol_deadlink += mol_importdata[3]
            mol_totallink = mol_importdata[4]
            mol_totaldeadlink = mol_importdata[5]
            scene.frame_set(frame = frame_current + 1)
            if framesubstep == int(framesubstep):
                etime2 = clock()
                print("      Blender: " + str(round(etime2 - stime2,3)) + " sec")
                stime2 = clock()
        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.000000001, context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}   


def register():
    define_props()
    bpy.utils.register_class(MolSimulateModal)
    bpy.utils.register_class(MolSimulate)
    bpy.utils.register_class(MolSetGlobalUV)
    bpy.utils.register_class(MolSetActiveUV)
    bpy.utils.register_class(MolecularPanel)
    pass


def unregister():
    bpy.utils.unregister_class(MolSimulateModal)
    bpy.utils.unregister_class(MolSimulate)
    bpy.utils.unregister_class(MolSetGlobalUV)
    bpy.utils.unregister_class(MolSetActiveUV)
    bpy.utils.unregister_class(MolecularPanel)
    pass

    
if __name__ == "__main__":
    register()
