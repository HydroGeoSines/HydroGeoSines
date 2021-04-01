# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import datetime as dt # this should probably not be added in here. Generally loaded in site through hgs
import os, sys
import inspect

from ..ext.hgs_analysis import Time_domain, Freq_domain
from ..models.site import Site
#from ...view import View

from .. import utils
from ..models.const import const

class Processing(object):
    # define all class attributes here 
    #attr = attr
    
    def __init__(self, site_obj):
        self._validate(site_obj)
        self._obj       = site_obj
        self.data       = site_obj.data.copy()
        self.results    = {}
    
    @staticmethod
    def _validate(obj):
        # check if object is of class Site
        if not isinstance(obj,Site):
            raise AttributeError("Must be a 'Site' object!")                       
            #print(id(Site)) # test id of class location to compare across package
        # check if both BP and GW exist    
        if any(cat not in obj.data["category"].unique() for cat in ("GW","BP")):            
            raise Exception('Error: Both BP and GW data is required but not found in the dataset!')
        # check for non valid categories
        utils.check_affiliation(obj.data["category"].unique(), obj.VALID_CATEGORY)
              
    """
    def results_update(self, name, results, update:bool = False):
        if (not name in self.results):
            self.results[name] = results
        if (not name in self.results[name]) or (update):
            print('UPDATE')
            self.results[name].update({name: results})
    """    
    #def ET_calc(self):
    #    self.data = acworth_site.add_ET(et_comp='g')
    
    def make_regular(self):
        data = self.data
        data = data.hgs.make_regular()
        data = data.hgs.BP_align()
        data.hgs.check_BP_align # check integrity
        self.data_regular = data
        return self
    
    def by_gwloc(self, gw_loc):
        # get idx to subset GW locations
        pos = self._obj.data["location"].isin(np.array(gw_loc).flatten())
        if pos.eq(False).all():
            raise Exception("Error: Non of the specified locations are present in the GW data!")

        pos_cat = self._obj.data["category"] == "GW"
        # drop all GW locations, but the selected ones
        self.data =  self._obj.data[~(pos_cat & (~pos))].copy()
        return self

    #%% 
    def BE_time(self, method:str = "all", derivative=True, update=False):
        name = (inspect.currentframe().f_code.co_name).lower()
        # output dict
        out = {}
        # get BE Time domain methods
        method_list = utils.method_list(Time_domain, ID="BE")
        method_dict = dict(zip(method_list,[i.replace("BE_", "").lower() for i in method_list]))

        # make GW data regular and align it with BP
        try:
            data = self.data_regular
        except AttributeError:   
            data = self.make_regular().data_regular

        # extract data categories
        gw_data = data.hgs.filters.get_gw_data
        bp_data = data.hgs.filters.get_bp_data
        
        grouped = gw_data.groupby(by=gw_data.hgs.filters.loc_part)
        for gw_loc, GW in grouped:          
            print(gw_loc)
            # create GW datetime filter for BP data
            filter_gw = bp_data.datetime.isin(GW.datetime)
            BP = bp_data.loc[filter_gw,:].value.values
            GW = GW.value.values
                         
            if derivative==True:
               BP, GW = np.diff(BP), np.diff(GW) # need to also divide by the time step length
                   
            # select method            
            if method.lower() == 'all':
                out[gw_loc[0]] = {gw_loc[1]:{name:dict.fromkeys(method_dict.values())}}
                for key, val in method_dict.items():
                    print(val)
                    result = getattr(Time_domain, key)(BP,GW) 
                    out[gw_loc[0]][gw_loc[1]][name][val] = result

            else: 
                #check for non valid method 
                utils.check_affiliation(method, method_dict.values())
                # pass the data to the right method
                result = getattr(Time_domain, list(method_dict.keys())[list(method_dict.values()).index(method)])(BP,GW) 
                out[gw_loc[0]] = {gw_loc[1]:{name:{method:result}}}

        if update:
            utils.dict_update(self.results, out)
            
        return out

    #%%
    def BE_freq(self, method:str = "Rau", freq_method:str='hals', update=False):
        name = (inspect.currentframe().f_code.co_name).lower()
        
        f_m2 = const['_etfqs']['M2']
        f_s2 = const['_etfqs']['S2']
        
        # output dict
        out = {}
        
        # for FFT, dataset needs to be regular!
        if freq_method.lower() == 'fft':
            # calculate the maximum frequency difference threshold based on the 
            # difference between S2 and M2. This allows best identification if a 
            # dataset has sufficient resolution
            max_freq_diff = (f_s2 - f_m2) / 3
            # make GW data regular and align it with BP
            try:
                data = self.data_regular
            except AttributeError:   
                data = self.make_regular().data_regular
            
            # perform FFT
            # !!! check if this exists to save time
            comps = self.fft(update=update)
            
        elif freq_method.lower() == 'hals':
            # this threshold is hard coded and makes sure that 
            # the right frequency components are availble to use this method
            max_freq_diff = 0.00001
            data = self.data
            # perform HALS
            # !!! check if this exists to save time
            comps = self.hals(update=update)
        else:
            raise Exception("Frequency method '{}' is not implemented!".format(freq_method))
        
        # extract data categories
        for loc in comps.keys():       
            for part, vals in comps[loc].items():
                # extract the complex frequency components
                idx, fdiff = utils.find_nearest_idx(vals[freq_method.lower()]['BP']['freq'], f_s2)
                if (fdiff < max_freq_diff):
                    BP_s2 = vals[freq_method.lower()]['BP']['complex'][idx]
                else:
                    raise Exception("S2 component for BP is required but closest component is too far away!")
                
                idx, fdiff = utils.find_nearest_idx(vals[freq_method.lower()]['ET']['freq'], f_s2)
                if (fdiff < max_freq_diff):
                    ET_s2 = vals[freq_method.lower()]['ET']['complex'][idx]
                else:
                    raise Exception("S2 component for ET is required but closest component is too far away!")
                
                idx, fdiff = utils.find_nearest_idx(vals[freq_method.lower()]['ET']['freq'], f_m2)
                if (fdiff < max_freq_diff):
                    ET_m2 = vals[freq_method.lower()]['ET']['complex'][idx]
                else:
                    raise Exception("M2 component for ET is required but closest component is too far away!")
                
                idx, fdiff = utils.find_nearest_idx(vals[freq_method.lower()]['GW']['freq'], f_s2)
                if (fdiff < max_freq_diff):
                    GW_s2 = vals[freq_method.lower()]['GW']['complex'][idx]
                else:
                    raise Exception("S2 component for GW is required but closest component is too far away!")
                
                idx, fdiff = utils.find_nearest_idx(vals[freq_method.lower()]['GW']['freq'], f_m2)
                if (fdiff < max_freq_diff):
                    GW_m2 = vals[freq_method.lower()]['GW']['complex'][idx]
                else:
                    raise Exception("M2 component for GW is required but closest component is too far away!")
                        
                #%% BE method by Rau et al. (2020)          
                if method.lower() == 'rau':
                    result = Freq_domain.BE_Rau(BP_s2, ET_m2, ET_s2, GW_m2, GW_s2, amp_ratio=1)
                    print(result)
                    
                    out.update({loc: {part: {name: {method: result}}}})
            
                #%% BE method by Acworth et al. (2016)
                elif method.lower() == 'acworth':
                    result = Freq_domain.BE_Acworth(BP_s2, ET_m2, ET_s2, GW_m2, GW_s2)
                    print(result)
                    
                    out.update({loc: {part: {name: {method: result}}}})
                else:
                    raise Exception("The BE method '{}' is not implemented!".format(method.lower()))

        if update:
            utils.dict_update(self.results, out)
        
        return out

    #%%
    def fft(self, update = False):
        name = (inspect.currentframe().f_code.co_name).lower()
        # output dict
        out = {}
        # make dataset regular
        try:
            data = self.data_regular
        except AttributeError:   
            data = self.make_regular().data_regular
        # data                
        data        = self.data
        gw_data     = data.hgs.filters.get_gw_data         
        categories  = data.category.unique()
        # grouping by location and parts (loc_part)
        grouped = gw_data.groupby(by=gw_data.hgs.filters.loc_part)
        for gw_loc, GW in grouped:
            print(gw_loc)
            # initiate output dict structure             
            out[gw_loc[0]] = {gw_loc[1]:{name:dict.fromkeys(categories)}}
            # loop through categories
            for cat in categories:
                print(cat)
                #ET = ET, GW = {ET, AT}, BP = AT 
                comps = Site.comp_select(cat)
                if cat != "GW":                                                        
                    group = getattr(data.hgs.filters, utils.join_tuple_string(("get",cat.lower(),"data")))
                    filter_gw = group.datetime.isin(GW.datetime)
                    group = group.loc[filter_gw,:]
                else: 
                    group = GW
                
                group   = group.hgs.filters.drop_nan
                tf      = group.hgs.dt.to_zero
                values  = group.value.values  
                values  = Freq_domain.lin_window_ovrlp(tf, values)
                values  = Freq_domain.fft_comp(tf, values)            
                # calculate real Amplitude and Phase
                var = utils.complex_to_real(tf, values["complex"])
                # add results to dictionary
                var["comps"] = list(comps.keys())
                var.update(values)
                # nested output dict with location, method, category
                out[gw_loc[0]][gw_loc[1]][name][cat] = var
        
        if update:
            utils.dict_update(self.results,out)
            
        return out

    #%%
    def hals(self, update = False):
        name = (inspect.currentframe().f_code.co_name).lower()
        # output dict
        out = {}
        # data                
        data        = self.data
        gw_data     = data.hgs.filters.get_gw_data         
        categories  = data.category.unique()
        # grouping by location and parts (loc_part)
        grouped = gw_data.groupby(by=gw_data.hgs.filters.loc_part)
        for gw_loc, GW in grouped:
            print(gw_loc)
            # initiate output dict structure             
            out[gw_loc[0]] = {gw_loc[1]:{name:dict.fromkeys(categories)}}
            # loop through categories
            for cat in categories:
                print(cat)
                #ET = ET, GW = {ET, AT}, BP = AT 
                comps = Site.comp_select(cat)
                freqs = [i["freq"] for i in comps.values()]
                if cat != "GW":                                                        
                    group = getattr(data.hgs.filters, utils.join_tuple_string(("get",cat.lower(),"data")))
                    filter_gw = group.datetime.isin(GW.datetime)
                    group = group.loc[filter_gw,:]
                else: 
                    group = GW
                
                group   = group.hgs.filters.drop_nan
                tf      = group.hgs.dt.to_zero
                values  = group.value.values  
                values  = Freq_domain.lin_window_ovrlp(tf, values)
                values  = Freq_domain.harmonic_lsqr(tf, values, freqs)            
                # calculate real Amplitude and Phase
                var = utils.complex_to_real(tf, values["complex"])
                # add results to dictionary
                var["comps"] = list(comps.keys())
                var.update(values)
                # nested output dict with location, method, category
                out[gw_loc[0]][gw_loc[1]][name][cat] = var
        
        if update:
            utils.dict_update(self.results,out)
            
        return out

    #%%
    def GW_correct(self, lag_h=24, et_method:str = "ts", fqs=None, update=False):
        name = (inspect.currentframe().f_code.co_name).lower()
        print("A complicated procedure ...")
        #TODO!: either adapt the BP_align to also align ET data or implement ET calc in Site to be used after bp_align (better!!)
        #TODO!: define dictionary with valid et_methods to use the utils.check_affiliation() method
        # output dict
        out = {}
        
        # check integrity of data
        if ((et_method is not None) and ('ET' not in self.data["category"].unique())):
            raise Exception('Error: ET time series is required but not found in the dataset!')
            
        # make GW data regular and align it with BP
        try:
            data = self.data_regular
        except AttributeError:   
            data = self.make_regular().data_regular
            
        #data.hgs.check_align(cat=ET)

        # extract data categories
        gw_data = data.hgs.filters.get_gw_data
        bp_data = data.hgs.filters.get_bp_data
        if et_method != None:
            et_data = data.hgs.filters.get_et_data
            #acworth_site.add_ET(et_comp='g')

        grouped = gw_data.groupby(by=gw_data.hgs.filters.loc_part)
        for gw_loc, GW in grouped:   

            print(gw_loc)
            
            out[gw_loc[0]] = {gw_loc[1]:{name:None}}

            tf = GW.hgs.dt.to_zero # same results as delta function with utc offset = None
            filter_gw = bp_data.datetime.isin(GW.datetime)
            BP = bp_data.loc[filter_gw,:].value.values
            if et_method in (None,"hals"):
                ET = None
            elif et_method == 'ts':
                ET = et_data.loc[filter_gw,:].value.values

            else:
                raise Exception("Error: Specified 'et_method' is not available!")    
            GW = GW.value.values
            
            #raise Exception('Error: Category ET must be regularly sampled!')

            WLc, var = Time_domain.regress_deconv(tf, GW, BP, ET, lag_h=lag_h, et_method=et_method, fqs=fqs)
            var["WLc"] = WLc
            out[gw_loc[0]][gw_loc[1]][name] = var
            
        if update:
            utils.dict_update(self.results,out) 
        return out
