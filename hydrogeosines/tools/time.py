import numpy as np
import pandas as pd
import pytz

class Time(object):

    # default time base is that of Excel
    dt_base = "1899-12-30"

    #%%
    @staticmethod
    def _excel2dt(dt_float):
        # ATTENTION: the time is rounded to the nearest second. This is due to an interface problem
        # where Excel does not offer sufficient resolution to work in Pandas
        return (np.datetime64('1899-12-30') + pd.to_timedelta(pd.Series(dt_float), unit='d')).dt.round('1s')
    
    @staticmethod
    def dt_num(ds, utc=False, dt_base=None):
        # calculate time difference to the base
        if utc:
            # convert to UTC and strip time zone offset
            td = (ds.dt.tz_convert('UTC').dt.tz_localize(None) - np.datetime64(Time.dt_base)).dt
            return (td.days + td.seconds/86400)
        else:
            # strip time zone offset
            td = (ds.dt.tz_localize(None) - np.datetime64(Time.dt_base)).dt
            return (td.days + td.seconds/86400)
        
    @staticmethod
    def dt_str(ds, format="%d/%m/%Y %H:%M:%S", utc=False):
        if utc:
            # convert to UTC and strip time zone offset
            return ds.dt.tz_convert('UTC').dt.tz_localize(None).dt.strftime(format)
        else:
            return ds.dt.tz_localize(None).dt.strftime(format)
    
    @staticmethod
    def spl_period(ds, unit='s'):
        if (unit == 's'):
            factor = 3600
        elif(unit == 'm'):
            factor = 60
        elif(unit == 'h'):
            factor = 1
        else:
            raise Exception("Error: Time unit must either be 'h' (hour), 'm' (minute) or 's' (second)!")
        return np.round(np.median(np.diff(Time.dt_num(ds).values))*24*factor)