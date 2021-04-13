# -*- coding: utf-8 -*-
"""
Created on Wed Apr  7 13:31:59 2021

@author: Daniel
"""

import hydrogeosines as hgs

#import pygtide as pyg
from hydrogeosines.models.ext.et import ET

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
#gw_correct_results  = process_csiro.GW_correct(lag_h=24, fqs=None)

pivot = process_csiro.data_regular.hgs.pivot
pivot.head(3)

mask = pivot.columns.get_level_values("category") == "ET"
pivot_noET = pivot.loc[:, ~mask]   

#%%
acworth_site = hgs.Site('acworth', geoloc=[141.762065, -31.065781, 160])

acworth_site.import_csv('tests/data/fowlers_gap/acworth_gw.csv',
                        input_category=["GW","BP","GW"], utc_offset=10, unit=["Cm","mm","M"],
                        loc_names = ["Site_A","Baro","Site_C"], how="add", check_dublicates=True)

data_ac = acworth_site.data     

process_acworth = hgs.Processing(acworth_site)

# not working properly (site_obj is changed instead of site_obj.data)
#process_acworth.ET_calc()

## Make data regular and aligned 
regular = process_acworth.data.hgs.make_regular() #inter_max = 3600,part_min=20,category="GW",spl_freq=1200
regular = regular.hgs.BP_align() # inter_max = 3600, method = "backfill", inter_max_total = 10
# check integrity
regular.hgs.check_BP_align

# pivot data to get multiindex by datetime. perfectly aligned now
pivot = regular.hgs.pivot

ET_data = ET.calc_ET_align(regular,geoloc=acworth_site.geoloc)

s = data_ac.loc[:,["datetime","value"]]
s = s.set_index("datetime")
s = s[~s.index.duplicated(keep='first')]
s = s.interpolate(method="cubic")

#%% Test be_freq method with acworth data and et
acworth_site = hgs.Site('acworth', geoloc=[141.762065, -31.065781, 160])

acworth_site.import_csv('tests/data/fowlers_gap/acworth_gw.csv',
                        input_category=["GW","BP","GW"], utc_offset=10, unit=["Cm","mm","M"],
                        loc_names = ["Site_A","Baro","Site_C"], how="add", check_dublicates=True)

process_acworth = hgs.Processing(acworth_site)
process_acworth.ET_calc()
be_freq_hals = process_acworth.BE_freq(freq_method="hals")
be_freq_fft = process_acworth.BE_freq(freq_method="fft")

