# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:30:26 2021

@author: Daniel
"""

import hydrogeosines as hgs
import numpy as np
import pandas as pd

#%%  Testing MVC principal
death_valley = hgs.Site('death valley', geoloc=[-116.471360, 36.408130, 688])
death_valley.import_csv('tests/data/death_valley/Rau_et_al_2021.csv',
                        input_category=["GW","BP","ET"], utc_offset=0, unit=["m","m","nstr"],
                        how="add", check_duplicates=True)

#%%
# tmp = death_valley.data.hgs.get_loc_unit('ET')

#%% Processing
# create Instance of Processing with csiro_site
process = hgs.Processing(death_valley)

# test hals method
fft_results  = process.fft(update=True)

#%% Output
csiro_output  = hgs.Output(fft_results) # process.results container or results

# for visualization
csiro_output.plot(xlim=[0.5, 5], file='fft.png') # possible different plotting style methods, e.g. simple, report, etc

