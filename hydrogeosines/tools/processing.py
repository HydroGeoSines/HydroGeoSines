# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np

class Processing:
    # define all class attributes here 
    #attr = attr
            
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Processing here
        #self.attribute = variable
                    
    def check_dublicates(self):
        # search for dublicates (in rows)
        if any(self.duplicated(subset=None, keep='first')):                
            print("Dublicate entries detected and deleted")
            return self.drop_duplicates(subset=None, keep='first', inplace=True, ignore_index=True)
        else:
            return self
 