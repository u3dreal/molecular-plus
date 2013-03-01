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
cdef Particle *parlistcopy
cdef ParSys *psys
cdef KDTree *kdtree = <KDTree *>malloc( 1 *cython.sizeof(KDTree) )

cpdef init(importdata):
    global fps
    global substep
    global parnum
    global parlist
    global parlistcopy
    global kdtree
    global psysnum
    global psys
    cdef int i
    cdef int ii

    fps = float(importdata[0][0])
    substep = int(importdata[0][1])
    psysnum = importdata[0][2]
    parnum = importdata[0][3]
    psys = <ParSys *>malloc( psysnum *cython.sizeof(ParSys) )
    parlist = <Particle *>malloc( parnum *cython.sizeof(Particle) )
    parlistcopy = <Particle *>malloc( parnum *cython.sizeof(Particle) )
    cdef int jj = 0
    for i in xrange(psysnum):
        psys[i].id = i
        psys[i].parnum = importdata[i+1][0]
        psys[i].particles = <Particle *>malloc( psys[i].parnum *cython.sizeof(Particle) )
        psys[i].particles = &parlist[jj]
        for ii in xrange(psys[i].parnum):
            parlist[jj].id = jj
            parlist[jj].loc[0] = importdata[i + 1][1][(ii * 3)]
            parlist[jj].loc[1] = importdata[i + 1][1][(ii * 3) + 1]
            parlist[jj].loc[2] = importdata[i + 1][1][(ii * 3) + 2]
            parlist[jj].vel[0] = importdata[i + 1][2][(ii * 3)]
            parlist[jj].vel[1] = importdata[i + 1][2][(ii * 3) + 1]
            parlist[jj].vel[2] = importdata[i + 1][2][(ii * 3) + 2]
            parlist[jj].size = importdata[i + 1][3][ii]
            parlist[jj].sqsize = sq_number(importdata[i + 1][3][ii])
            parlist[jj].mass = importdata[i + 1][4][ii]
            parlist[jj].state = importdata[i + 1][5][ii]
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
            parlist[jj].sys = &psys[i]
            parlist[jj].collided_with = <Particle *>malloc( 1 *cython.sizeof(Particle) )
            parlist[jj].collided_num = 0
            parlist[jj].link_with = <Particle *>malloc( 1 *cython.sizeof(Particle) )
            parlist[jj].link_withnum = 0
            jj += 1
            
    jj = 0

    KDTree_create_nodes(kdtree,parnum)
    for i in range(parnum):
        parlistcopy[i] = parlist[i]
    KDTree_create_tree(kdtree,parlistcopy,0,parnum - 1,"root",0)
    
    #testkdtree(3)
    
    return parnum

cdef testkdtree(int verbose = 0):
    global kdtree
    global parnum
    if verbose >= 3:
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
    if verbose >= 1:
        print("start searching")
    b = KDTree_rnn_query(kdtree,a,2)
    output = []
    if verbose >= 2:
        print("Result")
        for i in xrange(kdtree.num_result):
            print("Query Node:",b[i].index," Query Particle:",b[i].particle[0].id)
            #print("Query Node:",b[i].index)
            #print("Query Particle:",b[i].particle[0].id)
    if verbose >= 1:
        print("number of particle find:",kdtree.num_result)
    free(b)
    
    
cpdef simulate(importdata):
    global kdtree
    global parlist
    global parlistcopy
    global parnum
    global psysnum
    global psys
    
    cdef int i
    cdef int ii
    
    update(importdata)
    
    for i in range(parnum):
        parlistcopy[i] = parlist[i]
    KDTree_create_tree(kdtree,parlistcopy,0,parnum - 1,"root",0)
    
    #testkdtree(1)
    
    for i in xrange(parnum):
        #print("simulate par:",parlist[i].id," z vel:",parlist[i].vel[2])
        collide(&parlist[i])
    
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
    

cdef collide(Particle *par):
    global kdtree
    cdef Node *neighbours
    cdef Particle par2
    cdef float stiff
    cdef float target
    cdef float sqtarget
    cdef float lenghtx
    cdef float lenghty
    cdef float lenghtz
    cdef float sqlenght
    cdef float lenght
    cdef float factor
    cdef float ratio1
    cdef float ratio2
    cdef float factor1
    cdef float factor2
    cdef float col_normal1[3]
    cdef float col_normal2[3]
    cdef float ypar_vel[3]
    cdef float xpar_vel[3]
    cdef float yi_vel[3]
    cdef float xi_vel[3]
    cdef float friction
    cdef int i
    #print("point0")
    neighbours = KDTree_rnn_query(kdtree,par.loc,par.size * 2)
    #print("point0.1")
    for i in xrange(kdtree.num_result):
        #print("point1.1")
        par2 = neighbours[i].particle[0]
        if par.id == par2.id:
            return
        if arraysearch(&par2,par.collided_with,par.collided_num) == -1: 
        #if par2 not in par.collided_with:
            #print("point1.2")
            if par2.sys.id != par.sys.id :
                #print("point1.3")
                if par2.sys.othercollision_active == False or par.sys.othercollision_active == False:
                    #print("point1.4")
                    return
            #print(par.sys.collision_group)
            if par2.sys.collision_group != par.sys.collision_group:
                #print("point2.0")
                return
            if par2.sys.id == par.sys.id and par.sys.selfcollision_active == False:
                #print("point3.0")
                return
            #print("point4.0")
            stiff = (fps * (substep +1))
            target = (par.size + par2.size) * 0.99
            sqtarget = target**2
            #print("point5.0")
            if par.state <= 1 and par2.state <= 1 and arraysearch(&par2,par.link_with,par.link_withnum) == -1 and arraysearch(par,par2.link_with,par2.link_withnum) == -1:
            #if par.state <= 1 and par2.state <= 1 and par2 not in par.link_with and par not in par2.link_with:
                #print("point6.0")
                lenghtx = par.loc[0] - par2.loc[0]
                lenghty = par.loc[1] - par2.loc[1]
                lenghtz = par.loc[2] - par2.loc[2]
                #print("Z:",par.loc[2] , par2.loc[2])
                sqlenght  = square_dist(par.loc,par2.loc,3)
                #print("point6.1")
                #print(sqlenght,sqtarget)
                if sqlenght != 0 and sqlenght < sqtarget:
                    #print("Hit!!!")
                    lenght = sqlenght**0.5
                    factor = (lenght - target) / lenght
                    ratio1 = (par2.mass/(par.mass + par2.mass))
                    ratio2 = (par.mass/(par.mass + par2.mass))
                    
                    par.vel[0] -= (lenghtx * factor * ratio1) * stiff
                    par.vel[1] -= (lenghty * factor * ratio1) * stiff
                    par.vel[2] -= (lenghtz * factor * ratio1) * stiff
                    par2.vel[0] += (lenghtx * factor * ratio2) * stiff
                    par2.vel[1] += (lenghty * factor * ratio2) * stiff
                    par2.vel[2] += (lenghtz * factor * ratio2) * stiff
                    
                    #print("point6.2")
                    """
                    col_normal1[0] = (par2.loc[0] - par.loc[0]) / lenght
                    col_normal1[1] = (par2.loc[1] - par.loc[1]) / lenght
                    col_normal1[2] = (par2.loc[2] - par.loc[2]) / lenght
                    #print("par2.vel:",par2.vel)
                    #print("Normal",col_normal1)
                    #print("Normal_length",(col_normal1[0]**2 + col_normal1[1]**2 + col_normal1[2]**2)**0.5)
                    col_normal2[0] = col_normal1[0] * -1
                    col_normal2[1] = col_normal1[1] * -1
                    col_normal2[2] = col_normal1[2] * -1
                     
                    factor1 = dot_product(par.vel,col_normal1)      
                    ypar_vel[0] = factor1 * col_normal1[0]
                    ypar_vel[1] = factor1 * col_normal1[1]
                    ypar_vel[2] = factor1 * col_normal1[2]
                    xpar_vel[0] = par.vel[0] - ypar_vel[0]
                    xpar_vel[1] = par.vel[1] - ypar_vel[1]
                    xpar_vel[2] = par.vel[2] - ypar_vel[2]
                    #print("point6.3")
                    factor2 = dot_product(par2.vel,col_normal2)
                    yi_vel[0] = factor2 * col_normal2[0]
                    yi_vel[1] = factor2 * col_normal2[1]
                    yi_vel[2] = factor2 * col_normal2[2]
                    xi_vel[0] = par2.vel[0] - yi_vel[0]
                    xi_vel[1] = par2.vel[1] - yi_vel[1]
                    xi_vel[2] = par2.vel[2] - yi_vel[2]
                    
                    #print("yi_vel:",yi_vel)
                    #print("xi_vel:",xi_vel)
                    

                    Ua = factor1
                    #print("Ua:",Ua)       
                    Ub = -factor2
                    #print("Ub:",Ub)  
                    Cr = 1
                    Ma = par.mass
                    Mb = par2.mass     
                    Va = (Cr*Mb*(Ub-Ua)+Ma*Ua+Mb*Ub)/(Ma+Mb)
                    Vb = (Cr*Ma*(Ua-Ub)+Ma*Ua+Mb*Ub)/(Ma+Mb)
                    #print("Va:",Va)
                    #print("Vb:",Vb)  
                    
                    #print("factor:",-(factor * ratio1) * stiff)
                    mula = 1
                    #print("mula:",mula)
                    mulb = 1
                    #print("mulb:",mulb)
                    ypar_vel[0] = col_normal1[0] * Va * mula
                    ypar_vel[1] = col_normal1[1] * Va * mula
                    ypar_vel[2] = col_normal1[2] * Va * mula
                    yi_vel[0] = col_normal1[0] * Vb * mulb
                    yi_vel[1] = col_normal1[1] * Vb * mulb
                    yi_vel[2] = col_normal1[2] * Vb * mulb
                    #print("yi_vel after:",yi_vel)
                    #print("xi_vel after:",xi_vel)

                    #print("point6.4")
                    friction = 1 - ((par.sys.friction + par2.sys.friction ) / 2)
                    xpar_vel[0] *= friction
                    xpar_vel[1] *= friction
                    xpar_vel[2] *= friction
                    xi_vel[0] *= friction
                    xi_vel[1] *= friction
                    xi_vel[2] *= friction
                    
                    #print("par_vel befor:",par.vel)
                    #print("i_vel befor:",par2.vel)
                    par.vel[0] = ypar_vel[0] + xpar_vel[0]
                    par.vel[1] = ypar_vel[1] + xpar_vel[1]
                    par.vel[2] = ypar_vel[2] + xpar_vel[2]
                    par2.vel[0] = yi_vel[0] + xi_vel[0]
                    par2.vel[1] = yi_vel[1] + xi_vel[1]
                    par2.vel[2] = yi_vel[2] + xi_vel[2]
                    #print("par_vel after:",par.vel)
                    #print("i_vel after:",par2.vel)
                    #print("point6.5")
                    par2.vel[1] += 1.0
                    par.vel[1] -= 1.0

                    if abs(Va) < abs(((factor * ratio1) * stiff)):
                        par.vel[0] -= ((lenghtx * factor * ratio1) * stiff)
                        par.vel[1] -= ((lenghty * factor * ratio1) * stiff)
                        par.vel[2] -= ((lenghtz * factor * ratio1) * stiff)
                    if abs(Vb) < abs(((factor * ratio2) * stiff)):
                        par2.vel[0] += ((lenghtx * factor * ratio2) * stiff)
                        par2.vel[1] += ((lenghty * factor * ratio2) * stiff)
                        par2.vel[2] += ((lenghtz * factor * ratio2) * stiff)
                    """
                    
                    #par2.collided_with.append(par)
                    #if (par.sys.relink_chance + par.sys.relink_chance / 2) > 0:
                        #create_link(par,[par2,lenght**2])

                    #print("point8.0")
                #print("point9.0")
            #print("point10.0")
        #print("point11.0")
    #print("point12.0")
    
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
            #print("update par:",psys[i].particles[ii].id," z vel:",psys[i].particles[ii].vel[2])
    
 
cdef KDTree_create_nodes(KDTree *kdtree,int parnum):
    cdef int i
    kdtree.nodes = <Node *>malloc( (parnum + 1) *cython.sizeof(Node) )
    kdtree.root_node = <Node *>malloc( 1 *cython.sizeof(Node) )
    for i in xrange(parnum):
        kdtree.nodes[i].index = i
        kdtree.nodes[i].particle = <Particle *>malloc( 1 *cython.sizeof(Particle) )
        kdtree.nodes[i].left_child = <Node *>malloc( 1 *cython.sizeof(Node) )
        kdtree.nodes[i].right_child = <Node *>malloc( 1 *cython.sizeof(Node) )
        kdtree.nodes[i].left_child[0].index = -1
        kdtree.nodes[i].right_child[0].index = -1
    kdtree.nodes[parnum + 1].index = -1
    kdtree.nodes[parnum + 1].name = "null"
    kdtree.nodes[parnum + 1].particle = <Particle *>malloc( 1 *cython.sizeof(Particle) )
    kdtree.nodes[parnum + 1].left_child = <Node *>malloc( 1 *cython.sizeof(Node) )
    kdtree.nodes[parnum + 1].right_child = <Node *>malloc( 1 *cython.sizeof(Node) )
    kdtree.nodes[parnum + 1].left_child[0].index = -1
    kdtree.nodes[parnum + 1].right_child[0].index = -1
    return

    
cdef Node KDTree_create_tree(KDTree *kdtree,Particle *kdparlist,int start,int end,char *name,int depth):
    global parnum
    cdef int index
    cdef int len = (end - start) + 1
    if len <= 0:
        return kdtree.nodes[parnum + 1]
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
    cdef float sqdist
    cdef int k 
    cdef int i
    kdtree.num_result = 0
    free(kdtree.result)
    kdtree.result = <Node *>malloc( 1 *cython.sizeof(Node) )
    kdtree.result[0] = kdtree.nodes[parnum + 1]
    if kdtree.root_node[0].index != kdtree.nodes[0].index:
        kdtree.result[0] = kdtree.nodes[parnum + 1]
        num_result = 1
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
    int id
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
    ParSys *sys
    Particle *collided_with
    Particle *link_with
    int collided_num
    int link_withnum
 
 
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

  
cdef int arraysearch(Particle *element,Particle *array,int len):
    cdef int i
    for i in xrange(len):
        if element.id == array[i].id:
            return i
    return -1
    
 
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

    
cdef float dot_product(float u[3],float v[3]):
    cdef float dot
    dot = (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])
    return dot
