# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:30:26 2021

@author: Daniel
"""

import hydrogeosines as hgs
import numpy as np
import pandas as pd

#%%  Testing MVC principal
## Model
fowlers = hgs.Site('csiro', geoloc=[141.762065, -31.065781, 160])
# read data
fowlers.import_csv('tests/data/fowlers_gap/acworth_short.csv', 
                        input_category=['BP', 'GW', 'GW', 'GW', 'ET'], 
                        utc_offset = 10, 
                        unit=['m', 'm', 'm', 'm', 'm**2/s**2'], 
                        loc_names = ["Baro", "FG822-1", "FG822-2", "Smith", "ET"],
                        how="add", check_duplicates=True)

#%%
# add et
process = hgs.Processing(fowlers)

#%% test gw_correct
gw_correct_results  = process.GW_correct(lag_h=24, et_method=None)

correct_output  = hgs.Output(gw_correct_results)

correct_output.plot()
