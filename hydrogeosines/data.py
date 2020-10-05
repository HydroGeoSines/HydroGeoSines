import numpy as np
import pandas as pd

# import sub-classes
from .tools.processing import Processing
from .tools.analysis import Analysis
from .tools.visualize import Visualize
from .tools.time import Time

#%% the data handling class

class Data(pd.DataFrame,Processing,Analysis,Visualize):
    
    # this method is makes it so our methods return an instance
    # of ExtendedDataFrame, instead of a regular DataFrame
    @property
    def _constructor(self):
        return Data

    @property
    def dtf(self):
        return Time.dt_num(self.datetime)

    @property
    def dts(self):
        return Time.dt_str(self.datetime)
    
    @property
    def dtf_utc(self):
        return Time.dt_num(self.datetime, utc=True)
    
    @property
    def dts_utc(self):
        return Time.dt_str(self.datetime, utc=True)

    @property
    def spd(self):
        return 86400/Time.spl_period(self.datetime, unit='s')

    def is_regular(self, loc: str):
        tmp = self[self['location'] == loc]['datetime']
        tmp = np.diff(Time.dt_num(tmp)*86400)
        idx = (tmp != tmp[0])
        if np.any(idx):
            return False
        else:
            return True

    #%% EXPERIMENTAL
    def dt_pivot(self):
        return self.pivot_table(index="datetime", columns=["type", "location"], values="value")
  