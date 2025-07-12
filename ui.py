import bpy
from .utils import get_object

class MS_PT_MolecularHelperPanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Molecular+"
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

        if obj and obj.particle_systems.active:
            box = layout.box()
            #row = box.row()
            psys = get_object(context, obj).particle_systems.active
            parcount = len(psys.particles)

            if not scn.mol_simrun:
                row = box.row()
                row.label(text = "System : " + str(parcount))
                row.label(text = "Total : " + str(scn.mol_parnum))
                row.operator("object.mol_set_subs", text="", icon="FILE_REFRESH")
            else:
                row = box.row()
                row.label(text="Remaining : " + scn.mol_timeremain)

            box = layout.box()
            row = box.row()
            if not scn.mol_simrun and not psys.point_cache.is_baked:
                row.operator("object.mol_simulate", icon='PLAY', text="Simulate")
                if not psys.point_cache.info.startswith('1 frames') or psys.point_cache.info.startswith('0 frames'):
                    row = box.row()
                    row.operator('object.resume_sim', icon='TRACKING_FORWARDS', text="Resume")
                    row = box.row()
                    row.operator("object.bake_sim", icon='REC', text="Current Cache to Bake")

            if psys.point_cache.is_baked and not scn.mol_simrun:
                row.operator("object.clear_pcache", icon='CANCEL', text="Free All Bakes")

            if scn.mol_simrun:
                row.operator("object.cancel_sim", icon='PAUSE', text="Pause")

            row = box.row()
            row = row.split(factor=0.75, align=True)
            row.prop(scn, "mol_substep", text="SubSteps")
            row.prop(scn, "mol_autosubsteps", text="Auto", toggle = 1)
            row = box.row()
            row.prop(scn,"mol_cpu",text = "Threads")
            row.prop(scn, "timescale", text="Timescale", slider=True)

        else:
            box = layout.box()
            row = box.row()
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
        obj = context.object
        if obj and 'mol_type' in obj:
            return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        obj = context.object

        if obj['mol_type'] == 'COLLIDER':
            row = layout.row()
            row.label(text="Collision: " + obj.name)
            row.operator("object.mol_remove_collision",text="", icon='X')
            row = layout.row()
            row.prop(obj.collision, "damping_factor", text="Damping")
            row = layout.row()
            row.prop(obj.collision, "friction_factor", text="Friction")
            row = layout.row()
            row.prop(obj.collision, "stickiness", text="Stickiness", slider=True)

        if obj['mol_type'] == 'EMITTER' or obj['mol_type'] == 'PIN':
            psys = obj.particle_systems.active.settings
            row = layout.row()
            row.label(text="Active Object: " + obj.name)
            box = layout.box()
            row = box.row()
            row.prop(psys, "mol_voxel_size", text="Voxel Size")
            row = box.row()
            row.prop(psys, "size_random", text="Random")
            if psys.distribution == 'GRID':
                row = layout.row()
                #row = row.split(factor=0.15, align=True)
                row.label(text="Grid: ")
                box = layout.box()
                row = box.row()
                row = row.split(factor=0.3, align=True)
                row.prop(psys, "hexagonal_grid", text="Hex")
                row.prop(psys, "grid_random", text="Random")
            row = layout.row()
            row.label(text="Interaction: ")
            row = layout.row()
            row.prop(psys, "mol_selfcollision_active", icon = 'PROP_ON', text="")
            row.prop(psys, "mol_othercollision_active", icon='PIVOT_ACTIVE', text="")
            row.prop(psys, "mol_links_active", icon='CON_TRACKTO', text="")
            row.prop(psys, "mol_other_link_active", icon='GROUP_VERTEX', text="")


class MS_PT_MolecularCreatePanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Create"
    bl_idname = "OBJECT_PT_molecular_create"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"
    
    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj and obj.type == 'MESH':
            if 'mol_type' in obj:
                return False
            else:
                return True
        else:
            return False

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("molecular_operators.molecular_makeemitter", icon = 'MOD_PARTICLE_INSTANCE',text = "Emitter")
        if bpy.app.version[0] == 4 and bpy.app.version[1] >= 1:
            row.operator("molecular_operators.molecular_makegrid2d", icon='LIGHTPROBE_VOLUME', text="2D Grid")
        else:
            row.operator("molecular_operators.molecular_makegrid2d", icon = 'LIGHTPROBE_GRID',text = "2D Grid")
        row = layout.row()
        row.operator("molecular_operators.molecular_makegrid3d", icon = 'MOD_REMESH',text = "3D Grid")
        row.operator("molecular_operators.molecular_makecollider", icon = 'MOD_PHYSICS', text = "Collider")
        row=layout.row()
        row.operator('molecular_operators.molecular_maketape', icon='MOD_SIMPLIFY', text="Sticky Tape")
        row.operator('molecular_operators.molecular_makepin', icon='MOD_SIMPLIFY', text="Sticky Pin")


class MS_PT_MolecularUVToolsPanel(bpy.types.Panel):
    """Creates a Panel in the UVTool properties window"""
    bl_label = "UV Tools"
    bl_idname = "OBJECT_PT_molecular_uvtools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj and 'mol_type' in obj:
            if obj['mol_type'] == 'EMITTER':
                return True
            else:
                return False
        else:
            return False
    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.mol_cache_global_uv", text="Cache Object UVs", icon='GEOMETRY_NODES')
        row = layout.row()
        row.operator("object.mol_cache_active_uv", text="Cache active UVs", icon='GEOMETRY_NODES')
        if len(context.view_layer.objects.selected) == 2:
            uv_obj = get_object(context, context.view_layer.objects.selected[0])
        else:
            uv_obj = get_object(context, context.object)

        labeltext = "baking UV from " + uv_obj.name
        row = layout.row()
        row.label(text = labeltext)


class MS_PT_MolecularToolsPanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Tools"
    bl_idname = "OBJECT_PT_molecular_tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        if obj and 'mol_type' in obj:
            if obj['mol_type'] == 'EMITTER':
                return True
            else:
                return False
        else:
            return False

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.operator("object.convert_to_geo", text="Convert to Geonodes", icon='GEOMETRY_NODES')
        row = layout.row()
        row.prop(context.scene, "mol_render", text="Render after Bakeing")


class MS_PT_MolecularDonorPanel(bpy.types.Panel):
    """Creates a Panel in the Tool properties window"""
    bl_label = "Support"
    bl_idname = "OBJECT_PT_molecular_donations"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Molecular+"
    bl_options = {'HEADER_LAYOUT_EXPAND'}

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        row = box.row()
        row.operator("wm.url_open", text=" Donate ", icon='URL').url = "https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=J7W7MNCKVBYAA"
        row.operator("wm.url_open", text=" Discord ", icon='URL').url = "https://discord.com/invite/tAwvNEAfA3"
        row.operator("wm.url_open", text=" q3de ", icon='URL').url = "http://www.q3de.com/research/molecular"

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
            box.prop(psys.settings,"mol_collision_group",text = "Collision Group:")
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
            row.prop(psys.settings,"mol_relink_group",text = "Link Groups:")


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
            row.prop(psys.settings,"mol_link_broken",text = "Broken")
            row.prop(psys.settings,"mol_link_brokenrand",text = "Rand Broken")
            row = box.row()
            if psys.settings.texture_slots[0]:
                row.active = True
                row.enabled = True
                row.prop(psys.settings, "mol_bake_weak_map", text="Weakmap")
                row = box.row()
                row.label(text="Using Texture " + psys.settings.texture_slots[0].texture.name)
            else:
                row.label(text="No Texture found in Particle textures[0]")
                row = box.row()
                row.active = False
                row.enabled = False
                row.prop(psys.settings, "mol_bake_weak_map", text="Weakmap")
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
                row.prop(psys.settings,"mol_link_ebroken",text = "E Broken")
                row.prop(psys.settings,"mol_link_ebrokenrand",text = "Rand E Broken")

        ###   Relinking   ###

        box = layout.box()
        row = box.row()
        row.label(text = "Re-Links :")
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
            row.prop(psys.settings,"mol_relink_broken",text = "Broken")
            row.prop(psys.settings,"mol_relink_brokenrand",text = "Rand Broken")
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
            row.prop(psys.settings,"mol_relink_ebrokenrand",text = "Rand E Broken")

        box = layout.box()
        row = box.row()
        if 'uv_cache' in obj:
            row.enabled =True
            row.prop(psys.settings,"mol_bakeuv",text = "Bake UV")


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


panel_classes = (MS_PT_MolecularPanel,MolecularAdd, MolecularRemove, MS_PT_MolecularHelperPanel, MS_PT_MolecularCreatePanel, MS_PT_MolecularInspectPanel, MS_PT_MolecularUVToolsPanel, MS_PT_MolecularToolsPanel, MS_PT_MolecularDonorPanel)
