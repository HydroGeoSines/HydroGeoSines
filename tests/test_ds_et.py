# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 13:31:59 2021

@author: Daniel
"""

import hydrogeosines as hgs

#import pygtide as pyg


#%% Csiro Data
## Model
csiro_site = hgs.Site('csiro', geoloc=[141.762065, -31.065781, 160])
# read data
csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_GW_short.csv', 
                        input_category=["GW"]*3, 
                        utc_offset=10, unit=["m"]*3, 
                        loc_names = ["Loc_A","Loc_B","Loc_C"],
                        how="add", check_dublicates=True) 

csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_BP_short.csv', 
                        input_category="BP", 
                        utc_offset=10, unit="mbar", loc_names = "Baro",
                        how="add", check_dublicates=True) 

data = csiro_site.data

# add et
csiro_site.add_ET()
process_csiro = hgs.Processing(csiro_site)
gw_correct_results  = process_csiro.GW_correct(lag_h=24, fqs=None)

pivot = process_csiro.data_regular.hgs.pivot
pivot.head(3)

mask = pivot.columns.get_level_values("category") == "ET"
pivot_noET = pivot.loc[:, ~mask]        