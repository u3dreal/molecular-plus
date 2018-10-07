
import bpy


class MolecularPanel(bpy.types.Panel):
    """Creates a Panel in the Object properties window"""
    bl_label = "Molecular Script"
    bl_idname = "OBJECT_PT_molecular"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "particle"

    @classmethod
    def poll(cls, context):
        return context.object.particle_systems.active

    def draw_header(self, context):
        layout = self.layout
        obj = context.object
        psys = obj.particle_systems.active
        row = layout.row()
        if not psys is None:
            row.prop(psys.settings, "mol_active", text='')

    def draw(self, context):
        layout = self.layout
        scn = bpy.context.scene
        obj = context.object
        psys = obj.particle_systems.active
        if psys is None:
            return
        layout.enabled = psys.settings.mol_active
        row = layout.row()
        row.label(text = "Density:")
        box = layout.box()
        box.prop(
            psys.settings,
            "mol_density_active",
            text="Calculate particles weight by density"
        )
        subbox = box.box()
        subbox.enabled  = psys.settings.mol_density_active
        row = subbox.row()
        row.prop(psys.settings, "mol_matter", text="Preset:")
        row = subbox.row()

        if int(psys.settings.mol_matter) == 0:
            row.enabled = True
        elif int(psys.settings.mol_matter) >= 1:
            row.enabled = False

        row.prop(psys.settings, "mol_density", text = "Kg per CubeMeter:")
        pmass = (psys.settings.particle_size ** 3) * psys.settings.mol_density
        row = subbox.row()
        weight_text = "Total system approx weight: {0:.4} kg".format(
            len(psys.particles) * pmass
        )
        row.label(icon ="INFO", text=weight_text) 
        row = layout.row()
        row.label(text = "Collision:")
        box = layout.box()
        box.prop(
            psys.settings,
            "mol_selfcollision_active",
            text="Activate Self Collision"
        )
        box.prop(
            psys.settings,
            "mol_othercollision_active",
            text="Activate Collision with others"
        )
        box.prop(
            psys.settings,
            "mol_collision_group",
            text="Collide only with:"
        )
        box.prop(
            psys.settings,
            "mol_friction",
            text="Friction:"
        )
        box.prop(
            psys.settings,
            "mol_collision_damp",
            text = "Damping:"
        )

        row = layout.row()
        row.label(text="Links:")
        box = layout.box()
        box.prop(
            psys.settings,
            "mol_links_active",
            text="Activate Particles linking"
        )
        box.prop(
            psys.settings,
            "mol_other_link_active",
            text="Activate Particles linking with Others"
        )
        box.prop(
            psys.settings,
            "mol_link_group",
            text="Linking only with:"
        )

        subbox = box.box()
        subbox.enabled  = psys.settings.mol_links_active
        subbox.label(text="Initial Linking (at birth):")
        row = subbox.row()
        row.prop(psys.settings, "mol_link_length", text="search length")
        row.prop(psys.settings, "mol_link_rellength", text="Relative")
        row = subbox.row()
        row.prop(psys.settings, "mol_link_max", text="Max links")
        row = subbox.row()
        row.prop(psys.settings, "mol_link_friction", text="Link friction")
        layout.separator()
        row = subbox.row()
        row.prop(psys.settings, "mol_link_tension", text="Tension")
        row.prop(psys.settings, "mol_link_tensionrand", text="Rand Tension")
        row = subbox.row()
        row.prop(psys.settings, "mol_link_stiff", text="Stiff")
        row.prop(psys.settings, "mol_link_stiffrand", text="Rand Stiff")
        #row = subbox.row()
        #row.prop(psys.settings, "mol_link_stiffexp", text="Exponent")
        row = subbox.row()
        row.prop(psys.settings, "mol_link_damp", text="Damping")
        row.prop(psys.settings, "mol_link_damprand", text="Rand Damping")
        row = subbox.row()
        row.prop(psys.settings, "mol_link_broken", text="broken")
        row.prop(psys.settings, "mol_link_brokenrand", text="Rand Broken")
        row = subbox.row()
        layout.separator()
        row = subbox.row()
        row.prop(
            psys.settings,
            "mol_link_samevalue",
            text="Same values for compression/expansion"
        )
        row = subbox.row()
        row.enabled = not psys.settings.mol_link_samevalue
        row.prop(psys.settings, "mol_link_estiff", text="E Stiff")
        row.prop(psys.settings, "mol_link_estiffrand", text="Rand E Stiff")
        #row = subbox.row()
        #row.enabled = not psys.settings.mol_link_samevalue
        #row.prop(psys.settings, "mol_link_estiffexp", text="E Exponent")
        row = subbox.row()
        row.enabled = not psys.settings.mol_link_samevalue
        row.prop(psys.settings, "mol_link_edamp", text="E Damping")
        row.prop(psys.settings, "mol_link_edamprand", text="Rand E Damping")
        row = subbox.row()
        row.enabled = not psys.settings.mol_link_samevalue
        row.prop(psys.settings, "mol_link_ebroken", text="E broken")
        row.prop(psys.settings, "mol_link_ebrokenrand", text="Rand E Broken")

        subbox = box.box()
        subbox.active = psys.settings.mol_links_active
        subbox.label(text="New Linking (at collision):")
        row = subbox.row()
        row.prop(psys.settings, "mol_relink_group", text="Only links with:")
        row = subbox.row()
        row.prop(psys.settings, "mol_relink_chance", text="% linking")
        row.prop(psys.settings, "mol_relink_chancerand", text="Rand % linking")
        row = subbox.row()
        row.prop(psys.settings, "mol_relink_max", text="Max links")
        row = subbox.row()
        layout.separator()
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_tension",text = "Tension")
        row.prop(psys.settings,"mol_relink_tensionrand",text = "Rand Tension")
        row = subbox.row()
        row.prop(psys.settings,"mol_relink_stiff",text = "Stiff")
        row.prop(psys.settings,"mol_relink_stiffrand",text = "Rand Stiff")
        #row = subbox.row()
        #row.prop(psys.settings, "mol_relink_stiffexp", text="Exp")
        row = subbox.row()
        row.prop(psys.settings, "mol_relink_damp", text="Damping")
        row.prop(psys.settings, "mol_relink_damprand", text="Rand Damping")
        row = subbox.row()
        row.prop(psys.settings, "mol_relink_broken", text="broken")
        row.prop(psys.settings, "mol_relink_brokenrand", text="Rand broken")
        row = subbox.row()
        layout.separator()
        row = subbox.row()
        row.prop(
            psys.settings,
            "mol_relink_samevalue",
            text="Same values for compression/expansion"
        )
        row = subbox.row()
        row.enabled = not psys.settings.mol_relink_samevalue
        row.prop(psys.settings, "mol_relink_estiff",text="E Stiff")
        row.prop(psys.settings, "mol_relink_estiffrand",text="Rand E Stiff")
        #row = subbox.row()
        #row.enabled = not psys.settings.mol_relink_samevalue
        #row.prop(psys.settings, "mol_relink_estiffexp", text="Exp")
        row = subbox.row()
        row.enabled = not psys.settings.mol_relink_samevalue
        row.prop(psys.settings, "mol_relink_edamp", text="E Damping")
        row.prop(psys.settings, "mol_relink_edamprand", text="Rand E Damping")
        row = subbox.row()
        row.enabled = not psys.settings.mol_relink_samevalue
        row.prop(psys.settings, "mol_relink_ebroken", text="E broken")
        row.prop(psys.settings, "mol_relink_ebrokenrand", text="Rand E broken")

        row = layout.row()
        row.label(text="UV's:")
        box = layout.box()
        row = box.row()

        if obj.data.uv_layers.active != None:
            row.prop(
                psys.settings,
                "mol_bakeuv",
                text="Bake UV at ending (current: \"{0}\")".format(
                    obj.data.uv_textures.active.name
                )
            )
        else:
            row.active = False
            row.prop(
                psys.settings,
                "mol_bakeuv",
                text="Bake UV at ending (current: None)"
            )

        row = layout.row()
        row.label(text='')
        row = layout.row()
        row.label(text="Simulate")
        row = layout.row()
        row.prop(scn, "frame_start", text="Start Frame")
        row.prop(scn, "frame_end", text="End Frame")
        #row = layout.row()
        #row.prop(scn,"mol_timescale_active",text = "Activate TimeScaling")
        #row = layout.row()
        #row.enabled = scn.mol_timescale_active
        #row.prop(scn,"timescale",text = "TimeScale")
        row = layout.row()
        row.prop(scn, "mol_substep", text="Substeps")
        row.label(text='')
        row = layout.row()
        row.label(text = "CPU used:")
        row.prop(scn, "mol_cpu", text="CPU")
        row = layout.row()
        row.prop(scn, "mol_bake", text="Bake all at ending")
        row.prop(scn, "mol_render", text="Render at ending")
        row = layout.row()

        if scn.mol_simrun == False and psys.point_cache.is_baked == False:
            row.enabled = True
            row.operator(
                "object.mol_simulate",
                icon='RADIO',
                text="Start Molecular Simulation"
            )
            row = layout.row()
            row.enabled = False
            row.operator("ptcache.free_bake_all", text="Free All Bakes")

        if psys.point_cache.is_baked == True and scn.mol_simrun == False:
            row.enabled = False
            row.operator(
                "object.mol_simulate",
                icon = 'RADIO',
                text="Simulation baked"
            )
            row = layout.row()
            row.enabled = True
            row.operator("ptcache.free_bake_all", text="Free All Bakes")

        if scn.mol_simrun == True:
            row.enabled = False
            row.operator(
                "object.mol_simulate",
                icon = 'RADIO',
                text="Process: {} left".format(scn.mol_timeremain)
            )
            row = layout.row()
            row.enabled = False
            row.operator("ptcache.free_bake_all", text="Free All Bakes")

        box = layout.box()
        row = box.row()
        box.enabled = True
        row.label(text="Molecular Tools:", icon='MODIFIER')
        subbox = box.box()
        row = subbox.row()
        row.label(text="Particle UV:")
        row = subbox.row()
        row.alignment = 'CENTER'
        row.label(icon='INFO', text="Set current particles position")
        row = subbox.row()
        row.alignment = 'CENTER'
        row.label(text="Has global or current uv in angular velocity")
        row = subbox.row()
        row.alignment = 'CENTER'
        row.label(text="Retrieve it with Cycles particle info node")
        row = subbox.row()
        row.operator(
            "object.mol_set_global_uv",
            icon='GROUP_UVS',
            text="Set Global UV"
        )
        row = subbox.row()

        if obj.data.uv_layers.active != None:
            row.operator(
                "object.mol_set_active_uv",
                icon='GROUP_UVS',
                text = "Set Active UV (current: \"{0}\")".format(
                    obj.data.uv_textures.active.name
                )
            )
        else:
            row.active = False
            row.operator(
                "object.mol_set_active_uv",
                icon='GROUP_UVS',
                text="Set Active UV ( no uvs found)"
            )

        subbox = box.box()
        row = subbox.row()
        row.label(text = "SUBSTEPS CALCULATOR:")
        row = subbox.row()
        row.label(
            icon='INFO',
            text="Current systems have: {} particles".format(psys.particles)
        )
        row = subbox.row()
        row.prop(psys.settings, "mol_var1", text="Current numbers of particles")
        row = subbox.row()
        row.prop(psys.settings,"mol_var2",text = "Current substep")
        row = subbox.row()
        row.prop(psys.settings,"mol_var3", text="Targeted numbers of particles")
        diff = (psys.settings.mol_var3 / psys.settings.mol_var1)
        factor = psys.settings.mol_var3 ** (1/3) / psys.settings.mol_var1 ** (1/3)
        newsubstep = int(round(factor * psys.settings.mol_var2))
        row = subbox.row()
        row.label(
            icon='FORWARD',
            text="You must set new substep to: {}".format(newsubstep)
        )
        row = subbox.row()
        row.label(
            icon='ERROR',
            text="Multiply particles size by: {}".format(round(1 / factor, 5))
        )
        row = subbox.row()
        row.label(
            icon='ERROR',
            text="Multiply others sys particle number by: {}".format(round(diff, 5))
        )

        box = layout.box()
        row = box.row()
        box.active = False
        box.alert = False
        row.alignment = 'CENTER'
        row.label(text="THANKS TO ALL DONATORS !")
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="If you want donate to support my work")
        row = box.row()
        row.alignment = 'CENTER'
        row.operator(
            "wm.url_open",
            text="click here to Donate",
            icon='URL'
        ).url = "www.pyroevil.com/donate/"
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text="or visit: ")
        row = box.row()
        row.alignment = 'CENTER'
        row.label(text = "www.pyroevil.com/donate/")
