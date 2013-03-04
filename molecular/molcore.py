from math import floor
from sys import getsizeof
from time import clock
from random import random

def init(importdata):
    global fps
    global substep
    global psys
    global kdtree
    global parlist
    
    fps = importdata[0][0]
    substep = importdata[0][1]
    psys = []
    for i in importdata[1:]:
        psys.append(ParSys(i))
    parnum = 0
    for i in psys:
        parnum += i.parnum
    parlist = []  
    for i in psys:
        for ii in i.particle:
            parlist.append(ii)
    timer = clock()
    kdtree = KDTree()
    kdtree.create_nodes(len(parlist))
    kdtree.create_tree(parlist,"root")
    print("  KDtree generation take:",round(clock()-timer,5),"sec")
    """
    point = (0,0,0)
    r = 2
    timer = clock()
    rquery = kdtree.rnn_query(point,r)
    print("  RNN query number find:",len(rquery))
    print("  KDtree RNN query take:",round(clock()-timer,5),"sec")
    timer = clock()
    bquery = kdtree.brute_query(point,r)
    print("  Brute query number find:",len(bquery))
    print("  Brute query take:",round(clock()-timer,5),"sec")
    if len(rquery) != len(bquery):
        print("> DONT MATCH!!!")
    else:
        print("  Match!")
    """
    for i in psys:
        for ii in i.particle:
            create_link(ii)
            
    #for i in kdtree.nodes:
        #ppar = i.particle.id
        #print(parlist[ppar].id)
    return parnum


def simulate(importdata):
    global kdtree
    global parlist
    
    update_ParSys(importdata)
    #print(len(parlist))
    kdtree.create_tree(parlist,"root")
    for parsys in psys:
        for par in parsys.particle:
            collide(par)
            solve_link(par)
            #print(par.state)
    exportdata = []
    parloc = []
    parvel = []
    parloctmp = []
    parveltmp = []
    for parsys in psys:
        for par in parsys.particle:
            parloctmp += par.loc
            parveltmp += par.vel
        parloc.append(parloctmp)  
        parvel.append(parveltmp)
        parloctmp = []
        parveltmp = []   
    exportdata = [parloc,parvel]
    return exportdata
            
            
    
def collide(par):
    global kdtree
    
    neighbours = kdtree.rnn_query(par.loc,par.size * 2)
    
    for ii in neighbours:
        i = ii[0].particle
        if i not in par.collided_with:
            if i.sys != par.sys :
                if i.sys.othercollision_active == False or par.sys.othercollision_active == False:
                    return
            #print(par.sys.collision_group)
            if i.sys.collision_group != par.sys.collision_group:
                return
            if i.sys == par.sys and par.sys.selfcollision_active == False:
                return
            
            stiff = (fps * (substep +1))
            target = (par.size + i.size) * 0.99
            sqtarget = target**2
            
            if par.state <= 1 and i.state <= 1 and i not in par.link_with and par not in i.link_with:
                lenghtx = par.loc[0] - i.loc[0]
                lenghty = par.loc[1] - i.loc[1]
                lenghtz = par.loc[2] - i.loc[2]
                sqlenght  = ii[1]
                if sqlenght != 0 and sqlenght < sqtarget:
                    lenght = sqlenght**0.5
                    factor = (lenght - target) / lenght
                    ratio1 = (i.mass/(par.mass + i.mass))
                    ratio2 = (par.mass/(par.mass + i.mass))
                    
                    par.vel[0] -= (lenghtx * factor * ratio1) * stiff
                    par.vel[1] -= (lenghty * factor * ratio1) * stiff
                    par.vel[2] -= (lenghtz * factor * ratio1) * stiff
                    i.vel[0] += (lenghtx * factor * ratio2) * stiff
                    i.vel[1] += (lenghty * factor * ratio2) * stiff
                    i.vel[2] += (lenghtz * factor * ratio2) * stiff
                    
                  
                    
                    col_normal1 = [(i.loc[0] - par.loc[0]) / lenght,(i.loc[1] - par.loc[1]) / lenght,(i.loc[2] - par.loc[2]) / lenght]
                    #print("i.vel:",i.vel)
                    #print("Normal",col_normal1)
                    #print("Normal_length",(col_normal1[0]**2 + col_normal1[1]**2 + col_normal1[2]**2)**0.5)
                    col_normal2 = [col_normal1[0] * -1,col_normal1[1] * -1,col_normal1[2] * -1]
                     
                    factor1 = dot_product(par.vel,col_normal1)      
                    ypar_vel = [factor1 * col_normal1[0],factor1 * col_normal1[1],factor1 * col_normal1[2]]
                    xpar_vel = [par.vel[0] - ypar_vel[0],par.vel[1] - ypar_vel[1],par.vel[2] - ypar_vel[2]]
                    
                    factor2 = dot_product(i.vel,col_normal2)
                    yi_vel = [factor2 * col_normal2[0],factor2 * col_normal2[1],factor2* col_normal2[2]]
                    xi_vel = [i.vel[0] - yi_vel[0],i.vel[1] - yi_vel[1],i.vel[2] - yi_vel[2]]
                    
                    #print("yi_vel:",yi_vel)
                    #print("xi_vel:",xi_vel)
                    
                    """
                    Ua = factor1
                    #print("Ua:",Ua)       
                    Ub = -factor2
                    #print("Ub:",Ub)  
                    Cr = 1
                    Ma = par.mass
                    Mb = i.mass     
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
                    """
                    friction = 1 - ((par.sys.friction + i.sys.friction ) / 2)
                    xpar_vel[0] *= friction
                    xpar_vel[1] *= friction
                    xpar_vel[2] *= friction
                    xi_vel[0] *= friction
                    xi_vel[1] *= friction
                    xi_vel[2] *= friction
                    
                    #print("par_vel befor:",par.vel)
                    #print("i_vel befor:",i.vel)
                    par.vel = [ypar_vel[0] + xpar_vel[0],ypar_vel[1] + xpar_vel[1],ypar_vel[2] + xpar_vel[2]]
                    i.vel = [yi_vel[0] + xi_vel[0],yi_vel[1] + xi_vel[1],yi_vel[2] + xi_vel[2]]
                    #print("par_vel after:",par.vel)
                    #print("i_vel after:",i.vel)
                    
                    """
                    if abs(Va) < abs(((factor * ratio1) * stiff)):
                        par.vel[0] -= ((lenghtx * factor * ratio1) * stiff)
                        par.vel[1] -= ((lenghty * factor * ratio1) * stiff)
                        par.vel[2] -= ((lenghtz * factor * ratio1) * stiff)
                    if abs(Vb) < abs(((factor * ratio2) * stiff)):
                        i.vel[0] += ((lenghtx * factor * ratio2) * stiff)
                        i.vel[1] += ((lenghty * factor * ratio2) * stiff)
                        i.vel[2] += ((lenghtz * factor * ratio2) * stiff)
                    """
                    
                    i.collided_with.append(par)
                    if (par.sys.relink_chance + par.sys.relink_chance / 2) > 0:
                        create_link(par,[i,lenght**2])
                    
                    
                    
def solve_link(par):
    broken_links = []
    for link in par.links:
        
        stiff = link.stiffness * (fps * (substep +1))
        damping = link.damping
        timestep = 1/(fps * (substep +1))
        exp = link.exponent
        par1 = link.start
        par2 = link.end
        Loc1 = par1.loc
        Loc2 = par2.loc
        V1 = link.start.vel
        V2 = link.end.vel
        LengthX = Loc2[0] - Loc1[0]
        LengthY = Loc2[1] - Loc1[1]
        LengthZ = Loc2[2] - Loc1[2]
        Length = (LengthX**2 + LengthY**2 + LengthZ**2)**(0.5)
        if link.lenght != Length:
            Vx = V2[0] - V1[0]
            Vy = V2[1] - V1[1]
            Vz = V2[2] - V1[2]
            V = (Vx * LengthX + Vy * LengthY+Vz * LengthZ) / Length
            ForceSpring = ((Length - link.lenght)**(exp)) * stiff
            ForceDamper = damping * V
            ForceX = (ForceSpring + ForceDamper) * LengthX / Length
            ForceY = (ForceSpring + ForceDamper) * LengthY / Length
            ForceZ = (ForceSpring + ForceDamper) * LengthZ / Length
            Force1 = [ForceX,ForceY,ForceZ]
            Force2 = [-ForceX,-ForceY,-ForceZ]
            ratio1 = (par2.mass/(par1.mass + par2.mass))
            ratio2 = (par1.mass/(par1.mass + par2.mass))
            par1.vel[0] += Force1[0] * ratio1
            par1.vel[1] += Force1[1] * ratio1
            par1.vel[2] += Force1[2] * ratio1
            par2.vel[0] += Force2[0] * ratio2
            par2.vel[1] += Force2[1] * ratio2
            par2.vel[2] += Force2[2] * ratio2
            if Length > (link.lenght  * (1 + link.broken)) or Length < (link.lenght  * (1 - link.broken)):
                #print("broke!!!!!")
                broken_links.append(link)
                if par2 in par1.link_with:
                    par1.link_with.remove(par2)
                if par1 in par2.link_with:
                    par2.link_with.remove(par1)
                    
    par.links = list(set(par.links) - set(broken_links))
                
    


    
def update_ParSys(data):
    global psys
    global substep
    global parlist
    i = 0
    ii = 0
    #print(data[1][2])
    parlist = []
    for parsys in psys:
        for par in parsys.particle:
            par.loc = data[i][0][(ii * 3):(ii * 3 + 3)]
            par.vel = data[i][1][(ii * 3):(ii * 3 + 3)]
            if par.state == 0 and data[i][2][ii] == 0:
                par.state = data[i][2][ii] + 1
                create_link(par)
                parlist.append(par)
            elif par.state == 1 and data[i][2][ii] == 0:
                par.state = 1
                parlist.append(par)
            else:
                par.state = data[i][2][ii]
            par.collided_with = []
            #print("state:",par.state)
            ii += 1
        ii = 0
        i += 1

def create_link(par,parothers = None):
    global kdtree
    if par.sys.links_active == 0:
        return
    if parothers == None:
        neighbours = kdtree.rnn_query(par.loc,par.sys.link_length)
    else:
        neighbours = [parothers]
    
    for ii in neighbours:
        if parothers == None:
            i = ii[0].particle
        else:
            i = ii[0]
        if par != i:
            if par not in i.link_with and i.state <= 1 and par.state <= 1:
                link = links()
                link.lenght = ii[1]**0.5
                link.start = par
                link.end = i
                if parothers == None:
                    stiffrandom = (par.sys.link_stiffrand + i.sys.link_stiffrand) / 2 * 2
                    link.stiffness = ((par.sys.link_stiff + i.sys.link_stiff)/2) * (((random() * stiffrandom) - (stiffrandom / 2)) + 1)
                    link.exponent = abs((par.sys.link_stiffexp + i.sys.link_stiffexp) / 2)
                    damprandom = ((par.sys.link_damprand + i.sys.link_damprand) / 2) * 2
                    link.damping = ((par.sys.link_damp + i.sys.link_damp) / 2) * (((random() * damprandom) - (damprandom / 2)) + 1)
                    brokrandom = ((par.sys.link_brokenrand + i.sys.link_brokenrand) / 2) * 2
                    link.broken = ((par.sys.link_broken + i.sys.link_broken) / 2) * (((random() * brokrandom) - (brokrandom  / 2)) + 1)
                    par.links.append(link)
                    par.link_with.append(i)
                    i.link_with.append(par)
                    del link
                if parothers != None and par.sys.relink_group == i.sys.relink_group:
                    relinkrandom = random()
                    chancerdom = (par.sys.relink_chancerand + i.sys.relink_chancerand) / 2 * 2
                    if relinkrandom <= ((par.sys.relink_chance + i.sys.relink_chance) / 2) * (((random() * chancerdom) - (chancerdom / 2)) + 1):
                        stiffrandom = (par.sys.relink_stiffrand + i.sys.relink_stiffrand) / 2 * 2
                        link.stiffness = ((par.sys.relink_stiff + i.sys.relink_stiff)/2) * (((random() * stiffrandom) - (stiffrandom / 2)) + 1)
                        link.exponent = abs((par.sys.relink_stiffexp + i.sys.relink_stiffexp) / 2)
                        damprandom = ((par.sys.relink_damprand + i.sys.relink_damprand) / 2) * 2
                        link.damping = ((par.sys.relink_damp + i.sys.relink_damp) / 2) * (((random() * damprandom) - (damprandom / 2)) + 1)
                        brokrandom = ((par.sys.relink_brokenrand + i.sys.relink_brokenrand) / 2) * 2
                        link.broken = ((par.sys.relink_broken + i.sys.relink_broken) / 2) * (((random() * brokrandom) - (brokrandom  / 2)) + 1)
                        par.links.append(link)
                        par.link_with.append(i)
                        i.link_with.append(par)
                        del link
   
    
    #print("num link",len(par.links))
    
   
class links:
    def __init__(self):
        self.lenght = "lenght of the link"
        self.start = "first particle starting from"
        self.end = "second particle ending with"
        self.stiffness = "stiffness of the link"
        self.exponent = "exponent of the stiffness"
        self.damping = "damping of the link"
        self.broken = "max stretch factor to link broken"
    
class ParSys:
    def __init__(self,data):
        global hashgrid
        
        self.parnum = data[0]
        self.particle = [0] * self.parnum
        self.sqsize_list = []
        self.selfcollision_active = data[6][0]
        self.othercollision_active = data[6][1]
        self.collision_group = data[6][2]
        self.links_active = data[6][3]
        self.link_length = data[6][4]
        self.link_stiff = data[6][5]
        self.link_stiffrand = data[6][6]
        self.link_stiffexp = data[6][7]
        self.friction = data[6][8]
        self.link_damp = data[6][9]
        self.link_damprand = data[6][10]
        self.link_broken = data[6][11]
        self.link_brokenrand = data[6][12]
        self.relink_group = data[6][13]
        self.relink_chance = data[6][14]
        self.relink_chancerand = data[6][15]
        self.relink_stiff = data[6][16]
        self.relink_stiffexp = data[6][17]
        self.relink_stiffrand = data[6][18]
        self.relink_damp = data[6][19]
        self.relink_damprand = data[6][20]
        self.relink_broken = data[6][21]
        self.relink_brokenrand = data[6][22] 
        
        for i in range(self.parnum):
            self.particle[i] = Particle()
            self.particle[i].id = i
            self.particle[i].loc = data[1][(i * 3):(i * 3 + 3)]
            self.particle[i].vel = data[2][(i * 3):(i * 3 + 3)]
            self.particle[i].size = data[3][i]
            self.particle[i].sqsize = sq_number(self.particle[i].size)
            if self.particle[i].sqsize not in self.sqsize_list:
                self.sqsize_list.append(self.particle[i].sqsize)
            self.particle[i].mass = data[4][i]
            self.particle[i].state = data[5][i]
            self.particle[i].sys = self
            #print(self.particle[i].size,self.particle[i].sqsize)
            
        
class Particle(ParSys):
    def __init__(self):
        self.id = 0
        self.loc = [0,0,0]
        self.vel = [0,0,0]
        self.size = "is size"
        self.sqsize = "near square number for hashing"
        self.mass = "is mass"
        self.state = "is alive state"
        self.sys = "is parent system"
        self.collided_with = []
        self.links = []
        self.link_with = []

class KDTree:
    root_node = "node on top"
    nodes = []
    result = []
    index = 0
    def create_nodes(self,parnum):
        if self.nodes == []:
            for i in range(parnum):
                node = Nodes()
                self.nodes.append(node)
                self.index = 0
    def create_tree(self,parlist,name,depth = 0):
        if not parlist:
            return None
        
        k = len(parlist[0].loc)
        axis = depth % k
        parlist.sort(key= lambda p: p.loc[axis])
        median = int(len(parlist) / 2)
        if depth == 0:
            self.index = 0
        node = self.nodes[self.index]
        node.name = name
        if parlist and depth == 0:
            self.root_node = node
        self.index += 1
        node.particle = parlist[median]
        node.left_child = self.create_tree(parlist[:median],"left" + str(depth+1),depth + 1)
        node.right_child = self.create_tree(parlist[median + 1:],"right" + str(depth+1),depth + 1)
        return node
    
    def rnn_query(self,point,dist):
        self.result = []
        if self.root_node == None:
            return []
        else:
            sqdist = dist**2
            #print("   distance to reach:",dist)
            k = len(self.root_node.particle.loc)
            self.rnn_search(self.root_node,point,dist,sqdist,k)
            
        return self.result
            
    def rnn_search(self,node,point,dist,sqdist,k,depth = 0):
        
        if node == None:
            return None
        
        axis = depth % k
        #print("    " + node.name + "(" + str(node.particle.id) + ")" + " viewed at " + str(square_dist(point,node.particle.loc,k)**0.5))

        if (point[axis] - node.particle.loc[axis])**2 <= sqdist:
            realdist = square_dist(point,node.particle.loc,k)
            if realdist <= sqdist:
                #print("    " + node.name + "(" + str(node.particle.id) + ")" + " added")
                self.result.append((node,realdist))
            self.rnn_search(node.left_child,point,dist,sqdist,k,depth + 1)
            self.rnn_search(node.right_child,point,dist,sqdist,k,depth + 1)
        
        else:
            if point[axis] <= node.particle.loc[axis]:
                self.rnn_search(node.left_child,point,dist,sqdist,k,depth + 1)
            if point[axis] >= node.particle.loc[axis]:
                self.rnn_search(node.right_child,point,dist,sqdist,k,depth + 1)


    def brute_query(self,point,dist):
        self.result = []
        k = len(point)
        dist = dist**2
        for i in self.nodes:
            #print("    " + i.name + "(" + str(i.particle.id) + ")" + " viewed at " + str(square_dist(point,i.particle.loc,k)**0.5))
            if square_dist(i.particle.loc,point,k) <= dist:
                #print("    " + i.name + "(" + str(i.particle.id) + ")" + " added")
                self.result.append(i)
        return self.result



class Nodes:
    def __init__(self):
        name = "node name"
        loc = [0,0,0]
        particle = "particle"
        self.left_child = None
        self.right_child = None
   
        
def sq_number(val):
    nearsq = 8
    while val > nearsq or val < nearsq / 2:
        if val > nearsq:
            nearsq = nearsq * 2
        elif val < nearsq / 2:
            nearsq = nearsq / 2
    return nearsq        

def square_dist(point1,point2,k):
    sq_dist = 0
    for i in range(k):
        sq_dist += (point1[i] - point2[i])**2
    return sq_dist

def cross_product(u,v):
    cross = [(u[1] * v[2] - u[2] * v[1]),(u[2] * v[0] - u[0] * v[2]),(u[0] * v[1] - u[1] * v[0])]
    return cross
def dot_product(u,v):
    dot = (u[0] * v[0]) + (u[1] * v[1]) + (u[2] * v[2])
    return dot
