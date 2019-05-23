import random
import numpy as np

class Neutron:
    
    MASS = 939.565 #MEV/c2
    
    def __init__(self, E, position, momentum):
        self.E = E
        self.position = position
        self.momentum = momentum
        
    def scattering(self, nuclide):
        pass
        
    def move(self):
        pass
        
        
class Nuclide:
    
    def __init__(self, A, Z):
        self.A = A
        self.Z = Z
        self.cross_sections = {}
        
    def add_cross_section(self, reaction, file_name):
        data_file = open(file_name)
        outArray=[]

        for line in data_file:
            if (line[0]=='#'):
                continue
            E = float(line[0:12])
            sig = float(line[13:26])
            outArray.append([E,sig])
    
        outArray = np.array(outArray)
        self.cross_sections[reaction] = outArray
        
    def get_cross_section(self, reaction, E_neutron):
        data = self.cross_sections[reaction]
        if ( E_neutron < data[0][0] ):
            y0 = data[0][1]
            y1 = data[1][1]
            x0 = data[0][0]
            x1 = data[1][0]
            
        elif ( E_neutron > data[-1][0] ):
            y0 = data[-2][1]
            y1 = data[-1][1]
            x0 = data[-2][0]
            x1 = data[-1][0]
        else:
            for i in range(len(data)):
                if ( E_neutron > data[i][0] ) and ( E_neutron <= data[i+1][0]):
                    y0 = data[i][1]
                    y1 = data[i+1][1]
                    x0 = data[i][0]
                    x1 = data[i+1][0]
        l = y0 + (y1 - y0)/(x1 - x0) * (E_neutron - x0)
        return l
        
        
class Material:

    def __init__(self, density, name):
        self.density = density
        self.name = name
        self.nuclides = []
        
    def add_nuclide(self, quantity, nuclide):
        self.nuclides.append([quantity, nuclide])
        
    def macro_cross_section(self, E_neutron):
        pass
        
    def losuj_proces(self, E_neutron):
        
        # generate likelihood
        likelihood = {}
        for nuclide in self.nuclides:
            #print(nuclide[0], nuclide[1].A)
            for process in nuclide[1].cross_sections:
                label = str(nuclide[1].A) + ':' + process
                #print(process, nuclide[1].get_cross_section(process, E_neutron))
                likelihood[label] = nuclide[1].get_cross_section(process, E_neutron) * nuclide[0]
        print(likelihood)
        
        # normalize
        suma = sum(likelihood.values())
        for x in likelihood:
            likelihood[x] = likelihood[x] / suma
            #print(likelihood[x], sum(likelihood.values()) )
        print(likelihood)
        
        # draw
        rand = random.random()
        a = list(likelihood.values())
        i = 0
        while (rand > 0):
            i += 1
            i = i % 4
            rand += -a[i]
            
        
        for key, value in likelihood.items():
            if value == a[i]:
                print(key, value)
                process = key
                
        # this part needs to be changed to [process, <nuclide:xxx>]
        return process
                
        
# losowanie procesu(E) losuj_proces(energi neutronu)
# normalizowanie do 1
# zwraca proces fission, elastic, 'capture', na jakim nuklidzie
        
if __name__ == '__main__':
    neutron = Neutron(1.0, [0, 0, 0], [0, 1, 0])
    
    # material init
    tlen = Nuclide(16, 8)
    wodor = Nuclide(1, 1)
    woda = Material(1.0, 'woda')
    woda.add_nuclide(2, wodor)
    woda.add_nuclide(1, tlen)
    
    # csec init
    tlen.add_cross_section('total', 'w183')
    tlen.add_cross_section('other', 'w182')
    wodor.add_cross_section('total', 'w184')
    wodor.add_cross_section('other', 'w186')
    
    # test
    woda.losuj_proces(2)
    
    #print(neutron.position)
    #print(nuclide.cross_sections)
    #print(material.name)
    #material.x = 0.1
    #w183 = Nuclide(183, 74)
    #w183.add_cross_section('total', 'w183')
    #print(w183.get_cross_section('total', 1.4975e+8))
    
