import bpy

realframe = 0
cframe = 0
stage = -1
substep = 16
timestep = 1 / (24*substep)

objs = bpy.data.objects
psysts = []
for obj in objs:
    for psys in obj.particle_systems:
        if "mol_active" in psys.settings:
            if psys.settings["mol_active"] == True:
                psysts.append(psys)
                psys.settings.timestep = timestep

bpy.context.scene.frame_end += substep

print("Script Start *****")
bpy.context.scene.frame_set(frame = 1)


ParLoc = {}
ParPrevLoc = {}
ParVel = {}
ParPrevVel = {}

a = {}
exportdata = []
for psys in psysts:
    a['point_cache'] = psys.point_cache
    bpy.ops.ptcache.free_bake(a)
    parsloc = []
    parsvel = []
    for par in psys.particles:
        parsloc.append((par.location.x,par.location.y,par.location.z))
        parsvel.append((par.velocity.x,par.velocity.y,par.velocity.z))
    exportdata.append((parsloc,parsvel))
print(len(exportdata))
print(exportdata)

def Refresh():
    bpy.data.scenes[0].update()

class ModalTimerOperator(bpy.types.Operator):
    '''Operator which runs its self from a timer.'''
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        global realframe
        global cframe
        global Par
        global stage
        global ParLoc
        global ParPrevLoc
        global ParVel
        global ParPrevVel
        global timestep
        
        if event.type == 'ESC' or bpy.context.scene.frame_current == bpy.context.scene.frame_end:
            cframe = realframe - 1
            bpy.context.scene.frame_set(frame = cframe)
            bpy.context.scene.frame_end -= substep
            a = {}
            for psys in psysts:
                a['point_cache'] = psys.point_cache
                bpy.ops.ptcache.bake_from_cache(a)
            print("Script End   *****")
            #bpy.ops.render.render(animation=True)
            return self.cancel(context)

        if event.type == 'TIMER':
            
                        
            if stage == 4:
                for psys in psysts:
                    for i in psys.particles:
                        i.location = ParLoc[i]
                        i.prev_location = ParPrevLoc[i]
                        i.velocity = ParVel[i]
                        i.prev_velocity = ParPrevVel[i]
 
                stage = 0
                print("Frame:",realframe)
                
            if stage == 3:
                for psys in psysts:
                    psys.settings.effector_weights.gravity = 0
                    psys.settings.effector_weights.all= 0
                stage = 4
            
            if stage == 2:
                for psys in psysts:
                    for i in psys.particles:             
                        i.location = ParLoc[i]
                        i.prev_location = ParPrevLoc[i]
                        i.velocity = ParVel[i]
                        i.prev_velocity = ParPrevVel[i]
                stage = 3
                           
            if stage == 1:
                for psys in psysts:
                    for i in psys.particles:
                        ParLoc[i] = tuple(i.location.xyz)
                        ParPrevLoc[i] = tuple(i.prev_location.xyz)
                        ParVel[i] = tuple(i.velocity.xyz)
                        ParPrevVel[i] = tuple(i.prev_velocity.xyz)
                #print(len(ParLoc))
                cframe = realframe - 1
                realframe += 1
                bpy.context.scene.frame_set(frame = cframe)
                stage = 2
                      

            if stage == 0:
                cframe += 1
                #'''
                for psys in psysts:
                    psys.settings.effector_weights.gravity = 1
                    psys.settings.effector_weights.all= 1
                    for i in psys.particles:
                        stiff = 1 / timestep
                        for psys2 in psysts:
                            for ii in psys2.particles:
                                target = (i.size + ii.size) * 0.99
                                sqtarget = target**2
                                if i.alive_state == 'ALIVE' and ii.alive_state == 'ALIVE':
                                    lenghtx = i.location[0] - ii.location[0]
                                    lenghty = i.location[1] - ii.location[1]
                                    lenghtz = i.location[2] - ii.location[2]
                                    sqlenght = (lenghtx * lenghtx) + (lenghty * lenghty) + (lenghtz * lenghtz)
                                    if sqlenght != 0 and sqlenght < sqtarget:
                                        lenght = sqlenght**0.5
                                        factor = (lenght - target) / lenght
                                        i.velocity[0] -= ((lenghtx * factor * 0.5) * stiff)
                                        i.velocity[1] -= ((lenghty * factor * 0.5) * stiff)
                                        i.velocity[2] -= ((lenghtz * factor * 0.5) * stiff)
                                        ii.velocity[0] += ((lenghtx * factor * 0.5) * stiff)
                                        ii.velocity[1] += ((lenghty * factor * 0.5) * stiff)
                                        ii.velocity[2] += ((lenghtz * factor * 0.5) * stiff)
                #'''
                    
                bpy.context.scene.frame_set(frame = cframe)
                if cframe == (realframe + (substep - 1)):
                    stage = 1
            
            if stage == -1:
                for psys in psysts:
                    psys.settings.effector_weights.gravity = 0
                    psys.settings.effector_weights.all= 0
                    for i in psys.particles:
                        i.velocity = (0,0,0)
                        i.prev_velocity = (0,0,0)
                cframe += 1
                realframe += 1
                bpy.context.scene.frame_set(frame = cframe)
                if cframe == 4:
                    for psys in psysts:
                        psys.settings.effector_weights.gravity = 1
                        psys.settings.effector_weights.all= 1
                    stage = 0


        return {'PASS_THROUGH'}

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.00001, context.window)
        return {'RUNNING_MODAL'}

    def cancel(self, context):
        context.window_manager.event_timer_remove(self._timer)
        return {'CANCELLED'}


def register():
    bpy.utils.register_class(ModalTimerOperator)


def unregister():
    bpy.utils.unregister_class(ModalTimerOperator)


if __name__ == "__main__":
    register()

    # test call
    bpy.ops.wm.modal_timer_operator()