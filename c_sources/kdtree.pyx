cimport cython

cdef void KDTree_create_nodes(KDTree *kdtree,int parnum):#noexcept nogil:
    cdef int i = 0
    i = 2
    while i < parnum:
        i = i * 2
    kdtree.numnodes = i
    
    # Allocate all nodes in a single block
    kdtree.nodes = <Node *>malloc((kdtree.numnodes + 1) * cython.sizeof(Node))
    
    # Pre-allocate particles and child nodes in blocks to reduce malloc calls
    kdtree.particle_pool = <SParticle *>malloc((kdtree.numnodes + 1) * cython.sizeof(SParticle))
    kdtree.left_child_pool = <Node *>malloc((kdtree.numnodes + 1) * cython.sizeof(Node))
    kdtree.right_child_pool = <Node *>malloc((kdtree.numnodes + 1) * cython.sizeof(Node))
    kdtree.pool_size = kdtree.numnodes + 1
    
    kdtree.root_node = &kdtree.nodes[0]

    for i in range(kdtree.numnodes + 1):
        kdtree.nodes[i].index = (i if i < kdtree.numnodes else -1)
        kdtree.nodes[i].name = -1
        kdtree.nodes[i].parent = -1

        # Use pre-allocated particles
        kdtree.nodes[i].particle = &kdtree.particle_pool[i]

        # Use pre-allocated child nodes
        kdtree.nodes[i].left_child = &kdtree.left_child_pool[i]
        kdtree.nodes[i].right_child = &kdtree.right_child_pool[i]
        kdtree.nodes[i].left_child[0].index = -1
        kdtree.nodes[i].right_child[0].index = -1

    kdtree.thread_nodes = <int *>malloc(128 * cython.sizeof(int))
    kdtree.thread_start = <int *>malloc(128 * cython.sizeof(int))
    kdtree.thread_end = <int *>malloc(128 * cython.sizeof(int))
    kdtree.thread_name = <int *>malloc(128 * cython.sizeof(int))
    kdtree.thread_parent = <int *>malloc(128 * cython.sizeof(int))
    kdtree.thread_depth = <int *>malloc(128 * cython.sizeof(int))

    for i in range(64):
        kdtree.axis[i] = i % 3

    return


cdef Node KDTree_create_tree(
        KDTree *kdtree,
        SParticle *kdparlist,
        int start,
        int end,
        int name,
        int parent,
        int depth,
        int initiate
        )noexcept nogil:

    global parnum

    cdef int index = 0
    cdef int len = (end - start) + 1

    if len <= 0:
        return kdtree.nodes[kdtree.numnodes]

    cdef int axis
    cdef int k = 3
    axis =  kdtree.axis[depth]
    # depth % k
    quick_sort(kdparlist + start, len, axis)

    cdef int median = int((start + end) / 2)

    if depth == 0:
        kdtree.thread_index = 0
        index = 0
    else:
        index = (parent * 2) + name

    if index > kdtree.numnodes:
        return kdtree.nodes[kdtree.numnodes]

    kdtree.nodes[index].name = name
    kdtree.nodes[index].parent = parent

    if len >= 1 and depth == 0:
        kdtree.root_node[0] = kdtree.nodes[0]

    kdtree.nodes[index].particle[0] = kdparlist[median]

    if parnum > 127:
        if depth == 4 and initiate == 1:
            kdtree.thread_nodes[kdtree.thread_index] = index
            kdtree.thread_start[kdtree.thread_index] = start
            kdtree.thread_end[kdtree.thread_index] = end
            kdtree.thread_name[kdtree.thread_index] = name
            kdtree.thread_parent[kdtree.thread_index] = parent
            kdtree.thread_depth[kdtree.thread_index] = depth
            kdtree.thread_index += 1
            return kdtree.nodes[index]

    kdtree.nodes[index].left_child[0] = KDTree_create_tree(
        kdtree,
        kdparlist,
        start,
        median - 1,
        1,
        index,
        depth + 1,
        initiate
    )
    kdtree.nodes[index].right_child[0] = KDTree_create_tree(
        kdtree,
        kdparlist,
        median + 1,
        end,
        2,
        index,
        depth + 1,
        initiate
    )

    return kdtree.nodes[index]

# Iterative version of KDTree_create_tree to reduce stack overhead
cdef void KDTree_create_tree_iterative(
        KDTree *kdtree,
        SParticle *kdparlist,
        int start,
        int end,
        int name,
        int parent,
        int depth,
        int initiate
        )noexcept nogil:

    global parnum

    # Stack for iterative implementation
    cdef int stack_start[64]
    cdef int stack_end[64]
    cdef int stack_name[64]
    cdef int stack_parent[64]
    cdef int stack_depth[64]
    cdef int stack_initiate[64]
    
    cdef int stack_top = 0
    
    # Push initial values to stack
    stack_start[0] = start
    stack_end[0] = end
    stack_name[0] = name
    stack_parent[0] = parent
    stack_depth[0] = depth
    stack_initiate[0] = initiate
    stack_top = 1
    
    cdef int current_start, current_end, current_name, current_parent, current_depth, current_initiate
    cdef int index = 0
    cdef int len = 0
    cdef int axis
    cdef int median
    
    while stack_top > 0:
        # Pop from stack
        stack_top -= 1
        current_start = stack_start[stack_top]
        current_end = stack_end[stack_top]
        current_name = stack_name[stack_top]
        current_parent = stack_parent[stack_top]
        current_depth = stack_depth[stack_top]
        current_initiate = stack_initiate[stack_top]
        
        len = (current_end - current_start) + 1

        if len <= 0:
            continue

        axis = kdtree.axis[current_depth]
        # depth % k
        quick_sort(kdparlist + current_start, len, axis)

        median = int((current_start + current_end) / 2)

        if current_depth == 0:
            kdtree.thread_index = 0
            index = 0
        else:
            index = (current_parent * 2) + current_name

        if index > kdtree.numnodes:
            continue

        kdtree.nodes[index].name = current_name
        kdtree.nodes[index].parent = current_parent

        if len >= 1 and current_depth == 0:
            kdtree.root_node[0] = kdtree.nodes[0]

        kdtree.nodes[index].particle[0] = kdparlist[median]

        if parnum > 127:
            if current_depth == 4 and current_initiate == 1:
                kdtree.thread_nodes[kdtree.thread_index] = index
                kdtree.thread_start[kdtree.thread_index] = current_start
                kdtree.thread_end[kdtree.thread_index] = current_end
                kdtree.thread_name[kdtree.thread_index] = current_name
                kdtree.thread_parent[kdtree.thread_index] = current_parent
                kdtree.thread_depth[kdtree.thread_index] = current_depth
                kdtree.thread_index += 1
                continue

        # Push right child to stack first (so left is processed first)
        if median + 1 <= current_end:
            if stack_top < 63:  # Prevent stack overflow
                stack_start[stack_top] = median + 1
                stack_end[stack_top] = current_end
                stack_name[stack_top] = 2
                stack_parent[stack_top] = index
                stack_depth[stack_top] = current_depth + 1
                stack_initiate[stack_top] = current_initiate
                stack_top += 1

        # Push left child to stack
        if current_start <= median - 1:
            if stack_top < 63:  # Prevent stack overflow
                stack_start[stack_top] = current_start
                stack_end[stack_top] = median - 1
                stack_name[stack_top] = 1
                stack_parent[stack_top] = index
                stack_depth[stack_top] = current_depth + 1
                stack_initiate[stack_top] = current_initiate
                stack_top += 1


cdef void KDTree_rnn_query(
        KDTree *kdtree,
        Particle *par,
        float point[3],
        float dist
        )noexcept nogil:
    if  par.state < 3:
        return

    global parlist
    cdef float sqdist  = 0
    cdef int k  = 0
    cdef int i = 0
    par.neighboursnum = 0
    par.neighbours[0] = -1

    if kdtree.root_node[0].index != kdtree.nodes[0].index:
        par.neighbours[0] = -1
        par.neighboursnum = 0
        return
    else:
        sqdist = dist * dist
        KDTree_rnn_search_iterative(
            kdtree, &par[0],
            kdtree.root_node[0],
            point,
            dist,
            sqdist,
            3,
            60  # Maximum depth to prevent stack overflow
        )


#@cython.cdivision(True)
cdef void KDTree_rnn_search(KDTree *kdtree, Particle *par, Node node, float point[3],
        float dist, float sqdist, int k, int depth)noexcept nogil:

    cdef int axis = 0
    cdef float realsqdist = 0

    if node.index == -1:
        return

    cdef SParticle tparticle = node.particle[0]

    axis = kdtree.axis[depth]

    if (fabs(point[axis] - tparticle.loc[axis])) <= dist:
        realsqdist = square_dist(point, tparticle.loc, 3)

        if realsqdist <= sqdist:
            par.neighbours[par.neighboursnum] = node.particle[0].id
            par.neighboursnum += 1
            if (par.neighboursnum) >= par.neighboursmax:
                par.neighboursmax = par.neighboursmax * 2
                par.neighbours = <int *>realloc(par.neighbours, (par.neighboursmax) * cython.sizeof(int))

        KDTree_rnn_search(kdtree, &par[0], node.left_child[0], point, dist, sqdist, 3, depth + 1)

        KDTree_rnn_search(kdtree, &par[0], node.right_child[0], point, dist, sqdist, 3, depth + 1)

    else:
        if point[axis] <= tparticle.loc[axis]:
            KDTree_rnn_search(kdtree, &par[0], node.left_child[0], point, dist, sqdist, 3, depth + 1)

        if point[axis] >= tparticle.loc[axis]:
            KDTree_rnn_search(kdtree, &par[0], node.right_child[0], point, dist, sqdist, 3, depth + 1)

# Iterative version of KDTree_rnn_search to reduce stack overhead
cdef void KDTree_rnn_search_iterative(KDTree *kdtree, Particle *par, Node root_node, float point[3],
        float dist, float sqdist, int k, int max_depth)noexcept nogil:

    # Stack for iterative implementation
    cdef Node stack_nodes[64]
    cdef int stack_depths[64]
    cdef int stack_top = 0
    
    cdef Node current_node
    cdef int current_depth
    cdef int axis
    cdef float realsqdist
    cdef SParticle tparticle
    
    # Push root node to stack
    stack_nodes[0] = root_node
    stack_depths[0] = 0
    stack_top = 1
    
    while stack_top > 0:
        # Pop from stack
        stack_top -= 1
        current_node = stack_nodes[stack_top]
        current_depth = stack_depths[stack_top]
        
        if current_node.index == -1:
            continue
            
        tparticle = current_node.particle[0]
        axis = kdtree.axis[current_depth]

        if (fabs(point[axis] - tparticle.loc[axis])) <= dist:
            realsqdist = square_dist(point, tparticle.loc, 3)

            if realsqdist <= sqdist:
                par.neighbours[par.neighboursnum] = tparticle.id
                par.neighboursnum += 1
                if (par.neighboursnum) >= par.neighboursmax:
                    par.neighboursmax = par.neighboursmax * 2
                    par.neighbours = <int *>realloc(par.neighbours, (par.neighboursmax) * cython.sizeof(int))

            # Push children to stack (right first, then left, so left is processed first)
            if current_depth < max_depth:  # Prevent excessive depth
                if stack_top < 62:  # Make room for two nodes
                    stack_nodes[stack_top] = current_node.right_child[0]
                    stack_depths[stack_top] = current_depth + 1
                    stack_top += 1
                    
                    stack_nodes[stack_top] = current_node.left_child[0]
                    stack_depths[stack_top] = current_depth + 1
                    stack_top += 1

        else:
            # Push appropriate child to stack
            if current_depth < max_depth:  # Prevent excessive depth
                if point[axis] <= tparticle.loc[axis]:
                    if stack_top < 63:
                        stack_nodes[stack_top] = current_node.left_child[0]
                        stack_depths[stack_top] = current_depth + 1
                        stack_top += 1
                elif point[axis] >= tparticle.loc[axis]:
                    if stack_top < 63:
                        stack_nodes[stack_top] = current_node.right_child[0]
                        stack_depths[stack_top] = current_depth + 1
                        stack_top += 1