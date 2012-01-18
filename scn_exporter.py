import bpy
import sys
import imp
import time
sys.path.append(bpy.path.abspath('//'))
import vmol
imp.reload(vmol)
#test
cframe = 0

print('MOLECULAR SCRIPT START...')

timer = time.clock()
objPar=bpy.context.object.particle_systems[0].particles
ParLoc = []
empty = [0,0,0]
ParLoc = [axes for i in objPar for axes in empty]
ParVel = [axes for i in objPar for axes in empty]

objPar.foreach_get('location',ParLoc)
ParNum=len(objPar)

Fps = bpy.data.scenes[0].render.fps
Psize = bpy.context.object.particle_systems[0].settings.particle_size

Obstacles = []
for obj in bpy.data.objects:
    if obj.type == "MESH":
        if obj.collision.use == True:
            #print("Object:",obj.name)
            ObjWorldMatrix = obj.matrix_world
            ifaces=0
            face = []
            for faces in obj.data.faces:
                fverts = faces.vertices
                triangle = []
                for i in range(len(fverts)-2):
                    ivert1 = i-i
                    ivert2 = ((i*2)-i)+1
                    ivert3 = ((i*2)-i)+2
                    vert1 = (ObjWorldMatrix * obj.data.vertices[fverts[ivert1]].co).to_tuple()
                    vert2 = (ObjWorldMatrix * obj.data.vertices[fverts[ivert2]].co).to_tuple()
                    vert3 = (ObjWorldMatrix * obj.data.vertices[fverts[ivert3]].co).to_tuple()
                    triangle.append((vert1,vert2,vert3))
                   #print(triangle)
                face.append(triangle)
                ifaces =+ 1
            #print(face)
            Obstacles.append(face)
            
                    
#print("Vertices:",Obstacles[0][1][0])

print("Scene prepared to be exported in:",round((time.clock()-timer),5),'sec')
vmol.Init(ParLoc,ParNum,Psize,Obstacles)

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
            print('...MOLECULAR SCRIPT END')
            #bpy.ops.render.render(animation=True)
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