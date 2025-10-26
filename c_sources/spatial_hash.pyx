cimport cython
from cython.parallel import parallel, prange
from libc.stdlib cimport malloc, realloc, free, calloc
from libc.math cimport floor, ceil, fabs




cdef void SpatialHash_create(SpatialHash *hash, int max_particles, int num_threads) noexcept nogil:
    """Initialize the spatial hash grid structure"""
    hash.total_particles = 0
    hash.num_threads = num_threads

    # Pre-allocate main arrays
    hash.particle_indices = <int *>malloc(max_particles * cython.sizeof(int))
    hash.particle_cells = <int *>malloc(max_particles * cython.sizeof(int))

    # Will be allocated once we know grid dimensions
    hash.cell_counts = NULL
    hash.cell_starts = NULL
    hash.temp_counts = NULL

    # Allocate thread-local arrays
    hash.thread_cell_counts = <int **>malloc(num_threads * 8)  # sizeof(int *)
    hash.thread_particle_indices = <int **>malloc(num_threads * 8)  # sizeof(int *)

    cdef int i
    for i in range(num_threads):
        hash.thread_cell_counts[i] = NULL
        hash.thread_particle_indices[i] = NULL


cdef void SpatialHash_destroy(SpatialHash *hash) noexcept nogil:
    """Free all allocated memory"""
    cdef int i

    if hash.particle_indices != NULL:
        free(hash.particle_indices)
    if hash.particle_cells != NULL:
        free(hash.particle_cells)
    if hash.cell_counts != NULL:
        free(hash.cell_counts)
    if hash.cell_starts != NULL:
        free(hash.cell_starts)
    if hash.temp_counts != NULL:
        free(hash.temp_counts)

    if hash.thread_cell_counts != NULL:
        for i in range(hash.num_threads):
            if hash.thread_cell_counts[i] != NULL:
                free(hash.thread_cell_counts[i])
            if hash.thread_particle_indices[i] != NULL:
                free(hash.thread_particle_indices[i])
        free(hash.thread_cell_counts)
        free(hash.thread_particle_indices)


cdef inline int SpatialHash_get_cell_index(SpatialHash *hash, float x, float y, float z) noexcept nogil:
    """Convert 3D position to 1D cell index"""
    cdef int cell_x = <int>floor((x - hash.min_bounds[0]) / hash.cell_size)
    cdef int cell_y = <int>floor((y - hash.min_bounds[1]) / hash.cell_size)
    cdef int cell_z = <int>floor((z - hash.min_bounds[2]) / hash.cell_size)

    # Clamp to valid range
    if cell_x < 0: cell_x = 0
    elif cell_x >= hash.grid_width: cell_x = hash.grid_width - 1

    if cell_y < 0: cell_y = 0
    elif cell_y >= hash.grid_height: cell_y = hash.grid_height - 1

    if cell_z < 0: cell_z = 0
    elif cell_z >= hash.grid_depth: cell_z = hash.grid_depth - 1

    return cell_x + cell_y * hash.grid_width + cell_z * hash.grid_width * hash.grid_height


cdef void SpatialHash_calculate_bounds(SpatialHash *hash, SParticle *particles, int particle_count) noexcept nogil:
    """Calculate bounding box and determine grid dimensions"""
    if particle_count == 0:
        return

    # Initialize bounds with first particle
    hash.min_bounds[0] = particles[0].loc[0]
    hash.max_bounds[0] = particles[0].loc[0]
    hash.min_bounds[1] = particles[0].loc[1]
    hash.max_bounds[1] = particles[0].loc[1]
    hash.min_bounds[2] = particles[0].loc[2]
    hash.max_bounds[2] = particles[0].loc[2]

    # Find actual bounds
    cdef int i
    for i in range(1, particle_count):
        if particles[i].loc[0] < hash.min_bounds[0]:
            hash.min_bounds[0] = particles[i].loc[0]
        elif particles[i].loc[0] > hash.max_bounds[0]:
            hash.max_bounds[0] = particles[i].loc[0]

        if particles[i].loc[1] < hash.min_bounds[1]:
            hash.min_bounds[1] = particles[i].loc[1]
        elif particles[i].loc[1] > hash.max_bounds[1]:
            hash.max_bounds[1] = particles[i].loc[1]

        if particles[i].loc[2] < hash.min_bounds[2]:
            hash.min_bounds[2] = particles[i].loc[2]
        elif particles[i].loc[2] > hash.max_bounds[2]:
            hash.max_bounds[2] = particles[i].loc[2]

    # Add small padding to avoid edge cases
    cdef float padding = hash.cell_size * 0.1
    hash.min_bounds[0] -= padding
    hash.min_bounds[1] -= padding
    hash.min_bounds[2] -= padding
    hash.max_bounds[0] += padding
    hash.max_bounds[1] += padding
    hash.max_bounds[2] += padding

    # Calculate grid dimensions
    hash.grid_width = <int>ceil((hash.max_bounds[0] - hash.min_bounds[0]) / hash.cell_size)
    hash.grid_height = <int>ceil((hash.max_bounds[1] - hash.min_bounds[1]) / hash.cell_size)
    hash.grid_depth = <int>ceil((hash.max_bounds[2] - hash.min_bounds[2]) / hash.cell_size)
    hash.total_cells = hash.grid_width * hash.grid_height * hash.grid_depth

    # Ensure minimum grid size
    if hash.grid_width < 1: hash.grid_width = 1
    if hash.grid_height < 1: hash.grid_height = 1
    if hash.grid_depth < 1: hash.grid_depth = 1
    hash.total_cells = hash.grid_width * hash.grid_height * hash.grid_depth


cdef void SpatialHash_build(SpatialHash *hash, SParticle *particles, int particle_count, float max_search_radius) noexcept nogil:
    """Build the spatial hash grid using parallel counting sort"""
    hash.total_particles = particle_count
    hash.cell_size = max_search_radius * 1.5  # Slightly larger than search radius for efficiency

    if particle_count == 0:
        return

    # Calculate bounds and grid dimensions
    SpatialHash_calculate_bounds(hash, particles, particle_count)

    # Allocate or reallocate cell arrays if needed
    if hash.cell_counts != NULL:
        free(hash.cell_counts)
    if hash.cell_starts != NULL:
        free(hash.cell_starts)
    if hash.temp_counts != NULL:
        free(hash.temp_counts)

    hash.cell_counts = <int *>calloc(hash.total_cells, cython.sizeof(int))
    hash.cell_starts = <int *>malloc(hash.total_cells * cython.sizeof(int))
    hash.temp_counts = <int *>calloc(hash.total_cells, cython.sizeof(int))

    # Allocate thread-local arrays
    cdef int thread_id
    for thread_id in range(hash.num_threads):
        if hash.thread_cell_counts[thread_id] != NULL:
            free(hash.thread_cell_counts[thread_id])
        if hash.thread_particle_indices[thread_id] != NULL:
            free(hash.thread_particle_indices[thread_id])

        hash.thread_cell_counts[thread_id] = <int *>calloc(hash.total_cells, cython.sizeof(int))
        hash.thread_particle_indices[thread_id] = <int *>malloc(particle_count * cython.sizeof(int))

    # Phase 1: Count particles per cell (parallel)
    cdef int i, cell_index
    with nogil:
        for i in prange(particle_count, num_threads=hash.num_threads):
            thread_id = cython.parallel.threadid()
            cell_index = SpatialHash_get_cell_index(hash,
                                                    particles[i].loc[0],
                                                    particles[i].loc[1],
                                                    particles[i].loc[2])
            hash.particle_cells[i] = cell_index
            hash.thread_cell_counts[thread_id][cell_index] += 1

    # Phase 2: Combine thread-local counts
    for thread_id in range(hash.num_threads):
        for i in range(hash.total_cells):
            hash.cell_counts[i] += hash.thread_cell_counts[thread_id][i]

    # Phase 3: Calculate starting positions for each cell
    hash.cell_starts[0] = 0
    for i in range(1, hash.total_cells):
        hash.cell_starts[i] = hash.cell_starts[i-1] + hash.cell_counts[i-1]

    # Phase 4: Sort particles into cells (parallel)
    # Reset temp_counts for use as current position tracker
    for i in range(hash.total_cells):
        hash.temp_counts[i] = 0

    # Use thread-local arrays to avoid race conditions
    with nogil:
        for i in prange(particle_count, num_threads=hash.num_threads):
            thread_id = cython.parallel.threadid()
            cell_index = hash.particle_cells[i]
            hash.thread_particle_indices[thread_id][i] = i

    # Sequential phase to maintain deterministic ordering within cells
    for i in range(particle_count):
        cell_index = hash.particle_cells[i]
        hash.particle_indices[hash.cell_starts[cell_index] + hash.temp_counts[cell_index]] = i
        hash.temp_counts[cell_index] += 1


cdef void SpatialHash_query_neighbors(SpatialHash *hash, Particle *particle, Particle *all_particles, float search_radius) noexcept nogil:
    """Find all neighbors within search_radius of the given particle"""
    if hash.total_particles == 0:
        particle.neighboursnum = 0
        return

    particle.neighboursnum = 0

    cdef float pos[3]
    pos[0] = particle.loc[0]
    pos[1] = particle.loc[1]
    pos[2] = particle.loc[2]

    cdef float search_radius_sq = search_radius * search_radius

    # Determine which cells to check
    cdef int min_cell_x = <int>floor((pos[0] - search_radius - hash.min_bounds[0]) / hash.cell_size)
    cdef int max_cell_x = <int>floor((pos[0] + search_radius - hash.min_bounds[0]) / hash.cell_size)
    cdef int min_cell_y = <int>floor((pos[1] - search_radius - hash.min_bounds[1]) / hash.cell_size)
    cdef int max_cell_y = <int>floor((pos[1] + search_radius - hash.min_bounds[1]) / hash.cell_size)
    cdef int min_cell_z = <int>floor((pos[2] - search_radius - hash.min_bounds[2]) / hash.cell_size)
    cdef int max_cell_z = <int>floor((pos[2] + search_radius - hash.min_bounds[2]) / hash.cell_size)

    # Clamp to valid ranges
    if min_cell_x < 0: min_cell_x = 0
    if max_cell_x >= hash.grid_width: max_cell_x = hash.grid_width - 1
    if min_cell_y < 0: min_cell_y = 0
    if max_cell_y >= hash.grid_height: max_cell_y = hash.grid_height - 1
    if min_cell_z < 0: min_cell_z = 0
    if max_cell_z >= hash.grid_depth: max_cell_z = hash.grid_depth - 1

    cdef int cell_x, cell_y, cell_z, cell_index
    cdef int start_idx, end_idx, particle_idx, candidate_id
    cdef float dx, dy, dz, dist_sq

    # Check all relevant cells
    for cell_x in range(min_cell_x, max_cell_x + 1):
        for cell_y in range(min_cell_y, max_cell_y + 1):
            for cell_z in range(min_cell_z, max_cell_z + 1):
                cell_index = cell_x + cell_y * hash.grid_width + cell_z * hash.grid_width * hash.grid_height

                if cell_index < 0 or cell_index >= hash.total_cells:
                    continue

                start_idx = hash.cell_starts[cell_index]
                end_idx = start_idx + hash.cell_counts[cell_index]

                # Check all particles in this cell
                for particle_idx in range(start_idx, end_idx):
                    if particle_idx >= hash.total_particles:
                        break

                    candidate_id = hash.particle_indices[particle_idx]

                    # Skip self
                    if candidate_id == particle.id:
                        continue

                    # Calculate distance using passed particle array
                    dx = pos[0] - all_particles[candidate_id].loc[0]
                    dy = pos[1] - all_particles[candidate_id].loc[1]
                    dz = pos[2] - all_particles[candidate_id].loc[2]
                    dist_sq = dx*dx + dy*dy + dz*dz

                    # Add to neighbors if within radius
                    if dist_sq <= search_radius_sq:
                        # Expand neighbor array if needed
                        if particle.neighboursnum >= particle.neighboursmax:
                            particle.neighboursmax = particle.neighboursmax * 2
                            particle.neighbours = <int *>realloc(particle.neighbours,
                                                                particle.neighboursmax * cython.sizeof(int))

                        particle.neighbours[particle.neighboursnum] = candidate_id
                        particle.neighboursnum += 1


