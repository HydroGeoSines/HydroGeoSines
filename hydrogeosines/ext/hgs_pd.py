# -*- coding: utf-8 -*-
"""
Created on Thu Nov 19 08:55:47 2020

@author: Daniel
"""

import pandas as pd 

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
    
    @property
    def df_obj(self):
        # returns df object columns as list
        return list(self._obj.select_dtypes(include=['object']).columns)
        
    @property
    def freq_median(self):
        # returns median sample frequency grouped by object-dtype columns, in minutes
        df = self._obj[self._obj.value.notnull()]
        return df.groupby(self.df_obj)["datetime"].apply(lambda x: (x.diff(periods=1).dt.seconds.div(60)).median())
    

