# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""
from .time import Time
from .processing import Processing

import pandas as pd
import numpy as np
import pytz
from itertools import repeat

class Load(Processing):
    # define all class attributes here 
    #attr = attr
            
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Processing here
        #self.attribute = variable
                    
    def import_csv(self, filepath, utc_offset: float, input_type, unit='m', method: str="add", check_dublicates=False):
        VALID_TYPE = {"ET", "BP", "GW"}
        #TODO: add header=True and location as keywords to enable a more fleixble location naming
        #TODO: add dt_num column?
            
        # load the csv file into variable
        data = pd.read_csv(filepath, parse_dates=[0], infer_datetime_format=True)

        # make sure the first column is a correctly identified datetime    
        if data.dtypes[0] == "datetime64[ns]":
            data.rename(columns={data.columns[0]: "datetime"}, inplace=True)
            # drop duplicates if necessary
            data.drop_duplicates(subset=['datetime'], inplace=True)
            data.datetime = data.datetime.dt.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset))).dt.tz_convert('UTC')
            dt_col      = data.columns[0]
            val_cols    = data.columns[1::].values
            
        else:    
            raise Exception("Error: First column must be a datetime column") 
            
        if isinstance(input_type, str):
            if input_type not in VALID_TYPE:
                raise ValueError("Keyword input_type must be one of %r." % VALID_TYPE)
            else:
                input_type = [input_type] * len(val_cols)
        elif isinstance(input_type, list):
            if len(input_type) != len(val_cols):
                raise ValueError("Data input length must be the same as data columns in import file")
            else:
                for i in input_type:
                    if i not in VALID_TYPE:
                        raise ValueError("Keyword input_type must be one of %r." % VALID_TYPE)
        else:
            raise ValueError("Keyword input_type must be data type 'str' or 'list'")
        
        if isinstance(unit, str):
                unit = [unit] * len(val_cols)
        elif isinstance(input_type, list):
            if len(input_type) != len(val_cols):
                raise ValueError("Keyword unit must be the same as data columns in import file")
        else:
            raise ValueError("Keyword unit must be data type 'str' or 'list'")
            
        # loop through every column of the original dataset
        for i, val in enumerate(val_cols):
            tmp = data[['datetime', val]]
            
            tmp = pd.melt(tmp, id_vars=[dt_col], var_name="location")
            tmp.insert(1, "dt_num", Time.dt_num(data['datetime']))
            tmp.insert(1, "type", input_type[i])
            tmp.insert(1, "utc_offset", utc_offset)
            
            if (input_type[i]== 'GW') or (input_type[i] == 'BP'):
                if unit[i] not in self.const['_pucf'].keys():
                    raise ValueError("Keyword unit must be one of %r." % self.const['_pucf'].keys())
                else:
                    tmp["value"] *= self.const['_pucf'][unit[i].lower()]
                    tmp["unit"] = str("m") # always set to SI unit meter
            else:
                tmp["unit"] = unit[i]
                
            # sort the data in a standard way for easier identification of dublicates
            tmp.sort_values(by=["location", "type", "datetime"], inplace=True)
            
            #if dt_num == True:
            #    data.insert(1,"dt_num",self.data.day_num())
                
            if method == "add":
                try:
                    self.data = self.data.append(tmp)
                    
                except AttributeError:
                    self.data = Data(columns=["datetime","dt_num","utc_offset","type","location","value","unit"])
                    self.data = self.data.append(tmp)
                    
                print("A new time series was added ...")
            #TODO: Implement other methods    
            else:     
                self.data = data   
        
        self.data.sort_values(by=["location", "type","datetime"], inplace = True)
        self.data.reset_index(inplace=True, drop=True)
                
        if check_dublicates == True:                       
            self.data.check_dublicates()

 