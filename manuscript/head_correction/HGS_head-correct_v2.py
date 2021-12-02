# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 09:30:26 2021

@author: Daniel
"""
import hydrogeosines as hgs

#%%  Testing MVC principal
fowlers = hgs.Site('Fowlers Gap', geoloc=[141.763316, -31.069359, 160])

fowlers.import_csv('manuscript/head_correction/FG-86_data.csv',
                        input_category = ['BP', 'GW'], 
                        loc_names = ["Baro", "FG86"],
                        utc_offset = 10,
                        unit=['hpa', 'm'],
                        how="add", check_duplicates=True)

#%%
process = hgs.Processing(fowlers).by_dates(start='2017-03-01', stop='2017-05-01')

#%%
process.info()

#%% test gw_correct
gw_correct_results  = process.GW_correct(lag_h=12)

#%%
correct_output  = hgs.Output(gw_correct_results)

fig = correct_output.plot(folder="export")
data = correct_output.export(folder="export")
