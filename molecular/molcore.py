#print("allo")
from math import floor
from sys import getsizeof
from time import clock

def init(importdata):
    global fps
    global substep
    global psys
    global hashgrid
    
    listsqsize = []
    fps = importdata[0][0]
    substep = importdata[0][1]
    psys = []
    hashgrid = KDTree()
    for i in importdata[1:]:
        psys.append(ParSys(i))
    parnum = 0
    for i in psys:
        parnum += i.parnum
        listsqsize += i.sqsize_list
    listsqsize = list(set(listsqsize))
    listsqsize.reverse()
    parlist = []  
    for i in psys:
        for ii in i.particle:
            parlist.append(ii)
    timer = clock()
    kdtree = KDTree()
    kdtree.create(parlist,"root")
    print("  KDtree generation take:",round(clock()-timer,5),"sec")
    point = (0,0,0)
    r = 0.5
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

    return parnum


def simulate(importdata):
    #print(importdata)
    exportdata = []
    update_ParSys(importdata)
    for parsys in psys:
        for par in parsys.particle:
            collide(par)
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
    global hashgrid
    
    neighbours = hashgrid.brute_query(par.loc,par.size)
    
    for ii in neighbours:
        stiff = 12
        i = ii.particle
        target = (par.size + i.size) * 0.99
        sqtarget = target**2
        #print(par.state)
        if par.state == 1 and i.state == 1:
            #print("collide!")
            lenghtx = par.loc[0] - i.loc[0]
            lenghty = par.loc[1] - i.loc[1]
            lenghtz = par.loc[2] - i.loc[2]
            sqlenght = (lenghtx * lenghtx) + (lenghty * lenghty) + (lenghtz * lenghtz)
            if sqlenght != 0 and sqlenght < sqtarget:
                lenght = sqlenght**0.5
                factor = (lenght - target) / lenght
                par.vel[0] -= ((lenghtx * factor * 0.5) * stiff)
                par.vel[1] -= ((lenghty * factor * 0.5) * stiff)
                par.vel[2] -= ((lenghtz * factor * 0.5) * stiff)
                i.vel[0] += ((lenghtx * factor * 0.5) * stiff)
                i.vel[1] += ((lenghty * factor * 0.5) * stiff)
                i.vel[2] += ((lenghtz * factor * 0.5) * stiff)
    


    
def update_ParSys(data):
    global psys    
    i = 0
    ii = 0
    print(data[1][2])
    for parsys in psys:
        for par in parsys.particle:
           par.loc = data[i][0][(ii * 3):(ii * 3 + 3)]
           par.vel = data[i][1][(ii * 3):(ii * 3 + 3)]
           par.state = data[i][2][ii]
           print("state:",par.state)
           ii += 1
        ii = 0
        i += 1
    
    
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
        self.link_stiffinv = data[6][8]
        self.link_damp = data[6][9]
        self.link_damprand = data[6][10]
        self.link_broken = data[6][11]
        self.link_brokenrand = data[6][12]
        self.relink_group = data[6][13]
        self.relink_chance = data[6][14]
        self.relink_chancerand = data[6][15]
        self.relink_stiff = data[6][16]
        self.relink_stiffexp = data[6][17]
        self.relink_stiffinv = data[6][18]
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

class KDTree():
    root_node = "node on top"
    nodes = []
    result = []
    def create(self,parlist,name,depth = 0):
        if not parlist:
            return None
        
        k = len(parlist[0].loc)
        axis = depth % k
        parlist.sort(key= lambda p: p.loc[axis])
        median = int(len(parlist) / 2)
        node = Nodes()
        self.nodes.append(node)
        node.name = name
        if parlist and depth == 0:
            self.root_node = node
        node.particle = parlist[median]
        node.left_child = self.create(parlist[:median],"left" + str(depth+1),depth + 1)
        node.right_child = self.create(parlist[median + 1:],"right" + str(depth+1),depth + 1)
        return node
    
    def rnn_query(self,point,dist):
        self.result = []
        if self.root_node == None:
            return []
        else:
            dist = dist**2
            #print("   distance to reach:",dist)
            k = len(self.root_node.particle.loc)
            self.rnn_search(self.root_node,point,dist,k)
            
        return self.result
            
    def rnn_search(self,node,point,dist,k,depth = 0):
        
        if node == None:
            return None
        
        axis = depth % k
        #print("    " + node.name + "(" + str(node.particle.id) + ")" + " viewed at " + str(square_dist(point,node.particle.loc,k)**0.5))
                  
        if (point[axis] - node.particle.loc[axis])**2 <= dist:
            if square_dist(point,node.particle.loc,k) <= dist:
                #print("    " + node.name + "(" + str(node.particle.id) + ")" + " added")
                self.result.append(node.particle)
            self.rnn_search(node.left_child,point,dist,k,depth + 1)
            self.rnn_search(node.right_child,point,dist,k,depth + 1)
        
        else:
            if point[axis] <= node.particle.loc[axis]:
                self.rnn_search(node.left_child,point,dist,k,depth + 1)
            if point[axis] >= node.particle.loc[axis]:
                self.rnn_search(node.right_child,point,dist,k,depth + 1)


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



class Nodes():
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
    
