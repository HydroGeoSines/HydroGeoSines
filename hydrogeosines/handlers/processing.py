# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import inspect
import warnings

from ..ext.hgs_analysis import Time_domain, Freq_domain
from ..models.site import Site
from ..models.ext.et import ET_data as etides
#from ...view import View

from .. import utils

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
               
    #TODO!: The method changes the site_obj itself. Maybe add_ET should return a new DataFrame, not self
    def ET_calc(self):
        self._obj.add_ET(et_comp='g')
        self.data = self._obj.data.copy()
    
    def make_regular(self):
        data = self.data
        data = data.hgs.make_regular()
        data = data.hgs.BP_align()
        data.hgs.check_alignment() # check integrity
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
    def BE_time(self, method:str="all", derivative=True, update=False):
        print("Processing BE_time method...")
        name = (inspect.currentframe().f_code.co_name).lower()
        # output dict
        out = {name:{}}
        # get BE Time domain methods
        method_list = utils.method_list(Time_domain, ID="BE")
        method_dict = dict(zip(method_list,[i.replace("BE_", "").lower() for i in method_list]))
        
        print("-------------------------------------------------")
        
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
            # create GW datetime filter for BP data
            datetime = GW.datetime
            filter_gw = bp_data.datetime.isin(datetime)
            BP = bp_data.loc[filter_gw,:].value.values
            GW = GW.value.values
                         
            if derivative==True:
               BP, GW = np.diff(BP), np.diff(GW) # need to also divide by the time step length
               datetime = datetime[1:]
            
            # aggregate data for results container
            data_group = pd.DataFrame(data = {"GW":GW,"BP":BP},index=datetime,columns=["GW","BP"])
            info = {"derivative": derivative}

            # select method            
            if method.lower() == 'all':
                results = dict.fromkeys(method_dict.values())
                for key, val in method_dict.items():
                    results[val] = getattr(Time_domain, key)(BP,GW)                    
                                        
            else: 
                #check for non valid method 
                utils.check_affiliation(method, method_dict.values())
                # pass the data to the right method in Time_domain using the method_dict
                results = {method:getattr(Time_domain, list(method_dict.keys())[list(method_dict.values()).index(method)])(BP,GW)} 
            
            # add results to the out dictionary  
            out[name].update({gw_loc:[results,data_group,info]})
            print("Successfully calculated using method '{}' on GW data from '{}'!".format(method,str(gw_loc)))

        if update:
            utils.dict_update(self.results, out)
            
        return out

    #%%
    def BE_freq(self, method:str = "Rau", freq_method:str='hals', update=False):
        name = (inspect.currentframe().f_code.co_name).lower() 
        info = method.lower()
        print("-------------------------------------------------")
        print("Method: {}".format(name))
        
        if freq_method not in ("hals","fft"):
            raise Exception("Frequency method '{}' is not implemented!".format(freq_method))
        
        if "ET" not in self.data["category"].unique():            
            raise Exception('Error: ET data is required but not found in the dataset!')    
                
        # this method relies on the distinct frequency components
        # M2 and S2
        freqs = {}
        freqs["m2"] = self._obj.const['_etfqs']['M2']
        freqs["s2"] = self._obj.const['_etfqs']['S2']
        max_freq_diff = {"hals": 1e-6, "fft": (freqs["s2"] - freqs["m2"]) / 3}
        mfd = max_freq_diff[freq_method.lower()]
        
        # output dict
        out = {name:{}}

        # !!! check if method results already exist to save time. 
        # Problematic if results was previously calculated without ET -> update can be buggy
        try:
            comps = self.results[freq_method.lower()]
        except KeyError:
            comps = getattr(self, freq_method.lower())(update=update)[freq_method.lower()]
            
        # print("start")
        #loc = [i[:-1] for i in list(comps.keys())]
        #print(dict(loc))
        #print(loc)
        #unique_loc = [tuple(i) for i in np.unique(loc, axis=0)]
        #print(unique_loc)
        
        ## reasamble dict so it only contains the required data
        data_list = [comps[i][0] for i in comps.keys()]
        comps = dict.fromkeys(comps)
        for key,val in zip(comps.keys(),data_list):
            comps[key] = val
        
        # create DataFrame for unique locations/parts
        df = pd.DataFrame.from_dict(comps,orient="index").reset_index().rename(columns={"level_0":"location","level_1":"part","level_2":"category"})
        grouped = df.groupby(by=(["location","part"]))
        for group, val in grouped:
            print("-------------------------------------------------")
            print('Location: {}, Part: {}'.format(group[0], group[1]))
            # print(group)
            complex_dict = {}
            for cat in val.category.unique():
                # print(cat)                
                data = val[val["category"] == cat]    
                            
                for key,freq in freqs.items():
                    # print(key,freq)
                    # for all categories and freq combinations except BP_s2
                    if ((cat != "BP") or (key != "m2")):
                        # print(cat, key)
                        idx, fdiff = utils.find_nearest_idx(np.hstack(data['freq']), freq)
                        if (fdiff < mfd):
                            complex_dict[str(cat)+"_"+ str(key)] = np.hstack(data['complex'])[idx]
                        else:
                            raise Exception("{} component for {} is required, but the closest component is too far away!".format(key.upper(),cat))
            
            #%% BE method by Rau et al. (2020)          
            if method.lower() == 'rau':
                # see if the response amplitude ratio was set previously
                try:
                    amp_ratio = self.results['k_ss_estimate'][group][0]['A_r']
                # if not, use 1
                except:
                    amp_ratio = 1
                    warnings.warn("Attention: Amplitude ratio is required for accurate BE results! Please run method 'K_Ss_estimate(loc='{}', update=True)' before!".format(group[0]))
                
                # print(amp_ratio)
                results = Freq_domain.BE_Rau(complex_dict["BP_s2"],
                                            complex_dict["ET_m2"], 
                                            complex_dict["ET_s2"], 
                                            complex_dict["GW_m2"], 
                                            complex_dict["GW_s2"], amp_ratio=amp_ratio)
                
                out[name].update({group:[results,data,info]})
        
            #%% BE method by Acworth et al. (2016)
            elif method.lower() == 'acworth':
                results = Freq_domain.BE_Acworth(complex_dict["BP_s2"],
                                            complex_dict["ET_m2"], 
                                            complex_dict["ET_s2"], 
                                            complex_dict["GW_m2"], 
                                            complex_dict["GW_s2"],)
                
                out[name].update({group:[results,data,info]})
                
            else:
                raise Exception("The BE method '{}' is not implemented!".format(method.lower()))

        if update:
            utils.dict_update(self.results, out)
        
        return out

    #%%
    def K_Ss_estimate(self, loc:str, method:str=None, scr_len:float=0, case_rad:float=0, scr_rad:float=0, scr_depth:float=0, freq_method:str='hals', update=False):
        name = (inspect.currentframe().f_code.co_name).lower()
        print("-------------------------------------------------")
        print("Method: {}".format(name))
        
        if freq_method not in ("hals","fft"):
            raise Exception("Frequency method '{}' is not implemented!".format(freq_method))
        
        if "ET" not in self.data["category"].unique():            
            raise Exception('Error: ET data is required but not found in the dataset!')    
        else:
            # print('unit check')
            unit = self.data.loc[self.data["category"] == 'ET', 'unit'].unique()
            # print(unit)
            if 'nstr' not in unit:
                raise Exception('Error: Strain units are required for ET data!')
        
        # this method relies on the distinct frequency components
        # M2 and S2
        freqs = {}
        freqs["m2"] = self._obj.const['_etfqs']['M2']
        freqs["s2"] = self._obj.const['_etfqs']['S2']
        max_freq_diff = {"hals": 1e-6, "fft": (freqs["s2"] - freqs["m2"]) / 3}
        mfd = max_freq_diff[freq_method.lower()]
        
        # output dict
        out = {name:{}}
        
        # !!! check if method results already exist to save time. 
        # !!!! check that location exists
        
        # Problematic if results was previously calculated without ET -> update can be buggy
        # print(self.results[freq_method.lower()].keys())
        comps = {}
        if freq_method.lower() in self.results.keys():
            for key, value in self.results[freq_method.lower()].items():
                if key[0] == loc:
                    comps[key] = value
        else:
            comps = getattr(self, freq_method.lower())(loc=loc, update=update)[freq_method.lower()]
            
        if not len(comps):
            comps = getattr(self, freq_method.lower())(loc=loc, update=update)[freq_method.lower()]
        
        if not len(comps):
            raise Exception("Location '{}' does not exist!".format(loc))
            
        # print('Comps:', comps)
        # print("start")
        #loc = [i[:-1] for i in list(comps.keys())]
        #print(dict(loc))
        #print(loc)
        #unique_loc = [tuple(i) for i in np.unique(loc, axis=0)]
        #print(unique_loc)
        
        ## reassemble dict so it only contains the required data
        data_list = [comps[i][0] for i in comps.keys()]
        # print(data_list)
        comps = dict.fromkeys(comps)
        for key,val in zip(comps.keys(),data_list):
            comps[key] = val
        
        # create DataFrame for unique locations/parts
        df = pd.DataFrame.from_dict(comps,orient="index").reset_index().rename(columns={"level_0":"location","level_1":"part","level_2":"category"})
        # print(df)
        grouped = df.groupby(by=(["location","part"]))
        for group, val in grouped:
            print('Location: {}, Part: {}'.format(group[0], group[1]))
            complex_dict = {}
            for cat in val.category.unique():
                # print(cat)                
                data = val[val["category"] == cat]    
                
                for key,freq in freqs.items():
                    # print(key,freq)
                    # for all categories and freq combinations except BP_s2
                    if ((cat != "BP") or (key != "m2")):
                        # print(cat, key)
                        idx, fdiff = utils.find_nearest_idx(np.hstack(data['freq']), freq)
                        if (fdiff < mfd):
                            complex_dict[str(cat)+"_"+ str(key)] = np.hstack(data['complex'])[idx]
                        else:
                            raise Exception("{} component for {} is required, but the closest component is too far away!".format(key.upper(),cat))
            
            #%% determine the phase shift ...
            phase_shift = np.angle(complex_dict["GW_m2"] / complex_dict["ET_m2"])
            
            #%% Negative phase shift: K and Ss estimation by Hsieh et al. (1987)          
            if (method == 'hsieh') or (phase_shift <= 0):
                info = 'hsieh'
                if (scr_len <=0):
                    raise Exception("For method '{}' the screen length (scr_len) must have a valid value!".format(method.lower()))
                if (case_rad <=0):
                    raise Exception("For method '{}' the casing radius (case_rad) must have a valid value!".format(method.lower()))
                if (scr_rad <=0):
                    raise Exception("For method '{}' the screen radius (scr_rad) must have a valid value!".format(method.lower()))
                    
                results = Freq_domain.K_Ss_Hsieh(complex_dict["ET_m2"], complex_dict["GW_m2"], scr_len, case_rad, scr_rad)
                out[name].update({group:[results,data,info]})
                pass
            
            #%% Positive phase shift: K and Ss estimation by Wang (2000)          
            if (method == 'wang') or (phase_shift > 0):
                info = 'wang'
                if (scr_depth <=0):
                    raise Exception("For method '{}' the screen depth (scr_depth) must have a valid value!".format(method.lower()))
                
                results = Freq_domain.K_Ss_Wang(complex_dict["ET_m2"], complex_dict["GW_m2"], scr_depth)
                out[name].update({group:[results,data,info]})
                
        if update:
            utils.dict_update(self.results, out)
        
        return out
    
    #%%
    def fft(self, loc:list=None, update=False):
        #TODO! NOT adviced to use on site.data with non-aligned ET 
        # !!! check for data gaps?
        name = (inspect.currentframe().f_code.co_name).lower()
        print("-------------------------------------------------")
        print("Method: {}".format(name))
        
        # output dict
        out = {name:{}}
        # make dataset regular
        try:
            data = self.data_regular
        except AttributeError:   
            data = self.make_regular().data_regular
            
        gw_data     = data.hgs.filters.get_gw_data         
        categories  = data.category.unique()
        # grouping by location and parts (loc_part)
        grouped = gw_data.groupby(by=gw_data.hgs.filters.loc_part)
        for gw_loc, GW in grouped:
            if (loc is None) or (gw_loc[0] in loc):
                print('Calculating FFT for location: {}'.format(gw_loc[0]))
                # loop through categories
                for cat in categories:
                    ident = (*gw_loc,cat)
                    # print(ident)
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
                    # apply detrending and signal processing
                    values  = Freq_domain.lin_window_ovrlp(tf, values)
                    values  = Freq_domain.fft_comp(tf, values)            
                    # calculate real Amplitude and Phase
                    results = utils.complex_to_real(tf, values["complex"])
                    results["comps"] = list(comps.keys())
                    results.update(values)  
                    #slim data container
                    data_group = pd.DataFrame(data = {cat:group.value.values}, index=group.datetime)
                    # nested output dict with list for [results, data, info]
                    out[name].update({ident:[results,data_group,None]})

        if not len(out[name]):
            raise Exception("Please use at least one valid location for '{}'!".format(name))
            
        if update:
            utils.dict_update(self.results,out)
        
        return out

    #%%
    def hals(self, loc:list=None, update=False):
        #!!! ALLOW DATA GAPS HERE !!!!
        name = (inspect.currentframe().f_code.co_name).lower()
        print("-------------------------------------------------")
        print("Method: {}".format(name))
        # output dict
        out = {name:{}}
        # data                
        data        = self.data
        gw_data     = data.hgs.filters.get_gw_data         
        categories  = data.category.unique()
        # grouping by location and parts (loc_part)
        grouped = gw_data.groupby(by=gw_data.hgs.filters.loc_part)
        for gw_loc, GW in grouped:
            # filter by location, if required
            if (loc is None) or (gw_loc[0] in loc):
                print('Calculating HALS for location: {}'.format(gw_loc[0]))
                # loop through categories
                for cat in categories:
                    ident = (*gw_loc,cat)
                    # print(ident)
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
                    # apply detrending and signal processing
                    values  = Freq_domain.lin_window_ovrlp(tf, values)
                    values  = Freq_domain.harmonic_lsqr(tf, values, freqs)            
                    # calculate real Amplitude and Phase
                    results = utils.complex_to_real(tf, values["complex"])
                    results["comps"] = list(comps.keys())
                    results.update(values)
                    # slim data container
                    data_group = pd.DataFrame(data = {cat:group.value.values}, index=group.datetime)
                    # nested output dict with list for [results, data, info]
                    out[name].update({ident:[results,data_group,None]})
        
        if not len(out[name]):
            raise Exception("Please use at least one valid location for '{}'!".format(name))
        
        if update:
            utils.dict_update(self.results, out)
            
        return out

    #%%
    def GW_correct(self, lag_h=24, et_method:str="ts", fqs=None, update=False):
        name    = (inspect.currentframe().f_code.co_name)
        # print(name)
        sig     = inspect.signature(getattr(Processing,name))
        info    = sig.parameters
        #info = {lag_h}
        #print(sig,info)
        #TODO!: define dictionary with valid et_methods to use the utils.check_affiliation() method
        # output dict
        out = {name:{}}
        
        # make GW data regular and align it with BP
        try:
            data = self.data_regular
        except AttributeError:   
            data = self.make_regular().data_regular            
            data.hgs.check_alignment(cat="BP")
                
        ## check integrity of ET data
        # ET data is already present and needed
        if ((et_method not in(None,"hals")) and ('ET' in self.data["category"].unique())): 
            ## check if et is aligned
            if data.hgs.check_alignment(cat="ET"):                
                et_data = data.hgs.filters.get_et_data
            else:                   
                et_data = etides.calc_ET_align(data,geoloc=self._obj.geoloc)
                print("ET was recalculated and aligned")
        else:
            et_data = None
            #et_data = etides.calc_ET_align(data,geoloc=self._obj.geoloc)
                        
        # extract data categories
        gw_data = data.hgs.filters.get_gw_data
        bp_data = data.hgs.filters.get_bp_data

        grouped = gw_data.groupby(by=gw_data.hgs.filters.loc_part)
        for gw_loc, GW in grouped:   
            print(gw_loc)            
            tf = GW.hgs.dt.to_zero # same results as delta function with utc offset = None
            datetime = GW.datetime
            filter_gw = bp_data.datetime.isin(datetime)           
            BP = bp_data.loc[filter_gw,:].value.values
            if et_method in (None,"hals"):
                ET = None
            elif et_method == 'ts':
                if et_data is None:
                    ET = etides.calc_ET_align(GW,geoloc=self._obj.geoloc)
                    ET = ET.value.values
                else:   
                    filter_gw = et_data.datetime.isin(datetime)
                    ET = et_data.loc[filter_gw,:].value.values
            else:
                raise Exception("Error: Specified 'et_method' is not available!")  
                
            GW = GW.value.values
            WLc, results = Time_domain.regress_deconv(tf, GW, BP, ET, lag_h=lag_h, et_method=et_method, fqs=fqs)
            results["WLc"] = WLc
            # add results to the out dictionary  
            data_group = pd.DataFrame(data = {"GW":GW,"BP":BP,"ET":ET},index=datetime,columns=["GW","BP","ET"])
            out[name].update({gw_loc:[results,data_group,info]})
            
        if update:
            utils.dict_update(self.results,out) 
            
        return out
        