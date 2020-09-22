import numpy as np
import pandas as pd
import inspect
import re
import pytz
from functools import reduce

from . import _time
from . import _series

from . import _const
const = _const.const

#%% the data handling class
class data(pd.DataFrame, _time.time, _series.series):
    
    def __init__(self, *args, **kwargs):
        # use the __init__ method from DataFrame to ensure
        # that we're inheriting the correct behavior
        super(data, self).__init__(*args, **kwargs)
        self.ET_unit = None
    
    # this method is makes it so our methods return an instance
    # of ExtendedDataFrame, instead of a regular DataFrame
    @property
    def _constructor(self):
        return data
    
    #%%
    @property
    def gw_names(self):
        gw_cols = self.columns.difference(['{BP}', '{ET}'])
        # columns = list(set(self.columns) - set(['{BP}', '{ET}']))
        return gw_cols
    
    #%%
    @property
    def bp(self):
        return self['{BP}']
    
    @property
    def et(self):
        return self['{ET}']
    
    @property
    def gw(self):
        return self[self.gw_names]
    
    #%%
    def combine(self, mode='full', utc_offset=0, et=False):
        if et is True:
            et = self.ET
        if self.BP.main is None:
            raise Exception("Error: Please set the main barometric pressure!")
        print("Try to combine datasets ...")
        # turn datetime to UTC
        datasets = []
        for i, val in enumerate([self.BP.main] + self.GW.data):
            tmp = val.copy()
            tmp.index = tmp.index.tz_convert('UTC')
            datasets.append(tmp)
        
        if (mode == 'full'):
            self.all = reduce(lambda left,right: pd.merge(left,right,on=['datetime'], how='outer'), datasets)
        elif(mode == 'exact'):
            self.all = reduce(lambda left,right: pd.merge(left,right,on=['datetime'], how='inner'), datasets)
        else:
            raise Exception("Error: The combine method '" + mode + "' does not exist!")
        
        # sort the dataframe
        self.all.sort_index(inplace=True)
        # add Earth tides if desired
        if et:
            tmp3 = et.calc(self.all)
            self.all.loc[:, 'et'] = tmp3.values
        # convert to desired time zone
        if (utc_offset != 0):
            self.all.index = self.all.index.tz_convert(tz=pytz.FixedOffset(int(60*utc_offset)))
        del tmp
        return self.all
    