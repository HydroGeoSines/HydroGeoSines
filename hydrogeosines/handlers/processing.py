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

from .. import utils

class Processing(object):
    # define all class attributes here 
    #attr = attr
    
    def __init__(self, site_obj, et=False):
        self._validate(site_obj)
        self._obj   = site_obj
        self.data = site_obj.data.copy()
    
    @staticmethod
    def _validate(obj):
        if not isinstance(obj,Site):
            raise AttributeError("Must be a 'Site' object!")                       
            #print(id(Site)) # test id of class location to compare across package
    
    ## allow subsetting of Site
    #TODO: implement method to slice site "by_location", e.g hgs.Processing(Site("Freiburg")).by_location("Site_A").BE_method()

    def by_gwloc(self, gw_loc):
        # get idx to subset GW locations
        pos = self._obj.data["location"].isin(np.array(gw_loc).flatten())
        pos_cat = self._obj.data["category"] == "GW"
        # drop all GW locations, but the selected ones
        self.data =  self._obj.data[~(pos_cat & (~pos))].copy()
        return self
        
    def BE_method(self, method:str = "all", derivative=True):
        method_list = utils.method_list(Analysis,ID="BE")
        method_dict = dict(zip(method_list,[i.replace("BE_", "").lower() for i in method_list]))
        #check for non valid method 
        utils.check_affiliation(method, method_dict.values())

        out = {}
        # make GW data regular and align it with BP
        data = self.data.hgs.make_regular()
        data = self.data.hgs.BP_align()
        # check integrity
        #data.hgs.check_BP_align
        data = data.hgs.pivot
        return data

        if any(cat not in data.columns for cat in ("GW","BP")):
            raise Exception('Error: Both BP and GW data is required but not found in the dataset!')
        X = data.hgs.filters.get_bp_values()
        Y = data.hgs.filters.get_gw_values()
            
        return X,Y
        """
        if derivative==True:
           X, Y = np.diff(X), np.diff(Y) # need to also divide by the time step length
          
        # select method
        if method.lower() == 'all':
            for i in range(len(method_list)):
                out[method_names[i]] = getattr(Analysis, method_list[i])(X,Y) 
        else:
            out[method] = getattr(Analysis, method_list[i])(X,Y) 
        if method.lower()=='average_of_ratios':
            out["average_of_ratios"] = Analysis.BE_average_of_ratios(X,Y)
        elif method.lower()=='median_of_ratios':
            result = Analysis.BE_median_of_ratios(X,Y)
        elif method.lower()=='linear_regression':
            result = Analysis.BE_linear_regression(X,Y)
        elif method.lower()=='clark':
            result = Analysis.BE_Clark(X,Y)
        elif method.lower()=='davis_and_rasmussen':
            result = Analysis.BE_Davis_and_Rasmussen(X,Y)
        elif method.lower()=='rahi':
            result = Analysis.BE_Rahi(X,Y)
        elif method.lower()=='rojstczer':
            result = Analysis.BE_Rojstaczer(X,Y)
        else:
            print('BE method does not exist!')
        # TODO: This methods also takes freq + noverlap as parameters. Probably better to move it to another place (different overarching processing method)   
        #elif method.lower()=='quilty and roeloffs':
        #    result = Analysis.BE_Quilty_and_Roeloffs(X,Y, freq, nperseg, noverlap)
        return result       
    	"""
    def hals(self, cat="GW"):
        out = {}
        #check for non valid category 
        utils.check_affiliation(cat, self._obj.VALID_CATEGORY)
        #ET = ET, GW = {ET, AT}, BP = AT 
        comps = Site.comp_select(cat)
        freqs = [i["freq"] for i in comps.values()]
        data  = self.data[self.data.category == cat]  
        grouped = data.groupby(by=data.hgs.filters.obj_col)
        for name, group in grouped:
            #out[name] = comps
            print(name)
            group   = group.hgs.filters.drop_nan
            tf      = group.hgs.dt.to_zero
            values  = group.value.values  
            values  = Analysis.lin_window_ovrlp(tf, values)
            values  = Analysis.harmonic_lsqr(tf, values, freqs)            
            # calculate real Amplitude and Phase
            var = utils.complex_to_real(tf, values["complex"])
            # add results to dictionary
            var["comps"] = list(comps.keys())
            var.update(values)
            out[name] = var

        return out

    def correct_GW(self, gw_locs=None, bp_loc:str=None, et_loc:str=None, lag_h=24, et_method=None, fqs=None):
        print("A complicated procedure ...")
        # first aggregate all the datasets into one
        data = self._obj.data.pivot(index='datetime', columns=['category', 'location'], values='value')
        if 'BP' not in data.columns:
            raise Exception('Error: BP is required but not found in the dataset!')
        if ((et_method is not None) and ('ET' not in data.columns)):
            raise Exception('Error: ET time series is required but not found in the dataset!')
        # apply tests to see if data is regular and complete
        # first, drop any rows with missing values
        if bp_loc is None:
            bp_loc = data['BP'].columns[0]
        if bp_loc not in data['BP'].columns:
            raise Exception("Error: BP location '{}' is not available!".format(bp_loc))
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
            if et_loc is None:
                et_loc = data['ET'].columns[0]
            if et_loc not in data['ET'].columns:
                raise Exception("Error: ET location '{}' is not available!".format(et_loc))
            # first, drop any rows with missing values
            ET = data['ET'][et_loc].values
            tmp = np.isnan(ET)
            tdiff = np.diff(data.index[~tmp])
            if np.any(tdiff != tdiff[0]):
                raise Exception('Error: Category ET must be regularly sampled!')
        else:
            raise Exception("Error: Specified 'et_method' is not available!")
        # prepare results container
        results = pd.DataFrame(index=data.index)
        # loop through GW category
        if gw_locs is None:
            gw_locs = data['GW'].columns
        params = {}
        for loc in gw_locs:
            if loc not in data['GW'].columns:
                raise Exception("Error: GW location '{}' is not available!".format(loc))
                
            print(loc)
            # first, drop any rows with missing values
            GW = data['GW'][loc].values
            tmp = np.isnan(GW)
            tdiff = np.diff(data.index[~tmp])
            if np.any(tdiff != tdiff[0]):
                raise Exception("Error: Location '{}' must be regularly sampled!".format(loc))
            # regress_deconv(self, tf, GW, BP, ET=None, lag_h=24, et=False, et_method='hals', fqs=None):
            values, params[loc] = Analysis.regress_deconv(tf, GW, BP, ET, lag_h=lag_h, et_method=et_method, fqs=fqs)
            results[loc] = values
        return results, params
