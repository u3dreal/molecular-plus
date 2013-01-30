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
    "blender": (2, 6, 4),
    "location": "Properties > Add > Curve",
    "description": ("Molecular script"),
    "warning": "",  # used for warning icon and text in addons panel
    "wiki_url": "http://pyroevil.cu.cc/?cat=7",
    "tracker_url": "http://pyroevil.cu.cc/?cat=7" ,
    "category": "Object"}
    

if "bpy" in locals():
    import imp
    imp.reload(molcore)
else:
    try:
        import bpy
        import sys
        sys.path.append(bpy.path.abspath('//'))
        import molcore
    except:
        from molecular import molcore
        pass


import bpy
from random import random
from math import pi
import imp
from time import clock



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
        item = []
        for i in range(1,12):
            item.append((str(i),"Collision Group " + str(i),"collide only with group " + str(i) ))
        parset.mol_collision_group = bpy.props.EnumProperty(items = item, description = "Choose a collision group you want to collide with")
        
        parset.mol_links_active = bpy.props.BoolProperty(name = "mol_links_active", description = "Activate links between particles of this system",default = False)
        parset.mol_link_length = bpy.props.FloatProperty(name = "mol_link_length", description = "Searching range to make a link between particles",min = 0, precision = 6, default = 1)
        parset.mol_link_stiff = bpy.props.FloatProperty(name = "mol_link_stiff", description = "Stiffness of links between particles",min = 0, default = 10)
        parset.mol_link_stiffrand = bpy.props.FloatProperty(name = "mol_link_stiffrand", description = "Random variation for stiffness",min = 0 ,max = 1 ,default = 0)
        parset.mol_link_stiffexp = bpy.props.FloatProperty(name = "mol_link_stiffexp", description = "Give a exponent force to the spring links", default = 1)
        parset.mol_link_stiffinv = bpy.props.BoolProperty(name = "mol_link_stiffinv", description = "When active, for decrease with the distance like magnetic field, inverse of a spring.",default = False)
        parset.mol_link_damp = bpy.props.FloatProperty(name = "mol_link_damp", description = "Damping effect on spring links",min = 0, default = 1)
        parset.mol_link_damprand = bpy.props.FloatProperty(name = "mol_link_damprand", description = "Random variation on damping", default = 0)
        parset.mol_link_broken = bpy.props.FloatProperty(name = "mol_link_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5)
        parset.mol_link_brokenrand = bpy.props.FloatProperty(name = "mol_link_brokenrand", description = "Give a random variation to the stretch limit",min = 0 ,max = 1, default = 0)
        
        item = []
        for i in range(1,12):
            item.append((str(i),"Relink Group " + str(i),"Relink only with group " + str(i) ))
        parset.mol_relink_group = bpy.props.EnumProperty(items = item, description = "Choose a group that new link are possible")        
        parset.mol_relink_chance = bpy.props.FloatProperty(name = "mol_relink_chance", description = "Chance of a new link are created on collision. 0 = off , 100 = 100% of chance",min = 0, max = 100, default = 0)
        parset.mol_relink_chancerand = bpy.props.FloatProperty(name = "mol_relink_chancerand", description = "Give a random variation to the chance of new link", default = 0)
        parset.mol_relink_stiff = bpy.props.FloatProperty(name = "mol_relink_stiff", description = "Stiffness of links between particles",min = 0, default = 10)
        parset.mol_relink_stiffrand = bpy.props.FloatProperty(name = "mol_relink_stiffrand", description = "Random variation for stiffness",min = 0, max = 1 ,default = 0)
        parset.mol_relink_stiffexp = bpy.props.FloatProperty(name = "mol_relink_stiffexp", description = "Give a exponent force to the spring links",min = 0, max = 20, default = 1)
        parset.mol_relink_stiffinv = bpy.props.BoolProperty(name = "mol_relink_stiffinv", description = "When active, for decrease with the distance like magnetic field, inverse of a spring.",default = False)
        parset.mol_relink_damp = bpy.props.FloatProperty(name = "mol_relink_damp", description = "Damping effect on spring links",min = 0, default = 1)
        parset.mol_relink_damprand = bpy.props.FloatProperty(name = "mol_relink_damprand", description = "Random variation on damping",min = 0 , max = 0, default = 0)
        parset.mol_relink_broken = bpy.props.FloatProperty(name = "mol_relink_broken", description = "How much link can stretch before they broken. 0.01 = 1% , 0.5 = 50% , 2.0 = 200% ...",min = 0, default = 0.5)
        parset.mol_relink_brokenrand = bpy.props.FloatProperty(name = "mol_relink_brokenrand", description = "Give a random variation to the stretch limit",min = 0, max = 1, default = 0)

        
        bpy.types.Scene.mol_fps_active = bpy.props.BoolProperty(name = "mol_fps_active", description = "Give another frame rate then the one set in the scene",default = False)
        bpy.types.Scene.mol_fps = bpy.props.IntProperty(name = "mol_fps", description = "Random variation on damping", default = 24)
        bpy.types.Scene.mol_substep = bpy.props.IntProperty(name = "mol_substep", description = "Substep. Higher equal more stable and accurate but more slower",min = 0, max = 900, default = 4)


def pack_data(initiate):
    global exportdata
    
    for obj in bpy.data.objects:
        for psys in obj.particle_systems:           
            if psys.settings.mol_matter != "-1":
                psys.settings.mol_density = float(psys.settings.mol_matter)
            if psys.settings.mol_active == True:
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
                    if par.alive_state == "UNBORN":
                        par_alive.append(2)
                    if par.alive_state == "ALIVE":
                        par_alive.append(0)
                    if par.alive_state == "DEAD":
                        par_alive.append(3)
                        
                psys.particles.foreach_get('location',par_loc)
                psys.particles.foreach_get('velocity',par_vel)
                
                if initiate:
                    psys.settings.count = psys.settings.count
                    psys.particles.foreach_get('size',par_size)
                    
                    params = [0] * 23
                    params[0] = psys.settings.mol_selfcollision_active
                    params[1] = psys.settings.mol_othercollision_active
                    params[2] = psys.settings.mol_collision_group
                    params[3] = psys.settings.mol_links_active
                    params[4] = psys.settings.mol_link_length
                    params[5] = psys.settings.mol_link_stiff
                    params[6] = psys.settings.mol_link_stiffrand
                    params[7] = psys.settings.mol_link_stiffexp
                    params[8] = psys.settings.mol_link_stiffinv
                    params[9] = psys.settings.mol_link_damp
                    params[10] = psys.settings.mol_link_damprand
                    params[11] = psys.settings.mol_link_broken
                    params[12] = psys.settings.mol_link_brokenrand
                    params[13] = psys.settings.mol_relink_group
                    params[14] = psys.settings.mol_relink_chance
                    params[15] = psys.settings.mol_relink_chancerand
                    params[16] = psys.settings.mol_relink_stiff
                    params[17] = psys.settings.mol_relink_stiffexp
                    params[18] = psys.settings.mol_relink_stiffinv
                    params[19] = psys.settings.mol_relink_damp
                    params[20] = psys.settings.mol_relink_damprand
                    params[21] = psys.settings.mol_relink_broken
                    params[22] = psys.settings.mol_relink_brokenrand                    
    
            if initiate:
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
        row.prop(psys.settings,"mol_active", text = "")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        psys = obj.particle_systems.active
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
        subsubbox = subbox.box()
        row = subsubbox.row()
        row.label(text = "Particle info:")
        row = subsubbox.row()
        row.label(icon = "INFO",text = "size: " + str(round(psys.settings.particle_size,5)) + " m")
        row.label(icon = "INFO",text = "volume: " + str(round(psys.settings.particle_size**3,5)) + " m3")
        row = subsubbox.row()
        pmass = (psys.settings.particle_size**3) * psys.settings.mol_density
        row.label(icon = "INFO",text = "mass: " + str(round(pmass,5)) + " kg")
        row = subbox.row()
        row.label(icon = "INFO",text = "Total system weight: " + str(round(len(psys.particles) * pmass,5)) + " kg") 
        row = layout.row()
        row.label(text = "Collision:")
        box = layout.box()
        box.prop(psys.settings,"mol_selfcollision_active", text = "Activate Self Collision")
        box.prop(psys.settings,"mol_othercollision_active", text = "Activate Collision with others")
        box.prop(psys.settings,"mol_collision_group",text = " Collide only with:")

        row = layout.row()
        row.label(text = "Links:")
        box = layout.box()
        box.prop(psys.settings,"mol_links_active", text = "Activate Particles linking")
        
        subbox = box.box()
        subbox.enabled  = psys.settings.mol_links_active
        subbox.label(text = "Initial Linking (at bird):")
        row = subbox.row()
        row.prop(psys.settings,"mol_link_length",text = "search length")
        row = subbox.row()
        row.prop(psys.settings,"mol_link_stiff",text = "Stiffness")
        row.prop(psys.settings,"mol_link_stiffrand",text = "Random Stiffness")
        row = subbox.row()
        row.prop(psys.settings,"mol_link_stiffexp",text = "Exponent")
        row.prop(psys.settings,"mol_link_stiffinv",text = "Invert Spring")
        row = subbox.row()
        row.prop(psys.settings,"mol_link_damp",text = "Damping")
        row.prop(psys.settings,"mol_link_damprand",text = "Random Damping")
        row = subbox.row()
        row.prop(psys.settings,"mol_link_broken",text = "broken")
        row.prop(psys.settings,"mol_link_brokenrand",text = "Random Broken")
        
        subbox = box.box()
        subbox.active = psys.settings.mol_links_active
        subbox.label(text = "New Linking (at collision):")
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_group",text = "Only links with:")
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_chance",text = "% linking")
        row.prop(psys.settings,"mol_relink_chancerand",text = "Random % linking")
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_stiff",text = "Stiffness")
        row.prop(psys.settings,"mol_relink_stiffrand",text = "Random Stiffness")
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_stiffexp",text = "Exp")
        row.prop(psys.settings,"mol_relink_stiffinv",text = "Invert Spring")
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_damp",text = "Damping")
        row.prop(psys.settings,"mol_relink_damprand",text = "Random Damping")
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_broken",text = "broken")
        row.prop(psys.settings,"mol_relink_brokenrand",text = "Random broken")
        
        row = layout.row()
        scn = bpy.context.scene
        row.label(text = "Simulate")
        row = layout.row()
        row.prop(scn,"frame_start",text = "Start Frame")
        row.prop(scn,"frame_end",text = "End Frame")
        row = layout.row()
        row.prop(scn,"mol_fps_active",text = "change fps")
        row = layout.row()
        row.enabled = scn.mol_fps_active
        row.prop(scn,"mol_fps",text = "fps")
        row.label(text = "")
        row = layout.row()
        row.prop(scn,"mol_substep",text = "substep")
        row.label(text = "")
        row = layout.row()
        row.operator("object.mol_simulate",text = "Start Molecular Simulation")



class MolSimulate(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.mol_simulate"
    bl_label = "Mol Simulate"


    def execute(self, context):
        global substep
        global old_endframe
        global exportdata

        print("Molecular Sim start...")
        stime = clock()
        scene = bpy.context.scene
        object = bpy.context.object
        scene.frame_set(frame = scene.frame_start)
        old_endframe = scene.frame_end
        substep = scene.mol_substep
        scene.render.frame_map_old = 1
        scene.render.frame_map_new = substep + 1
        scene.frame_end *= substep + 1
        
        if scene.mol_fps_active == True:
            fps = scene.mol_fps
        else:
            fps = scene.render.fps
        
        exportdata = []
        exportdata = [(fps,substep)]    
        pack_data(True)
        imp.reload(molcore)
        report = molcore.init(exportdata)
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
        
        #stime = clock()
        scene = bpy.context.scene
        frame_end = scene.frame_end
        frame_current = scene.frame_current
        if event.type == 'ESC' or frame_current == frame_end:
            scene.render.frame_map_new = 1
            scene.frame_end = old_endframe
            scene.frame_set(frame = scene.frame_start)
            #bpy.ops.render.render(animation=True)
            print("...Molecular Sim end")
            return self.cancel(context)

        if event.type == 'TIMER':
            if frame_current == scene.frame_start:            
                stime = clock()
            exportdata = []
            pack_data(False)
            importdata = molcore.simulate(exportdata)
            #print(importdata[1])
            i = 0
            for obj in bpy.data.objects:
                for psys in obj.particle_systems:
                    if psys.settings.mol_active == True:
                        #print(len(importdata[i][1]))
                        #print(len(psys.particles))
                        psys.particles.foreach_set('velocity',importdata[1][i])
                    i += 1
            framesubstep = frame_current/(substep+1)        
            if framesubstep == int(framesubstep):
                etime = clock()
                print("    frame " + str(framesubstep + 1) + " take:")
                print("      Molecular Script: " + str(round(etime - stime,3)) + " sec")
                stime = clock()
                stime2 = clock()
            scene.frame_set(frame = frame_current + 1)
            if framesubstep == int(framesubstep):
                etime2 = clock()
                print("      Blender: " + str(round(etime2 - stime2,3)) + " sec")
                stime2 = clock()

        return {'PASS_THROUGH'}

    def execute(self, context):
        self._timer = context.window_manager.event_timer_add(0.1, context.window)
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
