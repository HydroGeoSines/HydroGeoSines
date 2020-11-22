# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import os,sys

from .ext.hgs_analysis import Analysis
from ..model.site import Site
#from ...view import View

class Processing(object):
    # define all class attributes here 
    #attr = attr
    #site = Site 
    elements = []
    @staticmethod
    def HALS(site):
        Processing.elements.append(x)
        F_methods.Hals(site.data, site.denum)
    """
    def __init__(self, site, view, *args, **kwargs):
        self.site  = site
        self.view   = view    
        pass  
        #add attributes specific to Processing here
        #self.attribute = variable
        
        # testing des Inputs
        #isinstance(site,Site)
                    
    """
    #%% estimate amplitudes and phases based on linear least squares
    def hals(self, tf, data, freqs='ET'):
        self.method = {'function': inspect.currentframe().f_code.co_name}
        if (len(tf) != len(data)):
            raise Exception("Error: All input arrays must have the same length!")
        if freqs is 'ET':
            freqs = np.array(list(const['_etfqs'].values()))
        elif freqs is 'AT':
            freqs = np.array(list(const['_atfqs'].values()))
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
        time = tf
        y = data
        N = y.shape[0]
        f = freqs*2*np.pi
        num_freqs = len(f)
        # make sure that time vectors are relative
        # avoiding additional numerical errors
        time = time - np.floor(time[0])
        # assemble the matrix
        Phi = np.empty((N, 2*num_freqs + 1))
        for j in range(num_freqs):
            Phi[:,2*j] = np.cos(f[j]*time)
            Phi[:,2*j+1] = np.sin(f[j]*time)
        # account for any DC offsets
        Phi[:,-1] = 1
        # solve the system of linear equations
        theta, residuals, rank, singular = np.linalg.lstsq(Phi, y, rcond=None)
        # calculate the error variance
        error_variance = residuals[0]/y.shape[0]
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
    
        
