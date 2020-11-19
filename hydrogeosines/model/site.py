import numpy as np
import datetime as dt
import pandas as pd

from scipy.optimize import leastsq

# import sub-classes
from .read import Read

# import extended DataFrame
from ..ext import hgs_pd
#from .data import Data

from .glob import const

#%% define a class for the investigated site

class Site(Read):
    "Optional class documentation string, can be accessed via Site.__doc__"   
    VALID_CATEGORY = {"ET", "BP", "GW"}
    # define all class attributes here 
    #data_header = ["datetime", "location","category","unit","value"]
    #data_types  = 
    const       = const
    utc_offset  = {}
    
    def __init__(self, name, geoloc=None, data=None,*args, **kwargs):
        super().__init__(*args, **kwargs)
        
        for attr in self.VALID_CATEGORY:
             setattr(self,f'get_{attr.lower()}_data', self.func(attr))    
             
        # The site name
        self._name  = name
        # The Geo-Location
        self.geoloc = geoloc
        # Create a Dataframe from the extended Dataframe class "Data" 
        self.data   = data        

    #@staticmethod
    def func(self,category): 
        @property
        def inner():
            return self.__get_category(category)
        return inner   
    
    @property
    def geoloc(self):
        return self.__geoloc # property of self
        
    @geoloc.setter
    def geoloc(self, geoloc):
        if geoloc is not None:
            if not isinstance(geoloc, (list, np.ndarray)):
                raise Exception("Error: Input 'geoloc' must be a list with 3 values: Longitude, latitude, height in WGS84!")
            if (geoloc[0] < -180) or (geoloc[0] > 180) or (geoloc[1] < -90) or (geoloc[1] > 90) or (geoloc[2] < -1000) or (geoloc[2] > 8500):
                raise Exception("Error: Input 'geoloc' must contain valid geo-coordinates in WGS84!")
            self.__geoloc = geoloc
        else:
            self.__geoloc = None

    @property
    def data(self):
        return self.__data
       
    @data.setter
    def data(self,data):
        if data is None:
            self.__data = pd.DataFrame({"datetime":pd.Series([], dtype="datetime64[ns]"),
                                    "location":pd.Series([], dtype='object'),
                                    "category":pd.Series([], dtype='object'),
                                    "unit":pd.Series([], dtype='object'),
                                    "value":pd.Series([], dtype='float')}) 
            
    #%% slicing
    # inheritance? https://stackoverflow.com/questions/25511436/python-is-is-possible-to-have-a-class-method-that-acts-on-a-slice-of-the-class
    
    def __getitem__(self, index):
        print(index)
        return self[index]

    #%% general private getter private methods
    def __get_category(self, cat):
        return self.data[self.data['category'] == cat]
    
    @property
    def gw_data(self):
        # return self.data[self.data['category'] == 'GW'].pivot(index='datetime', columns='location', values='value')        
        return self.__get_category('GW').pivot(index='datetime', columns='location', values='value')
    
    
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