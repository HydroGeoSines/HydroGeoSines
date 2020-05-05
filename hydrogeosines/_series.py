import numpy as np
import datetime as dt
import pandas as pd
import inspect
import re
import pytz

#%% the series class
class series(object):
    def __init__(self, data, results):
        self.data = data
        self.results = results

    #%%
    @property
    def gw(self, obj=None):
        if obj is None:
            obj = self
        columns = list(set(obj.all.columns) - set(['{BP}', '{ET}']))
        return columns
    
    #%%
    def make_regular(self, obj=None):
        if obj is None:
            obj = self
        # print("Try to fill gaps ...")
        # print(obj.spl_period())
        obj.all = obj.all.resample('{:d}S'.format(obj.spl_period())).asfreq()
        # update the time object
        return obj.all
    
    #%%
    def fill_gaps(self, obj=None, limit=1, method='linear'):
        if obj is None:
            obj = self

        # print("Try to fill gaps ...")
        self.all = obj.all.interpolate(limit=limit, method=method)
        # update the time object
        return self.all
    
    #%%
    def kill_gaps(self, obj=None, method='baro'):
        if obj is None:
            obj = self
        # print("Try to kill gaps ...")
        # TO DO HOW TO DROP ROWS WITH NAN VALUES!!!!!
        if (method == 'baro'):
            col2 = obj.all.columns.str.contains('baro', case=False, na=False)
            baro_col = obj.all.columns[col2]
            if (len(baro_col) > 0):
                idx = obj.all[baro_col].isnull().values
                obj.all = obj.all.loc[~idx, :]
        elif(method=='all'):
            obj.all = obj.all.dropna(how='all')
        # update the time object
        obj.t = pd.Series(obj.all.index.values, name='datetime')
        return obj.all
    