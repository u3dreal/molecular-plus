import bpy

        
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
        row.prop(psys.settings,"MyBool", text = "Activate")

    def draw(self, context):
        layout = self.layout
        obj = context.object
        psys = obj.particle_systems.active
        layout.active = psys.settings.MyBool
        
        row = layout.row()
        row.label(text = "Density:")
        box = layout.box()
        box.prop(psys.settings,"MyBool", text = "Activate Density Control")
        box.prop(psys.settings,"MyEnum",text = "Preset:")
        box.prop(psys.settings, "MyFloat", text = "Kg per CubeMeter:")
        box.label(icon = "INFO",text = "Current particle size: " + str(round(psys.settings.particle_size,5)))
        box.label(icon = "INFO",text = "Particle volume: " + str(round(psys.settings.particle_size**3,5)))
        box.label(icon = "INFO",text = "Particle mass set to: " + str(round(psys.settings.mass,5)))
        box.label(icon = "INFO",text = "Total particles weight: ")
        
        row = layout.row()
        row.label(text = "Collision:")
        box = layout.box()
        box.prop(psys.settings,"MyBool", text = "Activate Self Collision")
        box.prop(psys.settings,"MyBool", text = "Activate Collision with others")
        box.prop(psys.settings,"MyEnum",text = " Collide only with:")

        row = layout.row()
        row.label(text = "Links:")
        box = layout.box()
        box.prop(psys.settings,"MyBool", text = "Activate Particles linking")
        
        subbox = box.box()
        subbox.label(text = "Initial Linking (at bird):")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "seacrh length")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "Stiffness")
        row.prop(psys.settings,"MyFloat",text = "Random Stiffness")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "Exponent")
        row.prop(psys.settings,"MyBool",text = "Invert Spring")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "Damping")
        row.prop(psys.settings,"MyFloat",text = "Random Damping")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "broken")
        row.prop(psys.settings,"MyFloat",text = "Random Broken")
        
        subbox = box.box()
        subbox.label(text = "New Linking (at collision):")
        row = subbox.row()
        row.prop(psys.settings,"MyEnum",text = "Only links with:")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "% linking")
        row.prop(psys.settings,"MyFloat",text = "Random % linking")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "Stiffness")
        row.prop(psys.settings,"MyFloat",text = "Random Stiffness")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "Exp")
        row.prop(psys.settings,"MyBool",text = "Invert Spring")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "Damping")
        row.prop(psys.settings,"MyFloat",text = "Random Damping")
        row = subbox.row()
        row.prop(psys.settings,"MyFloat",text = "broken")
        row.prop(psys.settings,"MyFloat",text = "Random broken")
        
        row = layout.row()
        row.label(text = "Simulate")
        row = layout.row()
        row.prop(psys.settings,"MyInt",text = "Start Frame")
        row.prop(psys.settings,"MyInt",text = "End Frame")
        row = layout.row()
        row.prop(psys.settings,"MyBool",text = "change fps")
        row.prop(psys.settings,"MyInt",text = "fps")
        row = layout.row()
        row.label(text = "")
        row.prop(psys.settings,"MyInt",text = "substep")
        row = layout.row()
        row.operator("object.simple_operator",text = "Start Simulate")

class SimpleOperator(bpy.types.Operator):
    """Tooltip"""
    bl_idname = "object.simple_operator"
    bl_label = "Simple Object Operator"


    def execute(self, context):
        print("My Button")
        return {'FINISHED'}
        
        
    

def register():
    bpy.utils.register_class(SimpleOperator)
    bpy.types.ParticleSettings.MyBool = bpy.props.BoolProperty(default = True)
    bpy.types.ParticleSettings.MyEnum = bpy.props.EnumProperty(items = [('id1','name1','descrip1'),('id2','name2','descrip2')])
    bpy.types.ParticleSettings.MyInt = bpy.props.IntProperty()
    bpy.types.ParticleSettings.MyFloat = bpy.props.FloatProperty()
    bpy.types.ParticleSettings.MyString = bpy.props.StringProperty()
    bpy.utils.register_class(MolecularPanel)
    #bpy.types.PARTICLE_PT_context_particles.append(test)


def unregister():
    bpy.utils.unregister_class(MolecularPanel)
    #bpy.types.PARTICLE_PT_context_particles.remove(test)


if __name__ == "__main__":
    register()