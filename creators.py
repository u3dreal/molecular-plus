import bpy  
from .utils import set_substeps

class MolecularGrid3d(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_makegrid3d"
    bl_label = "Create Molecular 3d grid"
    bl_description = "Create / Set Gridopbject 3d"
    bl_options = {'REGISTER'}
    
    def execute(self,  context):
        
        voxel_size = context.scene.mol_voxel_size
        
        for obj in context.view_layer.objects.selected:
            init = False
            if obj.particle_systems.active == None:
                init = True
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.particle_system_add()

            psys = obj.particle_systems.active.settings
            
        #ParticlsSystemSettings
            max_dim = max(obj.dimensions)
            
            psys.grid_resolution = max_dim/voxel_size
            psys.particle_size = voxel_size/2
            psys.display_size = voxel_size/4
            if context.scene.mol_hexgrid:
                psys.hexagonal_grid = True
            else:
                psys.hexagonal_grid = False
            
            if init:
                psys.frame_start = 1
                psys.frame_end = 1
                psys.lifetime = 500
                psys.grid_random = 0.02
                psys.use_size_deflect = True
                psys.use_modifier_stack = True
                psys.emit_from = 'VOLUME'
                psys.distribution = 'GRID'
                
            #Granular_Settings
                if psys.mol_active == False:
                    psys.mol_active = True
                    
                psys.mol_selfcollision_active = True
                psys.mol_friction = 0.15
                psys.mol_collision_damp = 0.25
                psys.mol_link_length = 3.5
            #update
            psys_res = psys.grid_resolution
            psys.grid_resolution = psys_res
            
            if context.scene.mol_autosubsteps:
                set_substeps()
            
        return {'FINISHED'}
    
    
class MolecularGrid2d(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_makegrid2d"
    bl_label = "Create Molecular 2d grid"
    bl_description = "Create / Set Gridopbject 2d"
    bl_options = {'REGISTER'}
    
    def execute(self,  context):
        
        voxel_size = context.scene.mol_voxel_size
        
        for obj in context.view_layer.objects.selected:
            init = False
            if obj.particle_systems.active == None:
                init = True
                bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
                bpy.context.view_layer.objects.active = obj
                bpy.ops.object.particle_system_add()

            psys = obj.particle_systems.active.settings
            
        #ParctilsSystemSettings
            max_dim = max(obj.dimensions)
            
            psys.grid_resolution = max_dim/voxel_size
            psys.particle_size = voxel_size/2
            psys.display_size = voxel_size/4
            if context.scene.mol_hexgrid:
                psys.hexagonal_grid = True
            else:
                psys.hexagonal_grid = False
                
            if init:
                psys.frame_start = 1
                psys.frame_end = 1
                psys.lifetime = 500
                psys.grid_random = 0.02
                psys.use_size_deflect = True
                psys.use_modifier_stack = True
                psys.emit_from = 'FACE'
                psys.distribution = 'GRID'
                
            #Granular_Settings
                if psys.mol_active == False:
                    psys.mol_active = True
                    
                psys.mol_selfcollision_active = True
                psys.mol_othercollision_active = True
                psys.mol_friction = 0.15
                psys.mol_collision_damp = 0.25
                psys.mol_link_length = 2.1
            
            #update
            psys_res = psys.grid_resolution
            psys.grid_resolution = psys_res
            
            if context.scene.mol_autosubsteps:
                set_substeps()
            
        return {'FINISHED'}
    
class MolecularCollider(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_makecollider"
    bl_label = "Create Molecular Collider object"
    bl_description = "Create / Set Collider object"
    bl_options = {'REGISTER'}
    
    def execute(self,  context):
        for obj in context.view_layer.objects.selected:
            bpy.context.view_layer.objects.active = obj
            bpy.ops.object.modifier_add(type='COLLISION')
            obj.collision.damping_factor = 0.5
            obj.collision.friction_factor = 0.5

        return {'FINISHED'}
create_classes = (MolecularCollider, MolecularGrid2d, MolecularGrid3d)