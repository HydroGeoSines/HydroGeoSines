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
import numpy as np
import pandas as pd
data = csiro_site.data.copy()
test = data.iloc[379000:].copy().reset_index(drop = True)
test2 = data.iloc[258000:262000].copy().reset_index(drop = True)
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


# Full data test set with gaps
data2 = csiro_site.data.copy()
data2.loc[12000:12500,"value"] = np.nan # BP value gap
data2.loc[30000:32000,"value"] = np.nan
data2.loc[151000:155000,"value"] = np.nan
data2.loc[300000:302000,"value"] = np.nan
# add dummy category
data2.loc[302000:303000,"category"] = "ET"

#%% Testing methods in hgs pandas
#new = data.groupby(data.hgs.filters.obj_col).apply(gap_routine,inter_max_total=90).reset_index(drop=True)
out2 = data2.hgs.make_regular(spl_freq=1200) #inter_max = 3600,part_min=20,category="GW",spl_freq=1200
out2 = out2.hgs.BP_align() # inter_max = 3600, method = "backfill", inter_max_total = 10
out3 = out2.hgs.pivot

# check if any BP entry is null and if for any row all the GW entries are null
if (out3["BP"].isnull().any().bool() == False) and (out3["GW"].isnull().all().any() == False):
    print("Now every GW entry has exactly one matching BP entry")
else:
    print("Ups, something went wrong in the data aligning process!")    
    
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
def make_regular(df, inter_max: int = 3600, part_min: int = 20, method: str = "backfill", category = "GW", spl_freq: int = None, inter_max_total: int= 10):
    """
    

    Parameters
    ----------
    df : pd.DataFrame
        Site data.
    inter_max : int, optional
        Maximum of interpolated time interval in seconds. The default is 3600.
    part_min : int, optional
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
        regular = mcfs.groupby(df.hgs.filters.obj_col).apply(gap_routine, mcf=spl_freq, inter_max = inter_max, part_min = part_min, 
                                  method = method, inter_max_total= inter_max_total).reset_index(drop=True)        
        # reassamble DataFrame          
        regular = pd.concat([regular,df],ignore_index=True)  
    
    else:
        print("No Gaps")
        regular = pd.concat([mcfs,df],ignore_index=True)
    return regular
    
#TODO: if first entry is np.nan, this is not backfilled with "time" method
out = make_regular(test,inter_max = 3600,part_min=0.2, method="backfill")  
#out2 = make_regular(test3,inter_max = 3600,part_min=0.2) # no gaps 
#beta = make_regular(data,inter_max = 3600,part_min=30,category="GW",spl_freq=1200)    
beta2 = make_regular(data2,inter_max = 3600,part_min=20,category="GW",spl_freq=1200)  

#%% align method
mcf_bp = test_BP.copy()
#TODO: replace non_valid entries? Dublicates already handled at import
spl_freqs_bp = mcf_bp.hgs.spl_freq_groupby
mcf_bp = mcf_bp.hgs.resample_by_group(spl_freqs_bp)

# merge does not work, because columns are attached
df_merge = pd.merge(out,mcf_bp,how="left", on = "datetime") 

filter_bp = mcf_bp.datetime.isin(out.datetime)
bp_data = mcf_bp.loc[filter_bp,:]
#mcf_bp.datetime.isin(["2001-03-28 07:50:00+00:00"])
#%%

def f(group,period=5):
    group['pct']=group['value'].pct_change(periods=period)*100
    return group    
print(data.groupby('location').apply(f,period=2))    

#%%
def BP_align(df, inter_max:int = 3600, method: str ="backfill", inter_max_total:int = 10):
    
    bp_data= df.hgs.filters.get_bp_data  
    gw_data= df.hgs.filters.get_gw_data
    df = df[~df["category"].isin(["GW","BP"])]
    # asign part label to bp_data
    if "part" in bp_data.columns: 
        bp_data["part"] = bp_data["part"].fillna("0")
    # category drop function is available in hgs filters
    #TODO: Check for non-valid values, create function for this
    
    # resample to most common frequency
    spl_freqs = bp_data.hgs.spl_freq_groupby
    bp_data = bp_data.hgs.resample_by_group(spl_freqs)
    
    # use GW datetimes as filter for required BP data
    filter_gw = bp_data.datetime.isin(gw_data.datetime)
    bp_data = bp_data.loc[filter_gw,:]
    # check for np.nan
    while bp_data.hgs.filters.is_nan:
        ## identify small gaps
        # group by identifier columns of site data
        bp_data = bp_data.groupby(bp_data.hgs.filters.obj_col).apply(gap_routine, mcf=spl_freqs, inter_max = inter_max, 
                                  method = method, inter_max_total= inter_max_total, split_location=False).reset_index(drop=True)   
        # resample to get gaps that are larger then max_gap
        bp_data = bp_data.hgs.resample(spl_freqs)
        # return datetimes that can not be interpolated because gaps are too big
        datetimes = bp_data.loc[np.isnan(bp_data["value"]),"datetime"]
        
        gw_data = gw_data[~gw_data.datetime.isin(datetimes)]
            # resample to most common frequency
        spl_freqs_gw = gw_data.hgs.spl_freq_groupby
        gw_data = gw_data.hgs.resample_by_group(spl_freqs_gw)
        gw_data = gw_data.groupby(gw_data.hgs.filters.obj_col).apply(gap_routine, mcf=spl_freqs_gw, inter_max = inter_max, 
                                  method = method, inter_max_total= inter_max_total, split_location=True).reset_index(drop=True) 
        
        filter_gw = bp_data.datetime.isin(gw_data.datetime)
        bp_data = bp_data.loc[filter_gw,:]
    #gw_data = gw_data.hgs.resample_by_group(spl_freqs_gw) 
    out = pd.concat([gw_data, bp_data, df],axis=0,ignore_index=True)
    return out

#align_data = pd.concat([beta2,test_BP],axis=0)
align_out  = BP_align(beta2, inter_max = 3600, method = "backfill", inter_max_total = 10)
#%% Gap filler

def gap_routine(group, mcf:int = 300, inter_max:int = 3600, part_min: int = 20, method: str = "backfill", inter_max_total: int= 10, split_location=True):
    """
    

    Parameters
    ----------
    group : pd.DataFrame
        HGS DataFrame with "location" column.
    mcf : int, optional
        Most common frequency. The default is 300.
    inter_max : int, optional
        Maximum timedelta in seconds to be interpolated. The default is 3600.
    part_min : int, optional
        Minimum size of location part as timedelta in days. The default is 20.
    method : str, optional
        Interpolation method for upsampling to inter_max. The default is "backfill".
    inter_max_total : int, optional
        Maximum percentage threshold of values to be interpolated. The default is 10.
    split_location : TYPE, optional
        Activate location splitting for large gaps. The default is True.

    Raises
    ------
    Exception
        DESCRIPTION.
    exception
        DESCRIPTION.

    Returns
    -------
    group : pd.Dataframe
        HGS DataFrame with all gaps due to null values being removed.

    """
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
        print("{:.2f} % of the '{}' data was interpolated due to gaps < {}s!".format((counter/len(s)*100),
                                                                                     group["location"].unique()[0],inter_max))
    else:
        raise Exception("Error: Interpolation limit of {:.2f} % was exceeded!")
    ## interpolate gaps smaller than maxgap
    # choose interpolation (runs on datetime index)
    group = upsample(group[mask],method=method)
    if split_location:
        ## identify large gaps, split group and reassamble
        # get minimum part_size (n_entries)
        part_size = int(part_min/(mcf_group/(60*60*24)))
        # location splitter for "part" column
        group = location_splitter(group,part_size=part_size, dt_threshold=inter_max)  
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

def location_splitter(df:pd.DataFrame, part_size:int = 30, dt_threshold:int = 3600):
    """
    Split dataframe into multiple parts using a maximum timedelta threshold. 

    Parameters
    ----------
    df : pd.DataFrame
        HGS DataFrame with "location" column.
    part_size : int, optional
        Minimum size of the location data subset. The default is 30.
    dt_threshold : int, optional
        Maximum timedelta threshold. The default is 3600.

    Returns
    -------
    df : pd.DataFrame
        Original dataframe with an additional column for location "parts".

    """
    diff = df.datetime.diff()
    # find gaps larger than td_threshold
    mask = diff.dt.total_seconds() >= dt_threshold
    idx = diff[mask].index # get start index of data block
    # split index into blocks
    blocks = np.split(df.index, idx, axis=0)
    # apply minimum blocksize
    blocks = [block for block in blocks if len(block) > part_size]
    if len(blocks) == 0:
        print("Not enough data for '{}' to ensure minimum part size!".format(df.location.unique()[0]))
        return pd.DataFrame(columns=df.columns)
    else:    
        # list of new data frames
        list_df = [df.iloc[i,:] for i in blocks]
        # add new column for location "parts"
        for i, val in enumerate(list_df):
            if "part" not in val.columns: 
                # use character string format
                val.insert(3,"part",str(i+1))    
            else:
                val.loc[val["part"] != np.nan,"part"] = str(i+1)
        # concat df back with new column for "part"         
        if len(list_df) == 1:
            return list_df[0]
        else:
            return pd.concat(list_df,ignore_index=True,axis=0)

a  = location_splitter(out,30,3600)
#%% gap mask    
def gap_mask(s:pd.Series, maxgap:int):
    """
    Mask NaN gaps that fall below a maxium gap size and also returns a counter.

    Parameters
    ----------
    s : pd.Series
        A Series with null entries
    maxgap : int
        Maximum number of consecutive null entries that are marked as True.

    Returns
    -------
    mask: numpy array
        Boolean mask of size s, which is False for all null(NaN) gaps larger then maxgap
    counter: int
        Number of null entries marked as True     

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
mask = mcf.copy()
x = mcf["value"]
mask, counter = gap_mask(x,12)

group = mcf[mask].hgs.upsample(method="backfill") 

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
mountain_site.import_csv('test_data/fowlers_gap/acworth_short_gaps.csv', utc_offset=10, input_type=["BP", 'GW', 'GW', 'GW', 'ET'], unit=["m", 'm', 'm', 'm', 'nm/s^2'], method="add", check_dublicates=True)

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

#MVC mäßig:
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

