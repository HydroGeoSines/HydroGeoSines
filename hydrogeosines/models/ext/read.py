# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

from ... import utils

import pandas as pd
import numpy as np
import pytz

class Read(object):
    # define all class attributes here 
    #attr = attr
        
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Load here
        #self.attribute = variable            
           
    def import_csv(self, filepath, input_category, utc_offset: float, unit = "m", how: str="add", loc_names=None, check_dublicates=False):        
        
        #check for non valid categories 
        utils.check_affiliation(input_category, self.VALID_CATEGORY)
        
        #check for non valid pressure units (GW,BP)
        if any(cat in input_category for cat in ("GW","BP")):
            utils.check_affiliation([u.lower() for u in np.array(unit).flatten()], self.const['_pucf'].keys())
        
        #check for non valid accelaration units (ET)
        if any(cat in input_category for cat in ("ET")):
            #TODO: add units and their converstion to glob.py 
            utils.check_affiliation([u.lower() for u in np.array(unit).flatten()], self.const['_etunit'].keys())                       
            
        # load the csv file into variable
        data = pd.read_csv(filepath, parse_dates=True, index_col=0, infer_datetime_format=True, dayfirst=True, header=0)
       
        # ignore column numbers beyond input length
        ncols = len(input_category)
        data = data.iloc[:, :ncols]

        data.index.rename(name="datetime", inplace=True) # streamline datetime name
            
        # make sure the first column is a correctly identified datetime    
        if not isinstance(data.index, pd.DatetimeIndex):
            raise Exception("Error: First column must be a datetime column")
            
        # make UTC correction
        data.index = pd.to_datetime(data.index.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset))).tz_convert(pytz.utc)) 
        
        # custom headers for locations
        if loc_names != None:
            locations = list(np.array([loc_names]).flatten())
        else:
            locations = data.columns
                
        # format table with multiindex and melt            
        header = utils.zip_formatter(locations, input_category, unit)
        data.columns = pd.MultiIndex.from_tuples(header, names=["location","category","unit"])                
        data = pd.melt(data.reset_index(), id_vars="datetime", var_name=["location","category","unit"], value_name="value").rename(columns=str.lower)                 
        
        # add "part" column as a placeholder 
        data["part"] = "all"
        
        # reformat unit column to SI units
        data["value"], data["unit"] = data.hgs.pucf_converter_vec(self.const["_pucf"]) # vectorizing
        
        # add utc_offset to site instead of data, to keep number of columns at a minimum
        self.utc_offset.update(dict(utils.zip_formatter(locations, utc_offset)))

        # how to use the data       
        if how == "add":
            self.data = self.data.append(data)                    
            print("A new time series was added ...")
        #TODO: Implement other methods    
        else:     
            raise ValueError("Method not available")   
            
        # make sure the datetime is formated correctly for later use
        self.data["datetime"] = pd.to_datetime(self.data["datetime"]) 
        # sort data in a standard way -> easier to read
        self.data.sort_values(by=["category","location","part"], inplace = True)
        # no dublicate indices
        self.data.reset_index(inplace=True, drop=True)             
        # no dublicate entries        
        if check_dublicates == True:                       
            self.data = self.data.hgs.check_dublicates