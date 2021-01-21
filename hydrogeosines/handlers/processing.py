# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import os, sys

from ..ext.hgs_analysis import Analysis
from ..models.site import Site
#from ...view import View

from ..utils.tools import Tools

class Processing(object):
    # define all class attributes here 
    #attr = attr

    def __init__(self, site_obj, loc=None):
        self._validate(site_obj)
        self._obj   = site_obj
    
    @staticmethod
    def BE_method(data, method, derivative=True):
        if derivatives==True:
           X, Y = np.diff(data.BE), np.diff(GW) # need to also divide by the time step length
        else:
           X, Y = data.BE, data.GW
        if method.lower()=='average of ratios':
            result = Analysis.BE_average_of_ratios(data)
        elif method.lower()=='median of ratios':
            result = Analysis.BE_median_of_ratios(data)
        elif method.lower()=='linear regression':
            result = Analysis.BE_linear_regression(data)
        elif method.lower()=='clark':
            result = Analysis.BE_Clark(data)
        elif method.lower()=='rahi':
            result = Analysis.BE_Rahi(data)
        elif method.lower()=='quilty and roeloffs':
            result = Analysis.BE_Quilty_and_Roeloffs(data)
    
    @staticmethod
    def _validate(obj):
        if not isinstance(obj,Site):
            raise AttributeError("Must be a 'Site' object!")                       
            #print(id(Site)) # test id of class location to compare across package
    
    def hals(self, cat = "GW"):         
        #check for non valid categories 
        Tools.check_affiliation(cat,self._obj.VALID_CATEGORY)
        #ET = ET, GW = {ET, AT}, BP = AT        
        freqs = Site.freq_select(cat)
        comps = Site.comp_select(cat)
        data  = self._obj.data[self._obj.data.category == cat] 
        
        tf      = data.hgs.dt.to_zero
        values  = data.value.values        
        values  = Analysis.lin_window_ovrlp(tf,values)
        values  = Analysis.harmonic_lsqr(tf, values, freqs)
        # calculate Amplitude and Phase
        var = Tools.complex_to_real(tf, values[1]["comp"])
        var.update(comps)

        #return {"comp":comp, "freq":freqs, "var":var}
        return var#.update(values[1]["freq"])


