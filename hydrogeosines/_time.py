import numpy as np
import pandas as pd
import pytz

#%% the time class
class time(object):
    # default time base is that of Excel
    dt_base='1899-12-30'

    def __init__(self, utc_offset=0):
        self.utc_offset = utc_offset
        pass
    
    #%%
    @staticmethod
    def _excel2dt(dt_float):
        # attention: the time is rounded to the nearest second
        return (np.datetime64('1899-12-30') + pd.to_timedelta(pd.Series(dt_float), unit='d')).dt.round('1s')
    
    #%%
    @property
    def t(self):
        # convert to UTC and strip time zone offset
        return self.all.index.tz_localize(None).to_series().reset_index(drop=True)
    
    #%% convert to UTC as native 
    def time_utc(self, obj=None):
        if obj is None:
            obj = self.all
        # convert to UTC and strip time zone offset
        return obj.index.tz_convert('UTC').tz_localize(None).to_series()
    
    #%%
    @property
    def utc(self):
        return self.time_utc().reset_index(drop=True)
    
    #%% convert numeric date time into human readable format
    def time_str(self, obj=None, format="%d/%m/%Y %H:%M:%S", utc=False):
        if obj is None:
            obj = self.all
        if utc:
            # convert to UTC and strip time zone offset
            return obj.index.tz_convert('UTC').tz_localize(None).to_series().dt.strftime(format)
        else:
            return obj.index.tz_localize(None).to_series().dt.strftime(format)
        
    #%%
    @property
    def ts(self):
        return self.time_str()
    
    #%%
    def time_float(self, obj=None, utc=False):
        if obj is None:
            obj = self.all
        # calculate time difference to the base
        if utc:
            # convert to UTC and strip time zone offset
            td = (obj.index.tz_convert('UTC').tz_localize(None).to_series() - np.datetime64(self.dt_base)).dt
            return (td.days + td.seconds/86400)
        else:
            # strip time zone offset
            td = (obj.index.tz_localize(None).to_series() - np.datetime64(time.dt_base)).dt
            return (td.days + td.seconds/86400)
        
    #%%
    @property
    def tf(self):
        return self.time_float()
    
    #%%
    # convert numeric date time into human readable format
    def diff_time_float(self, obj=None):
        if obj is None:
            obj = self.all
        return self.time_float().diff()
    
    #%%
    @property
    def dtf(self):
        return self.diff_time_float()
    
    #%%
    @staticmethod
    def utc_offset(obj, unit='h'):
        if (unit == 'h'):
            factor = 3600
        elif(unit == 'm'):
            factor = 60
        elif (unit == 's'):
            factor = 1
        else:
            raise Exception("Error: Unit must be 'h' (hour), 'm' (minute) or 's' (second)!")
        return obj.index[0].to_pydatetime().utcoffset().total_seconds()/factor
    
    #%%
    @property
    def dt_utc(self):
        return self.utc_offset(self.all)
    
    #%%
    # calculate median sampling rate in seconds
    def spl_period(self, obj=None, unit='s'):
        if obj is None:
            obj = self.all
        if (unit == 's'):
            factor = 3600
        elif(unit == 'm'):
            factor = 60
        elif(unit == 'h'):
            factor = 1
        else:
            raise Exception("Error: Time unit must either be 'h' (hour), 'm' (minute) or 's' (second)!")
        return int(np.round(np.median(np.diff(self.tf))*24*factor))

    #%% calculate median sampling rate in seconds
    def spd(self, obj=None):
        if obj is None:
            obj = self
        return int(86400/obj.spl_period(unit='s'))
    
    #%% check if the time series is regularly spaced
    def is_regular(self, obj=None):
        if obj is None:
            obj = self.all
            # round this to acount for time resolution up to one second!
        tmp = np.around(self.diff_time_float(), 6)
        if (np.nanmedian(tmp) == np.nanmin(tmp)):
            return True
        else:
            return False
        
    #%%
    @property
    def regular(self):
        return self.is_regular()
    
    #%%
    def time_shift(self, obj=None, hours=0):
        if obj is None:
            obj = self.all
        # print(self)
        return (obj.index + pd.Timedelta(hours, unit='h')).to_series().reset_index(drop=True)
    
    #%%
    def tz_offset(self, obj=None, hours=0):
        if obj is None:
            obj = self.all
        # print(self)
        obj.index = obj.index.tz_localize(None).tz_localize(tz=pytz.FixedOffset(int(60*hours)))
        return obj.index.to_series().reset_index(drop=True)
    