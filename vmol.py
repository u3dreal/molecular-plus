from time import clock
class HashTree:
    def __init__(self,gridsize=1):
        self.gridsize = 1
        self.tree={}
        offset = (1 / gridsize) / 2
        self.GridArea = [(0,0,0),(offset,offset,offset),(-offset,offset,offset),(offset,-offset,offset),(-offset,-offset,offset)
                    ,(offset,offset,-offset),(-offset,offset,-offset),(offset,-offset,-offset),(-offset,-offset,-offset)]
        
    def add_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        for i in self.GridArea:
            intx = int((x + i[0]) / self.gridsize)
            inty = int((y + i[1]) / self.gridsize)
            intz = int((z + i[2]) / self.gridsize)
            if (intx,inty,intz) not in self.tree:
                self.tree[intx,inty,intz] = []
            if mol not in self.tree[intx,inty,intz]:
                self.tree[intx,inty,intz].append(mol)
            
    def remove_point(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        for i in self.GridArea:
            intx = int((x + i[0]) / self.gridsize)
            inty = int((y + i[1]) / self.gridsize)
            intz = int((z + i[2]) / self.gridsize)
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
        if (int(x),int(y),int(z)) != (int(px),int(py),int(pz)):
            for i in self.GridArea:
                intx = int((x + i[0]) / self.gridsize)
                inty = int((y + i[1]) / self.gridsize)
                intz = int((z + i[2]) / self.gridsize)
                intpx = int((px + i[0]) / self.gridsize)
                intpy = int((py + i[1]) / self.gridsize)
                intpz = int((pz + i[2]) / self.gridsize)
                if (intpx,intpy,intpz) in self.tree:
                    for i in range((self.tree[intpx,intpy,intpz].count(mol))):
                        if (intpx,intpy,intpz) in self.tree:
                            self.tree[intpx,intpy,intpz].remove(mol)
                if (intx,inty,intz) not in self.tree:
                    self.tree[intx,inty,intz] = []
                if mol not in self.tree[intx,inty,intz]:
                    self.tree[intx,inty,intz].append(mol)

                    
    def query(self,mol):
        x = mol.loc[0]
        y = mol.loc[1]
        z = mol.loc[2]
        intx = int(x / self.gridsize)
        inty = int(y / self.gridsize)
        intz = int(z / self.gridsize)
        if (intx,inty,intz) in self.tree:
            return self.tree[intx,inty,intz]
        
        
class Molecule:
    def __init__(self):
        temp='do nothing'
        self.loc = [0,0,0]
        self.prev_loc = [0,0,0]
        self.acceleration = [0,0,0]
        self.mass = 1
        self.index = 0
        
    def gravity(self):
        self.acceleration[0] = self.acceleration[0] + 0
        self.acceleration[1] = self.acceleration[1] + 0
        self.acceleration[2] = self.acceleration[2] + -9.8

    def verlet(self,DeltaTime):
        tmp = self.loc
        newloc=[0,0,0]
        newloc[0] = (((2- AirDamp) * self.loc[0]) - ((1- AirDamp) * self.prev_loc[0])) + self.acceleration[0]*((DeltaTime)*(DeltaTime))
        newloc[1] = (((2- AirDamp) * self.loc[1]) - ((1- AirDamp) * self.prev_loc[1])) + self.acceleration[1]*((DeltaTime)*(DeltaTime))
        newloc[2] = (((2- AirDamp) * self.loc[2]) - ((1- AirDamp) * self.prev_loc[2])) + self.acceleration[2]*((DeltaTime)*(DeltaTime))
        self.loc = newloc
        self.prev_loc = tmp
        self.acceleration = [0,0,0]
        PTree.update(self.prev_loc,self)
    
    def constraint(self):
        wallfriction = 0.0
        selfoldloc = (self.loc[0],self.loc[1],self.loc[1])
        if self.loc[2] <= 0.0000:
            self.loc[2] = 0.0000
            PTree.update(selfoldloc,self)

        if self.loc[0] <= -1.5000:
            self.loc[0] = -1.5000
            PTree.update(selfoldloc,self)

        if self.loc[0] >= 1.5000:
            self.loc[0] = 1.5000
            PTree.update(selfoldloc,self)

        if self.loc[1] <= -1.5000:
            self.loc[1] = -1.5000
            PTree.update(selfoldloc,self)

        if self.loc[1] >= 1.5000:
            self.loc[1] = 1.5000
            PTree.update(selfoldloc,self)
            
            
    def self_collide(self,MolSize):
        global PTree
        PNeighbours = PTree.query(self)
        target = MolSize * 2
        sqtarget = target**2
        #print(len(PNeighbours))
        if PNeighbours != None:
            for mol in PNeighbours:
                lenghtx = self.loc[0] - mol.loc[0]
                lenghty = self.loc[1] - mol.loc[1]
                lenghtz = self.loc[2] - mol.loc[2]
                sqlenght = (lenghtx * lenghtx) + (lenghty * lenghty) + (lenghtz * lenghtz)
                if sqlenght != 0 and sqlenght < sqtarget:
                    lenght = sqlenght**0.5
                    factor = (lenght - target) / lenght
                    selfoldloc = (self.loc[0],self.loc[1],self.loc[2])
                    mololdloc = (mol.loc[0],mol.loc[1],mol.loc[2])
                    self.loc[0] -= lenghtx * factor * 0.5
                    self.loc[1] -= lenghty * factor * 0.5
                    self.loc[2] -= lenghtz * factor * 0.5
                    mol.loc[0] += lenghtx * factor * 0.5
                    mol.loc[1] += lenghty * factor * 0.5
                    mol.loc[2] += lenghtz * factor * 0.5
                    PTree.update(selfoldloc,self)
                    PTree.update(mololdloc,mol)

            
        
def Init(ParLoc,ParNum,Psize):
    global mols
    global PTree
    global MolSize
    MolSize = Psize
    mols = [0]*ParNum
    stime = clock()
    for i in range(0,ParNum):
        mols[i]=Molecule()
        mols[i].loc = ParLoc[(i*3):(i*3+3)]
        mols[i].prev_loc = ParLoc[(i*3):(i*3+3)]
        mols[i].index = i
    print("Particles generation in:",round((clock()-stime),6),"sec")
    stime = clock()
    PTree = HashTree()
    for mol in mols:
        PTree.add_point(mol)        
    print("Hash grid generation in:",round((clock()-stime),6),"sec")
    return
def Simulate(Fps):
    global AirDamp
    AirDamp = 0.05
    SubStep = 1
    DeltaTime = (1/Fps)/SubStep
    for i in range(SubStep):
        for mol in mols:
            mol.gravity()
            mol.verlet(DeltaTime)
            mol.constraint()
            mol.self_collide(MolSize)
        info_grid()
    ParLoc=[]
    for mol in mols:
        for axe in mol.loc:
            ParLoc.append(axe)
    return ParLoc
    
def info_grid():
    global PTree
    mol_id = []
    for i in PTree.tree:
        for ii in PTree.tree[i]:
            mol_id.append(ii.index)
        print("Box:",i,"contains mol number:",mol_id)
        mol_id = []

        

    