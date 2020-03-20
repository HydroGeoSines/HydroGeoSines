
# This package contains subroutines for time domain data analysis


# Import packages 
import numpy as np
from scipy.stats import linregress


# Calculate linear trend coefficients (of temporal derivatives of GW p and BA p)
def calc_linear(self): 
    self.M, self.C, z, z, z = linregress(self.BA.dp, self.GW.dp)
    print 'Slope = %.3f, intercept = %.3f'% (self.M, self.C)
    return self
    
    
# Calculate regression deconvolution (of temporal derivatives of GW p and BA p)
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


# Calculate BE using average of ratios method
def calc_BE_AoR(self): 
    with np.errstate(divide='ignore'):
        ratio = self.GW.dp/self.BA.dp
    ratio[np.isinf(ratio)] = 0.
    self.BE_AoR_all = [0.]
    for i in range(1, len(ratio)):
        self.BE_AoR_all.append(np.mean(ratio[:i]))
    self.BE_AoR = self.BE_AoR_all[-1]
    print 'BE (AoR) = %.3f'% self.BE_AoR
    self.BE_AoR_ratios = ratio
    return self.BE_AoR, self.BE_AoR_all, self.BE_AoR_ratios
    
    
# Calculate BE using median of ratios method
def calc_BE_MoR(self): 
    with np.errstate(divide='ignore'):
        ratio = self.GW.dp/self.BA.dp
    ratio[np.isinf(ratio)] = 0.
    self.BE_MoR_all = [0.]
    for i in range(1, len(ratio)):
        self.BE_MoR_all.append(np.percentile(ratio[:i], 50.))
    self.BE_MoR = self.BE_MoR_all[-1]
    print 'BE (MoR) = %.3f'% self.BE_MoR
    return self.BE_MoR, self.BE_MoR_all
       
    
# Calculate BE using linear regression method
def calc_BE_LR(self): 
    self.BE_LR_all = [0.]
    for i in range(1, len(self.GW.dp)):
        with np.errstate(invalid='ignore'):
            self.BE_LR_all.append(linregress(self.GW.dp[:i], self.BA.dp[:i]).slope)
    self.BE_LR = self.BE_LR_all[-1]  
    print 'BE (LR)  = %.3f'% self.BE_LR
    return self.BE_LR, self.BE_LR_all
    
    
# Calculate BE using Clark (1967) method
def calc_BE_Clark(self):
    self.BE_Clk_all = []
    sdW, sdB= [0],[0]
    for dw,db in zip(self.GW.dp, self.BA.dp):
        sdB.append(sdB[-1]+np.abs(db))
        if db==0:
            sdW.append(sdW[-1])
        elif np.sign(dw)==np.sign(db):
            sdW.append(sdW[-1]+np.abs(dw))
        elif np.sign(dw)!=np.sign(db):
            sdW.append(sdW[-1]-np.abs(dw))
        self.BE_Clk_all.append(np.abs(sdW[-1]/sdB[-1]))
    self.BE_Clk = self.BE_Clk_all[-1]
    print 'BE (Clk) = %.3f'% self.BE_Clk
    return self.BE_Clk, self.BE_Clk_all
    
    
# Calculate BE using Rahi (2010) method
def calc_BE_Rahi(self):
    self.BE_Rah_all = []
    sdW, sdB= [0],[0]
    for dw,db in zip(self.GW.dp, self.BA.dp):
        if (np.sign(dw)==np.sign(db)) & (np.abs(dw)<np.abs(db)):
            sdW.append(sdW[-1]+np.abs(dw))
            sdB.append(sdB[-1]+np.abs(db))
        else:
            sdW.append(sdW[-1])
            sdB.append(sdB[-1])
        try:
            self.BE_Rah_all.append(sdW[-1]/sdB[-1])
        except:
            self.BE_Rah_all.append(0.)
    self.BE_Rah = self.BE_Rah_all[-1]
    print 'BE (Rah) = %.3f'% self.BE_Rah
    return self.BE_Rah, self.BE_Rah_all
    
'''    
Subroutines for future inclusion:

# Estimate air diffusivity
def calc_air_diffusivity(self):
    return self


# Calculate nonlinear trend
def calc_nonlin(self):
    return self


# Extract functions
def extract_fns(self):
    return self


# Calculate amplitudes    
def calc_amps(self):
    return self
'''