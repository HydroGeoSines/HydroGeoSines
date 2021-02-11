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

# TODO: 
#data_GW = csiro.get_gw_data
#data_resample = data.hgs.resample(freq = 5)
# datetime methods
data.hgs.dt.to_num

#%% Processing
process_csiro = hgs.Processing(Site = csiro_site)
hals_results  = process_csiro.hals()
be_results  = process_csiro.BE()

#%% Data preparation
data = csiro_site.data
test = data.iloc[379000:].reset_index(drop = True)
test2 = data.iloc[258000:260000].reset_index(drop = True)
test = test.append(test2, ignore_index= True)
# large gaps
test.loc[100:200,"value"] = np.nan
test.loc[1000:1250,"value"] = np.nan
test.loc[3900:4150,"value"] = np.nan

# small gaps
test.loc[50:60,"value"] = np.nan
test.loc[250:270,"value"] = np.nan
test.loc[350:380,"value"] = np.nan
test.loc[750:800,"value"] = np.nan
test.loc[3050:3080,"value"] = np.nan
test.loc[3550:3600,"value"] = np.nan

#%% Most common frequency (MCF)
mcf = test.copy()
mcf = mcf.hgs.filters.drop_nan # only needed for test data due to the ignore_index in append
#TODO: replace non_valid entries? Dublicates already handled at import
spl_freqs = mcf.hgs.spl_freq_groupby
mcf = mcf.hgs.resample_by_group(spl_freqs)
#%% gap interpolation
limit = 60*60 #1h interpolation limit
mcf.set_index("datetime",inplace=True)
inter = mcf.interpolate(method="time",limit = int(limit/spl_freqs.values), limit_area="inside") # not working, as gaps that are larger than the limit, area also partially filled
#%% gap identifier
gap = mcf.value.copy()
df_cumsum = gap.isnull().astype(int).groupby(gap.notnull().astype(bool).cumsum()).cumsum()
df_sum = gap.isnull().astype(int).groupby(gap.notnull().astype(bool).cumsum()).sum()
mask = gap.isnull()
#%%
mcf = test.copy()
out = []
for i in range(len(spl_freqs)):
    print(i)
    # check for index labels in df
    a = mcf.loc[:,mcf.hgs.filters.obj_col].isin(spl_freqs.index[i]).all(axis=1)
    temp = mcf[a].groupby(mcf.hgs.filters.obj_col).resample(str(int(spl_freqs[i]))+"S", on="datetime").mean()
    temp.reset_index(inplace=True)
    out.append(temp) 
out = pd.concat(out,axis=0,ignore_index=True,join="inner",verify_integrity=True) 
# reorganize index and column structure to match original hgs dataframe
out = out.reset_index()[mcf.columns]
    #mcf_new = mcf[a]
    #a = (a == a[:, [0]]).all(axis=1) 
#mask = df.groupby(["location","category","unit"]).apply(lambda x: gap_mask(x,maxgap))
 
#%%
def upsample(df, method = "time"):
   df = df.set_index("datetime")
   df = df.interpolate(method=method).reset_index()
   return df

#TODO: get amount of total interpolated data points (percent) -> raise exception
def make_regular(df, inter_max: int = 3600, block_min: int = 30, method = "backfill"):
    # find most common frequency (mcf)
    spl_freqs = df.hgs.spl_freq_groupby
    # resample to mcf
    mcfs = df.hgs.resample_by_group(spl_freqs)
    ## identify gaps
    # interpolate gaps smaller than maxgap
    grouped = mcfs.groupby(df.hgs.filters.obj_col)  
    out = [] 
    for name, group in grouped:
        print(name)                
        #print(group)
        # get mcf for group
        mcf_group = spl_freqs.xs(name)
        maxgap = inter_max/mcf_group
        # create mask for gaps
        s = group["value"]
        mask = gap_mask(s,maxgap)
        # choose interpolation (runs on datetime index)
        inter = upsample(group[mask],method=method)
        ## identify large gaps, split df and reassamble
        # get minimum block_size (n_entries)
        block_size = mcf_group*block_min
        # location splitter
        inter = location_splitter(inter,block_size, inter_max)

        # split into sub_locations
        
        # resample and check for remaining nan (should be none)
        #inter = inter.hgs.resample(mcf_group) 
        out.append(inter)

    out = pd.concat(out,axis=0,ignore_index=True,join="inner",verify_integrity=True) 
    # reorganize index and column structure to match original hgs dataframe
    out = out.reset_index()[df.columns]    
    return out
#TODO: if first entry is np.nan, this is not backfilled with "time" method
out = make_regular(test,inter_max = 3600)    

#%%  
import string
alpha = list(string.ascii_lowercase)

df = out2[1].copy()
  
def location_splitter(df, blocksize, inter_max):
    diff = df.datetime.diff()
    # find gaps larger than inter_max
    mask = diff.dt.total_seconds() >= inter_max
    idx = diff[mask].index # get start index of data block
    # split index into blocks
    blocks = np.split(df.index, idx, axis=0)
    # apply minimum blocksize
    blocks = [block for block in blocks if len(block) > blocksize]
    # list of new data frames
    list_df = [df.iloc[i] for i in blocks]
    # concat df back with new column for "slot"
    out = []
    for i in range(len(list_df)):
        print(i+1)
        new_df = list_df[i].copy()
        new_df["part"] = str(i+1)
        out.append(new_df)
        
    return out , mask, blocks, idx


a,b,c,d = location_splitter(df,30,3600)
#%%    
def gap_mask(s, maxgap):
    """
    Mask NaN gaps larger than a maxium gap size

    Parameters
    ----------
    s : pandas Series
        DESCRIPTION.
    maxgap : int
        DESCRIPTION.

    Returns
    -------
    numpy array
        Boolean mask of size s for all NaN gaps larger than maxgap

    """
    idx = s.isnull().astype(int).groupby(s.notnull().astype(bool).cumsum()).sum()
    sizes = idx[idx > 0] # size of gaps
    start = sizes.index + (sizes.cumsum() - sizes) # get start index
    stop  = start + sizes # get stop index
    gaps = [np.arange(a,b) for a,b in zip(start,stop)] # get indices of each individual gap
    
    ## create a mask for the gap sizes
    mask = np.zeros_like(s)
    for gap in gaps:
        mask[gap] = len(gap)    

    return (mask < maxgap) | s.notnull().to_numpy()

mask = mcf.copy()

x = mcf["value"]
mask["value"] = gap_mask(x, 12)

#def interpolate_time(df):
    
inter = mcf[mask["value"]].interpolate(method="backfill")  
inter = inter.reset_index()#[self._obj.columns]
inter = inter.hgs.resample_by_group(spl_freqs)  

#%%
length = df_sum[df_sum > 0] # length of gaps
start = length.index + (length.cumsum() - length) # identify location of gaps
#c = df2.index + (df2.cumsum() - df2)
g_td = ((gap.iloc[b+a-1].index - gap.iloc[b].index))


#%%
def bfill_nan(arr):
    """ Backward-fill NaNs """
    mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[0]), mask.shape[0]-1)
    idx = np.minimum.accumulate(idx[::-1], axis=0)[::-1]
    out = arr[idx]
    return out


def calc_mask(arr, maxgap):
    """ Mask NaN gaps longer than `maxgap` """
    isnan = np.isnan(arr)
    cumsum = np.cumsum(isnan).astype('float')
    diff = np.zeros_like(arr)
    diff[~isnan] = np.diff(cumsum[~isnan], prepend=0)
    diff[isnan] = np.nan
    diff = bfill_nan(diff)
    return (diff < maxgap) | ~isnan


mask = mcf.copy()

x = mcf["value"].values
mask["value"] = calc_mask(x, 12)
inter2 = mcf[mask["value"]].interpolate(method="time",limit = int(limit/spl_freqs.values), limit_area="inside")  
inter2 = inter.reset_index()#[self._obj.columns]
inter2 = inter.hgs.resample_by_group(spl_freqs)  
#%% hgs methods


#no_nan2 = data.dropna(how="any")
diff = data[data.location == "Baro"].datetime.diff()
most_common = diff.value_counts().idxmax()
#test = diff.apply(lambda x: x.apply(pd.value_counts).idxmax())
spl_freqs = data.hgs.spl_freq_groupby
resampled = data.hgs.resample_by_group(spl_freqs)
diff2 = resampled[resampled.location == "Site_C"].datetime.diff()
print(diff2.value_counts())
#%%
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
"""
#%%

