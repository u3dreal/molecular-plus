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
    "version": (0, 0, 1),
    "blender": (2, 6, 5),
    "location": "Properties > Add > Curve",
    "description": ("Molecular script"),
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "http://pyroevil.com/?cat=7",
    "tracker_url": "http://pyroevil.com/?cat=7" ,
    "category": "Object"}
    

if "bpy" in locals():
    import imp
    imp.reload(molcore)
    imp.reload(cmolcore)
else:
    try:
        import bpy
        import sys
        sys.path.append(bpy.path.abspath('//'))
        import molcore
        import cmolcore
    except:
        from molecular import molcore
        #from molecular import cmolcore
        pass


import bpy
from random import random
from math import pi
import imp
from time import clock
import cmolcore
import pstats, cProfile
import multiprocessing



def define_props():
    
    #if "mol_active" not in bpy.context.object.particle_systems['ParticleSystem'].settings:
        parset = bpy.types.ParticleSettings
        parset.mol_active = bpy.props.BoolProperty(name = "mol_active", description = "Activate molecular script for this particles system",default = False)
        parset.mol_density_active = bpy.props.BoolProperty(name="mol_density_active", description="Control particle weight by density",default = False)
        item = [("-1","custom","put your parameter below"),("1555","sand","1555kg per meter cu"),("1000","water","1000kg per meter cu"),("7800","iron","7800kg per meter cu")]
        parset.mol_matter = bpy.props.EnumProperty(items = item, description = "Choose a matter preset for density")
        parset.mol_density = bpy.props.FloatProperty(name = "mol_density", description = "Density of the matter kg/cube meter", default = 1000, min = 0.001)
        
        parset.mol_selfcollision_active = bpy.props.BoolProperty(name = "mol_selfcollision_active", description = "Activate self collsion between particles in the system",default = False)
        parset.mol_othercollision_active = bpy.props.BoolProperty(name = "mol_othercollision_active", description = "Activate collision with particles from others systems",default = False)
        parset.mol_friction = bpy.props.FloatProperty(name = "mol_friction", description = "Friction between particles at collision 0 = no friction , 1 = full friction",default = 0.005 , min = 0 , max = 1)
        item = []
        for i in range(1,12):
            item.append((str(i),"Collision Group " + str(i),"collide only with group " + str(i) ))
        parset.mol_collision_group = bpy.props.EnumProperty(items = item, description = "Choose a collision group you want to collide with")
        
        parset.mol_links_active = bpy.props.BoolProperty(name = "mol_links_active", description = "Activate links between particles of this system",default = False)
        parset.mol_link_rellength = bpy.props.BoolProperty(name = "mol_link_rellength", description = "Activate search distance relative to particles radius",default = True)
        parset.mol_link_length = bpy.props.FloatProperty(name = "mol_link_length", description = "Searching range to make a link between particles",min = 0, precision = 6, default = 1)
        parset.mol_link_tension = bpy.props.FloatProperty(name = "mol_link_tension", description = "Make link bigger or smaller than it's created (1 = normal , 0.9 = 10% smaller , 1.15 = 15% bigger)",min = 0, precision = 3, default = 1)
        parset.mol_link_tensionrand = bpy.props.FloatProperty(name = "mol_link_tensionrand", description = "Tension random",min = 0,max = 1, precision = 3, default = 0)
        parset.mol_link_max = bpy.props.IntProperty(name = "mol_link_max", description = "Maximum of links per particles",min = 0,default = 16)
        parset.mol_link_stiff = bpy.props.FloatProperty(name = "mol_link_stiff", description = "Stiffness of links between particles",min = 0, default = 1)
        parset.mol_link_stiffrand = bpy.props.FloatProperty(name = "mol_link_stiffrand", description = "Random variation for stiffness",min = 0 ,max = 1 ,default = 0)
        parset.mol_link_stiffexp = bpy.props.IntProperty(name = "mol_link_stiffexp", description = "Give a exponent force to the spring links", default = 1, min = 1 , max = 10)
        parset.mol_link_damp = bpy.props.FloatProperty(name = "mol_link_damp", description = "Damping effect on spring links",min = 0, default = 1)
        parset.mol_link_damprand = bpy.props.FloatProperty(name = "mol_link_damprand", description = "Random variation on damping", default = 0)
        parset.mol_link_broken = bpy.props.FloatProperty(name = "mol_link_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5)
        parset.mol_link_brokenrand = bpy.props.FloatProperty(name = "mol_link_brokenrand", description = "Give a random variation to the stretch limit",min = 0 ,max = 1, default = 0)
        
        parset.mol_link_samevalue = bpy.props.BoolProperty(name = "mol_link_samevalue", description = "When active , expansion and compression of the spring have same value",default = True)
        
        parset.mol_link_estiff = bpy.props.FloatProperty(name = "mol_link_estiff", description = "Expension stiffness of links between particles",min = 0, default = 1)
        parset.mol_link_estiffrand = bpy.props.FloatProperty(name = "mol_link_estiffrand", description = "Random variation for expansion stiffness",min = 0 ,max = 1 ,default = 0)
        parset.mol_link_estiffexp = bpy.props.IntProperty(name = "mol_link_estiffexp", description = "Give a exponent force to the expension spring links", default = 1, min = 1 , max = 10)
        parset.mol_link_edamp = bpy.props.FloatProperty(name = "mol_link_edamp", description = "Damping effect on expension spring links",min = 0, default = 1)
        parset.mol_link_edamprand = bpy.props.FloatProperty(name = "mol_link_edamprand", description = "Random variation on expension damping", default = 0)
        parset.mol_link_ebroken = bpy.props.FloatProperty(name = "mol_link_ebroken", description = "How much link can expand before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5)
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
        parset.mol_relink_stiff = bpy.props.FloatProperty(name = "mol_relink_stiff", description = "Stiffness of links between particles",min = 0, default = 1)
        parset.mol_relink_stiffrand = bpy.props.FloatProperty(name = "mol_relink_stiffrand", description = "Random variation for stiffness",min = 0, max = 1 ,default = 0)
        parset.mol_relink_stiffexp = bpy.props.IntProperty(name = "mol_relink_stiffexp", description = "Give a exponent force to the spring links",min = 1, max = 10, default = 1)
        parset.mol_relink_damp = bpy.props.FloatProperty(name = "mol_relink_damp", description = "Damping effect on spring links",min = 0, default = 1)
        parset.mol_relink_damprand = bpy.props.FloatProperty(name = "mol_relink_damprand", description = "Random variation on damping",min = 0 , max = 0, default = 0)
        parset.mol_relink_broken = bpy.props.FloatProperty(name = "mol_relink_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5)
        parset.mol_relink_brokenrand = bpy.props.FloatProperty(name = "mol_relink_brokenrand", description = "Give a random variation to the stretch limit",min = 0, max = 1, default = 0)

        parset.mol_relink_samevalue = bpy.props.BoolProperty(name = "mol_relink_samevalue", description = "When active , expansion and compression of the spring have same value",default = True)

        parset.mol_relink_estiff = bpy.props.FloatProperty(name = "mol_relink_estiff", description = "Stiffness of links between particles",min = 0, default = 1)
        parset.mol_relink_estiffrand = bpy.props.FloatProperty(name = "mol_relink_estiffrand", description = "Random variation for stiffness",min = 0, max = 1 ,default = 0)
        parset.mol_relink_estiffexp = bpy.props.IntProperty(name = "mol_relink_estiffexp", description = "Give a exponent force to the spring links",min = 1, max = 10, default = 1)
        parset.mol_relink_edamp = bpy.props.FloatProperty(name = "mol_relink_edamp", description = "Damping effect on spring links",min = 0, default = 1)
        parset.mol_relink_edamprand = bpy.props.FloatProperty(name = "mol_relink_deamprand", description = "Random variation on damping",min = 0 , max = 0, default = 0)
        parset.mol_relink_ebroken = bpy.props.FloatProperty(name = "mol_relink_ebroken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5)
        parset.mol_relink_ebrokenrand = bpy.props.FloatProperty(name = "mol_relink_ebrokenrand", description = "Give a random variation to the stretch limit",min = 0, max = 1, default = 0)
        
        bpy.types.Scene.mol_timescale_active = bpy.props.BoolProperty(name = "mol_timescale_active", description = "Activate TimeScaling",default = False)
        bpy.types.Scene.timescale = bpy.props.FloatProperty(name = "timescale", description = "SpeedUp or Slow down the simulation with this multiplier", default = 1)
        bpy.types.Scene.mol_substep = bpy.props.IntProperty(name = "mol_substep", description = "Substep. Higher equal more stable and accurate but more slower",min = 0, max = 900, default = 4)
        bpy.types.Scene.mol_bake = bpy.props.BoolProperty(name = "mol_bake", description = "Bake simulation when finish",default = True)
        bpy.types.Scene.mol_render = bpy.props.BoolProperty(name = "mol_render", description = "Start rendering animation when simulation is finish. WARNING: It's freeze blender until render is finish.",default = False)
        bpy.types.Scene.mol_cpu = bpy.props.IntProperty(name = "mol_cpu", description = "Numbers of cpu's included for process the simulation", default = multiprocessing.cpu_count(),min = 1,max =multiprocessing.cpu_count())

def pack_data(initiate):
    global exportdata
    global minsize
    psyslen = 0
    parnum = 0
    scene = bpy.context.scene
    for obj in bpy.data.objects:
        for psys in obj.particle_systems:           
            if psys.settings.mol_matter != "-1":
                psys.settings.mol_density = float(psys.settings.mol_matter)
            if psys.settings.mol_active == True:
                if scene.mol_timescale_active == True:
                    psys.settings.timestep = 1 / (scene.render.fps / scene.timescale)
                else:
                    psys.settings.timestep = 1 / scene.render.fps 
                parlen = len(psys.particles)
                par_loc = [0,0,0] * parlen
                par_vel = [0,0,0] * parlen
                par_size = [0] * parlen
                par_mass = []
                if psys.settings.mol_density_active:
                    for par in psys.particles:
                        par_mass.append(psys.settings.mol_density * (4/3*pi*((par.size/2)**3)))
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
                    psyslen += 1
                    psys.settings.count = psys.settings.count
                    psys.particles.foreach_get('size',par_size)
                    if minsize > min(par_size):
                        minsize = min(par_size)
                    
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
                    
                    params = [0] * 43
                    params[0] = psys.settings.mol_selfcollision_active
                    params[1] = psys.settings.mol_othercollision_active
                    params[2] = psys.settings.mol_collision_group
                    params[3] = psys.settings.mol_friction
                    params[4] = psys.settings.mol_links_active
                    if psys.settings.mol_link_rellength == True:
                        params[5] = psys.settings.particle_size * psys.settings.mol_link_length
                    else:
                        params[5] = psys.settings.mol_link_length
                    params[6] = psys.settings.mol_link_max
                    params[7] = psys.settings.mol_link_tension
                    params[8] = psys.settings.mol_link_tensionrand
                    params[9] = psys.settings.mol_link_stiff
                    params[10] = psys.settings.mol_link_stiffrand
                    params[11] = psys.settings.mol_link_stiffexp
                    params[12] = psys.settings.mol_link_damp
                    params[13] = psys.settings.mol_link_damprand
                    params[14] = psys.settings.mol_link_broken
                    params[15] = psys.settings.mol_link_brokenrand
                    params[16] = psys.settings.mol_link_estiff
                    params[17] = psys.settings.mol_link_estiffrand
                    params[18] = psys.settings.mol_link_estiffexp
                    params[19] = psys.settings.mol_link_edamp
                    params[20] = psys.settings.mol_link_edamprand
                    params[21] = psys.settings.mol_link_ebroken
                    params[22] = psys.settings.mol_link_ebrokenrand
                    params[23] = psys.settings.mol_relink_group
                    params[24] = psys.settings.mol_relink_chance
                    params[25] = psys.settings.mol_relink_chancerand
                    params[26] = psys.settings.mol_relink_max
                    params[27] = psys.settings.mol_relink_tension
                    params[28] = psys.settings.mol_relink_tensionrand
                    params[29] = psys.settings.mol_relink_stiff
                    params[30] = psys.settings.mol_relink_stiffexp
                    params[31] = psys.settings.mol_relink_stiffrand
                    params[32] = psys.settings.mol_relink_damp
                    params[33] = psys.settings.mol_relink_damprand
                    params[34] = psys.settings.mol_relink_broken
                    params[35] = psys.settings.mol_relink_brokenrand
                    params[36] = psys.settings.mol_relink_estiff
                    params[37] = psys.settings.mol_relink_estiffexp
                    params[38] = psys.settings.mol_relink_estiffrand
                    params[39] = psys.settings.mol_relink_edamp
                    params[40] = psys.settings.mol_relink_edamprand
                    params[41] = psys.settings.mol_relink_ebroken
                    params[42] = psys.settings.mol_relink_ebrokenrand                   
    
            if initiate:
                exportdata[0][2] = psyslen
                exportdata[0][3] = parnum
                exportdata.append((parlen,par_loc,par_vel,par_size,par_mass,par_alive,params))
                pass
            else:
                exportdata.append((par_loc,par_vel,par_alive))     
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
        layout = self.layout
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
            row.prop(psys.settings,"mol_link_damprand",text = "Random Damping")
            row = subbox.row()
            row.prop(psys.settings,"mol_link_broken",text = "broken")
            row.prop(psys.settings,"mol_link_brokenrand",text = "Random Broken")
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
            row.prop(psys.settings,"mol_link_edamprand",text = "E Random Damping")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_link_samevalue
            row.prop(psys.settings,"mol_link_ebroken",text = "E broken")
            row.prop(psys.settings,"mol_link_ebrokenrand",text = "E Random Broken")

            
            subbox = box.box()
            subbox.active = psys.settings.mol_links_active
            subbox.label(text = "New Linking (at collision):")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_group",text = "Only links with:")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_chance",text = "% linking")
            row.prop(psys.settings,"mol_relink_chancerand",text = "Random % linking")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_max",text = "Max links")
            row = subbox.row()
            layout.separator()
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_tension",text = "Tension")
            row.prop(psys.settings,"mol_relink_tensionrand",text = "Rand Tension")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_stiff",text = "Stiffness")
            row.prop(psys.settings,"mol_relink_stiffrand",text = "Random Stiffness")
            #row = subbox.row()
            #row.prop(psys.settings,"mol_relink_stiffexp",text = "Exp")
            #row.label(text = "")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_damp",text = "Damping")
            row.prop(psys.settings,"mol_relink_damprand",text = "Random Damping")
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_broken",text = "broken")
            row.prop(psys.settings,"mol_relink_brokenrand",text = "Random broken")
            row = subbox.row()
            layout.separator()
            row = subbox.row()
            row.prop(psys.settings,"mol_relink_samevalue", text = "Same values for compression/expansion")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_relink_samevalue
            row.prop(psys.settings,"mol_relink_estiff",text = "Stiffness")
            row.prop(psys.settings,"mol_relink_estiffrand",text = "Random Stiffness")
            #row = subbox.row()
            #row.enabled  = not psys.settings.mol_relink_samevalue
            #row.prop(psys.settings,"mol_relink_estiffexp",text = "Exp")
            #row.label(text = "")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_relink_samevalue
            row.prop(psys.settings,"mol_relink_edamp",text = "Damping")
            row.prop(psys.settings,"mol_relink_edamprand",text = "Random Damping")
            row = subbox.row()
            row.enabled  = not psys.settings.mol_relink_samevalue
            row.prop(psys.settings,"mol_relink_ebroken",text = "broken")
            row.prop(psys.settings,"mol_relink_ebrokenrand",text = "Random broken")
            
            row = layout.row()
            scn = bpy.context.scene
            row.label(text = "Simulate")
            row = layout.row()
            row.prop(scn,"frame_start",text = "Start Frame")
            row.prop(scn,"frame_end",text = "End Frame")
            row = layout.row()
            row.prop(scn,"mol_timescale_active",text = "Activate TimeScaling")
            row = layout.row()
            row.enabled = scn.mol_timescale_active
            row.prop(scn,"timescale",text = "TimeScale")
            row.label(text = "")
            row = layout.row()
            row.prop(scn,"mol_substep",text = "substep")
            row.label(text = "")
            row = layout.row()
            row.label(text = "CPU used:")
            row.prop(scn,"mol_cpu",text = "CPU")
            row = layout.row()
            row.prop(scn,"mol_bake",text = "Bake all at ending")
            row.prop(scn,"mol_render",text = "Render at ending")
            row = layout.row()
            row.operator("object.mol_simulate",text = "Start Molecular Simulation")
            box = layout.box()
            row = box.row()
            box.enabled = False
            row.label(text = "Thanks to all donators ! If you want donate")
            row = box.row()
            row.label(text = "to help me creating more stuffs like that")
            row = box.row()
            row.label(text = "just visit: www.pyroevil.com")



class MolSimulate(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.mol_simulate"
    bl_label = "Mol Simulate"


    def execute(self, context):
        global substep
        global old_endframe
        global exportdata
        global report
        global minsize
        global newlink
        global deadlink
        global totallink
        global totaldeadlink 
        
        minsize = 1000000000
        
        newlink = 0
        deadlink = 0
        totallink = 0
        totaldeadlink = 0
        
        print("Molecular Sim start--------------------------------------------------")
        stime = clock()
        scene = bpy.context.scene
        object = bpy.context.object
        scene.frame_set(frame = scene.frame_start)
        old_endframe = scene.frame_end
        substep = scene.mol_substep
        scene.render.frame_map_old = 1
        scene.render.frame_map_new = substep + 1
        scene.frame_end *= substep + 1
        
        if scene.mol_timescale_active == True:
            fps = scene.render.fps / scene.timescale
        else:
            fps = scene.render.fps
        cpu = scene.mol_cpu
        exportdata = []
        exportdata = [[fps,substep,0,0,cpu]]
        stime = clock()
        pack_data(True)
        #print("sys number",exportdata[0][2])
        etime = clock()
        print("  " + "PackData take " + str(round(etime - stime,3)) + "sec")
        stime = clock()
        imp.reload(molcore)
        imp.reload(cmolcore)
        report = cmolcore.init(exportdata)
        etime = clock()
        print("  " + "Export time take " + str(round(etime - stime,3)) + "sec")
        print("  total numbers of particles: " + str(report))
        print("  start processing:")
        bpy.ops.wm.mol_simulate_modal()
        return {'FINISHED'}

class MolSimulateModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.mol_simulate_modal"
    bl_label = "Simulate Molecular"
    _timer = None

    def modal(self, context, event):
        global substep
        global old_endframe
        global exportdata
        global stime
        global importdata
        global minsize
        global newlink
        global deadlink
        global totallink
        global totaldeadlink 
        
        #stime = clock()
        scene = bpy.context.scene
        frame_end = scene.frame_end
        frame_current = scene.frame_current
        if event.type == 'ESC' or frame_current == frame_end:
            if frame_current == frame_end and scene.mol_bake == True:
                fake_context = bpy.context.copy()
                for obj in bpy.data.objects:
                    for psys in obj.particle_systems:
                        if psys.settings.mol_active == True:
                            fake_context["point_cache"] = psys.point_cache
                            bpy.ops.ptcache.bake_from_cache(fake_context)
            scene.render.frame_map_new = 1
            scene.frame_end = old_endframe
            if frame_current == frame_end and scene.mol_render == True:
                bpy.ops.render.render(animation=True)
            scene.frame_set(frame = scene.frame_start)
            cmolcore.memfree()
            print("--------------------------------------------------Molecular Sim end")
            return self.cancel(context)

        if event.type == 'TIMER':
            if frame_current == scene.frame_start:            
                stime = clock()
            exportdata = []
            #stimex = clock()
            pack_data(False)
            #print("packdata time",clock() - stimex,"sec")
            importdata = cmolcore.simulate(exportdata)
            i = 0
            #stimex = clock()
            for obj in bpy.data.objects:
                for psys in obj.particle_systems:
                    if psys.settings.mol_active == True:
                        #print(len(importdata[i][1]))
                        #print(len(psys.particles))
                        psys.particles.foreach_set('velocity',importdata[1][i])
                    i += 1
            #print("inject new velocity time",clock() - stimex,"sec")
            framesubstep = frame_current/(substep+1)        
            if framesubstep == int(framesubstep):
                etime = clock()
                print("    frame " + str(framesubstep + 1) + ":")
                print("      links created:",newlink)
                print("      links broked :",deadlink)
                print("      total links:",totallink - totaldeadlink ,"/",totallink," (",round((((totallink - totaldeadlink) / totallink) * 100),2),"%)")
                print("      Molecular Script: " + str(round(etime - stime,3)) + " sec")
                newlink = 0
                deadlink = 0
                stime = clock()
                stime2 = clock()
            newlink += importdata[2]
            deadlink += importdata[3]
            totallink = importdata[4]
            totaldeadlink = importdata[5]
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
    bpy.utils.register_class(MolecularPanel)
    pass


def unregister():
    bpy.utils.unregister_class(MolSimulateModal)
    bpy.utils.unregister_class(MolSimulate)
    bpy.utils.unregister_class(MolecularPanel)
    pass

    
if __name__ == "__main__":
    register()
