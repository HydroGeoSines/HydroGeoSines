import hydrogeosines as hgs
import numpy as np
import pandas as pd
from copy import deepcopy

#%%  Testing MVC principal
# site = hgs.Site('death valley', geoloc=[-116.471360, 36.408130, 688])
# site.import_csv('tests/data/death_valley/BLM-1.csv',
#                         input_category=["GW","BP","ET"], utc_offset=0, unit=["m","m","nstr"],
#                         how="add", check_dublicates=True)

#%%  Testing MVC principal
site = hgs.Site('death valley', geoloc=[150.543527, -34.229377, 289.576])
site.import_csv('tests/data/thirlmere_lakes/GW075409.1.2.csv',
                        input_category=["GW","BP","ET"], utc_offset=10, unit=["m","m","nstr"],
                        how="add", check_dublicates=True)

#%% Processing
# create Instance of Processing with csiro_site
process = hgs.Processing(site)

# test hals method
hals_results  = process.hals()

#%%
be_freq_1  = process.BE_freq(method="rau", freq_method='hals')
print(be_freq_1)

#%% frequency domain stuff ...

hyd_prop  = process.K_Ss_estimate(scr_len=10, case_rad=0.127, scr_rad=0.127, scr_depth=78, update=True)
print(hyd_prop)

#%%
be_freq_2  = process.BE_freq(method="rau", freq_method='hals', update=True)
print(be_freq_2)
