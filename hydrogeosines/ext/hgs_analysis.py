# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:14:12 2020

@author: Daniel
"""

import os,sys
import pandas as pd
import numpy as np
import warnings
from scipy.optimize import curve_fit
from scipy.linalg import svdvals
from scipy.stats import linregress
from scipy.signal import csd

from .. import utils
from ..models import const

# static class
class Analysis(object):
    #def __init__(self, *args, **kwargs):
    #    pass

    @staticmethod
    def BE_average_of_ratios(X, Y):
        '''
        Calculate instantaneous barometric efficiency using the average of ratios method, a time domain solution.

        Parameters
        ----------
        X : N x 1 numpy array
            barometric pressure data,  provided as either measured values or as temporal derivatives.
        Y : N x 1 numpy array
            groundwater pressure data, provided as either measured values or as temporal derivatives.

        Returns
        -------
        scalar
            Instantaneous barometric efficiency calculated as the mean ratio of measured values or temporal derivatives.

        Notes
        -----
            ** Need to come up with a better way to avoid division by zero issues and similar
            -> maybe this works: https://stackoverflow.com/questions/26248654/how-to-return-0-with-divide-by-zero
        '''
        #with np.errstate(divide='ignore', invalid='ignore'):
        #    result = np.mean(np.divide(Y, X)[np.isfinite(np.divide(Y, X))])
        X,Y = np.round(X, 12), np.round(Y, 12)
        result = []
        for x,y in zip(X,Y):
            if x!=0.:
                result.append(y/x)
        return np.mean(result)

    @staticmethod
    def BE_median_of_ratios(X, Y):
        '''
        Calculate instantaneous barometric efficiency using the median of ratios, a time domain solution.

        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.

        Outputs:
            result - scalar. Instantaneous barometric efficiency calculated as the median ratio of measured values or temporal derivatives.
        '''
        with np.errstate(divide='ignore', invalid='ignore'):
            result = np.median(np.divide(Y, X)[np.isfinite(np.divide(Y, X))])
        return result

    @staticmethod
    def BE_linear_regression(X, Y):
        '''
        Calculate instantaneous barometric efficiency using linear regression, a time domain solution.

        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.

        Outputs:
            result - scalar. Instantaneous barometric efficiency calculated as a linear regression based on measured values or temporal derivatives.
        '''
        result = np.linregress(Y, X)[0]
        return result

    @staticmethod
    def BE_Clark(X, Y):
        '''
        Calculate instantaneous barometric efficiency using the Clark (1967) method, a time domain solution.

        Inputs:
            X - barometric pressure data,  provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.
            Y - groundwater pressure data, provided as either measured values or as temporal derivatives. Should be an N x 1 numpy array.

        Outputs:
            result - scalar. Instantaneous barometric efficiency calculated using the Clark (1967) method using measured values or temporal derivatives.
        Notes:
            ** Need to check that Clark's rules are implemented the right way around
        '''
        sX, sY = [0.], [0.]
        for x,y in zip(X, Y):
            sX.append(sX[-1]+abs(x))
            if x==0:
                sY.append(sY[-1])
            elif np.sign(x)==np.sign(y):
                sY.append(sY[-1]+abs(y))
            elif np.sign(x)!=np.sign(y):
                sY.append(sY[-1]-abs(y))
        result = linregress(sX, sY)[0]
        return result

    @staticmethod
    def BE_Davis_and_Rasmussen(X, Y):
        '''
        Calculate instantaneous barometric efficiency using the Davis and Rasmussen (1993) method, a time domain solution.

        Parameters
        ----------
        X : N x 1 numpy array
            barometric pressure data,  provided as either measured values or as temporal derivatives.
        Y : N x 1 numpy array
            groundwater pressure data, provided as either measured values or as temporal derivatives.

        Returns
        -------
        result : scalar
            Instantaneous barometric efficiency calculated using the Davis and Rasmussen (1993) method using measured values or temporal derivatives.
        
        Notes
        -----
            ** Work in progress - just need to marry the D&R algorithm with the automated segmenting algorithm
        '''
        cSnum    = np.zeros(1)
        cSden    = np.zeros(1)
        cSabs_dB = np.zeros(1)
        cSclk_dW = np.zeros(1)
        dB       = -np.diff(X)
        n        =  len(dB)
        j        =  len(dB[dB>0.])-len(dB[dB<0.])
        Sraw_dB  =  np.sum(dB)
        Sabs_dB  =  np.sum(np.abs(dB))
        dW       =  np.diff(Y)
        Sraw_dW  =  np.sum(dW)
        Sclk_dW  = np.zeros(1)
        for m in range(len(dW)):
            if np.sign(dW[m])==np.sign(dB[m]):
                Sclk_dW += np.abs(dW[m])
            elif np.sign(dW[m])!=np.sign(dB[m]):
                Sclk_dW -= np.abs(dW[m])
        cSnum    += (float(j)/float(n))*Sraw_dW
        cSden    += (float(j)/float(n))*Sraw_dB
        cSabs_dB += Sabs_dB
        cSclk_dW += Sclk_dW
        result = ((cSclk_dW/cSabs_dB-cSnum/cSabs_dB)/(1.-cSden/cSabs_dB))
        return result

    @staticmethod
    def BE_Rahi(X, Y):
        '''
        Calculate instantaneous barometric efficiency using the Clark (1967) method, a time domain solution.

        Parameters
        ----------
        X : N x 1 numpy array
            barometric pressure data,  provided as either measured values or as temporal derivatives.
        Y : N x 1 numpy array
            groundwater pressure data, provided as either measured values or as temporal derivatives.

        Returns
        -------
        result : scalar
            Instantaneous barometric efficiency calculated using the Rahi (2010) method using measured values or temporal derivatives.

        Notes
        -----
            ** Need to check that Rahi's rules are implemented the right way around.
        '''
        sX, sY = [0.], [0.]
        for x,y in zip(X, Y):
            if (np.sign(x)!=np.sign(y)) & (abs(y)<abs(x)):
                sX.append(sX[-1]+abs(x))
                sY.append(sY[-1]+abs(y))
            else:
                sX.append(sX[-1])
                sY.append(sY[-1])
        result = linregress(sX, sY)[0]
        return result

    @staticmethod
    def BE_Rojstaczer(X, Y, freq, nperseg, noverlap):
        '''
        

        Parameters
        ----------
        X : N x 1 numpy array
            barometric pressure data,  provided as either measured values or as temporal derivatives.
        Y : N x 1 numpy array
            groundwater pressure data, provided as either measured values or as temporal derivatives.
        freq : float
            The frequency of interest.
        nperseg : int
            The number of data points per segment.
        noverlap : int
            The amount of overlap between data points used when calculating power and cross spectral density outputs.

        Returns
        -------
        result : scalar
            Instantaneous barometric efficiency calculated using the Quilty and Roeloffs (1991) method using measured values or temporal derivatives.

        Notes
        -----
            ** Need to check that Rojstaczer's (or Q&R's) implementation was averaged over all frequencies
        '''
        
        csd_f, csd_p = csd(X, Y, fs=freq, nperseg=nperseg, noverlap=noverlap) #, scaling='density', detrend=False)
        psd_f, psd_p = csd(X, X, fs=freq, nperseg=nperseg, noverlap=noverlap) #, scaling='density', detrend=False)
        result = np.mean(np.abs(csd_p)/psd_p)
        return result

    @staticmethod
    def quantise(data, step):
        ''' Quantization of a signal '''
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
        f = np.array(freqs)*2*np.pi
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
        y_model = Phi@theta
        # the DC component
        dc_comp = theta[-1]
        # create complex coefficients
        hals_comp = theta[:-1:2]*1j + theta[1:-1:2]
        result = {'freq': freqs, 'complex': hals_comp, 'err_var': error_variance, 'cond_num': condnum, 'offset': dc_comp, 'y_model': y_model}

        return result

    @staticmethod
    def lin_window_ovrlp(tf, data, length=3, stopper=3, n_ovrlp=3):
        """
        Windowed linear detrend function with optional window overlap
        
        Parameters
        ----------
        time : N x 1 numpy array
            Sample times.
        y : N x 1 numpy array
            Sample values.
        length : int
            Window size in days
        stopper : int 
            minimum number of samples within each window needed for detrending
        n_ovrlp : int
            number of window overlaps relative to the defined window length
            
        Returns
            -------
            y.detrend : array_like
                estimated amplitudes of the sinusoids.
        
        Notes
        -----
        A windowed linear detrend function with optional window overlap for pre-processing of non-uniformly sampled data.
        The reg_times array is extended by value of "length" in both directions to improve averaging and window overlap at boundaries. High overlap values in combination with high
        The "stopper" values will cause reducion in window numbers at time array boundaries.   
        """
        
        x = np.array(tf).flatten()
        y = np.array(data).flatten()
        y_detr      = np.zeros(shape=(y.shape[0]))
        counter     = np.zeros(shape=(y.shape[0]))
        A = np.vstack([x, np.ones(len(x))]).T
        #num = 0 # counter to check how many windows are sampled   
        interval    = length/(n_ovrlp+1) # step_size interval with overlap 
        # create regular sampled array along t with step-size = interval.         
        reg_times   = np.arange(x[0]-(x[1]-x[0])-length,x[-1]+length, interval)
        # extract indices for each interval
        idx         = [np.where((x > tt-(length/2)) & (x <= tt+(length/2)))[0] for tt in reg_times]  
        # exclude samples without values (np.nan) from linear detrend
        idx         = [i[~np.isnan(y[i])] for i in idx]
        # only detrend intervals that meet the stopper criteria
        idx         = [x for x in idx if len(x) >= stopper]
        for i in idx:        
            # find linear regression line for interval
            coe = np.linalg.lstsq(A[i],y[i],rcond=None)[0]
            # and subtract off data to detrend
            detrend = y[i] - (coe[0]*x[i] + coe[1])
            # add detrended values to detrend array
            np.add.at(y_detr,i,detrend)
            # count number of detrends per sample (depends on overlap)
            np.add.at(counter,i,1)
    
        # window gaps, marked by missing detrend are set to np.nan
        counter[counter==0] = np.nan
        # create final detrend array
        y_detrend = y_detr/counter       
        if len(y_detrend[np.isnan(y_detrend)]) > 0:
            # replace nan-values assuming a mean of zero
            y_detrend[np.isnan(y_detrend)] = 0.0
    
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
            f_idx = utils.find_nearest(fft_f,f)
            A_fft.append(fft_amps[f_idx])
            # PHASE CORRECTION FOR TIDAL COMPONENTS
            num_waves = (tf[-1] - tf[0] + 1/spd)*f
            phase_corr = (num_waves - np.round(num_waves))*np.pi
            phi_temp = fft_phs[f_idx] - phase_corr
            phi_temp = utils.pi_range(phi_temp)
            phi_fft.append(phi_temp)

        return freqs, A_fft, phi_fft

    @staticmethod
    def regress_deconv(tf, GW, BP, ET=None, lag_h=24, et_method=None, fqs=None):
        et = True
        if ET is None and et_method is None:
            et = False
            et_method = 'hals'
        if fqs is None:
            fqs = np.array(list(const.const['_etfqs'].values()))
        # check that dataset is regularly sampled
        tmp = np.diff(tf)
        if (np.around(np.min(tmp), 6) != np.around(np.max(tmp), 6)):
            raise Exception("Error: Dataset must be regularly sampled!")
        if (len(tf) != len(GW) != len(BP)):
            raise Exception("Error: All input arrays must have the same length!")
        # decite if Earth tides are included or not
        if (et_method == 'hals'):
            print("DEBUG: PERFORM HALS")
            t  = tf
            # make time relative to avoid ET least squares errors
            dt = t[1] - t[0]
            spd = int(np.round(1/dt))
            # make the dataset relative
            dBP = np.diff(BP)/dt
            dWL = np.diff(GW)/dt
            # setup general parameters
            nlag = int((lag_h/24)*spd)
            n    = len(dBP)
            nn   = list(range(n))
            lags = list(range(nlag+1))
            nm = nlag+1
            # the regression matrix for barometric pressure
            v = np.zeros([n, nm])
            for i in range(nm):
                j = lags[i]
                k = np.arange(n-j)
                v[j+k, i] = -dBP[k]
            # consider ET
            if et:
                # prepare ET frequencies
                f = fqs
                NP = len(f)
                omega = 2.*np.pi*f
                # the regression matrix for Earth tides
                u1 = np.zeros([n, NP])
                u2 = u1.copy()
                for i in range(NP):
                    tau = omega[i]*t[nn]
                    u1[:,i] = np.cos(tau)
                    u2[:,i] = np.sin(tau)
                X = np.hstack([v, u1, u2])
            else:
                X = np.hstack([v])
            # perform regression ...
            Z = np.hstack([np.ones([n,1]), X])

            #%% perform least squares fitting
            # ----------------------------------------------
            # c  = np.linalg.lstsq(Z, dWL, rcond=None)[0]
            # ----------------------------------------------
            def brf_total(Z):
                #print(dir(Phi))
                def brf(x, *c):
                   # print(Phi)
                    return Z@c
                return brf
            c = 0.5*np.ones(Z.shape[1])
            c, covar = curve_fit(brf_total(Z), t, dWL, p0=c)

            #%% compute the singular values
            sgl = svdvals(Z)
            # 'singular value' is important: 1 is perfect,
            # larger than 10^5 or 10^6 there's a problem
            condnum = np.max(sgl) / np.min(sgl)
            # print('Conditioning number: {:,.0f}'.format(condnum))
            if (condnum > 1e6):
                warnings.warn('The solution is ill-conditioned!')

            # ----------------------------------------------
            nc = len(c)
            # calculate the head corrections
            dWLc = dt*np.cumsum(np.dot(X, c[1:nc]))
            # deal with the missing values
            WLc = GW - np.concatenate([[0], dWLc])
            # set the corrected heads
            WLc += (np.nanmean(GW) - np.nanmean(WLc))

            # adjust for mean offset
            # trend  = c[0]
            lag_t = np.linspace(0, lag_h, int((lag_h/24)*spd) + 1, endpoint=True)
            # error propagation
            brf   = c[np.arange(1, nm+1)]
            brf_covar = covar[1:nm+1,1:nm+1]
            brf_var = np.diagonal(brf_covar)
            brf_stdev = np.sqrt(brf_var)
            cbrf   = np.cumsum(brf)
            # the error propagation for summation
            cbrf_var = np.zeros(brf_var.shape)
            for i in np.arange(0, nm):
            #    if (i == 4): break
                diag = np.diagonal(brf_covar[0:i+1, 0:i+1])
                triaglow = np.tril(brf_covar[0:i+1, 0:i+1], -1)
            #    print(covatl)
                cbrf_var[i] = np.sum(diag) + 2*np.sum(triaglow)
            cbrf_stdev = np.sqrt(cbrf_var)
            params = {'brf': {'lag': lag_t, 'irf': brf, 'irf_stdev': brf_stdev, 'crf': cbrf, 'crf_stdev': cbrf_stdev}}

            # consider ET if desired ...
            if et:
                k = np.arange(nm+1, NP+nm+1)
                # this is the result for the derivative WL/dt
                trf = np.array([a+(1j*b) for a,b in zip(c[k], c[NP+k])])
                # this is the correction for the frequency content in the WL
                # !!!!
                params.update({'erf': {'freq': fqs, 'comp': trf}})
            # return the method results
            return WLc, params

        # this method uses Earth tide time series
        elif(et_method == 'ts'):
            print("DEBUG: PERFORM TS")
            if et:
                if (ET is None):
                    raise Exception("Error: Please input valid Earth tide data!")
                if (len(tf) != len(ET)):
                    raise Exception("Error: Earth tide data must have the same length!")
            # start ...
            t  = tf
            # make time relative to avoid ET least squares errors
            dt = t[1] - t[0]
            # the data
            WL = GW

            #%% temporal derivatives
            spd = int(np.round(1/dt))
            #dt = 1./24.
            dBP = np.diff(BP)/dt
            dWL = np.diff(WL)/dt
            if et:
                dET = np.diff(ET)/dt

            #%% prepare matrices ...
            lag = range(int((lag_h/24)*spd) + 1)
            n   = len(dBP)
            nn  = range(n)
            nm = len(lag)
            V = np.zeros([n, nm])
            for i in range(nm):
                j = lag[i]
                k = np.arange(n-j)
                ### need negative?
                V[j+k, i] = -dBP[k]

            #%%
            if et:
                nm = len(lag)
                W = np.zeros([n, nm])
                for i in range(nm):
                    j = lag[i]
                    k = np.arange(n-j)
                    ### need negative?
                    W[j+k, i] = dET[k]
                XY = np.hstack([V, W])
            else:
                XY = V
            # stack the matrices
            Z = np.hstack([np.ones([n,1]), XY])

            #%% perform least squares fitting
            def brf_total(Z):
                #print(dir(Phi))
                def brf(x, *c):
                   # print(Phi)
                    return Z@c
                return brf
            c = 0.5*np.ones(Z.shape[1])
            c, covar = curve_fit(brf_total(Z), t, dWL, p0=c)

            #%% compute the singular values
            sgl = svdvals(Z)
            # 'singular value' is important: 1 is perfect,
            # larger than 10^5 or 10^6 there's a problem
            condnum = np.max(sgl) / np.min(sgl)
            # print('Conditioning number: {:,.0f}'.format(condnum))
            if (condnum > 1e6):
                warnings.warn('The solution is ill-conditioned!')

            #%% determine the results
            nc = len(c)
            # calculate the head corrections
            dWLc = dt*np.cumsum(np.dot(XY, c[1:nc]))
            # deal with the missing values
            WLc = GW - np.concatenate([[0], dWLc])
            # set the corrected heads
            WLc += (np.nanmean(GW) - np.nanmean(WLc))

            #%% components
            # trend = c[0]
            lag_t = np.linspace(0, lag_h, int((lag_h/24)*spd) + 1, endpoint=True)
            # error propagation
            brf   = c[np.arange(1, nm+1)]
            brf_covar = covar[1:nm+1,1:nm+1]
            brf_var = np.diagonal(brf_covar)
            brf_stdev = np.sqrt(brf_var)
            cbrf   = np.cumsum(brf)
            # the error propagation for summation
            cbrf_var = np.zeros(brf_var.shape)
            for i in np.arange(0, nm):
            #    if (i == 4): break
                diag = np.diagonal(brf_covar[0:i+1, 0:i+1])
                triaglow = np.tril(brf_covar[0:i+1, 0:i+1], -1)
            #    print(covatl)
                cbrf_var[i] = np.sum(diag) + 2*np.sum(triaglow)
            cbrf_stdev = np.sqrt(cbrf_var)
            params = {'brf': {'lag': lag_t, 'irf': brf, 'irf_stdev': brf_stdev, 'crf': cbrf, 'crf_stdev': cbrf_stdev}}

            if et:
                erf = c[nm+1:2*nm+1]
                erf_covar = covar[nm+1:2*nm+1,nm+1:2*nm+1]
                erf_var = np.diagonal(erf_covar)
                erf_stdev = np.sqrt(erf_var)
                cerf = np.cumsum(erf)
                # the error propagation for summation
                cerf_var = np.zeros(brf_var.shape)
                for i in np.arange(0, nm):
                #    if (i == 4): break
                    diag = np.diagonal(erf_covar[0:i+1, 0:i+1])
                    triaglow = np.tril(erf_covar[0:i+1, 0:i+1], -1)
                #    print(covatl)
                    cerf_var[i] = np.sum(diag) + 2*np.sum(triaglow)
                cerf_stdev = np.sqrt(cerf_var)
                params.update({'erf': {'lag': lag_t, 'irf': erf, 'irf_stdev': erf_stdev, 'crf': cerf, 'crf_stdev': cerf_stdev}})

            return WLc, params
        else:
            raise Exception("Error: Please only use available Earth tide methods!")
