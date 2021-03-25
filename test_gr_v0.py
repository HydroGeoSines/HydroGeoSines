import hydrogeosines as hgs

#%%  Testing MVC principal
## MODEL
acworth_site = hgs.Site('acworth', geoloc=[141.762065, -31.065781, 160])	
print(acworth_site.data)

#%%
acworth_site.import_csv('tests/data/fowlers_gap/acworth_gw.csv', input_category=["GW","BP","GW"], utc_offset=10, unit=["Cm","mm","M"], how="add", check_dublicates=True) 
acworth_site.import_csv('tests/data/fowlers_gap/acworth_bp.csv', input_category='BP', utc_offset=10,  unit=["Hpa"], how="add", check_dublicates=False) 
acworth_site.import_csv('tests/data/fowlers_gap/acworth_bp.csv', input_category='BP', utc_offset=10,  unit="Cm", how="add", check_dublicates=True) 
#acworth_site.import_csv('tests/data/fowlers_gap/acworth_et.csv', input_category='ET', utc_offset=10,  unit='nm/s^2', how="add", check_dublicates=True)
#acworth_site.import_csv('test_data/fowlers_gap/acworth_short_gaps.csv', utc_offset=10, input_type=["BP", 'GW', 'GW', 'GW', 'ET'], unit=["m", 'm', 'm', 'm', 'nm/s^2'], method="add", check_dublicates=True) #, dt_fmt='%d/%m/%Y %H:%M'

#%%
## Model
acworth_site = hgs.Site('acworth', geoloc=[141.762065, -31.065781, 160])
# read
acworth_site.import_csv('tests/data/fowlers_gap/acworth_gw.csv', 
                        input_category=["GW","BP","GW"], 
                        utc_offset=10, unit=["Cm","mm","M"], loc_names = ["Site_A","Site_B","Site_C"],
                        how="add", check_dublicates=True)

# data
data = acworth_site.data
# hgs methods
data.hgs.resample(freq = 5)
# datetime methods
data.hgs.dt.to_num

#%%
print(data.hgs.dt.to_utc)
print(data.hgs.dt.unique)

#%%
acworth_site.add_ET()
data = acworth_site.data

#%% Processing
process_acworth = hgs.Processing(acworth_site)
hals_results  = process_acworth.hals()


