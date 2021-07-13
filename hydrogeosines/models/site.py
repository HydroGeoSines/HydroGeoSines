import numpy as np
import pandas as pd

# import additional functionalities
from .ext.read import Read
from .ext.et import ET

# import extended pandas DataFrame
from ..ext import pandas_hgs
#from .data import Data

from .const import const

#%% define a class for the investigated site

class Site(Read, ET):
    """Optional class documentation string, can be accessed via Site.__doc__"""
    # define all class attributes here
    VALID_CATEGORY  = {"ET", "BP", "GW"}
    const           = const

    def __init__(self, name, geoloc=None, data=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # The site name
        self._name  = name
        # The Geo-Location
        self.geoloc = geoloc
        # Create a Dataframe from the extended Dataframe class "Data"
        self.data   = data
        # UTC offset
        self.utc_offset = {} # move to instance?

    ## setting the geoloc property
    @property
    def geoloc(self):
        return self._geoloc # property of self

    @geoloc.setter
    def geoloc(self, geoloc):
        if geoloc is not None:
            if not isinstance(geoloc, (list, np.ndarray)):
                raise Exception("Error: Input 'geoloc' must be a list with 3 values: Longitude, latitude, height in WGS84!")
            if (geoloc[0] < -180) or (geoloc[0] > 180) or (geoloc[1] < -90) or (geoloc[1] > 90) or (geoloc[2] < -1000) or (geoloc[2] > 8500):
                raise Exception("Error: Input 'geoloc' must contain valid geo-coordinates in WGS84!")
            self._geoloc = geoloc
        else:
            self._geoloc = None

    ## setting the data property
    @property
    def data(self):
        return self._data

    @data.setter
    def data(self,data):
        if data is None:
            self._data = pd.DataFrame({"datetime": pd.Series([], dtype="datetime64[ns]"),
                                        "category": pd.Series([], dtype='object'),
                                        "location": pd.Series([], dtype='object'), 
                                        "part": pd.Series([], dtype='object'), 
                                        "unit": pd.Series([], dtype='object'), 
                                        "value": pd.Series([], dtype='float')})

        elif isinstance(data, pd.DataFrame):
           # verify the required hgs columns exist and that they are properly formated
           # TODO: add unit test/ automatic conversion and datetime check -> best include in hgs._validate
           data.hgs._validate(data)
           self._data = data
        else:
           raise Exception("Error: Input 'data' must be a pd.DataFrame")

    #%% Site specific functions    
    ## because constants are attributed to site
    @staticmethod
    def freq_select(cat):
        ''' returns a set of unique frequency values for a given input category. For "GW" both et and at frequencies are selected.'''
        freqs = []
        if cat in ("ET","GW"):
            freqs.append(const['_etfqs'].values())
        if cat in ("BP","GW"):
            freqs.append(const['_atfqs'].values())
        #flatten list of lists and return unique values
        return np.array(list(dict.fromkeys([item for sublist in freqs for item in sublist])))

    @staticmethod
    def comp_select(cat):
        nested = {}
        # returns a set of unique frequency values for a given input category
        if cat == "ET":
            comps = const["_etfqs"]
        if cat == "BP":
            comps = const["_atfqs"]
        if cat == "GW":
            comps = {**const["_etfqs"], **const["_atfqs"]}
            
        for key, value in comps.items():
            nested.update({key:{"freq":value}})    
        return nested
