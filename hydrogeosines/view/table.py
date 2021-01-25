# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np

#from ..utils.tools import Tools

class Tables(object):
    
    def __init__(self, *args, **kwargs):
        pass  
    
    def summary_freq(comp,freq, var):
        table = pd.DataFrame()
        return pd.DataFrame([freq],index=comp,columns=["freq"])
    
    
    