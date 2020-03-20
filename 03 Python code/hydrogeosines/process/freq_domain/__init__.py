
# This package contains subroutines for frequency domain data analysis


# Import packages
import numpy as np


# Calculate the DFT of GW p data
def calc_ft_GW(self):
    Ts = 1./24.
    Fs = 1./Ts
    n = len(self.GW.p)
    T = n/Fs
    k = np.arange(n)
    F = k/T    
    F = F[:n/2]
    #ft = np.fft.fft(self.GW.p) 
    ft = np.fft.fft(np.hanning(n)*(self.GW.p-np.mean(self.GW.p)))
    A = 2.*(2./n)*np.abs(ft)[:n/2]
    P = np.angle(ft[:n/2])   
    return F, A, P


# Calculate the DFT of BA p data
def calc_ft_BA(self):
    Ts = 1./24.
    Fs = 1./Ts
    n = len(self.BA.p)
    T = n/Fs
    k = np.arange(n)
    F = k/T    
    F = F[:n/2]
    #ft = np.fft.fft(self.GW.p) 
    ft = np.fft.fft(np.hanning(n)*(self.BA.p-np.mean(self.BA.p)))
    A = 2.*(2./n)*np.abs(ft)[:n/2]
    P = np.angle(ft[:n/2])   
    return F, A, P

'''    
Subroutines for future inclusion:

# Calculate continous wavelet transform
def calc_cwt(self):
    return
    

# Calculate BE using Quilty and Roeloffs (1991) method
def calc_BE_QaR(self):
    return self.BE_QaR


# Calculate BE using Acworth et al. (2016) method
def calc_BE_Acw(self):
    return self.BE_Acw
'''