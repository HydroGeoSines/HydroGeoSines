import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import hydrogeosines as hgs

#%% test the model
test = hgs.site('TEST', geoloc=[141.762065, -31.065781, 160])

#%%
hello = test.import_csv('test_data/fowlers_gap/acworth_short.csv', dt_fmt='%d/%m/%Y %H:%M')
print(hello)

#%%
corrected = test.correct(et_method='hals', et=True)
print(corrected)

#%%
hello1 = test.calc_BE(method='acworth')
print(hello1)

#%%
hello1 = test.calc_BE(method='rau')
print(hello1)

#%%
test.export_results('corrected.csv')

analysis
data
processing


site.analysis.calc_BE()
site.data