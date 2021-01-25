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
    def _validate(obj):
        if not isinstance(obj,Site):
            raise AttributeError("Must be a 'Site' object!")                       
            #print(id(Site)) # test id of class location to compare across package
    
    def BE_method(self, method, derivative=True):
        # TODO check for BE data
        X = self._obj.get_bp_data()
        Y = self._obj.get_bw_data()
        
        if derivative==True:
           X, Y = np.diff(X), np.diff(Y) # need to also divide by the time step length

        if method.lower()=='average of ratios':
            result = Analysis.BE_average_of_ratios(X,Y)
        elif method.lower()=='median of ratios':
            result = Analysis.BE_median_of_ratios(X,Y)
        elif method.lower()=='linear regression':
            result = Analysis.BE_linear_regression(X,Y)
        elif method.lower()=='clark':
            result = Analysis.BE_Clark(X,Y)
        elif method.lower()=='rahi':
            result = Analysis.BE_Rahi(X,Y)
        # TODO: This methods also takes freq + noverlap as parameters. Probably better to move it to another place (different overarching processing method)   
        #elif method.lower()=='quilty and roeloffs':
        #    result = Analysis.BE_Quilty_and_Roeloffs(X,Y, freq, nperseg, noverlap)
        return result    
    
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


