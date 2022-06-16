
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

fontsize = 9
mpl.rcParams.update(mpl.rcParamsDefault)
mpl.rcParams[ 'font.sans-serif'  ] = 'Calibri'
mpl.rcParams[ 'font.size'        ] = fontsize
mpl.rcParams[ 'xtick.direction'  ] = 'out'
mpl.rcParams[ 'ytick.direction'  ] = 'out'       
mpl.rcParams[ 'lines.linewidth'  ] = 1.0     
pd.plotting.register_matplotlib_converters()

st.subheader("Groundwater pressure dataset")
gw = st.file_uploader("Upload dataset", type=["csv"], key='gw')

st.subheader("Barometric pressure dataset")
bp = st.file_uploader("Upload dataset", type=["csv"], key='bp')

if (gw is not None)&(bp is not None):

    st.subheader("Analyse and plot input datasets")
    gw = pd.read_csv(gw, index_col=0, skiprows=1, names=['Datetime', 'Pgw_mH2O'])
    bp = pd.read_csv(bp, index_col=0, skiprows=1, names=['Datetime', 'Pba_mH2O'])
    
    f,s = plt.subplots(1, 1, figsize=[16.00/2.54, 6.00/2.54])
    s.set_title('Groundwater pressure', fontsize=fontsize)
    s.plot(range(len(gw.Pgw_mH2O)), gw.Pgw_mH2O, 'k-')
    s.set_xlabel('Date')
    s.set_ylabel('Pressure (mH$_2$O)')
    s.grid(True)
    f.tight_layout()
    st.pyplot(f)
    
    f,s = plt.subplots(1, 1, figsize=[16.00/2.54, 6.00/2.54])
    s.set_title('Barometric pressure', fontsize=fontsize)
    s.plot(range(len(bp.Pba_mH2O)), bp.Pba_mH2O, 'r-')
    s.set_xlabel('Date')
    s.set_ylabel('Pressure (mH$_2$O)')
    s.grid(True)
    f.tight_layout()
    st.pyplot(f)
    
    def dft_fn(data, Fs, flag=False):
        n   = len(data)
        T   = n/Fs
        k   = np.arange(n)
        F   = k/T    
        F   = F[:int(n/2)]
        if flag==False:
            fft = np.fft.fft(data) 
        elif flag==True:
            fft = np.fft.fft(np.hanning(n)*data)  
        A = 2.*(2./n)*np.abs(fft)[:int(n/2)]
        P = np.angle(fft[:int(n/2)])   
        return F, A, P                
       
    Fs = 24. #96.
    F, A, P = dft_fn(gw.Pgw_mH2O, Fs, flag=False)
    f,s = plt.subplots(1, 1, figsize=[16.00/2.54, 6.00/2.54])
    s.set_title('Groundwater pressure', fontsize=fontsize)
    s.plot(F[(F>=0.5)&(F<=2.5)], A[(F>=0.5)&(F<=2.5)], 'k-')
    s.set_xlabel('Frequency (cpd)')
    s.set_ylabel('Amplitude (m)')
    s.grid(True)
    f.tight_layout()
    st.pyplot(f)
    
    Fs = 24. #96.
    F, A, P = dft_fn(bp.Pba_mH2O, Fs, flag=False)
    f,s = plt.subplots(1, 1, figsize=[16.00/2.54, 6.00/2.54])
    s.set_title('Barometric pressure', fontsize=fontsize)
    s.plot(F[(F>=0.5)&(F<=2.5)], A[(F>=0.5)&(F<=2.5)], 'r-')
    s.set_xlabel('Frequency (cpd)')
    s.set_ylabel('Amplitude (m)')
    s.grid(True)
    f.tight_layout()
    st.pyplot(f)
