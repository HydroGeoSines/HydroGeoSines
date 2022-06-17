# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:30:26 2021

@author: Daniel
"""
import hydrogeosines as hgs

#%%  Testing MVC principal
example = hgs.Site('Death Valley')

example.import_csv('manuscript/head_correction/BLM-1_data.csv',
                        input_category = ['', 'GW', 'BP', '', '', 'ET'], 
                        loc_names = ["", "BLM-1", "Baro", "", "", "ET strain"],
                        utc_offset = 0,
                        unit=['', 'm', 'm', '', '', 'nstr'],
                        how="add", check_duplicates=True)

#%%
example_p = hgs.Processing(example)

#%%
example_p.describe()

#%% test gw_correct
gw_correct_results  = example_p.GW_correct(lag_h=12, et_method='hals')

#%%
correct_output  = hgs.Output(gw_correct_results)

fig = correct_output.plot(folder="export")
data = correct_output.export(folder="export")
