import numpy as np

class HgsFilters(object):
    """
    An extension that features hgs filters by category and location
    """
    VALID_CATEGORY  = {"ET", "BP", "GW"}
    NON_VALID_VALUES = {""}
    
    def __init__(self, hgs_obj):
        ## add attribute specific to Time here   
        #self._validate(hgs_obj)
        self._obj = hgs_obj
        
        # dynamically set a attribute that uses a function to access existing data categories
        for attr in self._obj.category.unique():
            setattr(self,f'get_{attr.lower()}_data', self.make_attr(attr)())
            setattr(self,f'get_{attr.lower()}_values', self.make_attr(attr)().value.values)
            setattr(self,f'get_{attr.lower()}_locs', self.make_attr(attr)()["location"].unique())
    
    # access function 
    def make_attr(self, category):
        def inner():
            return self._obj[self._obj['category'] == category].copy()
        return inner
    
    @property
    def obj_col(self):
        # returns df object columns as list
        return list(self._obj.select_dtypes(include=['object']).columns)
    
    @property
    def loc_part(self):
        # returns df location ID columns as list (not hardcoded)
        col_list = self.obj_col
        col_list.remove('category')
        col_list.remove('unit')
        return col_list
    
    @property
    def loc_names_unique(self):
        names = list(zip(self._obj.location, self._obj.part))
        return set(names)
    
    @property
    def is_nan(self):
        return self._obj['value'].isnull().values.any()
    
    @property
    def drop_nan(self):              
        return self._obj.dropna(axis=0, how="any", subset=["value"])
    
    def drop_loc(self,locs):
        locs = np.array(locs).flatten()
        idx = self._obj.location.isin(locs)
        return self._obj[~idx].reset_index(drop = True)
    
    def drop_cat(self,categories):
        categories = np.array(categories).flatten()
        idx = self._obj.category.isin(categories)
        return self._obj[~idx].reset_index(drop = True)
    