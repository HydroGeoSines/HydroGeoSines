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

#%%
## Model
csiro_site = hgs.Site('csiro', geo=[141.762065, -31.065781, 160])
# read
csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_GW_short.csv',
                        input_category=["GW"]*3,
                        utc_offset=10, unit=["m"]*3, loc_names = ["Site_A","Site_B","Site_C"],
                        how="add", check_dublicates=True)

csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_BP_short.csv',
                        input_category="BP",
                        utc_offset=10, unit="mbar", loc_names = "Baro",
                        how="add", check_dublicates=True)

#data_GW = csiro.get_gw_data
# data
data = csiro_site.data
# hgs methods
data_resample = data.hgs.resample(freq = 5)
# datetime methods
data.hgs.dt.to_num

#%% Processing
process_csiro = hgs.Processing(csiro)
hals_results  = csiro.hals()

## Processing
# create Instance of Processing with csiro_site
process_csiro = hgs.Processing(csiro_site)
# create Instance of Processing for specific locations of csiro_site
locations = ["Site_A","Site_B"]
process_csiro_SiteA_B = hgs.Processing(csiro_site).by_gwloc(locations)
hals_results  = process_csiro.hals()
#be_results  = process_csiro.BE()




#%% filter upsampling with gap_mask (included in make_regular)
mask = mcf.copy()
x = mcf["value"]
mask, counter = hgs.utils.gap_mask(x,12)

group = mcf[mask].hgs.upsample(method="backfill")


#%% Example and Ideas on MVC Paradigm
"""
## MODEL
mountain_data   = hgs.Data().import_csv()
mountain_site   = hgs.Site('MOUNTAIN', geoloc=[141.762065, -31.065781, 160])

# add data
mountain_site.import_csv('test_data/fowlers_gap/acworth_short_gaps.csv', utc_offset=10, input_type=["BP", 'GW', 'GW', 'GW', 'ET'], unit=["m", 'm', 'm', 'm', 'nm/s^2'], method="add", check_dublicates=True))

## CONTROLLER
hals_wf         = hgs.Processing.hals()
## VIEW
#terminal_output = hgs.TerminalOutput()

# Trennung von Daten und Logik, damit die Objekte nicht so riesig werden
# NICHT: hals_wf.site.do_something()
data_result = hals_wf.process_site_data(mountain_site.data)
terminal_output.print_data(data_result)
# ODER (falls Daten "behalten" werden sollen)
mountain_site.preprocessed['hals'] = hals_wf.process_site_data(mountain_site.data)
#
gw_data = mountain_site.gw_data ## INSTEAD: mountain_site.get_gw_data() <- METHOD

#___

filter_result = SiteFilter.by_location('loc')['datetime']
is_reg = filter_result.is_reguar # ()
# generischer Ansatz: Site.by('location').where('loc')

site1.set_path('fr.csv');
site1.load_csv();
site1.get_data();

MVC mäßig:

site1 = Site('Freiburg');
site1.load('freiburg.csv');

data = SiteController(site1).by_location('fr').process()

View().visualize(data);




#%%
print(acworth_site.data.dtypes) #datetime must be datetime64[ns] not object
print(out.df_obj)

#%% acworth_site pivot to dt table with 2 categories and multiindex
pivot = acworth_site.data.dt_pivot()

#%%
dt = acworth_site.data.dt_zero()
dt2 = out.dt_num(dt_base="2000-12-30")
#%%
test2 = acworth_site.data.dropna(axis=0,how="any",subset=["value"]).reset_index(drop=True)
test3 = acworth_site.data.drop_nan()
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
