# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 08:55:47 2020

@author: Daniel
"""

#TODO! set valid category outside as global variable

VALID_CATEGORY = {"ET", "BP", "GW"}

import pandas as pd 
import numpy as np

from .time import Time
from .filter import Filter

@pd.api.extensions.register_dataframe_accessor("hgs")
class HgsAccessor(object):
    def __init__(self, pandas_obj):
        self._validate(pandas_obj)
        self._obj = pandas_obj

    @staticmethod
    def _validate(obj):
        # verify there is a column datetime, location, category, unit and value
        if not set(["datetime", "location", "category", "unit","value"]).issubset(obj.columns):
            raise AttributeError("Must have 'datetime',location','category','unit' and 'value'.")
   
    
    
    for attr in self.VALID_CATEGORY:
        setattr(self,f'get_{attr.lower()}_data', self.func(attr))    
     
    #@staticmethod
    def func(self,category): 
        @property
        def inner():
            return self.__get_category(category)
        return inner  
    
    #%% general private getter private methods
    def __get_category(self, cat):
        return self.data[self.data['category'] == cat]
    
    @property
    def gw_data(self):
        # return self.data[self.data['category'] == 'GW'].pivot(index='datetime', columns='location', values='value')        
        return self.__get_category('GW').pivot(index='datetime', columns='location', values='value')
    
    
    
    
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