#cython: profile=False
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: language_level=3
#cython: cpow=True
#cython: initializedcheck=False
#cython: overflowcheck=False

"""
Direct Memory Access Cython Simulation Core

This module implements zero-copy particle simulation using direct memory access
to Blender's particle data structures via par.as_pointer().
"""

cimport cython
from cython.parallel import parallel, prange
from libc.stdlib cimport malloc, free
from libc.math cimport sqrt

print("Direct Memory Access Cython Core loaded")

cdef struct BlenderParticle:
    # Blender particle structure from source code
    int index
    float age
    float lifetime
    float location[3]
    float rotation[4]
    float size
    float velocity[3]
    float angular_velocity[3]


cdef class DirectMemorySimulator:
    """
    Direct memory access simulator using Blender particle pointers.
    """
    
    cdef BlenderParticle **particle_pointers
    cdef int particle_count
    cdef float timestep
    cdef int initialized

    def __cinit__(self):
        self.particle_pointers = NULL
        self.particle_count = 0
        self.timestep = 1.0 / 24.0
        self.initialized = 0

    def __dealloc__(self):
        if self.particle_pointers != NULL:
            free(self.particle_pointers)

    def setup_particle_pointers(self, particle_pointers_list):
        """Set up direct memory access using par.as_pointer()."""
        self.particle_count = len(particle_pointers_list)
        
        if self.particle_pointers != NULL:
            free(self.particle_pointers)
        
        self.particle_pointers = <BlenderParticle**>malloc(
            self.particle_count * sizeof(BlenderParticle*)
        )
        
        if self.particle_pointers == NULL:
            return False
        
        cdef int i
        for i in range(self.particle_count):
            self.particle_pointers[i] = <BlenderParticle*><size_t>particle_pointers_list[i]
        
        self.initialized = 1
        return True

    cdef int collision_detection_direct(self) nogil:
        """
        Direct memory collision detection.
        Returns number of collisions resolved.
        """
        cdef int i, j, collision_count = 0
        cdef float dx, dy, dz, dist_sq, min_dist_sq, dist, overlap
        cdef float collision_response = 0.8
        cdef float velocity_damping = 0.9
        cdef float separation_x, separation_y, separation_z
        cdef BlenderParticle *p1, *p2
        
        for i in prange(self.particle_count, schedule='dynamic'):
            p1 = self.particle_pointers[i]
            
            if p1.age >= p1.lifetime:
                continue
                
            for j in range(i + 1, self.particle_count):
                p2 = self.particle_pointers[j]
                
                if p2.age >= p2.lifetime:
                    continue
                
                dx = p1.location[0] - p2.location[0]
                dy = p1.location[1] - p2.location[1]
                dz = p1.location[2] - p2.location[2]
                dist_sq = dx*dx + dy*dy + dz*dz
                
                min_dist_sq = (p1.size + p2.size) * 0.25
                
                if dist_sq < min_dist_sq and dist_sq > 0.0001:
                    collision_count += 1
                    
                    dist = sqrt(dist_sq)
                    overlap = sqrt(min_dist_sq) - dist
                    
                    separation_x = (dx / dist) * overlap * collision_response * 0.5
                    separation_y = (dy / dist) * overlap * collision_response * 0.5
                    separation_z = (dz / dist) * overlap * collision_response * 0.5
                    
                    p1.location[0] += separation_x
                    p1.location[1] += separation_y
                    p1.location[2] += separation_z
                    
                    p2.location[0] -= separation_x
                    p2.location[1] -= separation_y
                    p2.location[2] -= separation_z
                    
                    p1.velocity[0] *= velocity_damping
                    p1.velocity[1] *= velocity_damping
                    p1.velocity[2] *= velocity_damping
                    
                    p2.velocity[0] *= velocity_damping
                    p2.velocity[1] *= velocity_damping
                    p2.velocity[2] *= velocity_damping
        
        return collision_count

    cdef int solve_links_direct(self) nogil:
        """
        Direct memory link solving.
        Returns number of links processed.
        """
        cdef int i, j, link_count = 0
        cdef BlenderParticle *p1, *p2
        cdef float dx, dy, dz, dist_sq, dist, target_dist
        cdef float link_strength = 0.1
        cdef float max_link_dist = 2.0
        cdef float max_link_dist_sq = max_link_dist * max_link_dist
        cdef float force_magnitude, fx, fy, fz
        
        for i in prange(self.particle_count, schedule='dynamic'):
            p1 = self.particle_pointers[i]
            
            if p1.age >= p1.lifetime:
                continue
                
            for j in range(i + 1, self.particle_count):
                p2 = self.particle_pointers[j]
                
                if p2.age >= p2.lifetime:
                    continue
                
                dx = p1.location[0] - p2.location[0]
                dy = p1.location[1] - p2.location[1]
                dz = p1.location[2] - p2.location[2]
                dist_sq = dx*dx + dy*dy + dz*dz
                
                if dist_sq > 0.0001 and dist_sq < max_link_dist_sq:
                    link_count += 1
                    
                    target_dist = (p1.size + p2.size) * 1.2
                    dist = sqrt(dist_sq)
                    
                    force_magnitude = (target_dist - dist) * link_strength
                    
                    fx = (dx / dist) * force_magnitude * 0.5
                    fy = (dy / dist) * force_magnitude * 0.5
                    fz = (dz / dist) * force_magnitude * 0.5
                    
                    p1.location[0] += fx
                    p1.location[1] += fy
                    p1.location[2] += fz
                    
                    p2.location[0] -= fx
                    p2.location[1] -= fy
                    p2.location[2] -= fz
                    
                    p1.velocity[0] += fx * 0.1
                    p1.velocity[1] += fy * 0.1
                    p1.velocity[2] += fz * 0.1
                    
                    p2.velocity[0] -= fx * 0.1
                    p2.velocity[1] -= fy * 0.1
                    p2.velocity[2] -= fz * 0.1
        
        return link_count

    def simulate_step_direct(self, timestep=1.0/24.0):
        """Main simulation step using direct memory access."""
        if not self.initialized:
            return None
        
        self.timestep = timestep
        
        cdef int collision_count = 0
        cdef int link_count = 0
        
        with nogil:
            collision_count = self.collision_detection_direct()
            link_count = self.solve_links_direct()
        
        return {
            'particle_count': self.particle_count,
            'collisions_resolved': collision_count,
            'links_processed': link_count,
            'performance_mode': 'direct_memory_access',
            'memory_copies': 0
        }


# Global simulator instance
cdef DirectMemorySimulator g_simulator = DirectMemorySimulator()


def simulate_direct_cython(particle_pointers_list, timestep=1.0/24.0):
    """
    Python interface for direct memory simulation.
    
    Args:
        particle_pointers_list: List of particle pointers from par.as_pointer()
        timestep: Simulation timestep
    
    Returns:
        Simulation results and performance metrics
    """
    global g_simulator
    
    success = g_simulator.setup_particle_pointers(particle_pointers_list)
    if not success:
        return None
    
    result = g_simulator.simulate_step_direct(timestep)
    return result


def get_performance_stats():
    """Get performance statistics for direct memory access."""
    return {
        'memory_mode': 'direct_access',
        'performance_improvement': 'Significant reduction in memory copying'
    }