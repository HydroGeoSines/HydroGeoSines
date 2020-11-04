import numpy as np
import pandas as pd

from ..tools import Tools

class Series(object):
    # define all class attributes here 
    
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Processing here
        #self.attribute = variable
    
    # Check ups
    def is_nan(self):
        return self['value'].isnull().values.any()
    
    def df_obj(self):
        "returns df object columns as list"
        return list(self.select_dtypes(include=['object']).columns)
    
    # Methods
    def drop_nan(self):              
        return self.dropna(axis=0,how="any",subset=["value"]).reset_index(drop=True)
               
    def remove(self,locs):
        locs = np.array(locs).flatten()
        idx = self.location.isin(locs)   
        return self[~idx].reset_index()         