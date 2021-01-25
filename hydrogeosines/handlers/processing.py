# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import datetime as dt # this should probably not be added in here. Generally loaded in site through hgs
import os, sys

from ..ext.hgs_analysis import Analysis
from ..models.site import Site
#from ...view import View

from ..utils.tools import Tools

class Processing(object):
    # define all class attributes here 
    #attr = attr
    
    def __init__(self, site_obj, loc=None, et=False):
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
    

    def hals(self, cat="GW"):
        #check for non valid categories 
        Tools.check_affiliation(cat, self._obj.VALID_CATEGORY)
        #ET = ET, GW = {ET, AT}, BP = AT        
        freqs = Site.freq_select(cat)

        #TODO: define a function for this type of category extraction
        comps = Site.comp_select(cat)
        data  = self._obj.data[self._obj.data.category == cat]       
        tf      = data.hgs.dt.to_zero
        values  = data.value.values  
        values  = Analysis.lin_window_ovrlp(tf, values)
        values  = Analysis.harmonic_lsqr(tf, values, freqs)
        
        # calculate Amplitude and Phase
        var = Tools.complex_to_real(tf, values[1]["comp"])
        var.update(comps)

        #return {"comp":comp, "freq":freqs, "var":var}
        return var#.update(values[1]["freq"])

    def correct_GW(self, location=None, lag_h=24, et_method=None, fqs=None):
        print("A complicated procedure ...")
        # first aggregate all the datasets into one
        data = self._obj.data.pivot(index='datetime', columns=['category', 'location'], values='value')
        if 'BP' not in data.columns:
            raise Exception('Error: BP is required but not found in the dataset!')
        if ((et_method is not None) and ('ET' not in data.columns)):
            raise Exception('Error: ET time series is required but not found in the dataset!')
        # apply tests to see if data is regular and complete
        # first, drop any rows with missing values
        data.dropna(how='any', inplace=True)
        tdiff = np.diff(data.index)
        idx = (tdiff != tdiff[0])
        if np.any(idx):
            raise Exception('Error: Dataset must be regularly sampled!')
        # DATASET IS ALL GOOD NOW
        # prepare results container
        results = pd.DataFrame(index=data.index)
        # prepare time, BP and ET
        delta = (data.index.tz_localize(None) - data.index.tz_localize(None)[0])
        tf = (delta.days + (delta.seconds / (60*60*24))).values
        BP = data['BP'].iloc[:, 0].values
        if et_method is None:
            ET = None
        else:
            ET = data['ET'].iloc[:, 0].values
        # loop through GW category
        gw_locs = data['GW'].columns.values
        params = {}
        for loc in gw_locs:
            print(loc)
            GW = data['GW'][loc].values
            # regress_deconv(self, tf, GW, BP, ET=None, lag_h=24, et=False, et_method='hals', fqs=None):
            values, params[loc] = Analysis.regress_deconv(tf, GW, BP, ET, lag_h=lag_h, et_method=et_method, fqs=fqs)
            results[loc] = values
        return results, params
