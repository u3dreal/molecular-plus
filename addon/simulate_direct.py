"""
Direct Memory Access Simulation Module

This module implements direct memory access to Blender's particle data
using par.as_pointer() for zero-copy particle simulation.
"""

import bpy
import ctypes
from ctypes import Structure, c_float, c_int, POINTER, cast
from .utils import get_object


class BlenderParticle(Structure):
    """
    Blender Particle structure mapping from source code.
    struct Particle {
        int index;
        float age;
        float lifetime;
        float3 location;
        float4 rotation;
        float size;
        float3 velocity;
        float3 angular_velocity;
    };
    """
    _fields_ = [
        ("index", c_int),
        ("age", c_float),
        ("lifetime", c_float),
        ("location", c_float * 3),
        ("rotation", c_float * 4),
        ("size", c_float),
        ("velocity", c_float * 3),
        ("angular_velocity", c_float * 3),
    ]


class DirectMemoryParticleSystem:
    """
    Direct memory access wrapper for Blender particle systems.
    Provides zero-copy access to particle data via par.as_pointer().
    """
    
    def __init__(self, psys):
        self.psys = psys
        self.particle_count = len(psys.particles)
        self.particle_pointers = []
        self._setup_direct_access()
    
    def _setup_direct_access(self):
        """Set up direct memory access using par.as_pointer()."""
        self.particle_pointers = []
        for par in self.psys.particles:
            pointer = par.as_pointer()
            self.particle_pointers.append(pointer)
    
    def get_particle_pointers(self):
        """Get the list of particle pointers for Cython processing."""
        return self.particle_pointers
    
    def access_particle_directly(self, index):
        """Access a particle directly via its pointer."""
        if index >= len(self.particle_pointers):
            return None
        
        pointer = self.particle_pointers[index]
        particle = cast(pointer, POINTER(BlenderParticle)).contents
        
        return {
            'location': [particle.location[0], particle.location[1], particle.location[2]],
            'velocity': [particle.velocity[0], particle.velocity[1], particle.velocity[2]],
            'size': particle.size,
            'age': particle.age,
            'lifetime': particle.lifetime,
            'pointer': pointer
        }


def pack_data_direct(context, initiate):
    """
    Direct memory access version of pack_data.
    Collects particle systems and sets up direct memory access.
    """
    scene = context.scene
    direct_systems = []
    total_particles = 0
    
    for ob in bpy.data.objects:
        obj = get_object(context, ob)
        
        for psys in obj.particle_systems:
            if not (psys.settings.mol_active and len(psys.particles) > 0):
                continue
            
            if psys.settings.mol_matter != "-1":
                psys.settings.mol_density = float(psys.settings.mol_matter)
            
            direct_psys = DirectMemoryParticleSystem(psys)
            direct_systems.append({
                'system': direct_psys,
                'settings': psys.settings,
                'object': obj,
                'psys': psys
            })
            
            total_particles += direct_psys.particle_count
    
    if initiate:
        _initialize_simulation_parameters(scene, direct_systems)
    
    return {
        'systems': direct_systems,
        'total_particles': total_particles,
        'mode': 'direct_memory_access'
    }


def _initialize_simulation_parameters(scene, direct_systems):
    """Initialize simulation parameters for direct memory access."""
    min_size = float('inf')
    
    for sys_data in direct_systems:
        direct_psys = sys_data['system']
        settings = sys_data['settings']
        
        if direct_psys.particle_count > 0:
            first_particle = direct_psys.access_particle_directly(0)
            if first_particle and first_particle['size'] < min_size:
                min_size = first_particle['size']
        
        if scene.timescale != 1.0:
            settings.timestep = 1 / (scene.render.fps / scene.timescale)
        else:
            settings.timestep = 1 / scene.render.fps
        
        if settings.mol_link_samevalue:
            settings.mol_link_estiff = settings.mol_link_stiff
            settings.mol_link_estiffrand = settings.mol_link_stiffrand
            settings.mol_link_estiffexp = settings.mol_link_stiffexp
            settings.mol_link_edamp = settings.mol_link_damp
            settings.mol_link_edamprand = settings.mol_link_damprand
            settings.mol_link_ebroken = settings.mol_link_broken
            settings.mol_link_ebrokenrand = settings.mol_link_brokenrand
        
        if settings.mol_relink_samevalue:
            settings.mol_relink_estiff = settings.mol_relink_stiff
            settings.mol_relink_estiffrand = settings.mol_relink_stiffrand
            settings.mol_relink_estiffexp = settings.mol_relink_stiffexp
            settings.mol_relink_edamp = settings.mol_relink_damp
            settings.mol_relink_edamprand = settings.mol_relink_damprand
            settings.mol_relink_ebroken = settings.mol_relink_broken
            settings.mol_relink_ebrokenrand = settings.mol_relink_brokenrand
    
    if min_size != float('inf'):
        scene.mol_minsize = min_size


def simulate_direct(direct_data):
    """Direct memory simulation using Cython backend."""
    from ..c_sources.simulate_direct import simulate_direct_cython
    
    systems = direct_data['systems']
    results = []
    
    for sys_data in systems:
        direct_psys = sys_data['system']
        settings = sys_data['settings']
        
        particle_pointers = direct_psys.get_particle_pointers()
        result = simulate_direct_cython(particle_pointers, settings.timestep)
        
        results.append({
            'particle_count': direct_psys.particle_count,
            'system_name': sys_data['object'].name,
            'collisions_resolved': result.get('collisions_resolved', 0),
            'links_processed': result.get('links_processed', 0),
            'mode': 'direct_memory_access'
        })
    
    return results