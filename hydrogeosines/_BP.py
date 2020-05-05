# external classes
import numpy as np
import datetime as dt
import pandas as pd
import re
import pytz

# own classes
from . import _time

#%% the barometric pressure class
class BP(object):
    def __init__(self, site):
        self.data = []
        self.utc_offset = []
        self.main = None
        self.site = site
        pass
    
    #%%
    def set_main(self, item=0, col=0):
        # get the first entry of the
        tmp = self.data[item].copy()
        tmp = tmp.iloc[:, col]
        tmp.columns = ['baro']
        self.main = tmp
        return self.main

    #%%
    # import GW data from file
    def import_csv(self, filepath, dt_col='datetime', dt_fmt='excel', bp_col='baro'):
        # load the csv file into variable
        filedata = pd.read_csv(filepath)
        # see what columns are available
        cols = filedata.columns.values
        # the new container to use
        data = pd.DataFrame()

        #%% check for valid datetime column
        reg = re.compile('datetime\s*\[UTC([\+\-0-9\.]+)\]', re.IGNORECASE)
        dt_bool = np.array([bool(reg.match(col)) for col in filedata.columns])
        if any(dt_bool):
            dt_col = cols[dt_bool][0]
            utc_offset = float(reg.search(dt_col).group(1))
        else:
            raise Exception('Error: Datetime column must exist and contain UTC offset specified as [UTC+\-hh]!')
        # decide on the date time format
        if (dt_fmt == 'excel'):
            data['datetime'] = _time.time._excel2dt(filedata[dt_col])
        else:
            data['datetime'] = pd.to_datetime(filedata[dt_col], format=dt_fmt)

        #%% search for baro data
        reg = re.compile('(baro\s*)\[([a-zA-Z]+)\]', re.IGNORECASE)
        baro_bool = [bool(reg.match(col)) for col in filedata.columns]
        if any(baro_bool):
            baro_col = cols[baro_bool][0]
            if (reg.search(baro_col).group(2).lower() in self.site._pucf):
                pconv = self.site._pucf[reg.search(baro_col).group(2).lower()]
            else:
                raise Exception("Error: The Baro unit '" + reg.search(baro_col).group(2) + "' is unknown.")
        else:
            raise Exception('Error: A baro column and unit must be specific as [xx]!')
        data['baro'] = filedata[baro_col]*pconv

        # create index and sort
        data.set_index('datetime', inplace=True)
        data.index = data.index.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset)))
        data.sort_index(inplace=True)
        # free up some memory
        del filedata
        self.data.append(data)
        self.utc_offset.append(utc_offset)
        return data