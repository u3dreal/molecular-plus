#print("allo")
from math import floor

def init(importdata):
    global fps
    global substep
    global psys
    global hashgrid
    
    fps = importdata[0][0]
    substep = importdata[0][1]
    #print(fps,substep)
    psys = []
    hashgrid = HashTree()
    for i in importdata[1:]:
        psys.append(ParSys(i))
    parnum = 0
    for i in psys:
        parnum += i.parnum
    print(hashgrid.sizelist)
    print(hashgrid.query(psys[0].particle[11]))
    return parnum
    

class ParSys:
    def __init__(self,data):
        global hashgrid
        
        self.parnum = data[0]
        self.particle = [0] * self.parnum
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
            self.particle[i].mass = data[4][i]
            self.particle[i].state = data[5][i]
            self.particle[i].sys = self
            hashgrid.add_point(self.particle[i])
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
 
       
class HashTree:
    def __init__(self):
        self.sizelist = []
        self.tree={}
        self.ngrid = []
        rrange = 1
        for xgrid in range(-rrange,rrange + 1):
            for ygrid in range(-rrange,rrange + 1):
                for zgrid in range(-rrange,rrange + 1):
                    self.ngrid.append((xgrid,ygrid,zgrid))
        #print(self.ngrid)
        #print(len(self.ngrid))
        #print("Gridsize at:",self.gridsize)
       
    def add_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        size = mol.sqsize 
        if size not in self.sizelist:
            self.sizelist.append(size)
        intx = floor(x / size)
        inty = floor(y / size)
        intz = floor(z / size)
        if (size,intx,inty,intz) not in self.tree:
            self.tree[size,intx,inty,intz] = []
        if mol not in self.tree[size,intx,inty,intz]:
            self.tree[size,intx,inty,intz].append((mol.id,mol.sqsize))
            #print (x,y,z,";",intx,inty,intz)
           
    def remove_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        size = mol.sqsize
        intx = floor(x / size)
        inty = floor(y / size)
        intz = floor(z / size)
        if (size,intx,inty,intz) in self.tree:
            for i in range((self.tree[size,intx,inty,intz].count(mol))):
                if (size,intx,inty,intz) in self.tree:
                    self.tree[size,intx,inty,intz].remove(mol)
                       
    def update(self,prev_loc,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        px = prev_loc[0]
        py = prev_loc[1]
        pz = prev_loc[2]
        size = mol.sqsize
        intx = floor(x / size)
        inty = floor(y / size)
        intz = floor(z / size)
        intpx = floor(px / size)
        intpy = floor(py / size)
        intpz = floor(pz / size)
        if (size,intx,inty,intz) != (size,intpx,intpy,intpz):
            if (size,intpx,intpy,intpz) in self.tree:
                for i in range((self.tree[size,intpx,intpy,intpz].count(mol))):
                    self.tree[size,intpx,intpy,intpz].remove(mol)
                    #print("rem mol:",mol.index,"from:",(size,intpx,intpy,intpz))
                    if len(self.tree[size,intpx,intpy,intpz]) == 0:
                        del self.tree[size,intpx,intpy,intpz]
                        #print("del box:",(size,intpx,intpy,intpz))
            if (size,intx,inty,intz) not in self.tree:
                self.tree[size,intx,inty,intz] = []
            if mol not in self.tree[size,intx,inty,intz]:
                self.tree[size,intx,inty,intz].append(mol)

                   
    def query(self,mol):
        neighbours = []
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        for size in self.sizelist:
            intx = floor(x / size)
            inty = floor(y / size)
            intz = floor(z / size)
            print(size,intx,inty,intz)
            if (size,intx,inty,intz) in self.tree:
                print(size)
                for i in self.ngrid:
                    ngridcoord = (size,intx + i[0],inty + i[1],intz + i[2])
                    if ngridcoord in self.tree:
                        neighbours.extend(self.tree[ngridcoord])
        return neighbours
        
 
def sq_number(val):
    nearsq = 8
    while val > nearsq or val < nearsq / 2:
        if val > nearsq:
            nearsq = nearsq * 2
        elif val < nearsq / 2:
            nearsq = nearsq / 2
    return nearsq
         
'''
class HashTree:
    def __init__(self):
        self.sizelist = []
        self.tree={}
        self.ngrid = []
        rrange = 1
        for xgrid in range(-rrange,rrange + 1):
            for ygrid in range(-rrange,rrange + 1):
                for zgrid in range(-rrange,rrange + 1):
                    self.ngrid.append((xgrid,ygrid,zgrid))
        #print(self.ngrid)
        #print(len(self.ngrid))
        #print("Gridsize at:",self.gridsize)
       
    def add_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        size = mol.sqsize
        if size not in self.sizelist:
            self.sizelist.append(size)
        intx = floor(x / size)
        inty = floor(y / size)
        intz = floor(z / size)
        if (size,intx,inty,intz) not in self.tree:
            self.tree[size,intx,inty,intz] = []
        if mol not in self.tree[size,intx,inty,intz]:
            self.tree[size,intx,inty,intz].append((mol.id,mol.sqsize))
            #print (x,y,z,";",intx,inty,intz)
           
    def remove_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        size = mol.sqsize
        intx = floor(x / size)
        inty = floor(y / size)
        intz = floor(z / size)
        if (size,intx,inty,intz) in self.tree:
            for i in range((self.tree[size,intx,inty,intz].count(mol))):
                if (size,intx,inty,intz) in self.tree:
                    self.tree[size,intx,inty,intz].remove(mol)
                       
    def update(self,prev_loc,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        px = prev_loc[0]
        py = prev_loc[1]
        pz = prev_loc[2]
        size = mol.sqsize
        intx = floor(x / size)
        inty = floor(y / size)
        intz = floor(z / size)
        intpx = floor(px / size)
        intpy = floor(py / size)
        intpz = floor(pz / size)
        if (size,intx,inty,intz) != (size,intpx,intpy,intpz):
            if (size,intpx,intpy,intpz) in self.tree:
                for i in range((self.tree[size,intpx,intpy,intpz].count(mol))):
                    self.tree[size,intpx,intpy,intpz].remove(mol)
                    #print("rem mol:",mol.index,"from:",(size,intpx,intpy,intpz))
                    if len(self.tree[size,intpx,intpy,intpz]) == 0:
                        del self.tree[size,intpx,intpy,intpz]
                        #print("del box:",(size,intpx,intpy,intpz))
            if (size,intx,inty,intz) not in self.tree:
                self.tree[size,intx,inty,intz] = []
            if mol not in self.tree[size,intx,inty,intz]:
                self.tree[size,intx,inty,intz].append(mol)

                   
    def query(self,mol,size):
        neighbours = []
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        for size in self.sizelist:
            intx = floor(x / size)
            inty = floor(y / size)
            intz = floor(z / size)
            if (size,intx,inty,intz) in self.tree:
                for i in self.ngrid:
                    ngridcoord = (size,intx + i[0],inty + i[1],intz + i[2])
                    if ngridcoord in self.tree:
                        neighbours.extend(self.tree[ngridcoord])
            return neighbours



        
def ApplyCns():
    
    global dctCns
    global vMass
    global vBrokenTotal

    vBrokenCns = []

    for ii in dctCns:
        
        #print (dctCns[ii][2])
        
        Loc1 = dctCns[ii][0].location
        Loc2 = dctCns[ii][1].location
        
        Length=(Loc2-Loc1).length
        tLength=(trunc(Length,vPrec)*(0.1**vPrec))
        
        InitLength = dctCns[ii][2]
        
        vStiff=(dctCns[ii][4])
        
        if tLength != InitLength:
            
            V1=dctCns[ii][0].velocity
            V2=dctCns[ii][1].velocity
            
            LengthX=Loc2[0]-Loc1[0]
            LengthY=Loc2[1]-Loc1[1]
            LengthZ=Loc2[2]-Loc1[2]
            
            Vx=V2[0]-V1[0]
            Vy=V2[1]-V1[1]
            Vz=V2[2]-V1[2]
            
            V=(Vx*LengthX+Vy*LengthY+Vz*LengthZ)/Length
            
            ForceSpring=(Length-InitLength)*vStiff
            
            ForceDamper=vDamping*V
            
            ForceX=(ForceSpring+ForceDamper)*LengthX/Length
            ForceY=(ForceSpring+ForceDamper)*LengthY/Length
            ForceZ=(ForceSpring+ForceDamper)*LengthZ/Length
            
            Force1=[ForceX,ForceY,ForceZ]
            Force2=[-ForceX,-ForceY,-ForceZ]
            
            ApplyForce(dctCns[ii][0],Force1)
            ApplyForce(dctCns[ii][1],Force2)
            #print(dctCns[ii][3])
            #print(vLimitMin+dctCns[ii][3])
            if tLength > (InitLength*(vLimitMax-dctCns[ii][3])) or tLength < (InitLength*(vLimitMin+dctCns[ii][3])):
                vBrokenTotal = vBrokenTotal+1
                vBrokenCns.append(ii)
                
    RemoveCns(vBrokenCns)
    vBrokenCns=[]

def ApplyForce(obj,force):
    
    vVel1 = obj.velocity    
    
    vVel2 = ((mathu.Vector(force)*vMass)*(vTimeStep*2)) + mathu.Vector(vVel1)
    
    obj.velocity = vVel2


    return
'''
