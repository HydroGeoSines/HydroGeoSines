# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:30:26 2021

@author: Daniel
"""

import hydrogeosines as hgs
import numpy as np
import pandas as pd

#%%  Testing MVC principal
site = hgs.Site('Porto Alegre', geoloc=[-30.03779, -51.19535, 40])
site.import_csv('tests/data/brasil/Brito.csv',
                        input_category=["GW", "BP", "ET"], 
                        utc_offset=-3, 
                        unit=["m", "m", "nm/s**2"],
                        loc_names = ["GW", "Baro", "ET"],
                        how="add", check_duplicates=True)

#%% Processing
# create Instance of Processing with csiro_site
process = hgs.Processing(site)
process.info()

#%% test gw_correct
gw_correct_results  = process.GW_correct(lag_h=8, et_method='hals')

correct_output  = hgs.Output(gw_correct_results)

#%%
correct_output.export(folder='export')
correct_output.plot(folder='export')
