import hydrogeosines as hgs
import matplotlib.pyplot as plt
import numpy as np

#%%  Testing MVC principal
hgs_data = hgs.Site('death valley', geoloc=[-116.471360, 36.408130, 688])
hgs_data.import_csv('tests/data/death_valley/death_valley.csv',
                        input_category=["GW","BP","ET"], utc_offset=0, unit=["m","m","m"],
                        how="add", check_dublicates=True)

data = hgs_data.data
raw = data.pivot(index='datetime', columns=['category', 'location'], values='value')

#%%
# acworth_site.add_ET(et_comp='g')
data = hgs_data.data
heads = data.pivot(index='datetime', columns=['category', 'location'], values='value')

#%% Processing
print("Calculate BE ...")
hgs_process = hgs.Processing(hgs_data)

# be_results = process_acworth.BE_freq(method='rau')
be_results = hgs_process.BE_freq(method='rau')

print(be_results)

be_results = hgs_process.BE_freq(method='rau', freq_method='fft', update=False)

print(be_results)
