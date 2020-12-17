# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 08:55:47 2020

@author: Daniel
"""

#TODO! set valid category outside as global variable



import pandas as pd 
import numpy as np

from .time import Time
from .hgs_filters import HgsFilters

@pd.api.extensions.register_dataframe_accessor("hgs")
class HgsAccessor(object):
    def __init__(self, pandas_obj):
        super().__init__()
        self._validate(pandas_obj)
        self._obj   = pandas_obj
    
    @staticmethod
    def _validate(obj):
        #TODO: verify that datetime localization exists (absolut, non-naive datetime)
        #TODO: varify that only valid data categories exist!
        # verify there is a column datetime, location, category, unit and value
        
        if not set(["datetime", "location", "category", "unit","value"]).issubset(obj.columns):
            raise AttributeError("Must have 'datetime',location','category','unit' and 'value'.")               
        
    ## setting datetime as a property and extending it by the Time methods
    @property
    def dt(self):
        return Time(self._obj.datetime)
    
    ## setting filters as a property and extending it by the HgsFilters methods
    @property
    def filters(self):
        return HgsFilters(self._obj)

    @property
    def pivot(self):
        return self._obj.pivot_table(index=self.dt._obj,columns=self.filters.obj_col, values="value")    
    
    #@property
    #def make_regular(self):
    #    tmp = self.pivot
    #    period = self.dt.spl_freq(tmp.index.to_series())
    #    tmp = tmp.resample('{:.0f}S'.format(period)).asfreq()
    #    return tmp  
    
    @property
    def spl_freq_groupby(self):
        # returns median sample frequency grouped by object-dtype columns, in seconds
        df = self._obj[self._obj.value.notnull()]
        return df.groupby(self.filters.obj_col)["datetime"].apply(lambda x: (x.diff(periods=1).dt.seconds).median())
       
    @property
    def check_dublicates(self):
        # search for dublicates (in rows)
        if any(self._obj.duplicated(subset=None, keep='first')):                
            print("Dublicate entries detected and deleted")            
            return self._obj.drop_duplicates(subset=None, keep='first', ignore_index=True)
        else:
            print("No dublicates being found ...")
            return self._obj
    
    def unit_converter_vec(self,unit_dict : dict):  
        # adjust values based on a unit conversion factor dictionary
        return self._obj.value*np.vectorize(unit_dict.__getitem__)(self._obj.unit.str.lower())
    
    def pucf_converter_vec(self,unit_dict : dict): # using vectorization        
        # convert pressure units for GW and BP into SI unit meter        
        idx     = (((self._obj.category == "GW") | (self._obj.category == "BP")) & (self._obj.unit != "m"))
        val     = np.where(idx, self.unit_converter_vec(unit_dict),self._obj.value) 
        unit    = np.where(idx, "m", self._obj.unit) 
        return val, unit    

    def pucf_converter(self,row): # loop based
        # convert pressure units for GW and BP into SI unit meter
        if row["category"] in ("GW", "BP") and row["unit"] != "m":
            return row["value"] * self.const['_pucf'][row["unit"].lower()], "m"
        else:
            return row["value"], "m" 
    
    #TODO: add upsampling method with interpolation based on ffill() and/or pad()
    def upsample(self,freq):
        pass        
 
    def resample(self, freq):
        # resamples by group and by a given frequency in "seconds".
        # should be used on the (calculated) median frequency of the datetime
        out = self._obj.groupby(self.filters.obj_col).resample(str(int(freq))+"S", on="datetime").mean()
        # reorganize index and column structure to match original hgs dataframe
        out = out.reset_index()[self._obj.columns]
        return out
                    
    def resample_by_group(self,freq_groupby):
        #TODO: write validation logic for freq_groupby. It must be same length as len(cat*loc*unit)
        # resample by median for each location and category individually
        out = []
        for i in range(len(freq_groupby)):
            a = self._obj.loc[:,self.filters.obj_col] == freq_groupby.reset_index().loc[i,self.filters.obj_col]
            a = a.values
            a = (a == a[:, [0]]).all(axis=1)                   
            temp = self._obj.iloc[a].groupby(self.filters.obj_col).resample(str(int(freq_groupby[i]))+"S", on="datetime").mean()
            temp.reset_index(inplace=True)
            out.append(temp) 
        out = pd.concat(out,axis=0,ignore_index=True,join="inner",verify_integrity=True) 
        # reorganize index and column structure to match original hgs dataframe
        out = out.reset_index()[self._obj.columns]
        return out     
  
    
    #%% hgs filters    
    """
    #%% GW properties
    @property
    def gw_locs(self):
        return self.data[self.data['category'] == 'GW']['location'].unique()
            
    @property
    def gw_dt(self):
        return self.data[self.data['category'] == 'GW']['datetime'].drop_duplicates().reset_index(drop=True)
    
    #@property
    #def gw_dtf(self):
    #    return Time.dt_num(self.gw_dt)
    
    #@property
    #def gw_dts(self):
    #    return Time.dt_str(self.gw_dt)
    
    #@property
    #def gw_spd(self):
    #    return 86400/Time.spl_period(self.gw_dt, unit='s')
    
    #%% BP properties
    @property
    def bp_locs(self):
        return self.data[self.data['category'] == 'BP']['location'].unique()

    @property
    def bp_data(self):
        return self.data[self.data['category'] == 'BP'].pivot(index='datetime', columns='location', values='value')
    
    #%% ET properties
    @property
    def et_locs(self):
        return self.data[self.data['category'] == 'ET']['location'].unique()
    
    @property
    def et_data(self):
        return self.data[self.data['category'] == 'ET'].pivot(index='datetime', columns='location', values='value')

    @property
    def is_aligned(self):
        tmp = self.data.groupby(by="datetime").count()
        idx = (tmp['location'].values == tmp['location'].values[0])
        if np.all(idx):
            return True
        else:
            return False
    
    @property
    def dt_pivot(self):
        return self.data.pivot(index='datetime', columns=['location'], values='value')

    
    
    @property
    # https://traces.readthedocs.io/en/master/examples.html
    def dt_regular(self):
        cols = len(self.data['location'].unique())
        grouped = self.data.groupby('location')
        rows = grouped.count().max().max()
        tdata = np.empty((rows, cols))
        tdata[:, :] = np.nan
        i = 0
        for name, group in grouped:
            rows = group.shape[0]
            tdata[:rows, i] = group.loc[:, 'dt_num'].values*24*60
            i += 1
            # print(name, group)
        
        # subtract minimum to enable better precision
        min_dt_num = np.min(tdata[0, :])
        max_dt_num = np.min(tdata[-1, :])
        tdata = tdata - min_dt_num
        print(tdata)
        # perform optimisation
        def residuals(params, tdata) :
            # sumvals = np.count_nonzero(np.isfinite(tdata))
            # print(sumvals)
            real = np.empty(())
            model = np.empty(())
            # iterate through columns
            for i in range(0, tdata.shape[1]):
                idx = np.isfinite(tdata[:, i])
                dt_num = tdata[idx, i]
                frac = np.around((dt_num - params[0]) / params[1])
                model = np.hstack((model, params[0] + frac*params[1]))
                # real
                real = np.hstack((real, dt_num))
                
            res = real - model
            print(res)
            return res

        result = leastsq(residuals, x0=(0, 5), args=(tdata))
        print(result)
        out = np.arange(result[0][0], (max_dt_num - min_dt_num)/24/60, result[0][1]/24/60)
        # print(tdata)
        return out
    
        
    #%% SOPHISTICATED DATA ALIGNMENT
    def make_congruent(self, dt_master):
        pass
    
    def regularize(self, method='interp'):
        # https://stackoverflow.com/questions/31977442/scipy-optimize-leastsq-how-to-specify-non-parameters
        # perform a fit to (start, dt) with existing data
        pass
    """
    
    #%% slicing
    # inheritance? https://stackoverflow.com/questions/25511436/python-is-is-possible-to-have-a-class-method-that-acts-on-a-slice-of-the-class
    
    def __getitem__(self, index):
        print(index)
        return self[index]

