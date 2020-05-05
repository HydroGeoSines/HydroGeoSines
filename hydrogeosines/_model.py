import numpy as np
import datetime
import pandas as pd
import inspect
import re
import pytz
from scipy.interpolate import interp1d
from scipy.optimize import curve_fit
from scipy.signal import detrend as detrend_func

#%% the modelling class
class model(object):
    def __init__(self, site):
        self.method = {}
        self.site = site
        pass
    
    #%% 
    def regress_deconv(self, tf, GW, BP, ET=None, lag_h=24, et=False, et_method='harmonic', fqs=None):
        self.method = {'function': inspect.currentframe().f_code.co_name}
        if fqs is None:
            fqs = np.array(list(self.site._etfqs.values()))
        # check that dataset is regularly sampled
        tmp = np.diff(tf)
        if (np.around(np.min(tmp), 6) != np.around(np.max(tmp), 6)):
            raise Exception("Error: Dataset must be regularly sampled!")
        if (len(tf) != len(GW) != len(BP)):
            raise Exception("Error: All input arrays must have the same length!")
        # decite if Earth tides are included or not
        if (et_method == 'harmonic'):
            t  = tf
            # make time relative to avoid ET least squares errors
            dt = t[1] - t[0]
            spd = int(np.round(1/dt))
            BPnan = np.isnan(BP)
            WLnan = np.isnan(GW)
            nans = (BPnan | WLnan)
            t = t[~nans]
            # make the dataset relative
            ddBP = np.diff(BP)/dt
            ddWL = np.diff(GW)/dt
            # set missing values to zero
            dBPnan = np.isnan(ddBP)
            dWLnan = np.isnan(ddWL)
            dnans = (dBPnan | dWLnan)
            dBP = ddBP[~dnans]
            dWL = ddWL[~dnans]
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
                v[j+k, i] = dBP[k]
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

            # ----------------------------------------------
            nc = len(c)
            # calculate the head corrections
            dWLc = np.empty(ddWL.shape)
            dWLc[:] = np.nan
            dWLc[~dnans] = dt*np.cumsum(np.dot(X, c[1:nc]))
            # deal with the missing values
            WLc = GW - np.concatenate([[0], dWLc])
            # set the corrected heads
            WLc -= (np.nanmean(GW) - np.nanmean(WLc))

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
                trf = [a+(1j*b) for a,b in zip(c[k], c[NP+k])]
                mag = np.abs(trf)
                phs = np.angle(trf)
                params.update({'erf': {'freq': fqs, 'alpha': mag, 'phi': phs}})
            # return the method results
            return WLc, params

        # this method uses Earth tide time series
        elif(et_method == 'pygtide'):
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
            ddBP = np.diff(BP)/dt
            ddWL = np.diff(WL)/dt
            if et:
                ddET = np.diff(ET)/dt
            # set missing values to zero
            dBPnan = np.isnan(ddBP)
            dWLnan = np.isnan(ddWL)
            if et:
                dETnan = np.isnan(ddET)
                dnans = (dBPnan | dWLnan | dETnan)
            else:
                dnans = (dBPnan | dWLnan)
            dBP = ddBP[~dnans]
            dWL = ddWL[~dnans]
            if et:
                dET = ddET[~dnans]

            #%% prepare matrices ...
            lag = range(int((lag_h/24)*spd) + 1)
            n   = len(dBP)
            nn  = range(n)
            nm = len(lag)
            V = np.zeros([n, nm])
            for i in range(nm):
                j = lag[i]
                k = np.arange(n-j)
                V[j+k, i] = -dBP[k]

            #%%
            if et:
                nm = len(lag)
                W = np.zeros([n, nm])
                for i in range(nm):
                    j = lag[i]
                    k = np.arange(n-j)
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

            #%% determine the results
            nc = len(c)
            # calculate the head corrections
            dWLc = np.empty(ddWL.shape)
            dWLc[:] = np.nan
            dWLc[~dnans] = dt*np.cumsum(np.dot(XY, c[1:nc]))
            # deal with the missing values
            WLc = GW - np.concatenate([[0], dWLc])
            # set the corrected heads
            WLc -= (np.nanmean(GW) - np.nanmean(WLc))

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
            
    #%% estimate amplitudes and phases based on linear least squares
    def apes_lsq(self, tf, data, freqs='ET'):
        self.method = {'function': inspect.currentframe().f_code.co_name}
        if (len(tf) != len(data)):
            raise Exception("Error: All input arrays must have the same length!")
        if freqs is 'ET':
            freqs = np.array(list(self.site._etfqs.values()))
        elif freqs is 'AT':
            freqs = np.array(list(self.site._atfqs.values()))
        elif isinstance(freqs, (list,np.ndarray)):
            raise Exception("Error: Variable 'freqs' must be a list or numpy array!")
        else:
            raise Exception("Error: Variable 'freqs' is not valid!")
        #!!! check that freqs is a numpy array

        '''
        Inputs:
         		tt - time indices. Should be an N x 1 numpy array.
         		y - estimated output. should be an N x 1 numpy array.
         		freqs - frequencies to look for.
         Outputs:
         		alpha_est - estimated amplitudes of the sinusoids.
         		phi_est - estimated phases of the sinusoids.
         		error_variance - variance of the error. MSE of
                reconstructed signal compared to y.
         theta - parameters such that ||y - Phi*theta|| is
             minimized, where Phi is the matrix defined by
             freqs and tt that when multiplied by theta is a
             sum of sinusoids.'''
        # time
        tt = tf
        y = data
        N = y.shape[0]
        f = freqs*2*np.pi
        num_freqs = len(f)
        Phi = np.empty((N, 2*num_freqs))
        Sins = np.zeros((N,num_freqs))
        Coss = np.zeros((N,num_freqs))
        for i in range(N):
            for j in range(num_freqs):
                Sins[i,j] = np.sin(f[j]*tt[i])
                Coss[i,j] = np.cos(f[j]*tt[i])

        Phi[:,::2] = Sins
        Phi[:,1::2] = Coss
        Phi = np.hstack((Phi,np.ones((N,1))))
        # when data is short, 'singular value' is important!
        # 1 is perfect, larger than 10^5 or 10^6 there's a problem
        theta = np.linalg.lstsq(Phi, y, rcond=None)[0]
        y_hat = Phi@theta
        #mean = theta[:,0]
        theta_nomean = theta[:-1]
        a_hat = theta_nomean[::2]
        b_hat = theta_nomean[1::2]

        alpha_est = np.sqrt(a_hat**2 + b_hat**2)
        phi_est = np.arctan2(b_hat,a_hat)

        error_variance = float(np.linalg.norm(y - y_hat)**2/y.shape[0])
        result = {'freq': freqs, 'alpha': alpha_est.flatten(), 'phi': phi_est.flatten(), 'var': error_variance, 'theta': theta.flatten()}
        return y_hat, result
    
    #%% detrend function for regular and irregular datasets
    def lin_window_ovrlp(self, tf, data, length=3, stopper=3, n_ovrlp=3):
        self.method = {'function': inspect.currentframe().f_code.co_name}
        """
        Required packages:
        - import scipy as sp
        - import numpy as np    
        Parameters:
        -length:    window size in days
        -stopper:   minimum number of y-values in window for detrending
        -n_ovrlp:   number of window overlaps
        
        Features:
            1.  windowed linear detrend with overlap functionality based on scipy.detrend function
            2.  reg_times is extended by value of length in both directions to improve averaging 
                and window overlap at boundaries. High overlap values in combination with high
                stopper values will cause reducion in window numbers at time array boundaries.
            3.  detrend window gaps are replaced with zeros    
            4.  handling of gaps (np.nan) in signal (y) that cause error in scipy detrend function
        """
        x = tf
        y = data
        y_detr = np.zeros(shape=(y.shape[0])) 
        counter = np.zeros(shape=(y.shape[0]))
        num = 0 # counter to check how many windows are sampled   
        interval = length/(n_ovrlp+1) # step_size interval with overlap 
        # create regular sampled array along t with step-size = interval   
        reg_times = np.arange(x[0]-(x[1]-x[0])-length, x[-1]+length, interval)
        
        for tt in reg_times:
            idx = np.where((x > tt-(length/2)) & (x <= tt+(length/2)))[0]
            # make sure no np.nan values exist in y[idx]
            if np.isnan(y[idx]).any():
                idx = idx[~np.isnan(y[idx])]
            # only detrend with sufficient samples in time
            if len(idx) >= stopper:
                # use counter for number of detrends at each index
                counter[idx] += 1
                detrend = detrend_func(np.copy(y.flatten()[idx]), type="linear")
                y_detr[idx] += detrend
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
        if counter[0] != n_ovrlp+1:
            print("Warning: Detrend window overlaps at t[0] reduced to {}. Consider adjusting value of stopper or n_ovrlp.".format(counter[0]-1))
        if counter[-1] != n_ovrlp+1:
            print("Warning: Detrend window overlaps at t[-1] reduced to {}. Consider adjusting value of stopper or n_ovrlp.".format(counter[-1]-1))
        
        return y_detrend, counter
    
    #%%
    def calc_BE():
        pass
    
    #%%
    def calc_K():
        pass
    