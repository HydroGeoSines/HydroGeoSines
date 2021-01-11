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


