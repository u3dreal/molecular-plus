import bpy
import blf
import math

from mathutils import Vector
from mathutils.geometry import barycentric_transform as barycentric
from time import sleep, strftime, gmtime, time

from . import simulate
from molecular_core import core
from .utils import get_object, destroy_caches, update_progress


class MolRemoveCollider(bpy.types.Operator):
    bl_idname = "object.mol_remove_collision"
    bl_label = "Remove Collision"

    def execute(self, context):
        bpy.ops.object.modifier_remove(modifier="Collision")
        del context.object["mol_type"]

        return {"FINISHED"}


class MolSet_Substeps(bpy.types.Operator):
    bl_idname = "object.mol_set_subs"
    bl_label = "Set SubSteps"

    def execute(self, context):
        parcount = 0
        for obj in bpy.data.objects:
            if obj.particle_systems.active != None:
                for psys in get_object(context, obj).particle_systems:
                    # print(psys.name)
                    parcount += len(psys.particles)

        context.scene.mol_parnum = parcount

        if context.scene.mol_autosubsteps:
            diff = psys.settings.mol_var3 / psys.settings.mol_var1
            factor = parcount ** (1 / 3) / psys.settings.mol_var1 ** (1 / 3)
            newsubstep = int(round(factor * psys.settings.mol_var2))
            context.scene.mol_substep = newsubstep

        return {"FINISHED"}


class MolSimulate(bpy.types.Operator):
    bl_idname = "object.mol_simulate"
    bl_label = "Simulate"
    resume: bpy.props.BoolProperty(
        name="Resume bake", description="Resume Sim", default=False
    )

    def execute(self, context):
        scene = context.scene
        if not self.resume:
            for ob in bpy.data.objects:
                destroy_caches(ob)

        print("Molecular Sim Start" + "-" * 50)
        mol_stime = time()

        scene.mol_simrun = True
        scene.mol_minsize = 1000000000.0
        scene.mol_newlink = 0
        scene.mol_deadlink = 0
        scene.mol_totallink = 0
        scene.mol_totaldeadlink = 0
        scene.mol_timeremain = "...Simulating..."
        scene.mol_old_currentframe = scene.frame_current
        scene.mol_old_startframe = scene.frame_start
        scene.mol_old_endframe = scene.frame_end
        mol_substep = scene.mol_substep
        scene.render.frame_map_old = 1
        scene.render.frame_map_new = mol_substep + 1

        if self.resume:
            scene.frame_start = scene.mol_old_currentframe
        if scene.frame_start != 1:
            scene.frame_start = scene.frame_start * (mol_substep + 1)

        scene.frame_end = scene.mol_old_endframe * (mol_substep + 1)

        scene.frame_set(frame=scene.frame_start)

        if scene.timescale != 1.0:
            fps = scene.render.fps * scene.timescale
        else:
            fps = scene.render.fps

        cpu = scene.mol_cpu
        mol_exportdata = context.scene.mol_exportdata
        mol_exportdata.clear()
        mol_exportdata.append([fps, mol_substep, 0, 0, cpu])
        mol_stime = time()
        simulate.pack_data(context, True)
        etime = time()
        print("  PackData took " + str(round(etime - mol_stime, 3)) + "sec")
        mol_stime = time()
        mol_report = core.init(mol_exportdata)
        etime = time()
        print("  Export time took " + str(round(etime - mol_stime, 3)) + "sec")
        print("  total numbers of particles: " + str(mol_report))
        print("  start processing:")
        bpy.ops.wm.mol_simulate_modal(resume=self.resume)
        return {"FINISHED"}


class MolApplyUVcache(bpy.types.Operator):
    bl_idname = "object.mol_uv_cache_apply"
    bl_label = "Mol Apply Cached UV"
    uv_object_name: bpy.props.StringProperty()

    def execute(self, context):
        ob = bpy.data.objects[self.uv_object_name]
        obj = get_object(context, ob)
        print("applying uv from:", obj.name)
        psys = obj.particle_systems.active
        psys.settings.use_rotations = True
        psys.settings.angular_velocity_mode = "RAND"
        psys.particles.foreach_set("angular_velocity", obj["uv_cache"])
        print("applied cached uv on:", psys.settings.name)
        return {"FINISHED"}


class MolCacheGlobalUV(bpy.types.Operator):
    bl_idname = "object.mol_cache_global_uv"
    bl_label = "Mol Cache global UV"

    def execute(self, context):
        obj = get_object(context, context.object)
        if len(context.view_layer.objects.selected) == 2:
            uv_obj = get_object(context, context.view_layer.objects.selected[1])
        else:
            uv_obj = obj

        print("start bake global uv from:", uv_obj.name)
        psys = obj.particle_systems.active
        psys.settings.mol_bakeuv = True
        par_uv = []
        for par in psys.particles:
            newuv = (par.location @ uv_obj.matrix_world) - uv_obj.location
            par_uv.append(newuv[0])
            par_uv.append(newuv[1])
            par_uv.append(newuv[2])

        context.object["uv_cache"] = par_uv
        context.object.particle_systems.active.settings.mol_bakeuv = True
        print("global uv cached on:", obj.name)
        return {"FINISHED"}


class MolCacheUV(bpy.types.Operator):
    bl_idname = "object.mol_cache_active_uv"
    bl_label = "Mol Cache UV"

    def execute(self, context):
        ob = context.object
        obj = get_object(context, ob)

        if len(context.view_layer.objects.selected) == 2:
            u_obj = context.view_layer.objects.selected[0]
            bpy.context.view_layer.objects.active = u_obj
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
            uv_obj = get_object(context, u_obj)
        else:
            uv_obj = obj
        psys = obj.particle_systems.active
        if not uv_obj.data.uv_layers.active:
            return {"FINISHED"}

        print("  start bake uv from:", uv_obj.name)

        obdata = uv_obj.data.copy()
        obj2 = bpy.data.objects.new(name="mol_uv_temp", object_data=obdata)
        obj2.matrix_world = uv_obj.matrix_world

        context.scene.collection.objects.link(obj2)
        mod = obj2.modifiers.new("tri_for_uv", "TRIANGULATE")
        mod.ngon_method = "BEAUTY"
        mod.quad_method = "BEAUTY"

        ctx = bpy.context.copy()
        ctx["object"] = obj2
        if bpy.app.version[0] == 4:
            with context.temp_override(**ctx):
                bpy.ops.object.modifier_apply(modifier=mod.name)
        else:
            bpy.ops.object.modifier_apply(ctx, modifier=mod.name)
        context.view_layer.update()
        par_uv = []
        me = obj2.data

        for par in psys.particles:
            parloc = (par.location @ obj2.matrix_world) - obj2.location

            point = obj2.closest_point_on_mesh(parloc)
            vindex1 = me.polygons[point[3]].vertices[0]
            vindex2 = me.polygons[point[3]].vertices[1]
            vindex3 = me.polygons[point[3]].vertices[2]

            v1 = (obj2.matrix_world @ me.vertices[vindex1].co).to_tuple()
            v2 = (obj2.matrix_world @ me.vertices[vindex2].co).to_tuple()
            v3 = (obj2.matrix_world @ me.vertices[vindex3].co).to_tuple()

            uvindex1 = me.polygons[point[3]].loop_start + 0
            uvindex2 = me.polygons[point[3]].loop_start + 1
            uvindex3 = me.polygons[point[3]].loop_start + 2
            uv1 = me.uv_layers.active.data[uvindex1].uv.to_3d()
            uv2 = me.uv_layers.active.data[uvindex2].uv.to_3d()
            uv3 = me.uv_layers.active.data[uvindex3].uv.to_3d()

            p = obj2.matrix_world @ point[1]

            v1 = Vector(v1)
            v2 = Vector(v2)
            v3 = Vector(v3)
            uv1 = Vector(uv1)
            uv2 = Vector(uv2)
            uv3 = Vector(uv3)
            newuv = barycentric(p, v1, v2, v3, uv1, uv2, uv3)

            parloc = par.location @ obj2.matrix_world

            dist = (
                Vector((parloc[0] - p[0], parloc[1] - p[1], parloc[2] - p[2]))
            ).length

            newuv[2] = dist

            par_uv.append(newuv[0])
            par_uv.append(newuv[1])
            par_uv.append(newuv[2])

        context.scene.collection.objects.unlink(obj2)
        bpy.data.objects.remove(obj2)
        bpy.data.meshes.remove(obdata)

        ob["uv_cache"] = par_uv
        bpy.context.view_layer.objects.active = ob
        context.object.particle_systems.active.settings.mol_bakeuv = True
        print("uv cached on:", obj.name)

        return {"FINISHED"}


def convert_time_to_string(total_time):
    HOUR_IN_SECONDS = 60 * 60
    MINUTE_IN_SCEONDS = 60
    time_string = ""
    if total_time > 10.0:
        total_time = int(total_time)
        if total_time > MINUTE_IN_SCEONDS and total_time <= HOUR_IN_SECONDS:
            minutes = total_time // MINUTE_IN_SCEONDS
            seconds = total_time - minutes * MINUTE_IN_SCEONDS
            time_string = "{0} min {1} sec".format(minutes, seconds)
        elif total_time <= MINUTE_IN_SCEONDS:
            time_string = "{0} seconds".format(total_time)
        elif total_time > HOUR_IN_SECONDS:
            hours = total_time // HOUR_IN_SECONDS
            minutes = total_time - (total_time // HOUR_IN_SECONDS) * HOUR_IN_SECONDS
            time_string = "{0} hours {1} min".format(hours, minutes)
    else:
        seconds = round(total_time, 2)
        time_string = "{0} seconds".format(seconds)
    return time_string


def draw_callback_px(self, context):
    """Draw on the viewports"""
    # BLF drawing routine
    font_id = 0
    texts = bpy.context.scene.mol_progress.split("\n")
    size = bpy.context.preferences.addons[__package__].preferences.log_size
    blf.color(font_id, 1.0, 1.0, 1.0, 0.5)
    for i, text in enumerate(texts):
        blf.position(font_id, size, size * (i + 1), 0)
        blf.size(font_id, size - 10, 50)
        blf.draw(font_id, text)


class MolSimulateModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""

    bl_idname = "wm.mol_simulate_modal"
    bl_label = "Simulate Molecular"
    _timer = None
    _draw_handler = None
    _profiling = False
    resume: bpy.props.BoolProperty()

    def check_bake_uv(self, context):
        # bake the UV in the beginning
        scene = context.scene
        frame_old = scene.frame_current
        for ob in bpy.data.objects:
            obj = get_object(context, ob)
            for psys in obj.particle_systems:
                if psys.settings.mol_bakeuv and "uv_cache" in ob:
                    scene.frame_set(frame=int(psys.settings.frame_start))
                    bpy.ops.object.mol_uv_cache_apply(
                        "INVOKE_DEFAULT", uv_object_name=obj.name
                    )

        scene.frame_set(frame=frame_old)

    def modal(self, context, event):
        scene = context.scene
        frame_end = scene.frame_end
        frame_current = scene.frame_current
        if frame_current == frame_end - 1:
            update_progress("finished", 1)

        ###### ESC END #######
        if event.type == "ESC" or frame_current == frame_end or scene.mol_cancel:
            if frame_current == frame_end and scene.mol_bake:
                bpy.ops.object.bake_sim()

            scene.render.frame_map_new = 1
            scene.frame_start = scene.mol_old_startframe
            scene.frame_end = scene.mol_old_endframe
            core.memfree()
            scene.mol_simrun = False
            mol_exportdata = scene.mol_exportdata
            mol_exportdata.clear()
            print("-" * 50 + "Molecular Sim end")

            if frame_current == frame_end and scene.mol_render:
                print("Rendering ..................")
                bpy.ops.render.render(animation=True)

            scene.frame_set(
                frame=int(math.floor((scene.frame_current / (scene.mol_substep + 1))))
            )
            sleep(0.1)
            return self.cancel(context)

        ###### TIMER #######
        if event.type == "TIMER":
            mol_substep = scene.mol_substep
            framesubstep = frame_current / (mol_substep + 1)

            if framesubstep == int(framesubstep):
                update_progress("Simulating", frame_current / frame_end)
                stime = time()

            context.scene.mol_exportdata.clear()
            simulate.pack_data(context, False)
            if framesubstep == int(framesubstep):
                etime = time()
                packtime = etime - stime
                stime2 = time()

            mol_importdata = core.simulate(context.scene.mol_exportdata)
            if framesubstep == int(framesubstep):
                etime2 = time()
                moltime = etime2 - stime2
                stime3 = time()
            i = 0
            for ob in bpy.data.objects:
                obj = get_object(context, ob)
                for psys in obj.particle_systems:
                    if psys.settings.mol_active and len(psys.particles):
                        psys.particles.foreach_set("velocity", mol_importdata[1][i])
                        # psys.particles.foreach_set('location', mol_importdata[0][i])
                        i += 1

            scene.mol_newlink = 0
            scene.mol_deadlink = 0

            scene.mol_newlink += mol_importdata[2]
            scene.mol_deadlink += mol_importdata[3]
            scene.mol_totallink = mol_importdata[4]
            scene.mol_totaldeadlink = mol_importdata[5]
            scene.frame_set(frame=frame_current + 1)

            if framesubstep == int(framesubstep):
                print("    frame " + str(int(framesubstep) + 1) + ":")
                print("      links created:", scene.mol_newlink)
                if scene.mol_totallink:
                    print("      links broken :", scene.mol_deadlink)
                    print(
                        "      total links:",
                        scene.mol_totallink - scene.mol_totaldeadlink,
                        "/",
                        scene.mol_totallink,
                        " (",
                        round(
                            (
                                (
                                    (scene.mol_totallink - scene.mol_totaldeadlink)
                                    / scene.mol_totallink
                                )
                                * 100
                            ),
                            2,
                        ),
                        "%)",
                    )
                #
                etime3 = time()
                blendertime = etime3 - stime3
                print(
                    "      Pack             : "
                    + str(round(packtime * (mol_substep + 1), 3))
                    + " sec"
                )
                print(
                    "      Molecular        : "
                    + str(round(moltime * (mol_substep + 1), 3))
                    + " sec"
                )
                print(
                    "      Blender          : "
                    + str(round(blendertime * (mol_substep + 1), 3))
                    + " sec"
                )
                print(
                    "      Total Frame      : "
                    + str(
                        round((blendertime + packtime + moltime) * (mol_substep + 1), 3)
                    )
                    + " sec"
                )

                remain = (
                    (blendertime + packtime + moltime)
                    * (mol_substep + 1)
                    * (float(scene.mol_old_endframe) - (framesubstep + 1.0))
                )
                days = int(strftime("%d", gmtime(remain))) - 1
                scene.mol_timeremain = strftime(
                    str(days) + " d %H h %M m %S s", gmtime(remain)
                )
                print("      Remaining estimated:", scene.mol_timeremain)

        return {"PASS_THROUGH"}

    def execute(self, context):
        # start time
        self.st = time()
        if not self.resume:
            self.check_bake_uv(context)
        self._timer = context.window_manager.event_timer_add(
            0.000000001, window=context.window
        )
        update_progress("Initializing", 0.0001)

        if (
            bpy.context.preferences.addons[__package__].preferences.show_stats
            and context.area.type == "VIEW_3D"
        ):
            self._handler = bpy.types.SpaceView3D.draw_handler_add(
                draw_callback_px, (self, context), "WINDOW", "POST_PIXEL"
            )

        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def cancel(self, context):
        # total time
        tt = time() - self.st
        tt_s = convert_time_to_string(tt)
        update_progress("Finished", 1)
        print("Total time : " + tt_s + " sec")

        self.report({"INFO"}, "Total time: {0}".format(tt_s))
        if bpy.context.preferences.addons[__package__].preferences.show_stats:
            bpy.types.SpaceView3D.draw_handler_remove(self._handler, "WINDOW")
        context.window_manager.event_timer_remove(self._timer)
        bpy.context.scene.mol_cancel = False
        obj = get_object(context, context.object)
        return {"CANCELLED"}


class MolClearCache(bpy.types.Operator):
    """Clear Particle Cache"""

    bl_idname = "object.clear_pcache"
    bl_label = "Clear Particle Cache"

    def execute(self, context):
        bpy.ops.ptcache.free_bake_all()
        for ob in bpy.data.objects:
            obj = get_object(context, ob)
            for psys in obj.particle_systems:
                if psys.settings.mol_active:
                    ccache = context.object.particle_systems.active.settings.use_modifier_stack
                    context.object.particle_systems.active.settings.use_modifier_stack = ccache

        context.scene.frame_current = 1

        return {"FINISHED"}


class MolResetCache(bpy.types.Operator):
    """Clear Particle Cache"""

    bl_idname = "object.reset_pcache"
    bl_label = "Clear Particle Cache"

    def execute(self, context):
        for ob in bpy.data.objects:
            obj = get_object(context, ob)
            for psys in obj.particle_systems:
                if psys.settings.mol_active:
                    ccache = context.object.particle_systems.active.settings.use_modifier_stack
                    context.object.particle_systems.active.settings.use_modifier_stack = ccache
                    context.scene.frame_current = 1

        return {"FINISHED"}


class MolCancelSim(bpy.types.Operator):
    """Cancel Particle Simulation"""

    bl_idname = "object.cancel_sim"
    bl_label = "Cancel Particle Simulation"

    def execute(self, context):
        context.scene.mol_cancel = True
        context.scene.mol_simrun = False

        return {"FINISHED"}


class MolBakeCache(bpy.types.Operator):
    """Bake Cache"""

    bl_idname = "object.bake_sim"
    bl_label = "Bake Particle Simulation"

    def execute(self, context):
        context_override = context.copy()
        for ob in bpy.data.objects:
            obj = get_object(context, ob)
            for psys in obj.particle_systems:
                if psys.settings.mol_active and len(psys.particles):
                    context_override["point_cache"] = psys.point_cache
                    if bpy.app.version[0] >= 4:
                        with context.temp_override(**context_override):
                            bpy.ops.ptcache.bake_from_cache()
                    else:
                        bpy.ops.ptcache.bake_from_cache(context_override)
        return {"FINISHED"}


class MolResumeSim(bpy.types.Operator):
    """Cancel Particle Simulation"""

    bl_idname = "object.resume_sim"
    bl_label = "Resume Particle Simulation from Current frame"

    def execute(self, context):
        bpy.ops.object.mol_simulate(resume=True)
        return {"FINISHED"}


class MolToolsConvertGeo(bpy.types.Operator):
    """Convert particles to Particle Instance Mesh"""

    bl_idname = "object.convert_to_geo"
    bl_label = "Convert for GeoNodes"

    def add_nodetree(self, context, node_tree):
        out_node = node_tree.nodes["Group Output"]
        out_node.location.x += 400

        in_node = node_tree.nodes["Group Input"]
        if bpy.app.version[0] == 4:
            node_tree.interface.new_socket(
                name="Material",
                in_out="INPUT",
                socket_type="NodeSocketMaterial",
            )
        else:
            node_tree.inputs.new(type="NodeSocketMaterial", name="Material")

        mesh2points = node_tree.nodes.new(type="GeometryNodeMeshToPoints")

        setMaterial = node_tree.nodes.new(type="GeometryNodeSetMaterial")
        setMaterial.location.x += 200

        node_tree.links.new(in_node.outputs["Geometry"], mesh2points.inputs["Mesh"])
        node_tree.links.new(
            mesh2points.outputs["Points"], setMaterial.inputs["Geometry"]
        )
        node_tree.links.new(
            setMaterial.outputs["Geometry"], out_node.inputs["Geometry"]
        )
        node_tree.links.new(setMaterial.inputs["Material"], in_node.outputs["Material"])

    def execute(self, context):
        obj = context.object
        psyss = obj.particle_systems.active.settings

        bpy.ops.mesh.primitive_plane_add(
            size=2,
            enter_editmode=False,
            align="WORLD",
            location=(0, 0, 0),
            scale=(1, 1, 1),
        )
        bpy.ops.object.editmode_toggle()
        bpy.ops.mesh.select_all(action="SELECT")
        bpy.ops.mesh.merge(type="CENTER")
        bpy.ops.object.editmode_toggle()
        bpy.ops.object.modifier_add(type="PARTICLE_INSTANCE")
        bpy.context.object.modifiers["ParticleInstance"].object = obj
        bpy.context.object.modifiers["ParticleInstance"].show_dead = False
        bpy.context.object.modifiers["ParticleInstance"].show_unborn = False

        bpy.ops.node.new_geometry_nodes_modifier()

        iobj = context.object
        iobj.name = obj.name + "_geo_instance"

        # eobj = get_object(context, obj)
        # particles = eobj.particle_systems.active.particles
        # par_uvs = np.zeros(len(particles) * 3, dtype=np.float32)
        # particles.foreach_get('angular_velocity', par_uvs)

        # iobj.data.attributes.new('uvs', 'FLOAT_VECTOR', 'POINT')
        # eiobj = get_object(context, iobj)
        # attr = eiobj.data.attributes['uvs']
        # attr.data.foreach_set('vector', par_uvs)

        # par_size = np.zeros(len(particles), dtype=np.float32)
        # particles.foreach_get('size', par_size)
        # iobj.data.attributes.new('size', 'FLOAT', 'POINT')
        # attr = eiobj.data.attributes['size']
        # attr.data.foreach_set('value', par_size)

        nodetree = iobj.modifiers["GeometryNodes"].node_group
        self.add_nodetree(context, nodetree)
        nodetree.nodes["Mesh to Points"].inputs[
            "Radius"
        ].default_value = psyss.particle_size
        bpy.ops.object.select_all(action="DESELECT")
        bpy.context.view_layer.objects.active = obj
        obj.select_set(True)

        return {"FINISHED"}


operator_classes = (
    MolSimulateModal,
    MolSimulate,
    MolApplyUVcache,
    MolCacheGlobalUV,
    MolCacheUV,
    MolSet_Substeps,
    MolClearCache,
    MolResetCache,
    MolCancelSim,
    MolBakeCache,
    MolResumeSim,
    MolRemoveCollider,
    MolToolsConvertGeo,
)
