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
#data.hgs.dt.to_num

#%% Processing
process_csiro = hgs.Processing(csiro_site)
hals_results  = process_csiro.hals()
#be_results  = process_csiro.BE()

#%% Data preparation
data = csiro_site.data.copy()
test = data.iloc[379000:].reset_index(drop = True)
test2 = data.iloc[258000:262000].reset_index(drop = True)
test = test.append(test2, ignore_index= True)
# large gaps
test.loc[100:200,"value"] = np.nan
test.loc[1000:1250,"value"] = np.nan
test.loc[3900:4150,"value"] = np.nan
test.loc[4500:4750,"value"] = np.nan


# small gaps
test.loc[50:60,"value"] = np.nan
test.loc[250:270,"value"] = np.nan
test.loc[350:380,"value"] = np.nan
test.loc[750:800,"value"] = np.nan
test.loc[3050:3080,"value"] = np.nan
test.loc[3550:3600,"value"] = np.nan

# Test set 2 for BP data
# index start 20289
test_BP = data.loc[data["category"]=="BP",:].copy()
test_BP.loc[20300:20310,"value"] = np.nan
test_BP.loc[20400:20410,"value"] = np.nan
test_BP.loc[20500:20550,"value"] = np.nan
test_BP.loc[20875:20900,"value"] = np.nan

# Test 3 no gaps
test3 = data.iloc[380000:-4].reset_index(drop = True)
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

#%% Define Function for non-valid entries
def non_valid():
    pass
 
#%% Upsample method
def upsample(df, method = "time"):
   df = df.set_index("datetime")
   df = df.interpolate(method=method).reset_index()
   return df

#%% make regular method
def make_regular(df, inter_max: int = 3600, block_min: int = 20, method: str = "backfill", category = "GW", spl_freq: int = None, inter_max_total: int= 10):
    """
    

    Parameters
    ----------
    df : pd.DataFrame
        Site data.
    inter_max : int, optional
        Maximum of interpolated time interval in seconds. The default is 3600.
    block_min : int, optional
        Minimum record duration in days. The default is 20.
    method : str, optional
        Interpolation method of Pandas to be used. The default is "backfill".
    category : str, array or list, optional
        Site category. The default is "GW".

    Returns
    -------
    out : pd.DataFrame
        DESCRIPTION.

    """
    # only use specified data category which is GW by default
    pos = df["category"].isin(np.array(category).flatten())
    df_reg = df.loc[pos,:].copy()
    # keep rest of data to reassemble original dataset
    df = df.drop(df_reg.index)
    # use custom sampling frequency
    if spl_freq is not None:
        # use predefined sampling frequency
        mcfs = df_reg.hgs.resample(spl_freq)
    else:    
        # find most common frequency (mcf)
        spl_freq = df_reg.hgs.spl_freq_groupby
        # resample to mcf
        mcfs = df_reg.hgs.resample_by_group(spl_freq)
    
    ## check for NaN in value Column
    if mcfs.hgs.filters.is_nan:        
        ## identify small and large gaps
        # group by identifier columns of site data
        regular = mcfs.groupby(df.hgs.filters.obj_col).apply(lambda x: gap_routine(x, mcf=spl_freq, inter_max = inter_max, block_min = block_min, 
                                  method = method, inter_max_total= inter_max_total))          
        # reassamble DataFrame          
        regular = pd.concat([regular,df],ignore_index=True)  
    
    else:
        print("No Gaps")
        regular = pd.concat([mcfs,df],ignore_index=True)
    return regular
    
#TODO: if first entry is np.nan, this is not backfilled with "time" method
#out = make_regular(test,inter_max = 3600,block_min=0.2, method="backfill")  
#out2 = make_regular(test3,inter_max = 3600,block_min=0.2) # no gaps 
beta = make_regular(data,inter_max = 3600,block_min=30,category="GW",spl_freq=1200)    

#def f(group):
#    regular = gap_routine(group, mcf=mcf_group, inter_max = inter_max, block_min = block_min, 
#                                  method = method, inter_max_total= inter_max_total) 
#    return group    
#print df.groupby('country').apply(f)

#%% align method
mcf_bp = test_BP.copy()
#TODO: replace non_valid entries? Dublicates already handled at import
spl_freqs_bp = mcf_bp.hgs.spl_freq_groupby
mcf_bp = mcf_bp.hgs.resample_by_group(spl_freqs_bp)

# merge does not work, because columns are attached
df_merge = pd.merge(out,mcf_bp,how="left", on = "datetime") 

filter_bp = mcf_bp.datetime.isin(out.datetime)
bp_data = mcf_bp.loc[filter_bp,:]
# check for np.nan
if bp_data.hgs.filters.is_nan:
    pass
    
#mcf_bp.datetime.isin(["2001-03-28 07:50:00+00:00"])

def BP_align(df):
    bp_data= df.hgs.filters.get_bp_data  
    gw_data= df.hgs.filters.get_gw_data
    #TODO: Check for non-valid values, create function for this
    
    # resample to most common frequency
    spl_freqs = bp_data.hgs.spl_freq_groupby
    mcfs = bp_data.hgs.resample_by_group(spl_freqs)
    
    # use GW datetimes as filter for required BP data
    filter_gw = mcfs.datetime.isin(gw_data.datetime)
    bp_data = mcf_bp.loc[filter_gw,:]
    
    # check for np.nan
    if bp_data.hgs.filters.is_nan:
        ## identify small gaps
        # group by identifier columns of site data
        grouped = mcfs.groupby(df.hgs.filters.obj_col)  
        out = [] 
        for name, group in grouped:           
            print(name)
            mcf_group = spl_freqs.xs(name)
            regular = gap_routine(group, mcf=mcf_group, inter_max = inter_max, inter_max_total= inter_max_total, method = method, split_location=False)    
            # append new dataframes
            out.append(regular)
        
        # reassamble DataFrame    
        out = pd.concat(out,axis=0,ignore_index=True,join="inner",verify_integrity=True)        
        out = pd.concat([out,df],ignore_index=True) 
        pass
    else:
        return bp_data

#%% Gap filler

def gap_routine(group, mcf:int = 300, inter_max:int = 3600, block_min: int = 20, method: str = "backfill", inter_max_total: int= 10, split_location=True):
            print(group.name)
            # get mcf for group
            if isinstance(mcf,int):
                mcf_group = mcf
            elif isinstance(mcf,pd.Series):    
                mcf_group = mcf.xs(group.name)
            else:
                raise Exception("Error: Wrong format for mcf in gap_routine!")
            maxgap = inter_max/mcf_group
            # create mask for gaps
            s = group["value"]
            mask, counter = gap_mask(s,maxgap)
            # use count of masked values to check ratio
            #TODO: raise exception
            if counter/len(s)*100 <= inter_max_total:
                print("{:.2f} % of the '{}' data was interpolated due to gaps < {}s!".format((counter/len(s)*100),group["location"].unique()[0],inter_max))
            else:
                raise Exception("Error: Interpolation limit of {:.2f} % was exceeded!")
            ## interpolate gaps smaller than maxgap
            # choose interpolation (runs on datetime index)
            group = upsample(group[mask],method=method)
            if split_location:
                ## identify large gaps, split group and reassamble
                # get minimum block_size (n_entries)
                block_size = int(block_min/(mcf_group/(60*60*24)))
                # location splitter for "part" column
                group = location_splitter(group,block_size, inter_max)  
            else: 
                pass
            # check for remaining nan (should be none)
            if group.hgs.filters.is_nan:
                print("Caution! Methods was not able to remove all NaN!")
            else:
                pass
            return group     
#%%  
import string
alpha = list(string.ascii_lowercase)

df = out[1].copy()
df = df.iloc[250:,:].reset_index()
  
def location_splitter(df, block_size:int = 30, inter_max:int = 3600):
    """
    

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    block_size : int, optional
        DESCRIPTION. The default is 30.
    inter_max : TYPE
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    diff = df.datetime.diff()
    # find gaps larger than inter_max
    mask = diff.dt.total_seconds() >= inter_max
    idx = diff[mask].index # get start index of data block
    # split index into blocks
    blocks = np.split(df.index, idx, axis=0)
    # apply minimum blocksize
    blocks = [block for block in blocks if len(block) > block_size]
    if len(blocks) == 0:
        print("Not enough data for '{}' to ensure minimum data block size!".format(df.location.unique()[0]))
        return None
    else:    
        # list of new data frames
        list_df = [df.iloc[i,:] for i in blocks]
        # add new column for location "parts"
        for i, val in enumerate(list_df):
            # use character string format
            val.insert(3,"part",str(i+1))       
        # concat df back with new column for "part"         
        if len(list_df) == 1:
            return list_df[0]
        else:
            return pd.concat(list_df,ignore_index=True,axis=0) 

a  = location_splitter(df,300,3600)
#%% gap mask    
def gap_mask(s, maxgap:int):
    """
    Mask NaN gaps larger than a maxium gap size

    Parameters
    ----------
    s : pandas Series
        DESCRIPTION.
    maxgap : int
        Maximum number of consecutive interpolated entries.

    Returns
    -------
    mask: numpy array
        Boolean mask of size s, which is False for all NaN gaps larger than maxgap
    counter: int
        Number of interpolated values    
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

    return (mask < maxgap) | s.notnull().to_numpy(), np.count_nonzero(np.logical_and(mask > 0, mask < maxgap))

mask = mcf.copy()

x = mcf["value"]
mask["value"], counter = gap_mask(x, 12)

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

