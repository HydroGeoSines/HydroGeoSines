# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:30:26 2021

@author: Daniel
"""

import hydrogeosines as hgs
import numpy as np
import pandas as pd


data = pd.read_csv('tests/data/Brazil.csv')
data.iloc[:, 0] = pd.to_datetime(data.iloc[:, 0], format="%m/%d/%y %H:%M")
                       
#%%  Testing MVC principal
site = hgs.Site('Porto Alegre')
# site.import_csv('tests/data/Brazil.csv',
#                         input_category=["GW", "BP", "ET"], 
#                         utc_offset=-3, 
#                         unit=["m", "m", "nm/s**2"],
#                         loc_names = ["GW", "Baro", "ET"],
#                         how="add", check_duplicates=True, dt_format="%m/%d/%y %H:%M")

site.import_df(data, input_category=["GW","BP","ET"], unit=["m", "m", "nm/s**2"],
                   utc_offset=float(-3), how="add", check_duplicates=True)

#%% Processing
# create Instance of Processing with csiro_site
process = hgs.Processing(site)
process.describe()

#%% test gw_correct
gw_correct_results  = process.GW_correct(lag_h=8, et_method='ts')

correct_output  = hgs.Output(gw_correct_results)

#%%
correct_output.export()

fig = correct_output.plot()
# correct_output.plot(folder='export')
