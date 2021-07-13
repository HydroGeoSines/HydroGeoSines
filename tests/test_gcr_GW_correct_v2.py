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
fowlers = hgs.Site('Fowlers Gap', geoloc=[141.73099, -31.2934, 160])

fowlers.import_csv('tests/data/fowlers_gap/acworth_all.csv', 
                        input_category=['BP', 'GW', 'GW', 'GW', 'ET'], 
                        utc_offset = 10, 
                        unit=['m', 'm', 'm', 'm', 'm**2/s**2'], 
                        loc_names = ["Baro", "FG822-1", "FG822-2", "Smith", "ET"],
                        how="add", check_duplicates=True)

#%%
process = hgs.Processing(fowlers).by_dates(start='2015-11-01', stop='2016-02-01').by_gwloc("FG822-2")

#%% test gw_correct
gw_correct_results  = process.GW_correct(lag_h=36, et_method='hals')

correct_output  = hgs.Output(gw_correct_results)

correct_output.plot()
