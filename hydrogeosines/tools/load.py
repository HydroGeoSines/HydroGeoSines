# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

from .processing import Processing

import pandas as pd
import numpy as np

class Load(Processing):
    # define all class attributes here 
    #attr = attr
            
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Processing here
        #self.attribute = variable
                    
    def import_csv(self,filepath,input_type: str, utc_offset: int, unit: str = "m", method: str ="add", check_dublicates=False):
        VALID_TYPE = {"ET", "BP", "GW"}
        #TODO: add header=True and location as keywords to enable a more fleixble location naming 
        
        if input_type not in VALID_TYPE:
            raise ValueError("data input type must be one of %r." % VALID_TYPE)
            
        # load the csv file into variable
        data = pd.read_csv(filepath,parse_dates=[0], infer_datetime_format=True)
            
        # make sure the first column is a correctly identified datetime    
        if data.dtypes[0] == "datetime64[ns]":
            data.rename(columns={data.columns[0]:"datetime"}, inplace = True)
            dt_col      = data.columns[0]
            val_cols    = data.columns[1::].values        
        else:    
            raise Exception("Error: First column must be a datetime column")  
        
        data = pd.melt(data,id_vars=[dt_col], var_name = "location") 
        data.insert(1,"dtype", input_type)
        
        #unit conversion always to meters    
        if unit.lower() in self.const['_pucf']: #case insensitive unit search
            pconv = self.const['_pucf'][unit.lower()]            
        else:
            raise ValueError("Error: The unit '" + unit + "' is unknown.")
    
        data["value"] = data.value*pconv
        data["unit"] = str("m") # always set to SI unit meter
        
        # sort the data in a standard way for easier identification of dublicates
        data.sort_values(by=["location", "dtype","datetime"], inplace = True)
        
        if method == "add":
            try:    
                self.data = self.data.append(data)
            except AttributeError:
                self.data = Data(columns=["datetime","dtype","location","value","unit"])
                self.data = self.data.append(data)
                
            self.data.sort_values(by=["location", "dtype","datetime"], inplace = True)
            self.data.reset_index(inplace=True, drop=True)
            print("New data was added...")
        #TODO: Implement other methods    
        else:     
            self.data = data   
            
        if check_dublicates == True:                       
            self.data.check_dublicates()

 