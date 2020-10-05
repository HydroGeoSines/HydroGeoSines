import hydrogeosines as hgs

#%% test the model
test = hgs.Site('TEST', geoloc=[141.762065, -31.065781, 160])

#%%
# test.import_csv('test_data/fowlers_gap/acworth_short_gaps.csv', utc_offset=10, input_type=["BP", 'GW', 'GW', 'GW', 'ET'], unit=["m", 'm', 'm', 'm', 'nm/s^2'], method="add", check_dublicates=True) #, dt_fmt='%d/%m/%Y %H:%M'
print(test.data)

test.import_csv('test_data/fowlers_gap/acworth_gw.csv', utc_offset=10, input_type='GW', unit='m', method="add", check_dublicates=True) 
test.import_csv('test_data/fowlers_gap/acworth_bp.csv', utc_offset=10, input_type='BP', unit='m', method="add", check_dublicates=True) 
test.import_csv('test_data/fowlers_gap/acworth_et.csv', utc_offset=10, input_type='ET', unit='nm/s^2', method="add", check_dublicates=True)

data = test.data

#%%
test.drop_nan()

#%%
pivot = test.dt_pivot
print(pivot)

regular = test.make_regular()
print(pivot)

#%%
# data = test.dt_regular

#%%
# test.remove(['Smith_5', 'FG822-1_2'])

# #%% 
# tmp = test.data.dtf
# print(tmp)

# #%%
# pivot = test.data.dt_pivot()

