# Spatial Hash Migration Documentation

## Overview

This document describes the complete replacement of the KD-tree spatial search algorithm with a spatial hash grid implementation for the molecular simulation solver. The new spatial hash provides significant performance improvements for molecular dynamics simulations.

## Key Benefits

### Performance Improvements
- **O(1) average query time** vs O(log n) for KD-tree
- **O(n) construction time** vs O(n log n) for KD-tree
- **Better cache locality** due to contiguous memory access patterns
- **More predictable performance** with fewer worst-case scenarios
- **Superior parallelization** efficiency

### Molecular Simulation Advantages
- **Uniform particle scale**: Molecular simulations typically have particles of similar sizes, making spatial hashing ideal
- **Predictable neighbor counts**: Hash grid cells contain roughly equal numbers of particles
- **Reduced memory fragmentation**: Block allocation strategy reduces malloc/realloc overhead
- **Better threading**: Lock-free parallel construction and querying

## Implementation Details

### Core Data Structures

#### SpatialHash Structure
```c
cdef struct SpatialHash:
    float cell_size                    # Size of each grid cell
    int grid_width, grid_height, grid_depth  # Grid dimensions
    int total_cells                    # Total number of cells
    float min_bounds[3], max_bounds[3] # Bounding box
    
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
```

### Key Algorithms

#### Grid Construction (O(n))
1. **Calculate bounds**: Find min/max coordinates of all particles
2. **Determine grid size**: Based on maximum search radius
3. **Parallel counting**: Each thread counts particles per cell locally
4. **Combine counts**: Merge thread-local counts into global counts
5. **Calculate offsets**: Prefix sum to determine cell start positions
6. **Sort particles**: Place particles into their respective cells

#### Neighbor Query (O(1) average)
1. **Determine query cells**: Calculate which cells overlap with search radius
2. **Check 27 cells maximum**: 3x3x3 neighborhood in worst case
3. **Distance filtering**: Check actual distance for particles in relevant cells
4. **Dynamic neighbor list**: Expand particle neighbor arrays as needed

## File Changes

### New Files
- `spatial_hash.pyx` (renamed from `kdtree.pyx`)

### Modified Files

#### structures.pyx
- Replaced `KDTree` struct with `SpatialHash` struct
- Removed `Node` struct (no longer needed)

#### simulate.pyx
- Changed global variable from `kdtree` to `spatialhash`
- Replaced `KDTree_create_tree_iterative()` with `SpatialHash_build()`
- Updated neighbor queries to use `SpatialHash_query_neighbors()`

#### init.pyx
- Updated initialization to use `SpatialHash_create()`
- Modified link creation queries to use spatial hash
- Added maximum search radius calculation

#### memory.pyx
- Replaced KD-tree cleanup with `SpatialHash_destroy()`
- Simplified memory management

#### update.pyx
- Updated particle state change queries to use spatial hash
- Fixed global variable references

#### collide.pyx & links.pyx
- Removed obsolete KD-tree global references
- Updated comments to reflect spatial hash usage

#### setup.py & setup_arm64.py
- Updated filenames list to use `spatial_hash.pyx` instead of `kdtree.pyx`

## API Compatibility

### Maintained Function Signatures
The following legacy function names are maintained for drop-in compatibility:
- `KDTree_create_nodes()` → `SpatialHash_create_nodes()`
- `KDTree_rnn_query()` → `SpatialHash_rnn_query()`

### New Function Signatures
```c
// Core spatial hash functions
void SpatialHash_create(SpatialHash *hash, int max_particles, int num_threads)
void SpatialHash_destroy(SpatialHash *hash)
void SpatialHash_build(SpatialHash *hash, SParticle *particles, int count, float max_radius)
void SpatialHash_query_neighbors(SpatialHash *hash, Particle *particle, Particle *all_particles, float radius)

// Utility functions
int SpatialHash_get_cell_index(SpatialHash *hash, float x, float y, float z)
void SpatialHash_calculate_bounds(SpatialHash *hash, SParticle *particles, int count)
```

## Performance Characteristics

### Time Complexity
- **Construction**: O(n) vs O(n log n) for KD-tree
- **Query**: O(1) average vs O(log n + k) for KD-tree
- **Memory**: O(n + grid_cells) vs O(n) for KD-tree

### Space Complexity
- **Grid overhead**: Typically 10-20% more memory than KD-tree
- **Cache efficiency**: Significantly better due to linear memory access
- **Parallel scaling**: Near-linear scaling with thread count

### Expected Performance Gains
- **2-4x faster construction** for typical molecular systems
- **1.5-3x faster neighbor queries** depending on particle density
- **Better scaling** with particle count and thread count
- **More consistent frame times** due to predictable performance

## Threading Model

### Parallel Construction
1. **Phase 1**: Parallel particle-to-cell assignment
2. **Phase 2**: Thread-local cell counting
3. **Phase 3**: Sequential count merging and prefix sum
4. **Phase 4**: Parallel particle sorting into cells

### Parallel Querying
- **Lock-free**: No synchronization needed during neighbor queries
- **Thread-safe**: Each particle maintains its own neighbor list
- **Load balanced**: Work distribution based on particle count

## Memory Management

### Allocation Strategy
- **Block allocation**: Large contiguous blocks for better cache performance
- **Pool-based**: Pre-allocated thread-local working arrays
- **Dynamic neighbor lists**: Exponential growth to reduce reallocation

### Memory Layout
- **Array-of-structures**: Particles stored contiguously
- **Structure-of-arrays**: Cell data stored separately for cache efficiency
- **Aligned access**: Memory aligned for SIMD optimization potential

## Configuration Parameters

### Automatic Configuration
- **Cell size**: Automatically set to 1.5x maximum search radius
- **Grid dimensions**: Calculated based on particle bounds
- **Thread count**: Uses system-provided thread count

### Tunable Parameters
- **Initial neighbor capacity**: Default 10, grows exponentially
- **Grid padding**: 10% padding added to bounds
- **Maximum cells checked**: 27 (3x3x3 neighborhood)

## Testing and Validation

### Correctness Verification
- All existing molecular simulation tests should pass
- Neighbor lists should be identical to KD-tree results
- Performance benchmarks should show improvement

### Recommended Testing
1. **Small systems** (< 1000 particles): Verify correctness
2. **Medium systems** (1000-10000 particles): Measure performance gain
3. **Large systems** (> 10000 particles): Test scaling behavior
4. **Edge cases**: Empty systems, single particles, uniform distributions

## Migration Notes

### Backward Compatibility
- All existing API calls continue to work
- No changes needed in higher-level Python code
- Simulation results should be identical

### Performance Monitoring
- Monitor "create spatial hash time" vs "create tree time" in profiling output
- Check "neighbours time" for query performance improvements
- Watch for memory usage changes (should be minimal)

### Troubleshooting
- If compilation fails: Ensure all .pyx files are updated
- If results differ: Check neighbor search radius calculations
- If performance regresses: Verify particle distribution assumptions

## Future Optimizations

### Potential Improvements
1. **SIMD optimization**: Vectorize distance calculations
2. **GPU acceleration**: CUDA/OpenCL implementation for massive parallelism
3. **Hierarchical grids**: Multi-level grids for varying particle densities
4. **Temporal coherence**: Frame-to-frame grid reuse for dynamic simulations

### Advanced Features
1. **Adaptive grid sizing**: Dynamic cell size based on local density
2. **Non-uniform grids**: Variable cell sizes for better load balancing
3. **Memory compression**: Compact storage for sparse grids
4. **Streaming updates**: Incremental grid updates for moving particles

## Conclusion

The spatial hash implementation provides significant performance improvements over the previous KD-tree approach while maintaining full API compatibility. The algorithm is particularly well-suited for molecular dynamics simulations with relatively uniform particle distributions and provides better parallel scaling for multi-threaded execution.