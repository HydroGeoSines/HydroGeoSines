# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 08:55:47 2020

@author: Daniel
"""

#TODO! set valid category outside as global variable



import pandas as pd 
import numpy as np

from .time import Time
from .series import Series
#from .filters import Filter

@pd.api.extensions.register_dataframe_accessor("hgs")
class HgsAccessor(object):
    def __init__(self, pandas_obj):
        super().__init__()
        self._validate(pandas_obj)
        self._obj   = pandas_obj
        
    ## setting the datetime property
    @property
    def dt(self):
        return Time(self._obj.datetime)

    @staticmethod
    def _validate(obj):
        # verify there is a column datetime, location, category, unit and value
        if not set(["datetime", "location", "category", "unit","value"]).issubset(obj.columns):
            raise AttributeError("Must have 'datetime',location','category','unit' and 'value'.")    
        
    @property
    def df_obj(self):
        # returns df object columns as list
        return list(self._obj.select_dtypes(include=['object']).columns)
        
    @property
    def freq_median(self):
        # returns median sample frequency grouped by object-dtype columns, in minutes
        df = self._obj[self._obj.value.notnull()]
        return df.groupby(self.df_obj)["datetime"].apply(lambda x: (x.diff(periods=1).dt.seconds.div(60)).median())
    
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
                    
    #%% Open for testing    
    """    
    for attr in VALID_CATEGORY:
        setattr(self,f'get_{attr.lower()}_data', self.func(attr))    
     
    #@staticmethod
    def func(self,category): 
        @property
        def inner():
            return self.__get_category(category)
        return inner  
    
    # general private getter private methods
    def __get_category(self, cat):
        return self.data[self.data['category'] == cat]
    
    @property
    def gw_data(self):
        # return self.data[self.data['category'] == 'GW'].pivot(index='datetime', columns='location', values='value')        
        return self.__get_category('GW').pivot(index='datetime', columns='location', values='value')
    """
    
    
    
    """

    @property
    def dtf(self):
        return Time.dt_num(self.datetime)

    @property
    def dts(self):
        return self.dt_str(self.datetime)
    
    @property
    def dtf_utc(self):
        return self.dt_num(self.datetime, utc=True)
    
    @property
    def dts_utc(self):
        return self.dt_str(self.datetime, utc=True)

    @property
    def spd(self):
        return 86400/self.spl_period(self.datetime, unit='s')

#%% does not belong here and needs to be rewritten
    def is_regular(self, loc: str):
        tmp = self[self['location'] == loc]['datetime']
        tmp = np.diff(self.dt_num(tmp)*86400)
        idx = (tmp != tmp[0])
        if np.any(idx):
            return False
        else:
            return True
    """    
    #%% hgs methods
    
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
    def dt_overlap(self):
        idx = self.data.duplicated(subset='datetime', keep='first')
        return self.data.loc[idx, 'datetime'].reset_index(drop=True)

    @property
    def dt_pivot(self):
        return self.data.pivot(index='datetime', columns=['location'], values='value')

    #def make_regular(self):
    #    tmp = self.dt_pivot
    #    period = Time.spl_period(tmp.index.to_series())
    #    tmp = tmp.resample('{:.0f}S'.format(period)).asfreq()
    #    return tmp
    
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