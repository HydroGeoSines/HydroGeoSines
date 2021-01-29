import numpy as np
import pandas as pd

class HgsFilters(object):
    """
    An extension that features hgs filters by category and location
    """
    VALID_CATEGORY  = {"ET", "BP", "GW"}
    
    def __init__(self,hgs_obj):        
        ## add attribute specific to Time here   
        #self._validate(hgs_obj)
        self._obj = hgs_obj
        
        # dynamically set a attribute that uses a function to access existing data categories
        for attr in self._obj.category.unique():
            setattr(self,f'get_{attr.lower()}_values', self.make_attr(attr))                   
     
    def make_attr(self,category):
        def inner():
            return self._obj[self._obj['category'] == category].value.values
        return inner  
    
    #@staticmethod
    #def _validate(obj):
    #    if not is_datetime(obj):
    #        raise AttributeError("Must be ...")
    
    @property
    def obj_col(self):
        # returns df object columns as list
        return list(self._obj.select_dtypes(include=['object']).columns)
    
    #%% Open for testing    
       

    """
    @property
    def gw_data(self):
        # return self.data[self.data['category'] == 'GW'].pivot(index='datetime', columns='location', values='value')        
        return self.__get_category('GW').pivot(index='datetime', columns='location', values='value')
    """
            
    @property
    def is_nan(self):
        return self._obj['value'].isnull().values.any()
    
    @property
    def drop_nan(self):              
        return self._obj.dropna(axis=0,how="any",subset=["value"])
               
    def drop_loc(self,locs):
        locs = np.array(locs).flatten()
        idx = self._obj.location.isin(locs)   
        return self._obj[~idx].reset_index()         