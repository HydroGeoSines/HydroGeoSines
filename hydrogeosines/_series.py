import numpy as np
import datetime as dt
import pandas as pd
import inspect
import re
import pytz

from . import _data

#%% the series class
class series(object):

    def __init__(self, *args, **kwargs):
        super(series, self).__init__(*args, **kwargs)
        pass
    
    # this function helps to assign a new DF to the existing object instance
    def _update_self(self, new):
        if self.shape[0] >= new.shape[0]:
            # decimate dataset
            dix = self.index.difference(new.index)
            print(dix)
            # drop other entries
            self.drop(dix, inplace=True)
        else:
            # expand dataset
            dix = new.index.difference(self.index)
            # print(dix)
            # self.loc[dix, :] = new.loc[dix, :]
            # this is very slow!!!
            for i in dix:
                self.loc[i, :] = new.loc[i, :]
            
        # update all values
        self.sort_index(inplace=True)
        return self
    
    #%% various functions
    def respl(self, period):
        tmp = self.resample('{:d}S'.format(np.round(period))).asfreq()
        self._update_self(tmp)
        return self
    
    def make_regular(self):
        new = self.resample('{:d}S'.format(self.spl_period())).asfreq()
        self._update_self(new)
        return self
    
    #%%
    def decimate(self, factor):
        dix = self.index.difference(self.index[::int(factor)])
        self.drop(dix, inplace=True)
        return self

    def somthing(self):
        self = tmp
        return self
    
    #%%
    def fill_gaps(self, limit=1, method='linear'):
        # print("Try to fill gaps ...")
        self.interpolate(limit=limit, method=method, inplace=True)
        # update the time object
        return self
    
    #%%
    def kill_gaps(self, method='baro'):
        # print("Try to kill gaps ...")
        # TO DO HOW TO DROP ROWS WITH NAN VALUES!!!!!
        if (method == 'baro'):
            col2 = self.columns.str.contains('{BP}', case=False, na=False)
            baro_col = self.columns[col2]
            if (len(baro_col) > 0):
                idx = self[baro_col].isnull().values.flatten()
                print(idx)
                self.drop(self.index[idx], inplace=True)
        elif(method=='any'):
            idx = self.isnull().any(axis=1)
            self.drop(self.index[idx], inplace=True)
        elif(method=='all'):
            self.dropna(how='all', inplace=True)
        else:
            raise Exception("Error: kill_gaps method does not exist!")
        return self
    