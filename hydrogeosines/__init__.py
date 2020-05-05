#%% hydrogeoscience under development
from types import MethodType
import numpy as np
import datetime as dt
import pandas as pd
import inspect
import re
import pytz

# import other sub-classes
from . import _time
from . import _BP
from . import _GW
from . import _ET
from . import _data
from . import _results#
from . import _model
    
# from . import models
# https://code.activestate.com/recipes/577504/

class site(object):
    
    # generally accessible constants
    # pressure conversion constants
    _pucf = {'m': 1, 'dm': 0.1, 'cm': 0.01, 'mm': 0.001, 'pa': 0.00010197442889221, 'hpa': 0.010197442889221, 'kpa': 0.10197442889221, 'mbar': 0.010197442889221, 'bar': 10.197442889221, 'mmhg': 0.013595475598539, 'psi': 0.70308890742557}
    # the most common Earth tide frequencies found in groundwater pressure (Merritt, 2004; McMillan et al., 2019)
    _etfqs = {'Q1': 0.893244, 'O1': 0.929536, 'M1': 0.966446, 'P1': 0.997262, 'S1': 1.0, 'K1': 1.002738, 'N2': 1.895982, 'M2': 1.932274, 'S2': 2.0, 'K2': 2.005476}
    # the most common atmospheric tide frequencies (McMillan et al., 2019)
    _atfqs = {'P1': 0.997262, 'S1': 1.0, 'K1': 1.002738, 'S2': 2.0, 'K2': 2.005476}
    
    def __init__(self, name, geoloc=None):
        # the site name
        self.name = name
        
        if geoloc is not None:
            if not isinstance(geoloc, (list,np.ndarray)):
                raise Exception("Error: Input 'geoloc' must have 3 values (longitude, latitude, height)!")
            self.geoloc = geoloc
        else:
            self.geoloc = None
        
        # make subclasses
        self.BP = _BP.BP(self)
        self.GW = _GW.GW(self)
        self.ET = _ET.ET(self)
        # # make sure that the inner classes have access to self
        self.results = _results.results(self.BP, self.GW, self.ET)
        self.data = _data.data(self, self.BP, self.GW, self.ET, self.results)
        self.model = _model.model(self)
    	