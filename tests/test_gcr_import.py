# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:30:26 2021

@author: Daniel
"""
import hydrogeosines as hgs
import numpy as np
import pandas as pd

#%%  Testing MVC principal
example_site = hgs.Site('Fowlers Gap', geoloc=[141.73099, -31.2934, 160])

# Load all our data attributed to the Site
example_site.import_csv('tests/data/notebook/GW_record.csv', 
                        input_category=["GW"]*2, 
                        utc_offset=10, 
                        unit=["m"]*2,
                        loc_names = ["Loc_A","Loc_B"], 
                        header = None,
                        check_duplicates=True)

#%%
example_site.import_csv('tests/data/notebook/BP_record.csv', 
                        input_category="BP", 
                        utc_offset=10,
                        unit="m", 
                        loc_names = "Baro",
                        header = None,
                        how="add", check_duplicates=True)

#%%
process = hgs.Processing(example_site) #.decimate(2).by_dates(start='2015-11-01', stop='2016-02-01').by_gwloc("FG822-2")

#%%
process.describe()
