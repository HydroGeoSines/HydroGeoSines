import hydrogeosines as hgs
import numpy as np
import pandas as pd
from copy import deepcopy

#%%  Testing MVC principal
site = hgs.Site('death valley', geoloc=[-116.471360, 36.408130, 688])
site.import_csv('tests/data/death_valley/BLM-1_double.csv',
                        input_category=["GW","BP","ET"], utc_offset=0, unit=["m","m","nstr"],
                        how="add", check_dublicates=True)

#%%  Testing MVC principal
# site = hgs.Site('thirlmere', geoloc=[150.543527, -34.229377, 289.576])
# site.import_csv('tests/data/thirlmere_lakes/GW075409.1.2.csv',
#                         input_category=["GW","BP","ET"], utc_offset=10, unit=["m","m","nstr"],
#                         how="add", check_dublicates=True)

#%% Processing
# create Instance of Processing with csiro_site
process = hgs.Processing(site)

# # test hals method
# hals_results  = process.hals()

#%% estimate hydraulic properties ...
hyd_prop  = process.K_Ss_estimate(loc='BLM-1', scr_len=10, case_rad=0.127, scr_rad=0.127, scr_depth=78)
# print(hyd_prop)

#%% quantify BE using the frequency domain approach
be_freq_2  = process.BE_freq(method="rau", freq_method='hals')
# print(be_freq_2)
