import numpy as np
import datetime as dt
import pandas as pd

# import sub-classes
from .tools.load import Load
from .data import Data

# import global parameters
from .glob import const

#%% define a class for the investigated site

class Site(Load):
    "Optional class documentation string, can be accessed via Site.__doc__"   
    
    # define all class attributes here 
    const   = const

    def __init__(self, name, geoloc=None,*args, **kwargs):
        super().__init__(*args, **kwargs)

        # The site name
        self.name = name
        # The Geo-Location
        self.geoloc = geoloc
        # Create a Dataframe from the extended Dataframe class "Data"
        self.data = Data(columns=["datetime","type","location","value","unit"])

    @property
    def geoloc(self):
        return self.__geoloc # property of self
        
    @geoloc.setter
    def geoloc(self, value):
        if value is not None:
            if not isinstance(value, (list, np.ndarray)):
                raise Exception("Error: Input 'geoloc' must be a list with 3 values: Longitude, latitude, height in WGS84!")
            if (value[0] < -180) or (value[0] > 180) or (value[1] < -90) or (value[1] > 90) or (value[2] < -1000) or (value[2] > 8500):
                raise Exception("Error: Input 'geoloc' must contain valid geo-coordinates in WGS84!")
            self.__geoloc = value
        else:
            self.__geoloc = None
        