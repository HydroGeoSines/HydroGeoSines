import hydrogeosines as hgs
import matplotlib.pyplot as plt
import numpy as np

#%%  Testing MVC principal
acworth_site = hgs.Site('death valley', geoloc=[-116.471360, 36.408130, 688])
acworth_site.import_csv('tests/data/death_valley/death_valley.csv',
                        input_category=["GW","BP","ET"], utc_offset=0, unit=["m","m","m"],
                        how="add", check_dublicates=True)

data = acworth_site.data
raw = data.pivot(index='datetime', columns=['category', 'location'], values='value')

#%%
# acworth_site.add_ET(et_comp='g')
data = acworth_site.data
heads = data.pivot(index='datetime', columns=['category', 'location'], values='value')

#%% Processing
print("Calculate BE ...")
process_acworth = hgs.Processing(acworth_site)

be_results = process_acworth.BE_freq(method='rau')
