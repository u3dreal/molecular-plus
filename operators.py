try:
    from time import process_time as clock
except ImportError:
    from time import clock
from time import sleep, strftime, gmtime, time

import bpy
from mathutils import Vector
from mathutils.geometry import barycentric_transform as barycentric

from . import simulate, core
from .utils import get_object, destroy_caches


class MolRemoveCollider(bpy.types.Operator):
    bl_idname = "object.mol_remove_collision"
    bl_label = "Remove Collision"
    
    def execute(self, context):
        bpy.ops.object.modifier_remove(modifier='Collision')
        
        return {'FINISHED'}
    
class MolSet_Substeps(bpy.types.Operator):
    bl_idname = "object.mol_set_subs"
    bl_label = 'Set SubSteps'

    def execute(self, context):
        parcount = 0
        for obj in bpy.data.objects:
            if obj.particle_systems.active != None:
                psys = get_object(context, obj).particle_systems.active
                parcount += len(psys.particles)
                
        context.scene.mol_parnum = parcount
                
        if context.scene.mol_autosubsteps:
            diff = (psys.settings.mol_var3 / psys.settings.mol_var1)
            factor = (parcount**(1/3) / psys.settings.mol_var1**(1/3))
            newsubstep = int(round(factor * psys.settings.mol_var2))
            context.scene.mol_substep = newsubstep
            
        return {'FINISHED'}


class MolSimulate(bpy.types.Operator):
    bl_idname = "object.mol_simulate"
    bl_label = 'Simulate'

    def execute(self, context):
        for ob in bpy.data.objects:
            destroy_caches(ob)

        print('Molecular Sim Start' + '-' * 50)
        mol_stime = clock()
        scene = context.scene
        scene.mol_simrun = True
        scene.mol_minsize = 1000000000.0
        scene.mol_newlink = 0
        scene.mol_deadlink = 0
        scene.mol_totallink = 0
        scene.mol_totaldeadlink = 0
        scene.mol_timeremain = "...Simulating..."
        scene.frame_set(frame=scene.frame_start)
        scene.mol_old_endframe = scene.frame_end
        mol_substep = scene.mol_substep
        scene.render.frame_map_old = 1
        scene.render.frame_map_new = mol_substep + 1
        scene.frame_end *= mol_substep + 1

        if scene.mol_timescale_active == True:
            fps = scene.render.fps * scene.timescale
        else:
            fps = scene.render.fps

        cpu = scene.mol_cpu
        mol_exportdata = context.scene.mol_exportdata
        mol_exportdata.clear()
        mol_exportdata.append([fps, mol_substep, 0, 0, cpu])
        mol_stime = clock()
        simulate.pack_data(context, True)
        etime = clock()
        print("  PackData took " + str(round(etime - mol_stime, 3)) + "sec")
        mol_stime = clock()
        mol_report = core.init(mol_exportdata)
        etime = clock()
        print("  Export time took " + str(round(etime - mol_stime, 3)) + "sec")
        print("  total numbers of particles: " + str(mol_report))
        print("  start processing:")
        bpy.ops.wm.mol_simulate_modal()
        return {'FINISHED'}


class MolSetGlobalUV(bpy.types.Operator):
    bl_idname = "object.mol_set_global_uv"
    bl_label = "Mol Set UV"
    
    objname : bpy.props.StringProperty()
        
    def execute(self, context):
        scene = context.scene
        obj = get_object(context, context.view_layer.objects[self.objname])
        
        print('  start bake global uv from:', obj.name)

        psys = obj.particle_systems.active
        
        par_uv = []
        for par in psys.particles:
            
            newuv = (par.location @ obj.matrix_world)
            par_uv.append(newuv[0])
            par_uv.append(newuv[1])
            par_uv.append(newuv[2])
        
        
        psys.particles.foreach_set("angular_velocity", par_uv)
        print('         global uv baked on:', psys.settings.name)

        return {'FINISHED'}


class MolSetActiveUV(bpy.types.Operator):
    bl_idname = "object.mol_set_active_uv"
    bl_label = "Mol Set Active UV"
    
    objname : bpy.props.StringProperty()
        
    def execute(self, context):

        obj = get_object(context, context.view_layer.objects[self.objname])
        
        if not obj.data.uv_layers.active:
            return {'FINISHED'}

        print('  start bake uv from:', obj.name)

        obdata = obj.data.copy()
        obj2 = bpy.data.objects.new(name="mol_uv_temp", object_data=obdata)
        obj2.matrix_world = obj.matrix_world

        context.scene.collection.objects.link(obj2)
        mod = obj2.modifiers.new("tri_for_uv", "TRIANGULATE")
        mod.ngon_method = 'BEAUTY'
        mod.quad_method = 'BEAUTY'

        ctx = bpy.context.copy()
        ctx["object"] = obj2
        bpy.ops.object.modifier_apply(ctx, modifier=mod.name)

        context.view_layer.update()

        psys = obj.particle_systems.active
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

            dist = (Vector((
                parloc[0] - p[0],
                parloc[1] - p[1],
                parloc[2] - p[2]
            ))).length

            newuv[2] = dist
            
            par_uv.append(newuv[0])
            par_uv.append(newuv[1])
            par_uv.append(newuv[2])

        context.scene.collection.objects.unlink(obj2)
        bpy.data.objects.remove(obj2)
        bpy.data.meshes.remove(obdata)
        
        print('         uv baked on:', psys.settings.name)
      
        psys.settings.use_rotations = True
        psys.settings.angular_velocity_mode = 'RAND'
        
        psys.particles.foreach_set("angular_velocity", par_uv)
        
        return {'FINISHED'}


def convert_time_to_string(total_time):
    HOUR_IN_SECONDS = 60 * 60
    MINUTE_IN_SCEONDS = 60
    time_string = ''
    if total_time > 10.0:
        total_time = int(total_time)
        if total_time > MINUTE_IN_SCEONDS and total_time <= HOUR_IN_SECONDS:
            minutes = total_time // MINUTE_IN_SCEONDS
            seconds = total_time - minutes * MINUTE_IN_SCEONDS
            time_string = '{0} min {1} sec'.format(minutes, seconds)
        elif total_time <= MINUTE_IN_SCEONDS:
            time_string = '{0} seconds'.format(total_time)
        elif total_time > HOUR_IN_SECONDS:
            hours = total_time // HOUR_IN_SECONDS
            minutes = total_time - (total_time // HOUR_IN_SECONDS) * HOUR_IN_SECONDS
            time_string = '{0} hours {1} min'.format(hours, minutes)
    else:
        seconds = round(total_time, 2)
        time_string = '{0} seconds'.format(seconds)
    return time_string


class MolSimulateModal(bpy.types.Operator):
    """Operator which runs its self from a timer"""
    bl_idname = "wm.mol_simulate_modal"
    bl_label = "Simulate Molecular"
    _timer = None
    
    def check_bake_uv(self, context):
        # bake the UV in the beginning
        scene = context.scene
        frame_old = scene.frame_current
        for ob in bpy.data.objects:
            obj = get_object(context, ob)

            for psys in obj.particle_systems:
                if psys.settings.mol_bakeuv:
                    #context.view_layer.update()
                    scene.frame_set(frame=psys.settings.frame_start)
                    #context.view_layer.update()
                    if psys.settings.mol_bakeuv_global:
                        bpy.ops.object.mol_set_global_uv("INVOKE_DEFAULT", objname = obj.name)
                    else:
                        bpy.ops.object.mol_set_active_uv("INVOKE_DEFAULT", objname = obj.name)

        scene.frame_set(frame=frame_old)

    def modal(self, context, event):
        scene = context.scene
        frame_end = scene.frame_end
        frame_current = scene.frame_current
        
        if event.type == 'ESC' or frame_current == frame_end:
            if scene.mol_bake:
                fake_context = context.copy()
                for ob in bpy.data.objects:
                    obj = get_object(context, ob)
                    for psys in obj.particle_systems:
                        if psys.settings.mol_active and len(psys.particles):
                            fake_context["point_cache"] = psys.point_cache
                            bpy.ops.ptcache.bake_from_cache(fake_context)
                            
            scene.render.frame_map_new = 1
            scene.frame_end = scene.mol_old_endframe
            core.memfree()
            scene.mol_simrun = False
            mol_exportdata = scene.mol_exportdata
            mol_exportdata.clear()
            print('-' * 50 + 'Molecular Sim end')
            
            if frame_current == frame_end and scene.mol_render:
                print("Rendering ..................")
                bpy.ops.render.render(animation=True)

            scene.frame_set(frame=scene.frame_start)
            return self.cancel(context)

        if event.type == 'TIMER':
            
            mol_substep = scene.mol_substep
            framesubstep = frame_current / (mol_substep + 1)
            
            if framesubstep == int(framesubstep):
                moltime = clock()
            
            mol_exportdata = context.scene.mol_exportdata
            mol_exportdata.clear()
            simulate.pack_data(context, False)
            mol_importdata = core.simulate(mol_exportdata)
            if framesubstep == int(framesubstep):
                etime = clock()
            i = 0
            for ob in bpy.data.objects:
                obj = get_object(context, ob)

                for psys in obj.particle_systems:
                    if psys.settings.mol_active and len(psys.particles):
                        psys.particles.foreach_set('velocity', mol_importdata[1][i])
                        i += 1
                        
            if framesubstep == int(framesubstep):
                print("    frame " + str(framesubstep + 1) + ":")
                print("      links created:", scene.mol_newlink)
                if scene.mol_totallink:
                    print("      links broken :", scene.mol_deadlink)
                    print("      total links:", scene.mol_totallink - scene.mol_totaldeadlink ,"/", scene.mol_totallink," (",round((((scene.mol_totallink - scene.mol_totaldeadlink) / scene.mol_totallink) * 100), 2), "%)")
                print("      Molecular Script: " + str(round((etime - moltime)*mol_substep, 3)) + " sec")
                remain = (etime - moltime) * mol_substep *(scene.mol_old_endframe - framesubstep - 1)
                days = int(strftime('%d', gmtime(remain))) - 1
                scene.mol_timeremain = strftime(str(days) + ' days %H hours %M mins %S secs', gmtime(remain))
                print("      Remaining estimated:", scene.mol_timeremain)
                scene.mol_newlink = 0
                scene.mol_deadlink = 0
                
            scene.mol_newlink += mol_importdata[2]
            scene.mol_deadlink += mol_importdata[3]
            scene.mol_totallink = mol_importdata[4]
            scene.mol_totaldeadlink = mol_importdata[5]
          
            scene.frame_set(frame=frame_current + 1)

            if framesubstep == int(framesubstep):
                etime2 = clock()
                print("      Blender: " + str(round((etime2 - etime)*mol_substep, 3)) + " sec")

        return {'PASS_THROUGH'}

    def execute(self, context):
        # start time
        self.st = time()
        self.check_bake_uv(context)
        self._timer = context.window_manager.event_timer_add(0.000000001, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        # total time
        tt = time() - self.st
        tt_s = convert_time_to_string(tt)
        
        print("Total time : " + tt_s + " sec")
        
        self.report({'INFO'}, 'Total time: {0}'.format(tt_s))
        
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


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
                    step = psys.point_cache.frame_step
                    psys.point_cache.frame_step = step
                    ccache = context.object.particle_systems.active.settings.use_modifier_stack
                    context.object.particle_systems.active.settings.use_modifier_stack = ccache
                    
        context.scene.frame_current = 1
        
        return {'FINISHED'}

class MolResetCache(bpy.types.Operator):
    """Clear Particle Cache"""
    bl_idname = "object.reset_pcache"
    bl_label = "Clear Particle Cache"

    def execute(self, context):
        ccache = context.object.particle_systems.active.settings.use_modifier_stack
        context.object.particle_systems.active.settings.use_modifier_stack = ccache
        context.scene.frame_current = 1
        
        return {'FINISHED'}
