import numpy as np
import datetime as dt
import pandas as pd

from scipy.optimize import leastsq

# import sub-classes
from .tools.load import Load
from .data import Data
from .tools.time import Time

# import global parameters
from .glob import const

#%% define a class for the investigated site

class dtprop(object):
    pass
    
class Site(Load):
    "Optional class documentation string, can be accessed via Site.__doc__"   
    
    # define all class attributes here 
    const   = const

    def __init__(self, name, geoloc=None,*args, **kwargs):
        super().__init__(*args, **kwargs)

        # The site name
        self.name = name
        # The Geo-Location
        self.geoloc = geoloc
        # Create a Dataframe from the extended Dataframe class "Data"
        self.data = Data(columns=["datetime","dt_num","utc_offset","type","location","value","unit"])

    @property
    def geoloc(self):
        return self.__geoloc # property of self
        
    @geoloc.setter
    def geoloc(self, value):
        if value is not None:
            if not isinstance(value, (list, np.ndarray)):
                raise Exception("Error: Input 'geoloc' must be a list with 3 values: Longitude, latitude, height in WGS84!")
            if (value[0] < -180) or (value[0] > 180) or (value[1] < -90) or (value[1] > 90) or (value[2] < -1000) or (value[2] > 8500):
                raise Exception("Error: Input 'geoloc' must contain valid geo-coordinates in WGS84!")
            self.__geoloc = value
        else:
            self.__geoloc = None

    #%% slicing
    # inheritance? https://stackoverflow.com/questions/25511436/python-is-is-possible-to-have-a-class-method-that-acts-on-a-slice-of-the-class
    
    def __getitem__(self, index):
        print(index)
        return self[index]
    
    #%% GW properties
    @property
    def gw_locs(self):
        return self.data[self.data['type'] == 'GW']['location'].unique()
    
    @property
    def gw_data(self):
        return self.data[self.data['type'] == 'GW'].pivot(index='datetime', columns='location', values='value')
    
    @property
    def gw_dt(self):
        return self.data[self.data['type'] == 'GW']['datetime'].drop_duplicates().reset_index(drop=True)
    
    @property
    def gw_dtf(self):
        return Time.dt_num(self.gw_dt)
    
    @property
    def gw_dts(self):
        return Time.dt_str(self.gw_dt)
    
    @property
    def gw_spd(self):
        return 86400/Time.spl_period(self.gw_dt, unit='s')
    
    #%% BP properties
    @property
    def bp_locs(self):
        return self.data[self.data['type'] == 'BP']['location'].unique()

    @property
    def bp_data(self):
        return self.data[self.data['type'] == 'BP'].pivot(index='datetime', columns='location', values='value')
    
    #%% ET properties
    @property
    def et_locs(self):
        return self.data[self.data['type'] == 'ET']['location'].unique()
    
    @property
    def et_data(self):
        return self.data[self.data['type'] == 'ET'].pivot(index='datetime', columns='location', values='value')

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

    def make_regular(self):
        tmp = self.dt_pivot
        period = Time.spl_period(tmp.index.to_series())
        tmp = tmp.resample('{:.0f}S'.format(period)).asfreq()
        return tmp
    
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
        dt = np.arange(result[0][0], (max_dt_num - min_dt_num)/24/60, result[0][1]/24/60)
        # print(tdata)
        return dt
    
    #%% define methods
    def remove(self, locs):
        if isinstance(locs, str):
            idx = (self.data['location'] == locs)
            print(idx)
            self.data = self.data[~idx]
            # self.data.drop(labels=idx, axis=0, inplace=True)
        if isinstance(locs, list):
            for loc in locs:
                idx = (self.data['location'] == loc)
                self.data = self.data[~idx]
        return self.data

    def drop_nan(self):
        idx = self.data['value'].isnull()
        self.data.drop(self.data.index[idx], inplace=True)
        
        return self.data
        
    #%% SOPHISTICATED DATA ALIGNMENT
    def make_congruent(self, dt_master):
        pass
    
    def regularize(self, method='interp'):
        # https://stackoverflow.com/questions/31977442/scipy-optimize-leastsq-how-to-specify-non-parameters
        # perform a fit to (start, dt) with existing data
        pass