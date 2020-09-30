import numpy as np
import pandas as pd

# import sub-classes
from .tools.processing import Processing
from .tools.analysis import Analysis
from .tools.visualize import Visualize

#%% the data handling class

class Data(pd.DataFrame,Processing,Analysis,Visualize):
    
    # default time base is that of Excel
    dt_base = "1899-12-30"
    
    # this method is makes it so our methods return an instance
    # of ExtendedDataFrame, instead of a regular DataFrame
    @property
    def _constructor(self):
        return Data
        
    def dt_num(self):
        t = pd.to_numeric(self.datetime)
        t = t - t[0]
        t = t/ 10**9 # from ns to seconds
        t = t/(60*60*24) # to days
        return t
    
    def dt_pivot(self):
        return self.pivot_table(index="datetime", columns=["dtype","location"], values="value")
  