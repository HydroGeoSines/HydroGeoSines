import hydrogeosines as hgs
import numpy as np
import pandas as pd
from copy import deepcopy

import matplotlib.pyplot as plt

fowlers_site = hgs.Site('Fowlers Gap', geoloc=[141.73099, -31.2934, 160])
fowlers_site.import_csv('tests/data/fowlers_gap/acworth_short.csv', 
                        input_category=['BP', 'GW', 'GW', 'GW', 'ET'],
                        utc_offset = 10,
                        unit=['m', 'm', 'm', 'm', 'm**2/s**2'],
                        loc_names = ["Baro", "FG822-1", "FG822-2", "Smith", "ET"],
                        how="add", check_duplicates=True)


#%%
process = hgs.Processing(fowlers_site)
# create Instance of Processing for specific locations of csiro_site and add a regularly sampled data container to the processing object 
# it is automatically reused in some of the methods, reducing computation times

locations = ["FG822-1", "FG822-2"]
process_sub_loc = hgs.Processing(fowlers_site).by_gwloc(locations).make_regular()

process_sub_date = hgs.Processing(fowlers_site).by_dates('2014-12-01', '2014-12-05')
process_sub_date_loc = hgs.Processing(fowlers_site).by_gwloc("FG822-2").by_dates('2014-11-01', '2014-12-05')


#%%

# test hals method
hals_results  = process_sub_date_loc.hals()

# test be method
be_results  = process.BE_time(method="all")

# test gw_correct
gw_correct_results  = process_sub_loc.GW_correct(lag_h=24, et_method = None, fqs=None)
