import numpy as np
import pandas as pd
import pytz

class Time(object):
    """
    Time is an extension for datetime object
    """
    ## define all class attributes here 
    # default time base is that of Excel
    dt_base = "1899-12-30"
    
    def __init__(self,datetime):        
        ## add attribute specific to Time here   
        self._validate(datetime)
        self._obj = datetime
    
    @staticmethod
    def _validate(obj):
        isinstance(obj.dtype,'datetime64[ns]')
        
    @property
    def is_what(self):
        print(self._obj)

    @property
    def to_float(self):
        return self.dt_num(self._obj)
    
    @property
    def to_zero(self):
        t = pd.to_numeric(self._obj)
        t = t - t[0]
        t = t/ 10**9 # from ns to seconds
        t = t/(60*60*24) # to days
        return t
    
    @staticmethod
    def _excel2dt(dt_float):
        # ATTENTION: the time is rounded to the nearest second. This is due to an interface problem
        # where Excel does not offer sufficient resolution to work in Pandas
        return (np.datetime64(Time.dt_base) + pd.to_timedelta(pd.Series(dt_float), unit='d')).dt.round('1s')
       
    def to_num(self, utc=False, dt_base=None):
        if dt_base == None:
            dt_base = Time.dt_base
        # calculate time difference to the base
        if utc:
            # convert to UTC and strip time zone offset
            td = (self.datetime.dt.tz_convert('UTC').dt.tz_localize(None) - np.datetime64(dt_base)).dt
            return (td.days + td.seconds/86400)
        else:
            # strip time zone offset
            td = (self.datetime.dt.tz_localize(None) - np.datetime64(dt_base)).dt
            return (td.days + td.seconds/86400)
    

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
           
    #data.index = pd.to_datetime(data.index.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset))).tz_convert(pytz.utc)) 
    @staticmethod
    def dt_str(dt, format="%d/%m/%Y %H:%M:%S", utc=False):
        if utc:
            # convert to UTC and strip time zone offset
            return dt.dt.tz_convert('UTC').dt.tz_localize(None).dt.strftime(format)
        else:
            return dt.dt.tz_localize(None).dt.strftime(format)
    