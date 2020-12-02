# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import os,sys

from ..ext.hgs_analysis import Analysis
from ..models.site import Site
#from ...view import View

from ..models.const import const

class Processing(object):
    # define all class attributes here 
    #attr = attr

    def __init__(self, site_obj):
        self._validate(site_obj)
        self._obj   = site_obj
    
    @staticmethod
    def _validate(obj):
        if not isinstance(obj,Site):
            raise AttributeError("Must be a 'Site' object!")                       
            #print(id(Site)) # test id of class location to compare across package
                
    def hals(self, constituents = "ET", loc=None, cat=None):
        #TODO: add loc and cat attribute. 
        #Is it possible to choose constituents by data category and replace the conditioning below?
        
        if constituents is 'ET':
            freqs = np.array(list(const['_etfqs'].values()))
        elif constituents is 'AT':
            freqs = np.array(list(const['_atfqs'].values()))
        elif isinstance(constituents, (list,np.ndarray)):
            raise Exception("Error: Variable 'freqs' must be a list or numpy array!")
        else:
            raise Exception("Error: Variable 'freqs' is not valid!")
            
        tf = self._obj.data.hgs.dt.to_zero
        data = self._obj.data.value.values        
        data = Analysis.lin_window_ovrlp(tf,data)
        data = Analysis.harmonic_lsqr(tf, data, freqs)
        return data



