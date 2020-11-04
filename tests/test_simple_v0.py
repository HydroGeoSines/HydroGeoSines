import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

#%%
hello = pd.read_csv('test_data/fowlers_gap/acworth_gaps.csv', parse_dates =[0], index_col=0)

# hello.set_index('Datetime[UTC+10]')

#%%
hello.iloc[[1,5,6,9],:] = np.nan
print(hello)

#%%
idx = hello.isnull().any(axis=1)

hello = hello.loc[~idx,:]

#%%
new = hello.asfreq(freq='600S')
print(new)

#%%
hello.loc[new.index, ]

#%%
for i,val in new.iterrows():
    if not i in hello:
        hello.loc[i, :] = new.loc[i, :]
        
hello.sort_index(inplace=True)
    
print(hello)

