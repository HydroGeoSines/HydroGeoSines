import numpy as np
import pandas as pd

# import sub-classes
from .time import Time
from .series import Series

#%% the data handling class
class Data(pd.DataFrame,Time,Series):
    
    # this makes it so our class returns an instance
    # of ExtendedDataFrame, instead of a regular DataFrame
    @property
    def _constructor(self):
        return Data(pd.DataFrame({"datetime":pd.Series([], dtype="datetime64[ns]"),
                                  "location":pd.Series([], dtype='object'),
                                  "category":pd.Series([], dtype='object'),
                                  "unit":pd.Series([], dtype='object'),
                                  "value":pd.Series([], dtype='float')}))
    
    """
    @_constructor.setter
    def _constructor(self, df):
        self.__geoloc = value
        
    def __init__(self, *args, **kwargs):
        df = pd.DataFrame({"datetime":pd.Series([], dtype="datetime64[ns]"),
                           "location":pd.Series([], dtype='object'),
                           "category":pd.Series([], dtype='object'),
                           "unit":pd.Series([], dtype='object'),
                           "value":pd.Series([], dtype='float')}) 

        super().__init__(data = df, *args, **kwargs)
    """     


    @property
    def dtf(self):
        return self.dt_num(self.datetime)

    @property
    def dts(self):
        return self.dt_str(self.datetime)
    
    @property
    def dtf_utc(self):
        return self.dt_num(self.datetime, utc=True)
    
    @property
    def dts_utc(self):
        return self.dt_str(self.datetime, utc=True)

    @property
    def spd(self):
        return 86400/self.spl_period(self.datetime, unit='s')

#%% does not belong here and needs to be rewritten
    def is_regular(self, loc: str):
        tmp = self[self['location'] == loc]['datetime']
        tmp = np.diff(self.dt_num(tmp)*86400)
        idx = (tmp != tmp[0])
        if np.any(idx):
            return False
        else:
            return True
    
