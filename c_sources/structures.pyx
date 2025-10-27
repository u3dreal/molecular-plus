cdef struct Links:
    float lenght
    int start
    int end
    float stiffness
    int exponent
    float damping
    float broken
    float estiffness
    int eexponent
    float edamping
    float ebroken
    float friction


cdef struct SpatialHash:
    float cell_size
    int grid_width
    int grid_height
    int grid_depth
    int total_cells
    float min_bounds[3]
    float max_bounds[3]

    # Cell data arrays
    int *cell_counts        # Number of particles in each cell
    int *cell_starts        # Starting index for particles in each cell
    int *particle_indices   # Sorted particle indices by cell
    int *particle_cells     # Which cell each particle belongs to

    # Working arrays for construction
    int *temp_counts        # Temporary cell counts for parallel construction
    int total_particles

    # Thread-local data for parallel construction
    int **thread_cell_counts
    int **thread_particle_indices
    int num_threads


cdef struct ParSys:
    int id
    int parnum
    Particle *particles
    int selfcollision_active
    int othercollision_active
    int collision_group
    float friction
    float collision_damp
    float collision_adhesion_distance
    float collision_adhesion_factor
    int links_active
    float link_length
    int link_rellength
    int link_max
    float link_tension
    float link_tensionrand
    float link_stiff
    float link_stiffrand
    float link_stiffexp
    float link_damp
    float link_damprand
    float link_broken
    float link_brokenrand
    float link_estiff
    float link_estiffrand
    float link_estiffexp
    float link_edamp
    float link_edamprand
    float link_ebroken
    float link_ebrokenrand
    int relink_group
    float relink_chance
    float relink_chancerand
    int relink_max
    float relink_tension
    float relink_tensionrand
    float relink_stiff
    float relink_stiffexp
    float relink_stiffrand
    float relink_damp
    float relink_damprand
    float relink_broken
    float relink_brokenrand
    float relink_estiff
    float relink_estiffexp
    float relink_estiffrand
    float relink_edamp
    float relink_edamprand
    float relink_ebroken
    float relink_ebrokenrand
    float link_friction
    int link_group
    int other_link_active


cdef struct SParticle:
    int id
    float loc[3]


cdef struct Particle:
    int id
    float loc[3]
    float vel[3]
    float size
    float mass
    int state
    float weak

    ParSys *sys
    int *collided_with
    int collided_num
    Links *links
    int links_num
    int links_activnum
    int *link_with
    int link_withnum
    int *neighbours
    int neighboursnum
    int neighboursmax


cdef struct Pool:
    int axis
    float offset
    float max
    Parity *parity


cdef struct Parity:
    Heap *heap


cdef struct Heap:
    int *par
    int parnum
    int maxalloc
