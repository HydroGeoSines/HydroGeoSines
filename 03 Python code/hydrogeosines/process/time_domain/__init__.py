
# This package contains subroutines for time domain data analysis


# Import packages 
import numpy as np
from scipy.stats import linregress


# Calculate linear trend coefficients (of GW p vs BA p)
def calc_linear(self): 
    self.M, self.C, z, z, z = linregress(self.BA.p, self.GW.p)
    print '%10.3f%10.3f'% (self.M, self.C)
    return self
    
    
# Calculate regression deconvolution (of GW p vs BA p)
def calc_regress_deconv(self): 
    period = [  25.819,   24.066,   24.000,   23.934,   23.869, 
                23.804,   12.658,   12.421,   12.000,   11.967]
    p = np.array(period) 
    NP = len(p)
    omega = 2.*np.pi/p
    dt = 1./24.
    Ts  = 1./24. 
    Fs  = 1./Ts     
    t  = self.GW.t
    ba = self.BA.p
    ba = ba-np.mean(ba)
    gw = self.GW.p
    y  = gw
    x  = ba
    dx = np.diff(x)/dt
    dy = np.diff(y)/dt
    nlag = 72
    n    = len(dx)
    nn   = range(n) 
    lags = range(nlag+1)
    nm = nlag+1
    v = np.zeros([n, nm])
    for i in range(nm):
        j = lags[i]
        k = np.arange(n-j)
        v[j+k, i] = dx[k] 
    u1 = np.zeros([n, NP])
    u2 = u1.copy()
    for i in range(NP):
        tau = omega[i]*t[nn]
        u1[:,i] = np.cos(tau)
        u2[:,i] = np.sin(tau)
    X = np.hstack([v, u1, u2])
    Z = np.hstack([np.ones([n,1]), X])
    c  = np.linalg.lstsq(Z, dy, rcond=None)[0]
    nc = len(c)
    py = y-dt*np.concatenate([[0.], np.cumsum(np.dot(X, c[1:nc]))])
    oerror = np.std(dy)
    perror = np.std(dy-np.dot(Z,c))
    trend  = c[0]
    brf    = c[np.arange(1, nm+1)]
    crf    = np.abs(np.cumsum(brf))
    k      = np.arange(nm+1, NP+nm+1)
    trf    = [a+(1j*b) for a,b in zip(c[k], c[NP+k])]
    mag    = np.abs(trf)
    phs    = np.angle(trf)
    return lags, crf, mag, phs


'''    
Subroutines for future inclusion:

# Estimate air diffusivity
def calc_air_diffusivity(self):
    return


# Calculate nonlinear trend
def calc_nonlin(self):
    return


# Extract functions
def extract_fns(self):
    return


# Calculate amplitudes    
def calc_amps(self):
    return
'''