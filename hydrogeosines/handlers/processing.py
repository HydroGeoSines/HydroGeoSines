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

from ..models import const

class Processing(object):
    # define all class attributes here 
    #attr = attr
    
    def __init__(self, site_obj, loc=None, et=False):
        self._validate(site_obj)
        self._obj   = site_obj
    
    @staticmethod
    def _validate(obj):
        if not isinstance(obj, Site):
            raise AttributeError("Must be a 'Site' object!")                       
            #print(id(Site)) # test id of class location to compare across package

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
        return var #.update(values[1]["freq"])
    
    
    def BE_method(self, method, derivative=True):
        data = self._obj.data.hgs.pivot
        if any(cat not in data.columns for cat in ("GW","BP")):
            raise Exception('Error: Both BP and GW data is required but not found in the dataset!')
        # TODO: what happens, if there are multiple locations with GW and BP data? Do we run the method on each location seperately? Do we want them in one single output?      
        X = self._obj.data.hgs.filters.get_bp_values()
        Y = self._obj.data.hgs.filters.get_gw_values()
        
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
    
    
    def BE_calc(self, method='rau', gw_locs=None, bp_loc:str=None, et_loc:str=None, freq_method:str='hals'):
        print("Start BE_calc procedure ...")
        # first aggregate all the datasets into one
        data = self._obj.data.pivot(index='datetime', columns=['category', 'location'], values='value')
        
        #%% check to see if BP complies with minimal requirements
        if 'BP' not in data.columns:
            raise Exception('Error: BP is required but not found in the dataset!')
        # if no BP series is declared, use the first one ...
        if bp_loc is None:
            bp_loc = data['BP'].columns[0]
        if bp_loc not in data['BP'].columns:
            raise Exception("Error: BP location '{}' is not available!".format(bp_loc))
        # calculate datetime as floating point numbers ...
        BP = data['BP'][bp_loc].values
        tmp = np.isnan(BP)
        tdelta = (data.index[~tmp].tz_localize(None) - data.index[~tmp].tz_localize(None)[0])
        bp_tf = (tdelta.days + (tdelta.seconds / (60*60*24))).values
        if (bp_tf.max() - bp_tf.min() < 20):
            raise Exception("Error: The BP duration for location {} must be at least 20 days for this analysis!".format(bp_loc))
        if (len(bp_tf)/(bp_tf.max() - bp_tf.min()) < 24):
            raise Exception("Error: The BP average sampling rate location {} must be at least 24 samples per hour for this analysis!".format(bp_loc))
        freqs = Site.freq_select("BP")
        bp_tf = bp_tf - bp_tf.min()
        BP_detr = Analysis.lin_window_ovrlp(bp_tf, BP)
        BP_mod, BP_hals  = Analysis.harmonic_lsqr(bp_tf, BP_detr, freqs)
        print(BP_hals)
        BP_m2_idx = Site.freq_idx("M2", "BP")
        BP_m2_idx = Site.freq_idx("M2", "BP")
        BP_s2_idx = Site.freq_idx("S2", "BP")
        BP_s2_idx = Site.freq_idx("S2", "BP")
                
        #%% check to see if ET complies with minimal requirements
        # if no BP series is declared, use the first one ...
        if et_loc is None:
            et_loc = data['ET'].columns[0]
        if et_loc not in data['ET'].columns:
            raise Exception("Error: ET location '{}' is not available!".format(et_loc))
        # calculate datetime as floating point numbers ...
        ET = data['ET'][et_loc].values
        tmp = np.isnan(ET)
        tdelta = (data.index[~tmp].tz_localize(None) - data.index[~tmp].tz_localize(None)[0])
        et_tf = (tdelta.days + (tdelta.seconds / (60*60*24))).values
        if (et_tf.max() - et_tf.min() < 20):
            raise Exception("Error: The ET duration for location '{}' must be at least 20 days for this analysis!".format(et_loc))
        if (len(et_tf)/(et_tf.max() - et_tf.min()) < 24):
            raise Exception("Error: The ET average sampling rate location {} must be at least 24 samples per hour for this analysis!".format(et_loc))
        freqs = Site.freq_select("ET")
        et_tf = et_tf - et_tf.min()
        ET_detr = Analysis.lin_window_ovrlp(et_tf, ET)
        ET_mod, ET_hals  = Analysis.harmonic_lsqr(et_tf, ET_detr, freqs)
        print(ET_hals)
        ET_m2_idx = Site.freq_idx("M2", "ET")
        ET_m2_idx = Site.freq_idx("M2", "ET")
        ET_s2_idx = Site.freq_idx("S2", "ET")
        ET_s2_idx = Site.freq_idx("S2", "ET")
        
        #%% loop through GW and check to see if it complies with minimal requirements
        # check and loop through GW category
        if gw_locs is None:
            gw_locs = data['GW'].columns
        be_results = {}
        GW_m2_idx = Site.freq_idx("M2", "GW")
        GW_m2_idx = Site.freq_idx("M2", "GW")
        GW_s2_idx = Site.freq_idx("S2", "GW")
        GW_s2_idx = Site.freq_idx("S2", "GW")
        print(GW_s2_idx)
        # loop through GW ...
        for loc in gw_locs:
            if loc not in data['GW'].columns:
                raise Exception("Error: GW location '{}' is not available!".format(loc))
                
            print(loc)
            # check and loop through GW category
            GW = data['GW'][loc].values
            tmp = np.isnan(GW)
            tdelta = (data.index[~tmp].tz_localize(None) - data.index[~tmp].tz_localize(None)[0])
            gw_tf = (tdelta.days + (tdelta.seconds / (60*60*24))).values
            if (gw_tf.max() - gw_tf.min() < 20):
                raise Exception("Error: The GW duration for location '{}' must be at least 20 days for this analysis!".format(et_loc))
            if (len(gw_tf)/(gw_tf.max() - gw_tf.min()) < 24):
                raise Exception("Error: The GW average sampling rate for location '{}' must be at least 24 samples per hour for this analysis!".format(et_loc))
            
            # which frequency domain method to use here ...
            if (freq_method == 'hals'):
                # perform a HALS based frequency analysis ...
                freqs = Site.freq_select("GW")
                gw_tf = gw_tf - gw_tf.min()
                GW_detr = Analysis.lin_window_ovrlp(gw_tf, GW)
                GW_mod, GW_hals  = Analysis.harmonic_lsqr(gw_tf, GW_detr, freqs)
                print(GW_hals)
            elif (freq_method == 'fft'):
                pass
            else:
                raise Exception("Error: The frequency-domain method '{}' is not available!".format(freq_method))
            
            # which BE method to use here ...
            if (method == 'rau'):
                # Calculate BE values
                # Equation 9, Rau et al. (2020), doi:10.5194/hess-24-6033-2020
                GW_ET_s2 = (GW_hals['comp'][GW_m2_idx] / ET_hals['comp'][ET_m2_idx]) * ET_hals['comp'][ET_s2_idx]
                GW_AT_s2 = GW_hals['comp'][GW_s2_idx] - GW_ET_s2
                # a phase check ...
                GW_ET_m2_dphi = np.angle(GW_hals['comp'][GW_m2_idx] / ET_hals['comp'][ET_m2_idx])
                print(GW_ET_m2_dphi)
                
                BE = np.abs(GW_AT_s2 / BP_hals['comp'][BP_s2_idx])
                be_results[loc] = {'BE': BE}
            
            elif (method == 'acworth'):
                # Calculate BE values
                # Equation 4, Acworth et al. (2016), doi:10.1002/2016GL071328
                BE = (np.abs(GW_hals['comp'][GW_s2_idx])  + np.abs(ET_hals['comp'][ET_s2_idx]) * np.cos(np.angle(BP_hals['comp'][BP_s2_idx]) - np.angle(ET_hals['comp'][ET_s2_idx])) * (np.abs(GW_hals['comp'][GW_m2_idx]) / np.abs(ET_hals['comp'][ET_m2_idx]))) / np.abs(BP_hals['comp'][BP_s2_idx])
                be_results[loc] = {'BE': BE}
                pass
            else:
                raise Exception("Error: The method '{}' is not available!".format(method))
                        
            # regress_deconv(self, tf, GW, BP, ET=None, lag_h=24, et=False, et_method='hals', fqs=None):
            
            
        return be_results

    
    def GW_correct(self, gw_locs=None, bp_loc:str=None, et_loc:str=None, lag_h=24, et_method=None, fqs=None):
        print("Start GW_correct procedure ...")
        # first aggregate all the datasets into one
        data = self._obj.data.pivot(index='datetime', columns=['category', 'location'], values='value')
        if 'BP' not in data.columns:
            raise Exception('Error: BP is required but not found in the dataset!')
        if ((et_method is not None) and ('ET' not in data.columns)):
            raise Exception('Error: ET time series is required but not found in the dataset!')
        # if no BP series is declared, use the first one ...
        if bp_loc is None:
            bp_loc = data['BP'].columns[0]
        if bp_loc not in data['BP'].columns:
            raise Exception("Error: BP location '{}' is not available!".format(bp_loc))
        # apply tests to see if data is regularly sampled
        BP = data['BP'][bp_loc].values
        tmp = np.isnan(BP)
        tdiff = np.diff(data.index[~tmp])
        if np.any(tdiff != tdiff[0]):
            raise Exception("Error: Category BP must be regularly sampled!")
        # prepare time, BP and ET
        # TODO: Is the localize step in the import_csv not sufficient? 
        ## BTW: the utc offset for each location is automatically stored in the site upon import
        delta = (data.index.tz_localize(None) - data.index.tz_localize(None)[0])
        tf = (delta.days + (delta.seconds / (60*60*24))).values
        if et_method is None:
            ET = None
        elif et_method == 'hals':
            ET = None
        elif et_method == 'ts':
            # if no BP series is declared, use the first one ...
            if et_loc is None:
                et_loc = data['ET'].columns[0]
            if et_loc not in data['ET'].columns:
                raise Exception("Error: ET location '{}' is not available!".format(et_loc))
            # apply tests to see if data is regularly sampled
            ET = data['ET'][et_loc].values
            tmp = np.isnan(ET)
            tdiff = np.diff(data.index[~tmp])
            if np.any(tdiff != tdiff[0]):
                raise Exception('Error: Category ET must be regularly sampled!')
        else:
            raise Exception("Error: Specified 'et_method' is not available!")
        # prepare results container with the same index as data
        results = pd.DataFrame(index=data.index)
        # check and loop through GW category
        if gw_locs is None:
            gw_locs = data['GW'].columns
        params = {}
        for loc in gw_locs:
            if loc not in data['GW'].columns:
                raise Exception("Error: GW location '{}' is not available!".format(loc))
                
            print(loc)
            # check and loop through GW category
            GW = data['GW'][loc].values
            tmp = np.isnan(GW)
            tdiff = np.diff(data.index[~tmp])
            if np.any(tdiff != tdiff[0]):
                raise Exception("Error: Location '{}' must be regularly sampled!".format(loc))
            # regress_deconv(self, tf, GW, BP, ET=None, lag_h=24, et=False, et_method='hals', fqs=None):
            results[loc], params[loc] = Analysis.regress_deconv(tf, GW, BP, ET, lag_h=lag_h, et_method=et_method, fqs=fqs)
        return results, params
