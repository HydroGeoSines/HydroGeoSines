import numpy as np
import datetime as dt
import pandas as pd
import pytz
import re
import pygtide

from scipy.interpolate import interp1d
from scipy.optimize import curve_fit

#%% the Earth tide class
class ET(object):
    def __init__(self, site, geoloc=None):
        self.et = None
        self.site = site
        if geoloc is not None:
            if not isinstance(geoloc, (list,pd.core.series.Series,np.ndarray)):
                raise Exception("Error: Input 'geoloc' must have 3 values (longitude, latitude, height)!")
            self.site.geoloc = geoloc
            self.geoloc = geoloc
        else:
            self.geoloc = self.site.geoloc
        pass

    #%%
    def calc(self, datetime, et_comp='pot', et_cat=7):
        if (et_comp == 'pot'):
            et_comp_i = -1
        elif(et_comp == 'g'):
            et_comp_i = 0
        else:
            raise Exception("Error: Keyword 'et_comp' most be 'pot' (potential) or 'g' (gravity)!")

        component = {-1: 'potential', 0: 'gravity'}
        # make sure that the geolocation is appropriately set!
        if (self.geoloc == None):
            raise Exception('Error: Geo-position (longitude, latitude and height) must be set!')

        # import the pygtide dt_utcect
        pt = pygtide.pygtide()
        # convert to UTC and strip of time zone
        dt_utc = datetime.index.tz_convert('UTC').tz_localize(None)
        # define the start date in UTC
        start = dt_utc.min().to_pydatetime()
        duration = ((dt_utc.max() - dt_utc.min()).days + 2)*24
        td = (dt_utc.to_series() - pd.to_datetime('1899-12-30')).dt
        dt_utc_tf = td.days + td.seconds/86400
        dt_utc_s = td.seconds
        # is this correct??
        samplerate = int(np.median(np.diff(dt_utc_s)))
        # set the recommended wave groups
        # as implemented in the wrapper
        pt.set_wavegroup()
        #pt.reset_wavegroup()
        pt.predict(self.geoloc[1], self.geoloc[1], self.geoloc[2], start, duration, samplerate, tidalcompo=et_comp_i, tidalpoten=et_cat)
        # retrieve the results as dataframe
        data = pt.results()
        # convert time to floating point for matching
        td = (data['UTC'] - pd.to_datetime('1899-12-30', utc=True)).dt
        et_utc_tf = td.days + td.seconds/86400
        #% interpolate the Earth tide data (cubic spline)
        #################################################################
        # NEGATIVE VALUE FIXES PHASE REVERSAL ISSUE !!!!!
        et_interp = interp1d(et_utc_tf, -data['Signal [(m/s)**2]'].values, kind='cubic')
        et = et_interp(dt_utc_tf)
        self.data = pd.Series(et, index=datetime.index, name=component[et_comp_i])
        # free up some memory
        del data
        return self.data
        