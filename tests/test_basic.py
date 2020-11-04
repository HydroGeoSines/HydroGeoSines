import hydrogeosines as hgs

#%% test the model
test = hgs.Site('TEST', geoloc=[141.762065, -31.065781, 160])

#wf_abc = hgs.Workflow('abc')
#wf_abc.process(test);

#%%
# test.import_csv('test_data/fowlers_gap/acworth_short_gaps.csv', utc_offset=10, input_type=["BP", 'GW', 'GW', 'GW', 'ET'], unit=["m", 'm', 'm', 'm', 'nm/s^2'], method="add", check_dublicates=True) #, dt_fmt='%d/%m/%Y %H:%M'
print(test.data)

test.import_csv('tests/data/fowlers_gap/acworth_gw.csv', input_category=["GW","GW","GW"], utc_offset=10, unit=["M","mm","cm"], how="add", check_dublicates=True) 
test.import_csv('tests/data/fowlers_gap/acworth_bp.csv', input_category='BP', utc_offset=10,  unit=["hpa"], how="add", check_dublicates=False) 
test.import_csv('tests/data/fowlers_gap/acworth_bp.csv', input_category='BP', utc_offset=10,  unit="cm", how="add", check_dublicates=True) 
#test.import_csv('tests/data/fowlers_gap/acworth_et.csv', input_category='ET', utc_offset=10,  unit='nm/s^2', how="add", check_dublicates=True)

#out = test.data.dtf()
out = test.data

print(test.data.dtypes) #datetime must be datetime64[ns] not object
print(out.df_obj())

#%% test pivot to dt table with 2 categories and multiindex
pivot = test.data.dt_pivot()

#%%
dt = test.data.dt_zero()
dt2 = out.dt_num(dt_base="2000-12-30")
#%%
test2 = test.data.dropna(axis=0,how="any",subset=["value"]).reset_index(drop=True)
test3 = test.data.drop_nan()
"""
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
"""
#%%

