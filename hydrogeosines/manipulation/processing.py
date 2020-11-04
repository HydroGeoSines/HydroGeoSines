# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np

class Processing(object):
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
            return self.drop_duplicates(subset=None, keep='first', ignore_index=True)
        else:
            print("No dublicates being found ...")
            return self    
            
    def pucf_converter(self,row): # loop based
        if row["category"] in ("GW", "BP") and row["unit"] != "m":
            return row["value"] * self.const['_pucf'][row["unit"].lower()], "m"
        else:
            return row["value"], "m" 
        
    def pucf_converter_vec(self,df): # using vectorization
        idx     = ((df.category == "GW") | (df.category == "BP") & (df.unit != "m"))
        val     = np.where(idx, df.value*np.vectorize(self.const["_pucf"].__getitem__)(df.unit.str.lower()),df.value) 
        unit    = np.where(idx, "m", df.unit) 
        return val, unit     
        
    def dt_pivot(self):
        return self.pivot_table(index=self.datetime,columns=["category", "location"], values="value")
    
        
