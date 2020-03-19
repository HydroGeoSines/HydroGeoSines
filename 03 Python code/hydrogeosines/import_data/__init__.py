
# This package contains subroutines for the importing of datasets


# Import packages
import numpy as np


# Define subclass for groundwater (GW) data
class GW:
    pass
    

# Import GW data from file    
def get_GW(self):  
    self.GW = GW
    self.GW.t = np.genfromtxt(self.wd+self.id+'.csv', delimiter=',', skip_header=1, usecols=0)
    self.GW.p = np.genfromtxt(self.wd+self.id+'.csv', delimiter=',', skip_header=1, usecols=1)
    return self.GW


# Define subclass for barometric (BA) data
class BA:
    pass
    

# Obtain BA data from file
def get_BA(self):  
    self.BA = BA
    self.BA.t = np.genfromtxt(self.wd+'Baro.csv', delimiter=',', skip_header=1, usecols=0)
    self.BA.p = np.genfromtxt(self.wd+'Baro.csv', delimiter=',', skip_header=1, usecols=1)
    return self.BA


'''
Subroutines for future inclusion:

# Define subclass for precipitation (PR) data
class PR:
    pass
    

# Obtain PR data from file
def get_PR(self):  
    self.PR = PR
    self.PR.t = np.genfromtxt(self.wd+'Precipitation.csv', delimiter=',', skip_header=1, usecols=0)
    self.PR.p = np.genfromtxt(self.wd+'Precipitation.csv', delimiter=',', skip_header=1, usecols=1)
    return self.PR


# Define subclass for stage (ST) data
class ST:
    pass
    

# Obtain ST data from file
def get_ST(self):  
    self.ST = ST
    self.ST.t = np.genfromtxt(self.wd+'Stage.csv', delimiter=',', skip_header=1, usecols=0)
    self.ST.p = np.genfromtxt(self.wd+'Stage.csv', delimiter=',', skip_header=1, usecols=1)
    return self.ST
    
    
# Define subclass for extraction (EX) data
class EX:
    pass
    

# Obtain EX data from file
def get_EX(self):  
    self.EX = EX
    self.EX.t = np.genfromtxt(self.wd+'Extraction.csv', delimiter=',', skip_header=1, usecols=0)
    self.EX.p = np.genfromtxt(self.wd+'Extraction.csv', delimiter=',', skip_header=1, usecols=1)
    return self.PR

'''