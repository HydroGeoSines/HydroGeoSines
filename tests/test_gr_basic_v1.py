import hydrogeosines as hgs
import numpy as np
import pandas as pd
from copy import deepcopy

#%% Csiro Data
## Model
csiro_site = hgs.Site('csiro', geoloc=[141.762065, -31.065781, 160])
# read data
csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_GW_short.csv', 
                        input_category=["GW"]*3, 
                        utc_offset=10, unit=["m"]*3, loc_names = ["Loc_A","Loc_B","Loc_C"],
                        how="add", check_duplicates=True) 

csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_BP_short.csv', 
                        input_category="BP", 
                        utc_offset=10, unit="mbar", loc_names = "Baro",
                        how="add", check_duplicates=True) 

#%%
csiro_site.add_ET(et_comp='g', et_cat=4)

#%% Processing
# create Instance of Processing with csiro_site
process_csiro = hgs.Processing(csiro_site)

# create Instance of Processing for specific locations of csiro_site
locations = ["Loc_A","Loc_B"]
process_csiro_SiteA_B = hgs.Processing(csiro_site).by_gwloc(locations)

#%%
# add a regularly sampled data container to the processing object 
# it is automatically reused in some of the methods, reducing computation times
process_csiro = hgs.Processing(csiro_site).by_gwloc(locations).make_regular()

# test hals method
# hals_results  = process_csiro.hals()

# test be method
be_results  = process_csiro.BE_time(method="all")

# test gw_correct
gw_correct_results  = process_csiro.GW_correct(lag_h=24, et_method = None, fqs=None)

#%%
be_freq  = process_csiro.BE_freq(method="rau", freq_method='hals', update=True)
print(be_freq)
