# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import datetime as dt # this should probably not be added in here. Generally loaded in site through hgs
import os, sys
import warnings

from ..ext.hgs_analysis import Analysis
from ..models.site import Site
#from ...view import View

from .. import utils

from ..models import const

class Processing(object):
    # define all class attributes here
    #attr = attr

    def __init__(self, site_obj, et=False):
        self._validate(site_obj)
        self._obj   = site_obj
        self.data = site_obj.data.copy()

    @staticmethod
    def _validate(obj):
        if not isinstance(obj, Site):
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
    
    def fft(self, cat, loc, length=3, freqs=None):
        min_duration = 60
        min_splrate = 12
        utils.check_affiliation(cat, self._obj.VALID_CATEGORY)
        if loc not in self._obj.data_pivot[cat].columns:
            raise Exception("Category '{}' and location '{}' set is not available!".format(cat, loc))
        if freqs is None:
            freqs = Site.freq_select(cat)
        if (length is None):
            length = 3
        values = self._obj.data_pivot[cat][loc].values
        tmp = np.isnan(values)
        tdelta = (self._obj.data_pivot.index[~tmp].tz_localize(None) - self._obj.data_pivot.index[~tmp].tz_localize(None)[0])
        tf = (tdelta.days + (tdelta.seconds / (60*60*24)))
        if (tf.max() - tf.min() < min_duration):
            raise Exception("The record duration for category {} and location {} must be at least {:.0f} days for this analysis!".format(cat, loc, min_duration))
        if (len(tf)/(tf.max() - tf.min()) < min_splrate):
            raise Exception("The average sampling rate for category {} and location {} must be at least {:.0f} samples per hour for this analysis!".format(cat, loc, min_splrate))
        if (length > 0):
            values_detr = Analysis.lin_window_ovrlp(tf, values, length)
        else:
            values_detr = values
        values_fft  = Analysis.fft_comp(tf, values_detr)
        if loc not in self._obj.results[cat]:
            self._obj.results[cat] = {loc: {}}
        self._obj.results[cat][loc] = {'FFT': {'y_detrend':  values_detr}}
        self._obj.results[cat][loc]['FFT'].update(values_fft)
        return

    #%% calculate BE using frequency-domain approaches
    def BE_freq(self, method='rau', gw_locs=None, bp_loc:str=None, et_loc:str=None, freq_method:str='hals', update=False):
        
        data = self._obj.data.pivot(index='datetime', columns=['category', 'location'], values='value')
        
        #%% select BP and perform
        if 'BP' not in data.columns:
            raise Exception('Error: BP is required but not found in the dataset!')
        # if no locations are listed, use deafult values
        if bp_loc is None:
            bp_loc = data['BP'].columns[0]
        if et_loc is None:
            et_loc = data['ET'].columns[0]
        if gw_locs is None:
            gw_locs = data['GW'].columns

        #%%
        # define the required frequency values in cpd
        m2_freq = self._obj.const['_etfqs']['M2']
        s2_freq = self._obj.const['_etfqs']['S2']
        be_results = {}
        if (freq_method == 'hals'):
            if (bp_loc not in self._obj.results['BP']) or ('HALS' not in self._obj.results['BP'][bp_loc]) or update:
                self.hals('BP', bp_loc)

            if (not et_loc in self._obj.results['ET']) or (not 'HALS' in self._obj.results['ET'][et_loc]) or update:
                self.hals('ET', et_loc)

            for gw_loc in gw_locs:
                if gw_loc not in data['GW'].columns:
                    raise Exception("Category 'GW' location '{}' is not available!".format(gw_loc))
                if (not gw_loc in self._obj.results['GW']) or (not 'HALS' in self._obj.results['GW'][gw_loc]) or update:
                    self.hals('GW', gw_loc)

            # find all the relevant dictionary keys and indices ...
            bp_s2_idx = list(self._obj.results['BP'][bp_loc]['HALS']['freqs']).index(s2_freq)
            bp_s2 = self._obj.results['BP'][bp_loc]['HALS']['comps'][bp_s2_idx]
            et_m2_idx = list(self._obj.results['ET'][et_loc]['HALS']['freqs']).index(m2_freq)
            et_m2 = self._obj.results['ET'][et_loc]['HALS']['comps'][et_m2_idx]
            et_s2_idx = list(self._obj.results['ET'][et_loc]['HALS']['freqs']).index(s2_freq)
            et_s2 = self._obj.results['ET'][et_loc]['HALS']['comps'][et_s2_idx]
            gw_m2_idx = list(self._obj.results['GW'][gw_loc]['HALS']['freqs']).index(m2_freq)
            gw_m2 = self._obj.results['GW'][gw_loc]['HALS']['comps'][gw_m2_idx]
            gw_s2_idx = list(self._obj.results['GW'][gw_loc]['HALS']['freqs']).index(s2_freq)
            gw_s2 = self._obj.results['GW'][gw_loc]['HALS']['comps'][gw_s2_idx]
            print(bp_s2_idx)

        elif (freq_method == 'fft'):
            if (bp_loc not in self._obj.results['BP']) or ('FFT' not in self._obj.results['BP'][bp_loc]) or update:
                self.fft('BP', bp_loc)

            if (not et_loc in self._obj.results['ET']) or (not 'FFT' in self._obj.results['ET'][et_loc]) or update:
                self.fft('ET', et_loc)

            for gw_loc in gw_locs:
                if gw_loc not in data['GW'].columns:
                    raise Exception("Category 'GW' location '{}' is not available!".format(gw_loc))
                if (not gw_loc in self._obj.results['GW']) or (not 'FFT' in self._obj.results['GW'][gw_loc]) or update:
                    self.fft('GW', gw_loc)

            # find all the relevant dictionary keys and indices ...
            bp_s2_idx = Tools.find_nearest_idx(self._obj.results['BP'][bp_loc]['FFT']['freqs'], s2_freq)
            bp_s2 = self._obj.results['BP'][bp_loc]['FFT']['comps'][bp_s2_idx]
            et_m2_idx = Tools.find_nearest_idx(self._obj.results['ET'][et_loc]['FFT']['freqs'], m2_freq)
            et_m2 = self._obj.results['ET'][et_loc]['FFT']['comps'][et_m2_idx]
            et_s2_idx = Tools.find_nearest_idx(self._obj.results['ET'][et_loc]['FFT']['freqs'], s2_freq)
            et_s2 = self._obj.results['ET'][et_loc]['FFT']['comps'][et_s2_idx]
            gw_m2_idx = Tools.find_nearest_idx(self._obj.results['GW'][gw_loc]['FFT']['freqs'], m2_freq)
            gw_m2 = self._obj.results['GW'][gw_loc]['FFT']['comps'][gw_m2_idx]
            gw_s2_idx = Tools.find_nearest_idx(self._obj.results['GW'][gw_loc]['FFT']['freqs'], s2_freq)
            gw_s2 = self._obj.results['GW'][gw_loc]['FFT']['comps'][gw_s2_idx]

        else:
            raise Exception("The frequency-domain method '{}' is not available!".format(freq_method))

        #%% select the method
        if (method == 'rau'):
            # Calculate BE values
            # Equation 9, Rau et al. (2020), doi:10.5194/hess-24-6033-2020
            GW_ET_s2 = (gw_m2 / et_m2) * et_s2
            GW_AT_s2 = gw_s2 - GW_ET_s2
            # a phase check ...
            GW_ET_m2_dphi = np.angle(gw_m2 / et_m2)

            if (np.abs(GW_ET_m2_dphi) > 5):
                warnings.warn("Attention: The phase difference between GW and ET is {.1f}°. BE could be affected by amplitude damping!".format(np.degrees(GW_ET_m2_dphi)))

            BE = np.abs(GW_AT_s2 / bp_s2)
            be_results[gw_loc] = {'BE': BE}

        #%%
        elif (method == 'acworth'):
            # Calculate BE values
            # Equation 4, Acworth et al. (2016), doi:10.1002/2016GL071328
            BE = (np.abs(gw_s2)  + np.abs(et_s2) * np.cos(np.angle(bp_s2) - np.angle(et_s2)) * (np.abs(gw_m2) / np.abs(et_m2))) / np.abs(bp_s2)
            be_results[gw_loc] = {'BE': BE}
            # provide a user warning ...
            if (np.abs(gw_m2) > np.abs(gw_s2)):
                warnings.warn("Attention: There are significant ET components present in the GW data. Please use the 'rau' method for more accurate results!")

        else:
            raise Exception("The method '{}' is not available!".format(method))

        return be_results


    #%% Correct GW heads using BRF-based analysis
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

            # check and loop through GW category
            print("Working on location '{}' ...".format(loc))
            GW = data['GW'][loc].values
            tmp = np.isnan(GW)
            tdiff = np.diff(data.index[~tmp])
            if np.any(tdiff != tdiff[0]):
                raise Exception("Error: Location '{}' must be regularly sampled!".format(loc))
            # regress_deconv(self, tf, GW, BP, ET=None, lag_h=24, et=False, et_method='hals', fqs=None):
            results[loc], params[loc] = Analysis.regress_deconv(tf, GW, BP, ET, lag_h=lag_h, et_method=et_method, fqs=fqs)
        return results, params

    #%% calculate BE using time-domain approaches
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
