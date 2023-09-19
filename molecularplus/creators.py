import bpy


class MolecularGrid3d(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_makegrid3d"
    bl_label = "Create Molecular 3d grid"
    bl_description = "Create / Set Gridobject 3d"
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

        # ParticlsSystemSettings
            max_dim = max(obj.dimensions)

            psys.grid_resolution = int(max_dim/voxel_size)
            psys.particle_size = max_dim/psys.grid_resolution/2
            psys.display_size = psys.particle_size/2
            psys.hexagonal_grid = context.scene.mol_hexgrid
            psys.emit_from = 'VOLUME'
            psys.distribution = 'GRID'
            psys.normal_factor = 0.0

            if init:
                psys.frame_start = 1
                psys.frame_end = 1
                psys.lifetime = 500
                psys.grid_random = 0.02
                psys.use_size_deflect = True
                psys.use_modifier_stack = True

            # Granular_Settings
                if not psys.mol_active:
                    psys.mol_active = True

                psys.mol_selfcollision_active = True
                psys.mol_friction = 0.15
                psys.mol_collision_damp = 0.25
                psys.mol_link_length = 3.5
            # update
            bpy.ops.object.reset_pcache()
            bpy.ops.object.mol_set_subs()

        return {'FINISHED'}


class MolecularGrid2d(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_makegrid2d"
    bl_label = "Create Molecular 2d grid"
    bl_description = "Create / Set Gridobject 2d"
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

        # ParctilsSystemSettings
            i = 1
            for parsys in obj.particle_systems:
                parsys.name = "stack : " + str(i)
                psys = parsys.settings
                psys.name = "pstack : " + str(i)
                max_dim = max(obj.dimensions)
                psys.grid_resolution = int(max_dim/voxel_size)
                psys.particle_size = max_dim/psys.grid_resolution/2
                psys.display_size = psys.particle_size/2
                psys.hexagonal_grid = context.scene.mol_hexgrid
                psys.emit_from = 'FACE'
                psys.distribution = 'GRID'
                psys.normal_factor = 0.0


                if init:
                    psys.frame_start = i
                    psys.frame_end = i
                    psys.lifetime = 500
                    psys.grid_random = 0.02
                    psys.use_size_deflect = True
                    psys.use_modifier_stack = True

                # Granular_Settings
                    if psys.mol_active == False:
                        psys.mol_active = True

                    psys.mol_selfcollision_active = True
                    psys.mol_othercollision_active = True
                    psys.mol_friction = 0.15
                    psys.mol_collision_damp = 0.25
                    psys.mol_link_length = 2.1

                    i += 20
            # update
            bpy.ops.object.reset_pcache()

            bpy.ops.object.mol_set_subs()

        return {'FINISHED'}

class MolecularEmitter(bpy.types.Operator):
    bl_idname = "molecular_operators.molecular_makeemitter"
    bl_label = "Create Molecular Emitter object"
    bl_description = "Create / Set Emitter object"
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

        # ParctilsSystemSettings
            max_dim = max(obj.dimensions)

            psys.grid_resolution = int(max_dim/voxel_size)
            psys.particle_size = voxel_size/2
            psys.display_size = voxel_size/4
            psys.hexagonal_grid = context.scene.mol_hexgrid
            psys.emit_from = 'FACE'
            psys.distribution = 'RAND'
            psys.normal_factor = 2.0

            if init:
                psys.lifetime = 500
                psys.count = 10000
                psys.grid_random = 0.02
                psys.use_size_deflect = True
                psys.use_modifier_stack = True
                psys.use_emit_random = True

            # Molecularular_Settings
                if psys.mol_active == False:
                    psys.mol_active = True

                psys.mol_selfcollision_active = True
                psys.mol_othercollision_active = True
                psys.mol_friction = 0.15
                psys.mol_collision_damp = 0.7
                psys.mol_link_length = 2.1

            # update
            bpy.ops.object.reset_pcache()
            bpy.ops.object.mol_set_subs()

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

create_classes = (MolecularEmitter, MolecularCollider, MolecularGrid2d, MolecularGrid3d)
