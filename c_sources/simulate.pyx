#cython: profile=False
#cython: boundscheck=False
#cython: wraparound=False
#cython: cdivision=True
#cython: language_level=3
#cython: cpow=True

# NOTE: order of slow functions to be optimize/multithreaded:
# spatial_hash_building, spatial_hash_querying, linksolving


cimport cython
from time import process_time as clock
from cython.parallel import parallel, prange, threadid
from libc.stdlib cimport malloc, realloc, free, rand, srand, abs
from libc.string cimport memcpy
from libc.math cimport sqrt

#cdef extern from "omp.h":
#    void omp_set_max_active_levels(int max_levels)

#def set_max_active_levels(int max_levels):
#    omp_set_max_active_levels(max_levels)

#set_max_active_levels(1)

cdef extern from *:
    int INT_MAX
    float FLT_MAX


cdef extern from "stdlib.h":
    ctypedef void const_void "const void"
    void qsort(
        void *base,
        int nmemb,
        int size,
        int(*compar)(const_void *, const_void *)
    )noexcept nogil


cdef float fps = 0
cdef int substep = 0
cdef float deltatime = 0
cdef int parnum = 0
cdef int psysnum = 0
cdef int cpunum = 0
cdef int newlinks = 0
cdef int totallinks = 0
cdef int totaldeadlinks = 0
cdef int *deadlinks = NULL
cdef Particle *parlist = NULL
cdef SParticle *parlistcopy = NULL
cdef ParSys *psys = NULL
cdef SpatialHash *spatialhash = NULL
print("cmolcore imported  v1.21.5")

cpdef simulate(importdata):
    global spatialhash
    global parlist
    global parlistcopy
    global parnum
    global psysnum
    global psys
    global cpunum
    global deltatime
    global newlinks
    global totallinks
    global totaldeadlinks
    global deadlinks

    cdef int i = 0
    cdef int ii = 0
    cdef int profiling = 0
    cdef float minX = INT_MAX
    cdef float minY = INT_MAX
    cdef float minZ = INT_MAX
    cdef float maxX = -INT_MAX
    cdef float maxY = -INT_MAX
    cdef float maxZ = -INT_MAX
    cdef float maxSize = -INT_MAX
    cdef Pool *parPool = <Pool *>malloc(1 * cython.sizeof(Pool))
    parPool.parity = <Parity *>malloc(2 * cython.sizeof(Parity))
    parPool[0].axis = -1
    parPool[0].offset = 0
    parPool[0].max = 0

    newlinks = 0
    for i in range(cpunum):
        deadlinks[i] = 0
    if profiling == 1:
        print("-->start simulate")
        stime2 = clock()
        stime = clock()

    update(importdata)

    if profiling == 1:
        print("-->update time", clock() - stime, "sec")
        stime = clock()

    for i in range(parnum):
        parlistcopy[i].id = parlist[i].id

        parlistcopy[i].loc[0] = parlist[i].loc[0]
        if parlist[i].loc[0] < minX:
            minX = parlist[i].loc[0]
        if parlist[i].loc[0] > maxX:
            maxX = parlist[i].loc[0]

        parlistcopy[i].loc[1] = parlist[i].loc[1]
        if parlist[i].loc[1] < minY:
            minY = parlist[i].loc[1]
        if parlist[i].loc[1] > maxY:
            maxY = parlist[i].loc[1]

        parlistcopy[i].loc[2] = parlist[i].loc[2]
        if parlist[i].loc[2] < minZ:
            minZ = parlist[i].loc[2]
        if parlist[i].loc[2] > maxZ:
            maxZ = parlist[i].loc[2]

        if parlist[i].sys.links_active == 1:
            if parlist[i].links_num > 0:
                for ii in range(parlist[i].links_num):
                    if parlist[i].links[ii].lenght > maxSize:
                        maxSize = parlist[i].links[ii].lenght

        if (parlist[i].size * 2) > maxSize:
            maxSize = (parlist[i].size * 2)

    if (maxX - minX) >= (maxY - minY) and (maxX - minX) >= (maxZ - minZ):
        parPool[0].axis = 0
        parPool[0].offset = 0 - minX
        parPool[0].max = maxX + parPool[0].offset

    if (maxY - minY) > (maxX - minX) and (maxY - minY) > (maxZ - minZ):
        parPool[0].axis = 1
        parPool[0].offset = 0 - minY
        parPool[0].max = maxY + parPool[0].offset

    if (maxZ - minZ) > (maxY - minY) and (maxZ - minZ) > (maxX - minX):
        parPool[0].axis = 2
        parPool[0].offset = 0 - minZ
        parPool[0].max = maxZ + parPool[0].offset

    if (parPool[0].max / ( cpunum * 10 )) > maxSize:
        maxSize = (parPool[0].max / ( cpunum * 10 ))


    cdef int pair
    cdef int heaps
    cdef float scale = 1 / ( maxSize * 2.1 )

    for pair in range(2):

        parPool[0].parity[pair].heap = \
            <Heap *>malloc((<int>(parPool[0].max * scale) + 1) * \
            cython.sizeof(Heap))

        for heaps in range(<int>(parPool[0].max * scale) + 1):
            parPool[0].parity[pair].heap[heaps].parnum = 0
            parPool[0].parity[pair].heap[heaps].maxalloc = 50

            parPool[0].parity[pair].heap[heaps].par = \
                <int *>malloc(parPool[0].parity[pair].heap[heaps].maxalloc * \
                cython.sizeof(int))

    for i in range(parnum):
        pair = <int>(((
            parlist[i].loc[parPool[0].axis] + parPool[0].offset) * scale) % 2
        )
        heaps = <int>((
            parlist[i].loc[parPool[0].axis] + parPool[0].offset) * scale
        )
        parPool[0].parity[pair].heap[heaps].parnum += 1

        if parPool[0].parity[pair].heap[heaps].parnum > \
                parPool[0].parity[pair].heap[heaps].maxalloc:

            parPool[0].parity[pair].heap[heaps].maxalloc = \
                <int>(parPool[0].parity[pair].heap[heaps].maxalloc * 1.25)

            parPool[0].parity[pair].heap[heaps].par = \
                <int *>realloc(
                    parPool[0].parity[pair].heap[heaps].par,
                    (parPool[0].parity[pair].heap[heaps].maxalloc + 2 ) * \
                    cython.sizeof(int)
                )

        parPool[0].parity[pair].heap[heaps].par[
            (parPool[0].parity[pair].heap[heaps].parnum - 1)] = parlist[i].id

    if profiling == 1:
        print("-->copy data time", clock() - stime, "sec")
        stime = clock()

    # Build spatial hash grid
    SpatialHash_build(spatialhash, parlistcopy, parnum, maxSize)

    if profiling == 1:
        print("-->create spatial hash time", clock() - stime,"sec")
        stime = clock()

    # Query neighbors using spatial hash
    with nogil:
        for i in prange(
                        parnum,
                        schedule='dynamic',
                        chunksize=2,
                        num_threads=cpunum
                        ):
            SpatialHash_query_neighbors(
                spatialhash,
                &parlist[i],
                parlist,
                parlist[i].size * 2
            )

    if profiling == 1:
        print("-->neighbours time", clock() - stime, "sec")
        stime = clock()

    #cdef int total_heaps = <int>(parPool[0].max * scale) + 1
    #cdef int total_pairs = 2

    # Create a list of tasks
    #tasks = [(pair, heaps, i) for pair in range(total_pairs) for heaps in range(total_heaps) for i in range(parPool[0].parity[pair].heap[heaps].parnum)]

    #cdef int index
    #for index in prange(len(tasks), nogil=True):
    #    pair, heaps, i = tasks[index]
    #    collide(&parlist[parPool[0].parity[pair].heap[heaps].par[i]])
    #    solve_link(&parlist[parPool[0].parity[pair].heap[heaps].par[i]])

    #    if parlist[parPool[0].parity[pair].heap[heaps].par[i]].neighboursnum > 1:
    #        parlist[parPool[0].parity[pair].heap[heaps].par[i]].neighboursnum = 0

    with nogil:
        for pair in range(2):
            for heaps in prange(
                                <int>(parPool[0].max * scale) + 1,
                                schedule='dynamic',
                                chunksize=2,
                                num_threads=cpunum
                                ):
                for i in range(parPool[0].parity[pair].heap[heaps].parnum):

                    collide(
                        &parlist[parPool[0].parity[pair].heap[heaps].par[i]]
                    )

                    solve_link(
                        &parlist[parPool[0].parity[pair].heap[heaps].par[i]]
                    )

                    if parlist[
                        parPool[0].parity[pair].heap[heaps].par[i]
                    ].neighboursnum > 1:

                       # free(parlist[i].neighbours)

                        parlist[
                            parPool[0].parity[pair].heap[heaps].par[i]
                        ].neighboursnum = 0

    if profiling == 1:
        print("-->collide/solve link time", clock() - stime, "sec")
        stime = clock()

    exportdata = []
    parloc = []
    parvel = []
    parloctmp = []
    parveltmp = []

    for i in range(psysnum):
        for ii in range(psys[i].parnum):
            parloctmp.append(psys[i].particles[ii].loc[0])
            parloctmp.append(psys[i].particles[ii].loc[1])
            parloctmp.append(psys[i].particles[ii].loc[2])
            parveltmp.append(psys[i].particles[ii].vel[0])
            parveltmp.append(psys[i].particles[ii].vel[1])
            parveltmp.append(psys[i].particles[ii].vel[2])
        parloc.append(parloctmp)
        parvel.append(parveltmp)
        parloctmp = []
        parveltmp = []

    totallinks += newlinks
    pydeadlinks = 0
    for i in range(cpunum):
        pydeadlinks += deadlinks[i]
    totaldeadlinks += pydeadlinks

    exportdata = [
        parloc,
        parvel,
        newlinks,
        pydeadlinks,
        totallinks,
        totaldeadlinks
    ]

    for pair in range(2):
        for heaps in range(<int>(parPool[0].max * scale) + 1):
            parPool[0].parity[pair].heap[heaps].parnum = 0
            free(parPool[0].parity[pair].heap[heaps].par)
        free(parPool[0].parity[pair].heap)
    free(parPool[0].parity)
    free(parPool)

    if profiling == 1:
        print("-->export time", clock() - stime, "sec")
        print("-->all process time", clock() - stime2, "sec")
    return exportdata
