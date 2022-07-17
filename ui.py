import bpy
from .utils import get_object
from . import bl_info

class MS_PT_MolecularHelperPanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Molecular+     "  + str(bl_info['version']).replace('(','').replace(')','').replace(',','.')
    bl_idname = "OBJECT_PT_molecular_helper"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"

    @classmethod
    def poll(cls, context):
        return True #context.object != None #psys.settings.mol_active  #context.object != None and context.object.type == 'MESH'

    def draw(self, context):

        scn = context.scene
        obj = context.object
        layout = self.layout
        box = layout.box()
        row = box.row()
        
        if obj != None:
            row.scale_y = 0.5
            row.label(text = "Molecular Object : " + obj.name)

            if context.object.particle_systems.active:
                psys = get_object(context, obj).particle_systems.active
                parcount = len(psys.particles)
                row = box.row()
                row.scale_y = 0.5
                row.label(text = "System particles : " + str(parcount))
                row = box.row()
                row.scale_y = 0.5
                row.label(text = "Total particles : " + str(scn.mol_parnum))
                row.operator("object.mol_set_subs", text="", icon="FILE_REFRESH")

                box = layout.box()
                row = box.row()
                if not scn.mol_simrun and not psys.point_cache.is_baked:
                    row.enabled = True
                    row.operator("object.mol_simulate", icon='RADIOBUT_ON', text="Start Simulation")
                    row = box.row()
                    row.enabled = False
                    row.operator("object.clear_pcache", text="Free All Bakes")


                if psys.point_cache.is_baked and not scn.mol_simrun:
                    row.enabled = False
                    row.operator("object.mol_simulate", icon='RADIOBUT_ON', text="Simulation baked")
                    row = box.row()
                    row.enabled = True
                    row.operator("object.clear_pcache", text="Free All Bakes")
                if scn.mol_simrun:
                    row.enabled = False
                    row.operator("object.mol_simulate", icon='RADIOBUT_ON', text="Process: " + scn.mol_timeremain + " left")
                    row = box.row()
                    row.operator("object.cancel_sim", icon='CANCEL', text="Cancel")

                row = box.row()
                row.prop(scn,"mol_bake",text = "Bake")
                row.prop(scn,"mol_render",text = "Render")
                row.prop(scn, "mol_autosubsteps", text="auto")
                row = box.row()
                row.prop(scn,"mol_substep", text = "Steps")
                row.prop(scn,"mol_cpu",text = "Threads")

                row = box.row()
                row.prop(scn, "frame_start", text="start")
                row.prop(scn, "frame_end", text="end")
                row = box.row()
                # row = box.row()
                # row.enabled = scn.mol_timescale_active
                row.prop(scn, "timescale", text="")
                #row.alignment = 'RIGHT'
                row.prop(scn, "mol_timescale_active", text="TimeScaling")
                #row.label(text="")
                #row = box.row()

        else:
            row.label(text="No Object selected")

            
class MS_PT_MolecularInspectPanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Inspect"
    bl_idname = "OBJECT_PT_molecular_inspect"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"
    
    @classmethod
    def poll(cls, context):
        return context.object and ('Collision' in context.object.modifiers)
    
    def draw(self, context):
        layout = self.layout
        obj = context.object
        
        row = layout.row()
        row.label(text = "Collision: " + obj.name)
        row.operator("object.mol_remove_collision",text="", icon='X')
        row = layout.row()
        row.prop(obj.collision, "damping_factor", text = "Damping")
        row = layout.row()
        row.prop(obj.collision, "friction_factor", text = "Friction")
        row = layout.row()
        row.prop(obj.collision, "stickiness", text = "Stickiness", slider=True)

            
class MS_PT_MolecularCreatePanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Create"
    bl_idname = "OBJECT_PT_molecular_create"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"
    
    @classmethod
    def poll(cls, context):
        return context.object != None and context.object.type == 'MESH' and not ('Collision' in context.object.modifiers)
    
    def draw(self,context):
        
        layout = self.layout
        scn = context.scene
        obj = context.object

        row = layout.row()
        row.alignment = 'RIGHT'
        row.prop(scn,"mol_voxel_size", text = "Size")
        row.prop(scn,"mol_hexgrid", text = "hexa")
        row = layout.separator()
        row = layout.row()
        row.operator("molecular_operators.molecular_makeemitter", icon = 'MOD_PARTICLE_INSTANCE',text = "Emitter")
        row.operator("molecular_operators.molecular_makegrid2d", icon = 'GRID',text = "2D Grid")
        row = layout.row()
        row.operator("molecular_operators.molecular_makegrid3d", icon = 'MOD_REMESH',text = "3D Grid")
        row.operator("molecular_operators.molecular_makecollider", icon = 'MOD_PHYSICS', text = "Collider")
    
        
        
class MS_PT_MolecularDonorPanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "q3de"
    bl_idname = "OBJECT_PT_molecular_donations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"
    bl_options = {'DEFAULT_CLOSED'}

    def draw(self, context):

        layout = self.layout
        box = layout.box()
        row = box.row()
        box.active = True
        row.alignment = 'CENTER'
        row.label(text = "If you like it")
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text = "Support the Development")
        row = box.row()
        row.alignment = 'CENTER'
        row.operator("wm.url_open", text=" click here to Donate ", icon='URL').url = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=J7W7MNCKVBYAA"
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text = "or visit")
        row = box.row()
        row.alignment = 'CENTER'
        row.operator("wm.url_open", text=" q3de.com ", icon='URL').url = "http://www.q3de.com/research/molecular"
        #row.label(text = "www.q3de.com")
        
class MS_PT_MolecularPanel(bpy.types.Panel):
    """Creates a Panel in the Physics properties window"""
    bl_label = "Molecular"
    bl_idname = "OBJECT_PT_molecular"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "physics"
    bl_category = "Molecular"

    @classmethod
    def poll(cls, context):
        if context.object.particle_systems.active and context.object.particle_systems.active.settings.mol_active == True:
            return True

    def draw(self, context):

        layout = self.layout
        scn = context.scene
        obj = context.object
        #obj = bpy.context.view_layer.depsgraph.objects.get(obj.name, None)

        psys = obj.particle_systems.active
        if psys is None:
            return

        #for the data
        psys_eval = get_object(context, obj).particle_systems.active

        if psys.settings.mol_active == False:
            return
        layout.enabled = psys.settings.mol_active
        #row = layout.row()

        ###   Density by Mass   ###
        box = layout.box()
        box.prop(psys.settings,"mol_density_active", icon = "PLUS",text = "Calculate particles weight by density")

        if psys.settings.mol_density_active:

            subbox = box.box()
            row = subbox.row()

            row.prop(psys.settings,"mol_matter",text = "Preset:")
            row = subbox.row()
            if psys.settings.mol_matter != "-1":
                pmass = (psys.settings.particle_size**3) * float(psys.settings.mol_matter)
                density = float(psys.settings.mol_matter)
                row.label(icon = "INFO",text = "Kg per CubeMeter:" + str(round(density,5))+ " kg")
            else:
                row.prop(psys.settings,"mol_density", text = "Kg per CubeMeter:")
                row = subbox.row()

                pmass = (psys.settings.particle_size**3) * psys.settings.mol_density

            row = subbox.row()
            row.label(icon = "INFO",text = "Mass per Particle: " + str(round(pmass,5)) + " kg")
            row = subbox.row()
            row.label(icon = "INFO",text = "Total system approx weight: " + str(round(len(psys_eval.particles) * pmass,4)) + " kg")


        #row = layout.separator()
        row = layout.row()

        ###   Collision   ###
        
        box = layout.box()
        row = box.row()
        row.label(text = "Collisions :")
        row = box.row()
        row.prop(psys.settings,"mol_selfcollision_active", icon = 'PHYSICS', text = "Self Collision")
        row.prop(psys.settings,"mol_othercollision_active", icon = 'PHYSICS', text = "Collision with Others")
        if psys.settings.mol_othercollision_active:
            box.prop(psys.settings,"mol_collision_group",text = "only with:")
        if psys.settings.mol_selfcollision_active or psys.settings.mol_othercollision_active:
            row = box.row()
            row.prop(psys.settings,"mol_friction",text = " Friction:")
            row.prop(psys.settings,"mol_collision_damp",text = " Damping:")

        ###   Links at Birth   ###
        
        box = layout.box()
        row = box.row()
        row.label(text = "Links :")
        row = box.row()
        row.prop(psys.settings,"mol_links_active", icon = 'CONSTRAINT', text = "Link at Birth")
        row.prop(psys.settings,"mol_other_link_active", icon = 'CONSTRAINT', text = "Link with Others at Birth")
        if psys.settings.mol_other_link_active:
            row = box.row()
            row.prop(psys.settings,"mol_relink_group",text = "Only with:")


        if psys.settings.mol_links_active :
            row = box.row()
            row.prop(psys.settings,"mol_link_length",text = "Search Distance")
            row.prop(psys.settings,"mol_link_rellength",text = "Relative")

            row = box.row()
            row.prop(psys.settings,"mol_link_max",text = "Max links")
            row = box.row()
            row.prop(psys.settings,"mol_link_friction",text = "Link friction")
            row = box.row()
            row.prop(psys.settings,"mol_link_tension",text = "Tension")
            row.prop(psys.settings,"mol_link_tensionrand",text = "Rand Tension")
            row = box.row()
            row.prop(psys.settings,"mol_link_stiff",text = "Stiff")
            row.prop(psys.settings,"mol_link_stiffrand",text = "Rand Stiff")
            #row = subbox.row()
            #row.prop(psys.settings,"mol_link_stiffexp",text = "Exponent")
            #row.label(text = "")
            row = box.row()
            row.prop(psys.settings,"mol_link_damp",text = "Damping")
            row.prop(psys.settings,"mol_link_damprand",text = "Rand Damping")
            row = box.row()
            row.prop(psys.settings,"mol_link_broken",text = "broken")
            row.prop(psys.settings,"mol_link_brokenrand",text = "Rand Broken")
            row = box.row()
            if psys.settings.texture_slots[0]:
                row.active = True
                row.enabled = True
                row.prop(psys.settings, "mol_bake_weak_map", text="WeakMap")
                row = box.row()
                row.label(text="Using Texture " + psys.settings.texture_slots[0].texture.name)
            else:
                row.label(text="No Texture found in Particle textures[0]")
                row = box.row()
                row.active = False
                row.enabled = False
                row.prop(psys.settings, "mol_bake_weak_map", text="WeakMap")
            box = layout.box()
            row = box.row()
            row.prop(psys.settings,"mol_link_samevalue", text="Same values for compression/expansion")
            row = box.row()

            if not psys.settings.mol_link_samevalue:
                row.prop(psys.settings,"mol_link_estiff",text = "E Stiff")
                row.prop(psys.settings,"mol_link_estiffrand",text = "Rand E Stiff")
                row = box.row()
                #row.enabled  = not psys.settings.mol_link_samevalue
                #row.prop(psys.settings,"mol_link_estiffexp",text = "E Exponent")
                #row.label(text = "")
                row = box.row()
                row.prop(psys.settings,"mol_link_edamp",text = "E Damping")
                row.prop(psys.settings,"mol_link_edamprand",text = "Rand E Damping")
                row = box.row()
                row.prop(psys.settings,"mol_link_ebroken",text = "E broken")
                row.prop(psys.settings,"mol_link_ebrokenrand",text = "Rand E Broken")

        ###   Relinking   ###

        box = layout.box()
        row = box.row()
        row.label(text = "ReLinks :")
        #row.prop(psys.settings,"mol_selfrelink_active", icon = 'CONSTRAINT', text = "Self Relink")
        #row.prop(psys.settings,"mol_other_link_active", icon = 'CONSTRAINT', text = "Relink with Others")
        #if psys.settings.mol_other_link_active: # or psys.settings.mol_selfrelink_active:# or psys.settings.mol_otherrelink_active:
        row = box.row()
        row.prop(psys.settings,"mol_relink_chance",text = "% linking")
        row.prop(psys.settings,"mol_relink_chancerand",text = "Rand % linking")
        
        if psys.settings.mol_relink_chance > 0.0:
            row = box.row()
            row.prop(psys.settings,"mol_relink_max",text = "Max links")
            row = box.row()
            row.prop(psys.settings,"mol_relink_tension",text = "Tension")
            row.prop(psys.settings,"mol_relink_tensionrand",text = "Rand Tension")
            row = box.row()
            row.prop(psys.settings,"mol_relink_stiff",text = "Stiff")
            row.prop(psys.settings,"mol_relink_stiffrand",text = "Rand Stiff")
            #row = subbox.row()
            #row.prop(psys.settings,"mol_relink_stiffexp",text = "Exp")
            #row.label(text = "")
            row = box.row()
            row.prop(psys.settings,"mol_relink_damp",text = "Damping")
            row.prop(psys.settings,"mol_relink_damprand",text = "Rand Damping")
            row = box.row()
            row.prop(psys.settings,"mol_relink_broken",text = "broken")
            row.prop(psys.settings,"mol_relink_brokenrand",text = "Rand broken")
            row = box.row()
            row.prop(psys.settings,"mol_relink_samevalue", text = "Same values for compression/expansion")
            row = box.row()

        if not psys.settings.mol_relink_samevalue:
            row.prop(psys.settings,"mol_relink_estiff",text = "E Stiff")
            row.prop(psys.settings,"mol_relink_estiffrand",text = "Rand E Stiff")
            row = box.row()
            row.prop(psys.settings,"mol_relink_edamp",text = "E Damping")
            row.prop(psys.settings,"mol_relink_edamprand",text = "Rand E Damping")
            row = box.row()
            row.prop(psys.settings,"mol_relink_ebroken",text = "E broken")
            row.prop(psys.settings,"mol_relink_ebrokenrand",text = "Rand E broken")

        box = layout.box()
        row = box.row()
        if obj.data.uv_layers.active != None:
            row.active = True
            row.prop(psys.settings,"mol_bakeuv",text = "Bake UV (current: " + str(obj.data.uv_layers.active.name) + ")" )
        else:
            row.active = False
            if row.active == False:
                row.prop(psys.settings,"mol_bakeuv",text = "Bake UV (current: None)" )
        row = box.row()
        row.active = False #psys.settings.mol_bakeuv
        row.prop(psys.settings,"mol_bakeuv_global",text = "Global")
        row = box.row()

class MolecularAdd(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_add"
    bl_label = "Add Molecular object"
    bl_description = "Add active object as Molecular"
    bl_options = {'REGISTER'}

    @classmethod
    def poll(cls, context):
        return context.object.particle_systems.active

    def execute(self, context):
        obj = context.object
        psys = obj.particle_systems.active
        psys.settings.mol_active = True

        return {'FINISHED'}

class MolecularRemove(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_remove"
    bl_label = "Remove Molecular object"
    bl_description = "Remove Molecular settings from Object"
    bl_options = {'REGISTER'}

    def execute(self, context):
        obj = context.object

        psys = obj.particle_systems.active
        psys.settings.mol_active = False
        
        return {'FINISHED'}


def append_to_PHYSICS_PT_add_panel(self, context):
    obj = context.object

    if not obj.type == 'MESH':
        return

    psys = obj.particle_systems.active
    if not psys:
        return
    column = self.layout.column(align=True)
    #split = column.split(factor=1.0)
    #column_left = split.column()
    #column_right = split.column()
    col = column

    #for the data
    psys_eval = get_object(context, obj).particle_systems.active

    if psys.settings.mol_active:

        col.operator(
                "molecular_operators.molecular_remove",
                 text="Molecular",
                 icon='X'
                )
    else:

        col.operator(
                "molecular_operators.molecular_add",
                text="Molecular",
                icon='MOD_PARTICLES'
                )


panel_classes = (MS_PT_MolecularPanel,MolecularAdd, MolecularRemove, MS_PT_MolecularHelperPanel, MS_PT_MolecularCreatePanel, MS_PT_MolecularInspectPanel, MS_PT_MolecularDonorPanel)
