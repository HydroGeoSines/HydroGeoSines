import hydrogeosines as hgs
import numpy as np
import pandas as pd
from copy import deepcopy
import random 

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

#%% Create Test Dataset
# Full data test set with gaps
data2 = csiro_site.data.copy()
data2.loc[12000:12500,"value"] = np.nan # BP value gap
#data2.loc[30000:30500,"value"] = np.nan # GW value large_gap1
#data2.loc[72000:75000,"value"] = np.nan # GW value large_gap1
data2.loc[151000:155000,"value"] = np.nan # GW value large_gap2
data2.loc[300000:302000,"value"] = np.nan # GW value large_gap3
#data2.loc[22000:22600,"value"] = np.nan # GW value small_gap1
# add dummy category
#data2.loc[302000:303000,"category"] = "ET" # add additional category for testing

k = 0.10 # 5% missing values
# get 5% of GW values
idx = random.sample(list(data2.loc[data2["category"]== "GW"].index), int(k*len(data2.loc[data2["category"]== "GW"])))
data2.drop(labels=idx,inplace=True) 

#data2.loc[data2["category"]== "GW"].hgs.pivot.to_csv('tests/data/notebook/GW_record.csv',sep=",",index=True,header=False)
#data2.loc[data2["category"]== "BP"].hgs.pivot.to_csv('tests/data/notebook/BP_record.csv',sep=",",index=True,header=False)

# check for gaps and outliers
import matplotlib.pyplot as plt
data2.loc[data2.location == "Loc_A"].plot.scatter(x="datetime",y="value")
data2.loc[data2.location == "Loc_B"].plot.scatter(x="datetime",y="value")
data2.loc[data2.location == "Loc_C"].plot.scatter(x="datetime",y="value")

#%% reload data
example_site = hgs.Site('example', geoloc=[141.762065, -31.065781, 160])
example_site.import_csv('tests/data/notebook/GW_record.csv', 
                        input_category=["GW"]*3, 
                        utc_offset=10, unit=["m"]*3, 
                        loc_names = ["Loc_A","Loc_B","Loc_C"],
                        header = None,
                        how="add", check_dublicates=True)

example_site.import_csv('tests/data/notebook/BP_record.csv', 
                        input_category="BP", 
                        utc_offset=10, unit="m", 
                        loc_names = ["Baro"],
                        header = None,
                        how="add", check_dublicates=True) 

data3 = example_site.data

data4 = data2.hgs.filters.drop_nan.reset_index(drop=True)
data5 = data3.hgs.filters.drop_nan.reset_index(drop=True)
#%% HGS pandas function examples
## easy access to data and values by location
bp_data = data.hgs.filters.get_bp_data  
gw_data = data.hgs.filters.get_gw_data

bp_values = data.hgs.filters.get_bp_values  
gw_values = data.hgs.filters.get_gw_values

bp_locs = data.hgs.filters.get_bp_locs  
gw_locs = data.hgs.filters.get_gw_locs

## Make data regular and aligned 
regular = data2.hgs.make_regular(spl_freq=1200, part_min = 15) #inter_max = 3600,part_min=20,category="GW",spl_freq=1200
regular = regular.hgs.BP_align() # inter_max = 3600, method = "backfill", inter_max_total = 10
# check integrity
regular.hgs.check_BP_align

# pivot data to get multiindex by datetime. perfectly aligned now
pivot = regular.hgs.pivot

# demonstrate Most common frequency (MCF) (included in make_regular)
mcf = data2.copy()
mcf = mcf.hgs.filters.drop_nan # used within hgs processing workflows

#TODO: replace non_valid entries? Dublicates already handled at import
# Sample frequency for each group
spl_freqs = mcf.hgs.spl_freq_groupby

# Resampling for each group
mcf = mcf.hgs.resample_by_group(spl_freqs)

#%% Processing
# create Instance of Processing with csiro_site
process_csiro = hgs.Processing(csiro_site)

# create Instance of Processing for specific locations of csiro_site
locations = ["Loc_A","Loc_D"]
process_csiro_SiteA = hgs.Processing(csiro_site).by_gwloc(locations)

# add a regularly sampled data container to the processing object 
# it is automatically reused in some of the methods, reducing computation times
locations = ["Loc_A","Loc_B"]
process_csiro = hgs.Processing(csiro_site).by_gwloc(locations).make_regular()

# test hals method
hals_results  = process_csiro.hals()

# test be method
be_results  = process_csiro.BE_time(method="all")

# test gw_correct
gw_correct_results  = process_csiro.GW_correct(lag_h=24, et_method = None, fqs=None)

be_freq = process_csiro.BE_freq()
#should still be empty
print(process_csiro.results)

#%% use UPDATE method
# test update functionality of processing methods
dummy  = process_csiro.hals(update=True)
dummy  = process_csiro.BE_time(method="all",update=True)
dummy  = process_csiro.GW_correct(lag_h=24, et_method = None, fqs=None,update=True)

#print(process_csiro.results)

# create a new site object with the "polluted" data
csiro_site_part = deepcopy(csiro_site)
csiro_site_part.data = data2.copy()

# test the BE method on polluted data
process_csiro_part = hgs.Processing(csiro_site_part)
be_results_2  = process_csiro_part.BE_time(method="all")

#%% filter upsampling with gap_mask (included in make_regular)
mask = mcf.copy()
x = mcf["value"]
mask, counter = hgs.utils.gap_mask(x,12)

group = mcf[mask].hgs.upsample(method="backfill") 

#%% View structure

#view_csiro = Output()
#view_csiro.plot(method=)
#view_csrio.export()
#%% Example and Ideas on MVC Paradigm
"""
## MODEL
mountain_data   = hgs.Data().import_csv() 
mountain_site   = hgs.Site('MOUNTAIN', geoloc=[141.762065, -31.065781, 160])

# add data
mountain_site.import_csv('test_data/fowlers_gap/acworth_short_gaps.csv', utc_offset=10, input_type=["BP", 'GW', 'GW', 'GW', 'ET'], unit=["m", 'm', 'm', 'm', 'nm/s^2'], method="add", check_dublicates=True)

## CONTROLLER
hals_wf         = hgs.Processing.hals()
## VIEW
#terminal_output = hgs.TerminalOutput()

# Trennung von Daten und Logik, damit die Objekte nicht so riesig werden
# NICHT: hals_wf.site.do_something()
data_result = hals_wf.process_site_data(mountain_site.data)
terminal_output.print_data(data_result)
# ODER (falls Daten "behalten" werden sollen)
mountain_site.preprocessed['hals'] = hals_wf.process_site_data(mountain_site.data)
#
gw_data = mountain_site.gw_data ## INSTEAD: mountain_site.get_gw_data() <- METHOD

#___

filter_result = SiteFilter.by_location('loc')['datetime']
is_reg = filter_result.is_regular # ()
# generischer Ansatz: Site.by('location').where('loc')

site1.set_path('fr.csv');
site1.load_csv();
site1.get_data();

#MVC mäßig:
site1 = Site('Freiburg');
site1.load('freiburg.csv');

data = SiteController(site1).by_location('fr').process()

View().visualize(data);
"""