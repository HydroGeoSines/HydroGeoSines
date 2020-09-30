import hydrogeosines as hgs

#%% test the model
test = hgs.Site('TEST', geoloc=[141.762065, -31.065781, 160])

#%%
test.import_csv('test_data/fowlers_gap/acworth_short_2.csv',input_type="GW",utc_offset=10, unit="cm",method="add",check_dublicates=True) #, dt_fmt='%d/%m/%Y %H:%M'
print(test.data)
print(test.data.dtypes)

#%%
hello = test.data.decimate(2)
print(hello)
print(test.data)

#%%
hello = test.data.respl(300)
print(hello)
print(test.data)

#%%
hello = test.data.decimate(3600)
print(hello)

#%%
hello = test.data.kill_gaps(method='any')
print(hello)

#%%
hello = test.data.make_regular()
print(hello)

#%%
hello = test.correct()
print(hello)

#%%
test2 = test.data.fill_gaps()
print(test2)

#%%
# hello1 = test.calc_BE(method='acworth')
# print(hello1)

# hello1 = test.calc_BE(method='rau')
# print(hello1)

#%%
test.export_data('decimated.csv')
