import bpy
import sys
import imp
import time
sys.path.append(bpy.path.abspath('//'))
import vmol
imp.reload(vmol)

cframe = 0

print('molecular script start...')

objPar=bpy.context.object.particle_systems[0].particles
ParLoc = []
empty = [0,0,0]
ParLoc = [axes for i in objPar for axes in empty]
ParVel = [axes for i in objPar for axes in empty]

objPar.foreach_get('location',ParLoc)
ParNum=len(objPar)

Fps = bpy.data.scenes[0].render.fps
Psize = bpy.context.object.particle_systems[0].settings.particle_size

a=vmol.Init(ParLoc,ParNum,Psize)
#
def Refresh():
    bpy.data.scenes[0].update()

class ModalTimerOperator(bpy.types.Operator):
    '''Operator which runs its self from a timer.'''
    bl_idname = "wm.modal_timer_operator"
    bl_label = "Modal Timer Operator"

    _timer = None

    def modal(self, context, event):
        global cframe
        if event.type == 'ESC' or bpy.context.scene.frame_current==bpy.data.scenes[0].frame_end:
            print('...molecular script end')
            return self.cancel(context)
            

        if event.type == 'TIMER':
            print('Frame:',bpy.context.scene.frame_current)
            if cframe >= (bpy.data.scenes[0].frame_start + 3):
                timer1=time.clock()
                ParLoc = vmol.Simulate(Fps)
                print('    >Moldule take:',round((time.clock()-timer1),5),'sec')
                timer2=time.clock()
                objPar.foreach_set('location',ParLoc)
                #objPar.foreach_set('velocity',ParVel)
                print('    >Blender take:',round((time.clock()-timer2),5),'sec')
            bpy.data.scenes[0].frame_set(frame=cframe)
            cframe += 1

        return {'PASS_THROUGH'}

    def execute(self, context):
        context.window_manager.modal_handler_add(self)
        self._timer = context.window_manager.event_timer_add(0.01, context.window)
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