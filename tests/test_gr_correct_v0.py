import hydrogeosines as hgs
import matplotlib.pyplot as plt
import numpy as np

#%%  Testing MVC principal
acworth_site = hgs.Site('death valley', geoloc=[-116.471360, 36.408130, 688])
acworth_site.import_csv('tests/data/death_valley/death_valley.csv',
                        input_category=["GW","BP","ET"], utc_offset=0, unit=["m","m","m"],
                        header=["BLM-1","Baro","ET"], how="add", check_dublicates=True)

data = acworth_site.data
raw = data.pivot(index='datetime', columns=['category', 'location'], values='value')

#%%
acworth_site.add_ET(et_comp='g')
data = acworth_site.data
heads = data.pivot(index='datetime', columns=['category', 'location'], values='value')

#%% Processing
print("Correct heads ...")
process_acworth = hgs.Processing(acworth_site)

corrected, params = process_acworth.correct_GW(et_method='hals', lag_h=8)

#%% plot corrected heads
plt.figure()
plt.plot(heads.index.values, heads['GW']['BLM-1'])
plt.plot(corrected.index.values, corrected['BLM-1'])

#%%
plt.figure()
lag_t = params['BLM-1']['brf']['lag']
crf = params['BLM-1']['brf']['crf']

plt.plot(lag_t, crf)
plt.ylim([0,1])

print(heads)
