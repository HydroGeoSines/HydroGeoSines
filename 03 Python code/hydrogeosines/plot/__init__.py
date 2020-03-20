
# This package contains subroutines for plotting outputs


# Import packages
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt


# Plot GW p data vs t
def plot_GW(self, pname=None):
    f,s = plt.subplots()
    f.suptitle(self.id)
    s.plot(self.GW.t, self.GW.p, 'k-')
    s.set_xlabel('Time')
    s.set_ylabel('Groundwater pressure')
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


# Plot BA p data vs t
def plot_BA(self, pname=None):
    f,s = plt.subplots()
    f.suptitle('Barometric pressure')
    s.plot(self.BA.t, self.BA.p, 'k-')
    s.set_xlabel('Time')
    s.set_ylabel('Barometric pressure')
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


# Plot dGWp/dt vs dBAp/dt, with estimated linear trend
def plot_linregress(self, pname=None):
    f,s = plt.subplots()
    f.suptitle(self.id)
    s.plot(self.BA.dp, self.GW.dp, 'ko', alpha=0.5)
    s.plot(self.BA.dp, self.M*self.BA.dp+self.C, 'r-')
    s.set_xlabel('$\Delta$ BA p / $\Delta$ t')
    s.set_ylabel('$\Delta$ GW p / $\Delta$ t')
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


# Plot Convergence of time domain BE metrics over time
def plot_BE_vs_time(self, pname):
    f,s = plt.subplots()
    f.suptitle(self.id)
    try:
        s.plot(self.BE_AoR_all, '-', label='Average-of-ratios')
    except:
        pass
    try:
        s.plot(self.BE_MoR_all, '-', label='Median-of-ratios')
    except:
        pass
    try:
        s.plot(self.BE_LR_all,  '-', label='Linear regression')
    except:
        pass
    try:
        s.plot(self.BE_Clk_all, '-', label='Clark (1967)')
    except:
        pass
    try:
        s.plot(self.BE_Rah_all, '-', label='Rahi (2010)')
    except:
        pass
    s.set_xlabel('Time')
    s.set_ylabel('Barometric efficiency')
    s.set_ylim(0,1)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    f.legend(loc=1, bbox_to_anchor=(1.30, 0.92), bbox_transform=f.transFigure, labelspacing=1.)
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


# Plot amplitude spectrum of GW p data
def plot_ft_avf_GW(self, pname=None):
    f,s = plt.subplots()
    f.suptitle('Groundwater pressure ('+self.id+')')
    frq = self.GW.frq[(self.GW.frq>=0.5) & (self.GW.frq<=2.5)]
    amp = self.GW.amp[(self.GW.frq>=0.5) & (self.GW.frq<=2.5)]
    s.plot(frq, amp, 'ko-', ms=4)
    s.set_xlabel('Frequency')
    s.set_ylabel('Amplitude')
    s.set_xlim(0.5, 2.5)
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


# Plot phase versus amplitude of GW p data
def plot_ft_pva_GW(self, pname=None):
    f,s = plt.subplots()
    f.suptitle('Groundwater pressure ('+self.id+')')
    amp = self.GW.amp[(self.GW.frq>=0.5) & (self.GW.frq<=2.5)]
    phs = self.GW.phs[(self.GW.frq>=0.5) & (self.GW.frq<=2.5)]
    s.plot(amp, phs, 'o', ms=4, mfc='r', mec='r')
    s.set_xlabel('Amplitude')
    s.set_ylabel('Phase')
    s.set_yticks(np.pi*np.arange(-0.5*np.pi, 0.75*np.pi, 0.25*np.pi))
    s.set_yticklabels(['-$\pi$/2', '-$\pi$/4', '0', '$\pi$/4', '$\pi$/2'])
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


# Plot amplitude spectrum of BA p data
def plot_ft_avf_BA(self, pname=None):
    f,s = plt.subplots()
    f.suptitle('Barometric pressure')
    frq = self.BA.frq[(self.BA.frq>=0.5) & (self.BA.frq<=2.5)]
    amp = self.BA.amp[(self.BA.frq>=0.5) & (self.BA.frq<=2.5)]
    s.plot(frq, amp, 'ko-', ms=4)
    s.set_xlabel('Frequency')
    s.set_ylabel('Amplitude')
    s.set_xlim(0.5, 2.5)
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)


# Plot phase versus amplitude of BA p data
def plot_ft_pva_BA(self, pname=None):
    f,s = plt.subplots()
    f.suptitle('Barometric pressure')
    amp = self.BA.amp[(self.BA.frq>=0.5) & (self.BA.frq<=2.5)]
    phs = self.BA.phs[(self.BA.frq>=0.5) & (self.BA.frq<=2.5)]
    s.plot(amp, phs, 'o', ms=4, mfc='r', mec='r')
    s.set_xlabel('Amplitude')
    s.set_ylabel('Phase')
    s.set_yticks(np.pi*np.arange(-0.5*np.pi, 0.75*np.pi, 0.25*np.pi))
    s.set_yticklabels(['-$\pi$/2', '-$\pi$/4', '0', '$\pi$/4', '$\pi$/2'])
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


# Plot CRF vs lag values obtained from regression deconvolution of GW p and BA p data
def plot_regress_deconv_crf(self, pname=None):
    f,s = plt.subplots()
    f.suptitle(self.id)
    s.plot(self.lags, self.crf, 'ko-', ms=4)
    s.set_xlabel('Lag (hours)')
    s.set_ylabel('Cumulative response function')
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    

# Plot amplitude and phase values obtained from regression deconvolution of GW p and BA p data
def plot_regress_deconv_pva(self, pname=None):
    f,s = plt.subplots()
    f.suptitle(self.id)
    s.plot(self.mag, self.phs, 'o', ms=4, mfc='r', mec='r')
    s.set_xlabel('Amplitude')
    s.set_ylabel('Phase')
    tide = ['O$_1$   ', 'P$_1$   ', 'S$_1$   ', 'K$_1$   ', '$\phi_1$',
            '$\psi_1$', 'N$_2$   ', 'M$_2$   ', 'S$_2$   ', 'K$_2$   ']
    period = [  25.819,   24.066,   24.000,   23.934,   23.869, 
                23.804,   12.658,   12.421,   12.000,   11.967]
    p = np.array(period) 
    NP = len(p)
    for i in range(NP):
        s.text(self.mag[i]+5e-4, self.phs[i]+5e-2, tide[i])
    s.set_yticks(np.pi*np.arange(-0.5*np.pi, 0.75*np.pi, 0.25*np.pi))
    s.set_yticklabels(['-$\pi$/2', '-$\pi$/4', '0', '$\pi$/4', '$\pi$/2'])
    s.grid(True)
    plt.tight_layout(rect=[0.00, 0.00, 1.00, 0.95])
    if pname!=None: 
        plt.savefig(pname)
    #plt.close(f)
    return


'''
Subroutines for future inclusion:


# Plot phase vs frequency of DFT results
def plot_phase_frequency(self): 
    return

'''