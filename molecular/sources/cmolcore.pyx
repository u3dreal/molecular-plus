cimport cython
from cython.parallel import parallel,prange
from libc.stdlib cimport malloc , realloc, free , rand , srand

cdef extern from "stdlib.h":
    ctypedef void const_void "const void"
    void qsort(void *base, int nmemb, int size,int(*compar)(const_void *, const_void *)) nogil

cdef float fps = 0
cdef int substep = 0
cdef int parnum = 0
cdef int psysnum = 0
cdef Particle *parlist
cdef ParSys *psys
cdef KDTree *kdtree = <KDTree *>malloc( 1 *cython.sizeof(KDTree) )
kdtree.result = <Node *>malloc( 1 *cython.sizeof(Node) )
    
cpdef init(importdata):
    global fps
    global substep
    global parnum
    global parlist
    global kdtree
    global psysnum
    global psys
    cdef int i
    cdef int ii

    fps = float(importdata[0][0])
    substep = int(importdata[0][1])
    psysnum = importdata[0][2]
    psys = <ParSys *>malloc( psysnum *cython.sizeof(ParSys) )
    cdef int jj = 0
    for i in xrange(psysnum):
        psys[i].parnum = importdata[i+1][0]
        parnum += psys[i].parnum
        psys[i].particles = <Particle *>malloc( psys[i].parnum *cython.sizeof(Particle) )
        for ii in xrange(psys[i].parnum):
            psys[i].particles[ii].id = jj
            psys[i].particles[ii].loc[0] = importdata[i + 1][1][(ii * 3)]
            psys[i].particles[ii].loc[1] = importdata[i + 1][1][(ii * 3) + 1]
            psys[i].particles[ii].loc[2] = importdata[i + 1][1][(ii * 3) + 2]
            psys[i].particles[ii].vel[0] = importdata[i + 1][2][(ii * 3)]
            psys[i].particles[ii].vel[1] = importdata[i + 1][2][(ii * 3) + 1]
            psys[i].particles[ii].vel[2] = importdata[i + 1][2][(ii * 3) + 2]
            psys[i].particles[ii].size = importdata[i + 1][3][ii]
            psys[i].particles[ii].sqsize = sq_number(importdata[i + 1][3][ii])
            psys[i].particles[ii].mass = importdata[i + 1][4][ii]
            psys[i].particles[ii].state = importdata[i + 1][5][ii]
            psys[i].selfcollision_active = importdata[i + 1][6][0]
            psys[i].othercollision_active = importdata[i + 1][6][1]
            psys[i].collision_group = int(importdata[i + 1][6][2])
            psys[i].links_active = importdata[i + 1][6][3]
            psys[i].link_length = importdata[i + 1][6][4]
            psys[i].link_stiff = importdata[i + 1][6][5]
            psys[i].link_stiffrand = importdata[i + 1][6][6]
            psys[i].link_stiffexp = importdata[i + 1][6][7]
            psys[i].friction = importdata[i + 1][6][8]
            psys[i].link_damp = importdata[i + 1][6][9]
            psys[i].link_damprand = importdata[i + 1][6][10]
            psys[i].link_broken = importdata[i + 1][6][11]
            psys[i].link_brokenrand = importdata[i + 1][6][12]
            psys[i].relink_group = int(importdata[i + 1][6][13])
            psys[i].relink_chance = importdata[i + 1][6][14]
            psys[i].relink_chancerand = importdata[i + 1][6][15]
            psys[i].relink_stiff = importdata[i + 1][6][16]
            psys[i].relink_stiffexp = importdata[i + 1][6][17]
            psys[i].relink_stiffrand = importdata[i + 1][6][18]
            psys[i].relink_damp = importdata[i + 1][6][19]
            psys[i].relink_damprand = importdata[i + 1][6][20]
            psys[i].relink_broken = importdata[i + 1][6][21]
            psys[i].relink_brokenrand = importdata[i + 1][6][22]
            psys[i].particles[ii].sys = psys[i]
            jj += 1
            
    jj = 0
    parlist = <Particle *>malloc( parnum *cython.sizeof(Particle) )
    for i in xrange(psysnum):
        for ii in xrange(psys[i].parnum):
            parlist[jj] = psys[i].particles[ii]
            jj += 1
    KDTree_create_nodes(kdtree,parnum)
    KDTree_create_tree(kdtree,parlist,0,parnum - 1,"root",0)
    
    print("RootNode:",kdtree.root_node[0].index)
    for i in xrange(parnum):
        print("Parent",kdtree.nodes[i].index,"Particle:",kdtree.nodes[i].particle[0].id)
        print("    Left",kdtree.nodes[i].left_child[0].index)
        print("    Right",kdtree.nodes[i].right_child[0].index)

    cdef float a[3]
    a[0] = 0
    a[1] = 0
    a[2] = 0
    cdef Node *b
    b = <Node *>malloc( parnum *cython.sizeof(Node) )
    b = KDTree_rnn_query(kdtree,a,2)
    output = []
    print("Result")
    for i in xrange(kdtree.num_result):
        print("Query Node:",b[i].index)
        print("Query Particle:",b[i].particle[0].id)
    print("number of particle find:",kdtree.num_result)
    
    return parnum

    
cpdef simulate(importdata):
    global kdtree
    global parlist
    global parnum
    global psysnum
    global psys
    
    cdef int i
    cdef int ii
    
    update(importdata)
    
    exportdata = []
    parloc = []
    parvel = []
    parloctmp = []
    parveltmp = []
    for i in xrange(psysnum):
        for ii in xrange(psys[i].parnum):
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
    exportdata = [parloc,parvel]
    
    return exportdata

    
cdef update(data):
    global parlist
    global parnum
    global psysnum
    global psys
    cdef int i = 0
    cdef int ii = 0
    for i in xrange(psysnum):
        for ii in xrange(psys[i].parnum):
            psys[i].particles[ii].loc[0] = data[i][0][(ii * 3)]
            psys[i].particles[ii].loc[1] = data[i][0][(ii * 3) + 1]
            psys[i].particles[ii].loc[2] = data[i][0][(ii * 3) + 2]
            psys[i].particles[ii].vel[0] = data[i][1][(ii * 3)]
            psys[i].particles[ii].vel[1] = data[i][1][(ii * 3) + 1]
            psys[i].particles[ii].vel[2] = data[i][1][(ii * 3) + 2]
            if psys[i].particles[ii].state == 0 and data[i][2][ii] == 0:
                psys[i].particles[ii].state = data[i][2][ii] + 1
                #create_link(par)
                #parlist.append(par)
            elif psys[i].particles[ii].state == 1 and data[i][2][ii] == 0:
                psys[i].particles[ii].state = 1
                #parlist.append(par)
            else:
                psys[i].particles[ii].state = data[i][2][ii]
            psys[i].particles[ii].collided_num = 0
    
 
cdef KDTree_create_nodes(KDTree *kdtree,int parnum):
    cdef int i
    kdtree.nodes = <Node *>malloc( parnum *cython.sizeof(Node) )
    kdtree.root_node = <Node *>malloc( 1 *cython.sizeof(Node) )
    for i in xrange(parnum):
        kdtree.nodes[i].index = i
        kdtree.nodes[i].particle = <Particle *>malloc( 1 *cython.sizeof(Particle) )
        kdtree.nodes[i].left_child = <Node *>malloc( 1 *cython.sizeof(Node) )
        kdtree.nodes[i].right_child = <Node *>malloc( 1 *cython.sizeof(Node) )
        kdtree.nodes[i].left_child[0].index = -2
        kdtree.nodes[i].right_child[0].index = -2
    return

    
cdef Node KDTree_create_tree(KDTree *kdtree,Particle *kdparlist,int start,int end,char *name,int depth):
    global parnum
    cdef Node *null
    cdef int index
    cdef int len = (end - start) + 1
    if len <= 0:
        null = <Node *>malloc( 1 *cython.sizeof(Node) )
        null[0].index = -1
        null[0].name = "null"
        null[0].left_child = null
        null[0].right_child = null
        return null[0]
    cdef int axis
    cdef int k = 3
    axis = depth % k
    #print("point0")
    if axis == 0:
        qsort(kdparlist + start,len,sizeof(Particle),compare_x)
    elif axis == 1:
        qsort(kdparlist + start,len,sizeof(Particle),compare_y)
    elif axis == 2:
        qsort(kdparlist + start,len,sizeof(Particle),compare_z)
    cdef int median = (start + end) / 2
    #print("start:",start)
    #print("median:",median)
    #print("end:",end)
    #print("len:",len)
    #print("depth:",depth)
    #print("parnum:",parnum)
    #print("point1")
    if depth == 0:
            kdtree.index = 0
            index = kdtree.index
    else:
        kdtree.index += 1
        index = kdtree.index
    #print("point2")
    kdtree.nodes[index].name = name
    #print("point2.1")
    if len >= 1 and depth == 0:
        kdtree.root_node[0] = kdtree.nodes[0]
    #print("point2.2")
    kdtree.nodes[index].particle[0] = kdparlist[median]
    #print("point3")
    kdtree.nodes[index].left_child[0] = KDTree_create_tree(kdtree,kdparlist,start,median - 1,"left",depth + 1)
    #print("point4")
    kdtree.nodes[index].right_child[0] = KDTree_create_tree(kdtree,kdparlist,median + 1,end,"right",depth + 1)
    #print("point5")
    return kdtree.nodes[index]


cdef Node *KDTree_rnn_query(KDTree *kdtree,float point[3],float dist):
    global parlist
    cdef Node null
    null.index = -1
    cdef float sqdist
    cdef int k 
    cdef int i
    kdtree.num_result = 0
    for i in range(parnum):
        kdtree.result[i] = null
    if kdtree.root_node[0].index != kdtree.nodes[0].index:
        kdtree.result[0] = null
        return kdtree.result
    else:
        sqdist = dist**2
        KDTree_rnn_search(kdtree,kdtree.root_node[0],point,dist,sqdist,3,0)
    return kdtree.result


cdef KDTree_rnn_search(KDTree *kdtree,Node node,float point[3],float dist,float sqdist,int k,int depth):
    cdef int axis
    cdef float realdist
    #print("point0")
    #print("nodeID:",node.index)
    if node.index == -1:
        return
    cdef Particle tparticle = node.particle[0]
    
    axis = depth % k
    #print("Depth:",depth)
    #print("Axis:",axis)
    #print("point0.1")
    if (point[axis] - tparticle.loc[axis])**2 <= sqdist:
        #print("sqdist:",sqdist)
        #print("par loc:",tparticle.loc[0],tparticle.loc[1],tparticle.loc[2])
        realdist = square_dist(point,tparticle.loc,3)
        #print("realdist:",realdist)
        #print("point0.2")
        if realdist <= sqdist:
            #print("point1")
            #print("Result number:",kdtree.num_result)
            kdtree.result[kdtree.num_result] = node
            #print("Node found:",node.index)
            #print("Node recorded:",kdtree.result[kdtree.num_result].index)
            kdtree.num_result += 1
            kdtree.result = <Node *>realloc(kdtree.result,(kdtree.num_result + 1) *cython.sizeof(Node) )
            #print("point1.1")

        #print("point1.2")
        #print("nodeID:",node.index)
        KDTree_rnn_search(kdtree,node.left_child[0],point,dist,sqdist,3,depth + 1)
        #print("point1.3")
        #print("nodeID:",node.index)
        KDTree_rnn_search(kdtree,node.right_child[0],point,dist,sqdist,3,depth + 1)
        #print("point2")
    else:
        if point[axis] <= tparticle.loc[axis]:
            #print("point2.1")
            KDTree_rnn_search(kdtree, node.left_child[0],point,dist,sqdist,3,depth + 1)
        if point[axis] >= tparticle.loc[axis]:
            #print("point2.2")
            KDTree_rnn_search(kdtree, node.right_child[0],point,dist,sqdist,3,depth + 1)
    #print("point3")
            
cdef struct KDTree:
    int index
    int num_result
    Node *result
    Node *root_node
    Node *nodes


cdef struct Node:
    int index
    char *name
    float loc[3]
    Particle *particle
    Node *left_child
    Node *right_child
    

cdef struct ParSys:
    int parnum
    Particle *particles
    int selfcollision_active
    int othercollision_active
    int collision_group
    int links_active
    float link_length
    float link_stiff
    float link_stiffrand
    float link_stiffexp
    float friction
    float link_damp
    float link_damprand
    float link_broken
    float link_brokenrand
    int relink_group
    float relink_chance
    float relink_chancerand
    float relink_stiff
    float relink_stiffexp
    float relink_stiffrand
    float relink_damp
    float relink_damprand
    float relink_broken
    float relink_brokenrand

    
cdef struct Particle:
    int id
    float loc[3]
    float vel[3]
    float size
    float sqsize
    float mass
    float state
    ParSys sys
    Particle *collided_with
    int collided_num
 
 
cdef int compare_x (const void *u, const void *v):
    cdef float w = ((<Particle*>u)).loc[0] - ((<Particle*>v)).loc[0]
    if w < 0:
        return -1
    if w > 0:
        return 1
    return 0

    
cdef int compare_y (const void *u, const void *v):
    cdef float w = ((<Particle*>u)).loc[1] - ((<Particle*>v)).loc[1]
    if w < 0:
        return -1
    if w > 0:
        return 1
    return 0
 
 
cdef int compare_z (const void *u, const void *v):
    cdef float w = ((<Particle*>u)).loc[2] - ((<Particle*>v)).loc[2]
    if w < 0:
        return -1
    if w > 0:
        return 1
    return 0
    
cdef int compare_id (const void *u, const void *v):
    cdef float w = ((<Particle*>u)).id - ((<Particle*>v)).id
    if w < 0:
        return -1
    if w > 0:
        return 1
    return 0   

   
cdef float sq_number(float val):
    cdef float nearsq = 8
    while val > nearsq or val < nearsq / 2:
        if val > nearsq:
            nearsq = nearsq * 2
        elif val < nearsq / 2:
            nearsq = nearsq / 2
    return nearsq
    
    
cdef float square_dist(float point1[3],float point2[3],int k):
    cdef float sq_dist = 0
    for i in xrange(k):
        sq_dist += (point1[i] - point2[i])**2
    return sq_dist