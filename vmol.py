from time import clock

class Molecule:
    def __init__(self):
        temp='do nothing'
        self.loc=[0,0,0]
        self.prev_loc=[0,0,0]
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
    
    def constraint(self):
        wallfriction = 0.0
        if self.loc[2] <= 0.0000:
            self.loc[2] = 0.0000

        if self.loc[0] <= -1.5000:
            self.loc[0] = -1.5000

        if self.loc[0] >= 1.5000:
            self.loc[0] = 1.5000

        if self.loc[1] <= -1.5000:
            self.loc[1] = -1.5000

        if self.loc[1] >= 1.5000:
            self.loc[1] = 1.5000
            
            
    def self_collide(self,MolSize):
        target = MolSize * 2
        sqtarget = target**2
        for mol in mols:
            lenghtx = self.loc[0] - mol.loc[0]
            lenghty = self.loc[1] - mol.loc[1]
            lenghtz = self.loc[2] - mol.loc[2]
            sqlenght = (lenghtx * lenghtx) + (lenghty * lenghty) + (lenghtz * lenghtz)
            if sqlenght != 0 and sqlenght < sqtarget:
                lenght = sqlenght**0.5
                factor = (lenght - target) / lenght
                self.loc[0] -= lenghtx * factor * 0.5
                self.loc[1] -= lenghty * factor * 0.5
                self.loc[2] -= lenghtz * factor * 0.5
                mol.loc[0] += lenghtx * factor * 0.5
                mol.loc[1] += lenghty * factor * 0.5
                mol.loc[2] += lenghtz * factor * 0.5
            
        
def Init(ParLoc,ParNum,Psize):
    global mols
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
    return
def Simulate(Fps):
    global AirDamp
    AirDamp = 0.05
    SubStep = 2
    DeltaTime = (1/Fps)/SubStep
    for i in range(SubStep):
        for mol in mols:
            mol.gravity()           
            mol.constraint()
            mol.self_collide(MolSize)
            mol.verlet(DeltaTime)
        kdtreedict = {}
        kdtreelist = [(0,0,0)]*(len(mols))
    ParLoc=[]
    for mol in mols:
        for axe in mol.loc:
            ParLoc.append(axe)
    return ParLoc

        

    