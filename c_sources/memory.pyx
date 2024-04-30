cpdef memfree():
    global kdtree
    global psysnum
    global parnum
    global psys
    global parlist
    global parlistcopy
    global fps
    global substep
    global deadlinks
    cdef int i = 0

    fps = 0
    substep = 0
    deltatime = 0
    cpunum = 0
    newlinks = 0
    totallinks = 0
    totaldeadlinks = 0
    free(deadlinks)
    deadlinks = NULL

    for i in range(parnum):
        if parnum >= 1:
            if parlist[i].neighboursnum >= 1:
                free(parlist[i].neighbours)
                parlist[i].neighbours = NULL
                parlist[i].neighboursnum = 0
            if parlist[i].collided_num >= 1:
                free(parlist[i].collided_with)
                parlist[i].collided_with = NULL
                parlist[i].collided_num = 0
            if parlist[i].links_num >= 1:
                free(parlist[i].links)
                parlist[i].links = NULL
                parlist[i].links_num = 0
                parlist[i].links_activnum = 0
            if parlist[i].link_withnum >= 1:
                free(parlist[i].link_with)
                parlist[i].link_with = NULL
                parlist[i].link_withnum = 0
            if parlist[i].neighboursnum >= 1:
                free(parlist[i].neighbours)
                parlist[i].neighbours = NULL
                parlist[i].neighboursnum = 0

    for i in range(psysnum):
        if psysnum >= 1:
            psys[i].particles = NULL

    if psysnum >= 1:
        free(psys)
        psys = NULL

    if parnum >= 1:
        free(parlistcopy)
        parlistcopy = NULL
        free(parlist)
        parlist = NULL

    parnum = 0
    psysnum = 0

    if kdtree.numnodes >= 1:
        for i in range(kdtree.numnodes):
            free(kdtree.nodes[i].particle)
            kdtree.nodes[i].particle = NULL
            free(kdtree.nodes[i].left_child)
            kdtree.nodes[i].left_child = NULL
            free(kdtree.nodes[i].right_child)
            kdtree.nodes[i].right_child = NULL

        free(kdtree.thread_nodes)
        kdtree.thread_nodes = NULL
        free(kdtree.thread_start)
        kdtree.thread_start = NULL
        free(kdtree.thread_end)
        kdtree.thread_end = NULL
        free(kdtree.thread_name)
        kdtree.thread_name = NULL
        free(kdtree.thread_parent)
        kdtree.thread_parent = NULL
        free(kdtree.thread_depth)
        kdtree.thread_depth = NULL
        free(kdtree.nodes)
        kdtree.nodes = NULL
        free(kdtree.root_node)
        kdtree.root_node = NULL

    free(kdtree)
    kdtree = NULL