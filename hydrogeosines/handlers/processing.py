# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import os,sys

from ..ext.hgs_analysis import Analysis
from ..model.site import Site
#from ...view import View

from ..model.const import const

class Processing(object):
    # define all class attributes here 
    #attr = attr
    #site = site
    
    @staticmethod
    def hals(site, constituents = "ET"):
        # testing des Inputs
        assert isinstance(site,Site)
        #print(id(Site)) # test id of class location to compare across package
        
        if constituents is 'ET':
            freqs = np.array(list(const['_etfqs'].values()))
        elif constituents is 'AT':
            freqs = np.array(list(const['_atfqs'].values()))
        elif isinstance(constituents, (list,np.ndarray)):
            raise Exception("Error: Variable 'freqs' must be a list or numpy array!")
        else:
            raise Exception("Error: Variable 'freqs' is not valid!")
            
        tf = site.data.hgs.dt.to_zero
        data = site.data.value.values        
        data = Analysis.lin_window_ovrlp(tf,data)
        data = Analysis.harmonic_lsqr(tf, data, freqs)
        return data

    #%% estimate amplitudes and phases based on linear least squares
    #def hals(self, tf, data, freqs='ET'):
    #    self.method = {'function': inspect.currentframe().f_code.co_name}
    #    


