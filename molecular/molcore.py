#print("allo")
from math import floor

def init(importdata):
    global fps
    global substep
    global psys
    
    fps = importdata[0][0]
    substep = importdata[0][1]
    #print(fps,substep)
    psys = []
    
    for i in importdata[1:]:
        psys.append(ParSys(i))
    parnum = 0
    for i in psys:
        parnum += i.parnum
    return parnum
    

class ParSys:
    def __init__(self,data):
        global hashgrid
        hashgrid = HashTree()
        
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
        self.loc = [0,0,0]
        self.vel = [0,0,0]
        self.size = "is size"
        self.sqsize = "near square number for hashing"
        self.mass = "is mass"
        self.state = "is alive state"
        self.sys = "is parent system"
 
       
class HashTree:
    def __init__(self):
        self.gridsize = []
        self.tree={}
        self.ngrid = []
        for xgrid in range(-1,2):
            for ygrid in range(-1,2):
                for zgrid in range(-1,2):
                    self.ngrid.append((xgrid,ygrid,zgrid))
        #print(self.ngrid)
        #print(len(self.ngrid))
        #print("Gridsize at:",self.gridsize)
       
    def add_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        intx = floor(x / self.gridsize)
        inty = floor(y / self.gridsize)
        intz = floor(z / self.gridsize)
        if (intx,inty,intz) not in self.tree:
            self.tree[intx,inty,intz] = []
        if mol not in self.tree[intx,inty,intz]:
            self.tree[intx,inty,intz].append(mol)
            #print (x,y,z,";",intx,inty,intz)
           
    def remove_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        intx = floor(x / self.gridsize)
        inty = floor(y / self.gridsize)
        intz = floor(z / self.gridsize)
        if (intx,inty,intz) in self.tree:
            for i in range((self.tree[intx,inty,intz].count(mol))):
                if (intx,inty,intz) in self.tree:
                    self.tree[intx,inty,intz].remove(mol)
                       
    def update(self,prev_loc,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        px = prev_loc[0]
        py = prev_loc[1]
        pz = prev_loc[2]
        intx = floor(x / self.gridsize)
        inty = floor(y / self.gridsize)
        intz = floor(z / self.gridsize)
        intpx = floor(px / self.gridsize)
        intpy = floor(py / self.gridsize)
        intpz = floor(pz / self.gridsize)
        if (intx,inty,intz) != (intpx,intpy,intpz):
            if (intpx,intpy,intpz) in self.tree:
                for i in range((self.tree[intpx,intpy,intpz].count(mol))):
                    self.tree[intpx,intpy,intpz].remove(mol)
                    #print("rem mol:",mol.index,"from:",(intpx,intpy,intpz))
                    if len(self.tree[intpx,intpy,intpz]) == 0:
                        del self.tree[intpx,intpy,intpz]
                        #print("del box:",(intpx,intpy,intpz))
            if (intx,inty,intz) not in self.tree:
                self.tree[intx,inty,intz] = []
            if mol not in self.tree[intx,inty,intz]:
                self.tree[intx,inty,intz].append(mol)

                   
    def query(self,mol):
        neighbours = []
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        intx = floor(x / self.gridsize)
        inty = floor(y / self.gridsize)
        intz = floor(z / self.gridsize)
        if (intx,inty,intz) in self.tree:
            for i in self.ngrid:
                ngridcoord = (intx + i[0],inty + i[1],intz + i[2])
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