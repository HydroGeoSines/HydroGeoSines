import numpy as np
import datetime as dt
import pandas as pd
import pytz
import re

class GW(object):
    def __init__(self, site):
        self.data = []
        self.site = site
        pass

    # import GW data from file
    def import_csv(self, filepath, dt_col='datetime', dt_fmt='excel'):
        # load the csv file into variable
        filedata = pd.read_csv(filepath)
        # see what columns are available
        cols = filedata.columns.values
        # the new container to use
        data = pd.DataFrame()

        #%% check for valid datetime column
        reg = re.compile('datetime\s*\[UTC([\+\-]+[0-9\.]+)\]', re.IGNORECASE)
        dt_bool = np.array([bool(reg.match(col)) for col in filedata.columns])
        if any(dt_bool):
            dt_col = cols[dt_bool][0]
            utc_offset = float(reg.search(dt_col).group(1))
        else:
            raise Exception('Error: Datetime column must exist and contain UTC offset specified as [UTC+\-hh]!')
        # decide on the date time format
        if (dt_fmt == 'excel'):
            data['datetime'] = site.time._excel2dt(filedata[dt_col])
        else:
            data['datetime'] = pd.to_datetime(filedata[dt_col], format=dt_fmt)

        #%% search for baro columns
        reg = re.compile('(baro\s*)\[([a-zA-Z]+)\]', re.IGNORECASE)
        baro_bool = np.array([bool(reg.match(col)) for col in filedata.columns])

        #%% LOAD GW DATA columns
        gw_cols = filedata.columns[(~dt_bool & ~baro_bool)]
        if (len(gw_cols) > 0):
            for i in range(len(gw_cols)):
                wl = re.compile('(.*)\[([a-zA-Z]+)\]', re.IGNORECASE)
                if (wl.search(gw_cols[i]) == None):
                    raise Exception("Error: All data columns in the CSV file must have units, e.g. [mm]")
                else:
                    if (wl.search(gw_cols[i]).group(2).lower() in self.site._pucf):
                        unit = wl.search(gw_cols[i]).group(2).lower()
                        p_factor = self.site._pucf[unit]
                        name = wl.search(gw_cols[i]).group(1).strip()
                        data[name] = (filedata[gw_cols[i]]*p_factor).rename(level = 0, index=name)

        # create index and sort
        data.set_index('datetime', inplace=True)
        data.index = data.index.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset)))
        data.sort_index(inplace=True)
        # free up some memory
        del filedata
        self.data.append(data)
        return data
