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
    #print(fps,substep)
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
    r = 0.2
    timer = clock()
    query = kdtree.rnn_query(point,r)
    print("  RNN query number find:",len(query))
    print("  KDtree RNN query take:",round(clock()-timer,5),"sec")
    timer = clock()
    query = kdtree.brute_query(point,r)
    print("  Brute query number find:",len(query))
    print("  Brute query take:",round(clock()-timer,5),"sec")
    return parnum
    

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
    full_list = []
    result = []
    def create(self,parlist,name,depth = 0):
        if not parlist:
            return None
        
        k = len(parlist[0].loc)
        axis = depth % k
        parlist.sort(key= lambda p: p.loc[axis])
        median = int(len(parlist) / 2)
        node = Nodes()
        node.name = name
        if parlist and depth == 0:
            self.full_list = parlist
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
            print("   distance to reach:",dist)
            k = len(self.root_node.particle.loc)
            self.rnn_search(self.root_node,point,dist,k)
            
        return self.result
            
    def rnn_search(self,node,point,dist,k,depth = 0):
        
        if node == None:
            return
        
        axis = depth % k
        print("    " + node.name + " viewed at " + str(square_dist(point,node.particle.loc,k)**0.5))
        if square_dist(point,node.particle.loc,k) < dist:
            print("    " + node.name + " added")
            self.result.append(node.particle)
            self.rnn_search(node.left_child,point,dist,k)
            self.rnn_search(node.right_child,point,dist,k)
        
        else:    
            if point[axis] <= node.particle.loc[axis]:
                self.rnn_search(node.left_child,point,dist,k)
            else:
                self.rnn_search(node.right_child,point,dist,k)


    def brute_query(self,point,dist):
        self.result = []
        k = len(point)
        dist = dist**2
        for i in self.full_list:
            if square_dist(i.loc,point,k) < dist:
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
    