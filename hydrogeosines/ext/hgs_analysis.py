# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:14:12 2020

@author: Daniel
"""

import os,sys
import pandas as pd
import numpy as np
import warnings
from scipy.signal import detrend as detrend_func # for lin_window_ovrlp

from ..utils.tools import Tools

# static class
class Analysis(object):
    #def __init__(self, *args, **kwargs):
    #    pass
    
    @staticmethod
    def BE_average_of_ratios(X, Y):
        '''  
        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            
        Outputs:
            result      - scalar. Instantaneous barometric efficiency calculated as the mean ratio of measured values or temporal derivatives.
        '''
        result = np.mean(np.divide(Y, X, out=np.zeros_like(Y), where=X!=0))
        return result
    
    @staticmethod
    def BE_median_of_ratios(X, Y):
        '''  
        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
        
        Outputs:
            result      - scalar. Instantaneous barometric efficiency calculated as the median ratio of measured values or temporal derivatives.
        '''
        result = np.median(np.divide(Y, X, out=np.zeros_like(Y), where=X!=0))
        return result

    @staticmethod
    def BE_linear_regression(X, Y):
        '''  
        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
        
        Outputs:
            result      - scalar. Instantaneous barometric efficiency calculated as a linear regression based on measured values or temporal derivatives.
        '''
        result = np.linregress(Y, X)[0]
        return result

    @staticmethod
    def BE_Clark(X, Y):
        '''  
        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
        
        Outputs:
            result      - scalar. Instantaneous barometric efficiency calculated using the Clark (1967) method using measured values or temporal derivatives.
        '''
        sX, sY = [0], [0]
        for x,y in zip(X, Y):
            sX.append(sX[-1]+abs(x))
            if x==0:
                sY.append(sY[-1])
            elif np.sign(y)==np.sign(x):
                sY.append(sY[-1]+abs(y))
            elif np.sign(y)!=np.sign(x):
                sY.append(sY[-1]-abs(y))
        result = np.abs(np.divide(sY[-1], sX[-1], out=np.zeros_like(Y), where=X!=0))
        return result

    @staticmethod
    def BE_Rahi(X, Y):
        '''  
        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
        
        Outputs:
            result      - scalar. Instantaneous barometric efficiency calculated using the Rahi (2010) method using measured values or temporal derivatives.
        '''
        sX, sY = [0], [0]
        for x,y in zip(X, Y):
            if (np.sign(y)==np.sign(x)) & (abs(y)<abs(x)):
                sY.append(sY[-1]+abs(y))
                sX.append(sX[-1]+abs(x))
            else:
                sY.append(sY[-1])
                sX.append(sX[-1])
        result = np.divide(sY[-1], sX[-1], out=np.zeros_like(Y), where=X!=0))
        return result

    @staticmethod
    def BE_Quilty_and_Roeloffs(X, Y, freq, noverlap):
        '''  
        Inputs:
            X           - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y           - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            freq        - float. The frequency of interest.
            nperseg     - integer. The "number per segment".
            noverlap    - integer. The amount of "overlap" used when calculating power and cross sepctral density outputs.
        
        Outputs:
            result      - scalar. Instantaneous barometric efficiency calculated using the Quilty and Roeloffs (1991) method using measured values or temporal derivatives.
        '''
        psd_f, psd_p = welch(X,  fs=Fs, nperseg=nperseg, noverlap=noverlap, scaling='density', detrend=False)
        csd_f, csd_p = csd(X, Y, fs=Fs, nperseg=nperseg, noverlap=noverlap, scaling='density', detrend=False)
        result = np.abs(np.real(csd_p))/psd_p
        outfreq = csd_f[np.abs(csd_f-round(freq, 4)).argmin()]
	result = result[csd_f==outfreq][0] 
        return result
        
    @staticmethod
    def quantise(data, step):
        return step*np.floor((data/step)+1/2)
    
    @staticmethod
    def harmonic_lsqr(tf, data, freqs):        
        '''
        Inputs:
            tf      - time float. Should be an N x 1 numpy array.
            data    - estimated output. Should be an N x 1 numpy array.
            freqs   - frequencies to look for. Should be a numpy array.
        Outputs:
            alpha_est - estimated amplitudes of the sinusoids.
            phi_est - estimated phases of the sinusoids.
            error_variance - variance of the error. MSE of reconstructed signal compared to y.
            theta - parameters such that ||y - Phi*theta|| is
             minimized, where Phi is the matrix defined by
             freqs and tt that when multiplied by theta is a
             sum of sinusoids.
        '''
        N = data.shape[0]
        f = freqs*2*np.pi
        num_freqs = len(f)
        # make sure that time vectors are relative
        # avoiding additional numerical errors
        tf = tf - np.floor(tf[0])
        # assemble the matrix
        Phi = np.empty((N, 2*num_freqs + 1))
        for j in range(num_freqs):
            Phi[:,2*j] = np.cos(f[j]*tf)
            Phi[:,2*j+1] = np.sin(f[j]*tf)
        # account for any DC offsets
        Phi[:,-1] = 1
        # solve the system of linear equations
        theta, residuals, rank, singular = np.linalg.lstsq(Phi, data, rcond=None)
        # calculate the error variance
        error_variance = residuals[0]/N
        # when data is short, 'singular value' is important!
        # 1 is perfect, larger than 10^5 or 10^6 there's a problem
        condnum = np.max(singular) / np.min(singular)
        # print('Conditioning number: {:,.0f}'.format(condnum))
        if (condnum > 1e6): 
            warnings.warn('The solution is ill-conditioned!')
        # 	print(Phi)
        y_hat = Phi@theta
        # the DC component
        dc_comp = theta[-1]
        # create complex coefficients
        hals_comp = theta[:-1:2]*1j + theta[1:-1:2]
        result = {'freq': freqs, 'comp': hals_comp, 'err_var': error_variance, 'cond_num': condnum, 'offset': dc_comp}
        
        return y_hat, result
        
    @staticmethod    
    def lin_window_ovrlp(tf, data, length=3, stopper=3, n_ovrlp=3):
        '''  
        Inputs:
            tf      - time float. Should be an N x 1 numpy array.
            data    - signal values. Should be an N x 1 numpy array.
            length  - window size in days
            stopper - minimum number of y-values in window for detrending
            n_ovrlp - number of window overlaps
        
        Features:
            1.  windowed linear detrend with overlap functionality based on scipy.detrend function
            2.  reg_times is extended by value of length in both directions to improve averaging 
                and window overlap at boundaries. High overlap values in combination with high
                stopper values will cause reducion in window numbers at time array boundaries.
            3.  detrend window gaps are replaced with zeros    
            4.  handling of gaps (np.nan) in signal (y) that cause error in scipy detrend function
        '''
        x           = tf
        y           = data
        y_detr      = np.zeros(shape=(y.shape[0])) 
        counter     = np.zeros(shape=(y.shape[0]))
        num         = 0 # counter to check how many windows are sampled   
        interval    = length/(n_ovrlp+1) # step_size interval with overlap 
        # create regular sampled array along tf with step-size = interval   
        reg_times   = np.arange(x[0]-(x[1]-x[0])-length,x[-1]+length, interval)
        
        for tt in reg_times:
            idx = np.where((x > tt-(length/2)) & (x <= tt+(length/2)))[0]
            # make sure no np.nan values exist in y[idx]
            if np.isnan(y[idx]).any():
                idx = idx[~np.isnan(y[idx])]
            # only detrend with sufficient samples in time
            if len(idx) >= stopper:
                # use counter for number of detrends at each index
                counter[idx] += 1
                detrend = detrend_func(np.copy(y.flatten()[idx]),type="linear")
                y_detr[idx]  += detrend
                num += 1
                
        ## window gaps are set to np.nan
        counter[counter==0] = np.nan
        y_detrend = y_detr/counter       
        if len(y_detrend[np.isnan(y_detrend)]) > 0:
            # replace nan-values assuming a mean of zero
            gap_number = len(y_detrend[np.isnan(y_detrend)])
            y_detrend[np.isnan(y_detrend)] = 0.0
            print("Number of values in y that could not be detrended is {} (including NaN)".format(gap_number))
        
        ## Warning for reduced window overlap at margins of time array    
        if counter[0]  != n_ovrlp+1:
            print("Warning: Detrend window overlaps at t[0] reduced to {}. Consider adjusting value of stopper or n_ovrlp.".format(counter[0]-1))
        if counter[-1] != n_ovrlp+1:
            print("Warning: Detrend window overlaps at t[-1] reduced to {}. Consider adjusting value of stopper or n_ovrlp.".format(counter[-1]-1))
        
        return y_detrend
    
    @staticmethod    
    def fft_analys(tf,data,freqs,spd): 
        fft_N = len(tf)
        hanning = np.hanning(fft_N)
        # perform FFT
        fft_f = np.fft.fftfreq(int(fft_N), d=1/spd)[0:int(fft_N/2)]
        # FFT windowed for amplitudes
        fft_win   = np.fft.fft(hanning*data) # use signal with trend        
        fft_amps = 2*(np.abs(fft_win)/(fft_N/2))[0:int(fft_N/2)]
        fft_phs = np.angle(fft_win)[0:int(fft_N/2)] 
        # np.fft.fft default is a cosinus input. Thus for sinus the np.angle function returns a phase with a -np.pi shift.
        #fft_phs = fft_phs  + np.pi/2  # + np.pi/2 for a sinus signal as input
        #fft_phs = -(np.arctan(fft_win.real/fft_win.imag)) 
    
        phi_fft = []
        A_fft  = []
        for f in freqs:
            f_idx = Tools.find_nearest(fft_f,f)
            A_fft.append(fft_amps[f_idx])               
            # PHASE CORRECTION FOR TIDAL COMPONENTS
            num_waves = (tf[-1] - tf[0] + 1/spd)*f
            phase_corr = (num_waves - np.round(num_waves))*np.pi     
            phi_temp = fft_phs[f_idx] - phase_corr
            phi_temp = Tools.pi_range(phi_temp)          
            phi_fft.append(phi_temp)
            
        return freqs, A_fft, phi_fft  