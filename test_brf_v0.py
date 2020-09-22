import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import hydrogeosines as hgs

#%% test the model
hgs = hgs.site('TEST', geoloc=[141.762065, -31.065781, 160])

hgs.data.import_csv('test_data/fowlers_gap/acworth_short.csv', dt_fmt='%d/%m/%Y %H:%M')

timefloat = hgs.data.tf.values
data = hgs.data.all['{BP}'].values
data1, result1 = hgs.method.lin_window_ovrlp(timefloat, data)
data2, result2 = hgs.method.hals(timefloat, data1, freqs='AT')

#%% 
# heads = hgs.data.correct_heads(locs=['Smith'])
hgs.data.correct_heads(et=True)

print(hgs.data.results.all)

#%%
# new_t = pd.date_range(start='2014-10-21 00:00', end='2016-05-18 05:15', freq='15min').to_series()
# new_t.to_csv('time.csv')

tmp = hgs.data.export_csv('data.csv')
tmp = hgs.results.export_csv('results.csv')