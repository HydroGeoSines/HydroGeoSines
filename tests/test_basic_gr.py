import hydrogeosines as hgs

#%%  Testing MVC principal
## MODEL
acworth_site = hgs.Site('acworth', geo=[141.762065, -31.065781, 160])
print(acworth_site.data)

#%%
acworth_site.import_csv('tests/data/fowlers_gap/acworth_gw.csv', input_category=["GW","BP","GW"], utc_offset=10, unit=["Cm","mm","M"], how="add", check_dublicates=True)
acworth_site.import_csv('tests/data/fowlers_gap/acworth_bp.csv', input_category='BP', utc_offset=10,  unit=["Hpa"], how="add", check_dublicates=False)
acworth_site.import_csv('tests/data/fowlers_gap/acworth_bp.csv', input_category='BP', utc_offset=10,  unit="Cm", how="add", check_dublicates=True)
#acworth_site.import_csv('tests/data/fowlers_gap/acworth_et.csv', input_category='ET', utc_offset=10,  unit='nm/s^2', how="add", check_dublicates=True)
#acworth_site.import_csv('test_data/fowlers_gap/acworth_short_gaps.csv', utc_offset=10, input_type=["BP", 'GW', 'GW', 'GW', 'ET'], unit=["m", 'm', 'm', 'm', 'nm/s^2'], method="add", check_dublicates=True) #, dt_fmt='%d/%m/%Y %H:%M'

#%% Processing
process_acw = hgs.Processing(acworth_site)

#%%
fft_results  = process_acw.fft()
fft_results  = process_acw.fft(cat='BP')

hals_results  = process_acw.hals()
