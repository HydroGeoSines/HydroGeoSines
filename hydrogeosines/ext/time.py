import numpy as np
import pandas as pd
from pandas.api.types import is_datetime64_any_dtype as is_datetime
import pytz

class Time(object):
    """
    Time is an extension for datetime object
    """
    ## define all class attributes here 
    # Excel origin: includes feb 29th even though it did not exist (Lotus 123 bug)
    dt_xls = "1900-01-01"
    epoch = pd.Timestamp(1970,1,1)
    #Epoch (defined as 1 January 1970 00:00:00 at GMT timezone +00:00 offset). 
    #Epoch is anchored on the GMT timezone and therefore is an absolute point in time.
    
    def __init__(self,datetime):        
        ## add attribute specific to Time here   
        self._validate(datetime)
        self._obj = datetime
    
    @staticmethod
    def _validate(obj):
        if not is_datetime(obj):
            raise AttributeError("Must be a 'datetime64'")
    
    @property
    def is_regular(self):
        tmp = np.diff(self.to_num)
        idx = (tmp != tmp[0])
        if np.any(idx):
            return False
        else:
            return True 
        
    @property    
    def to_num(self):
        delta = (self._obj.dt.tz_localize(None) - self.epoch).dt
        num = delta.days + (delta.seconds / (60*60*24))
        return num.values 
    
    @property
    def to_zero(self):
        t = pd.to_numeric(self._obj)
        t = t - t[0]
        t = t / 10**9 # from ns to seconds
        t = t / (60*60*24) # to days
        return t.values
    
    #only for testing the methods internally
    @property
    def get_timezone(self):
        return self._obj.dt.tz
    
    # what is the correct output of this method?
    @property
    def to_num_xls(self):
        # ATTENTION: the time is rounded to the nearest second. This is due to an interface problem
        # where Excel does not offer sufficient resolution to work in Pandas
        return (np.datetime64(self.dt_xls) + pd.to_timedelta(pd.Series(self.to_num_ext(dt_base = self.dt_xls)), unit='d')).dt.round('1s')
       
    def to_num_ext(self, utc=False, dt_base=None):
        if dt_base == None:
            dt_base = self.epoch
        # calculate time difference to the base
        if utc:
            # convert to UTC and strip time zone offset
            td = (self._obj.dt.tz_convert('UTC').dt.tz_localize(None) - np.datetime64(dt_base)).dt
            return (td.days + td.seconds/86400).values
        else:
            # strip time zone offset
            td = (self._obj.dt.tz_localize(None) - np.datetime64(dt_base)).dt
            return (td.days + td.seconds/86400).values
    
    def to_str(self, utc=False, format="%d/%m/%Y %H:%M:%S"):
        if utc:
            # convert to UTC and strip time zone offset
            return self._obj.dt.tz_convert('UTC').dt.tz_localize(None).dt.strftime(format)
        else:
            return self._obj.dt.tz_localize(None).dt.strftime(format)
        
    def spl_freq(self, unit='s'):
        #all(df.datetime.diff()[1:] == np.timedelta64(1, 's')) == True
        if (unit == 's'):
            factor = 3600
        elif(unit == 'm'):
            factor = 60
        elif(unit == 'h'):
            factor = 1
        else:
            raise Exception("Error: Time unit must either be 'h' (hour), 'm' (minute) or 's' (second)!")
        return np.round(np.median(np.diff(self.to_num))*24*factor)
    
   
    #data.index = pd.to_datetime(data.index.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset))).tz_convert(pytz.utc)) 
    """
    @property
    def dtf_utc(self):
        return self.dt_num(self.datetime, utc=True)
    
    @property
    def dts_utc(self):
        return self.dt_str(self.datetime, utc=True)

    @property
    def spd(self):
        return 86400/self.spl_period(self.datetime, unit='s')
    """
    
    