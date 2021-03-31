# -*- coding: utf-8 -*-
"""
Created on Fri Mar 19 12:22:07 2021

@author: Daniel
"""

#%% Load HGS and packages for testing
import numpy as np
import pandas as pd
import string
import collections.abc

import hydrogeosines as hgs


#%% Load Site Data
# Site Model
csiro_site = hgs.Site('csiro', geo=[141.762065, -31.065781, 160])
# Import
csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_GW_short.csv', 
                        input_category=["GW"]*3, 
                        utc_offset=10, unit=["m"]*3, loc_names = ["Site_A","Site_B","Site_C"],
                        how="add", check_dublicates=True) 

csiro_site.import_csv('tests/data/csiro/test_sample/CSIRO_BP_short.csv', 
                        input_category="BP", 
                        utc_offset=10, unit="mbar", loc_names = "Baro",
                        how="add", check_dublicates=True) 

#%% Test Data preparation
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

#%% Update function
def dict_update(d, u):
    for k, v in u.items():
        if isinstance(v, collections.abc.Mapping):
            d[k] = dict_update(d.get(k, {}), v)
        else:
            d[k] = v
    return d

#%% dict test
dict_test = {'Site_A': {'hals': 
                        {'BP': {'amp': [4.94468387e-04, 9.80648608e-04, 4.92825494e-04, 7.11063149e-06, 4.52898606e-06], 
                                'phs': [ 2.66415026, -0.65681186,  2.30896196,  2.98585062, -1.74334083], 
                                'comps': ['P1', 'S1', 'K1', 'S2', 'K2'], 
                                'freq': [0.997262, 1.0, 1.002738, 2.0, 2.005476]}, 
                         'GW': {'amp': [3.11592374e-08, 3.61990672e-08, 7.33833690e-08, 7.20057653e-07, 9.93940518e-07, 6.40781621e-07, 1.54480364e-08, 1.08472761e-08, 2.11143146e-07, 2.18627645e-07], 
                                'phs': [ 0.81561956,  2.5385584 , -1.81883362,  0.40186264,  2.54960733, -1.29069296,  0.88704074, -2.52994764, -3.13964303, -1.7573962 ], 
                                'comps': ['Q1', 'O1', 'M1', 'P1', 'S1', 'K1', 'N2', 'M2', 'S2', 'K2'], 
                                'freq': [0.893244, 0.929536, 0.966446, 0.997262, 1.0, 1.002738, 1.895982, 1.932274, 2.0, 2.005476]}}},
             'Site_B': {'hals': 
                        {'BP': {'amp': [4.94468387e-04, 9.80648608e-04, 4.92825494e-04, 7.11063149e-06, 4.52898606e-06], 
                                'phs': [ 2.66415026, -0.65681186,  2.30896196,  2.98585062, -1.74334083], 
                                'comps': ['P1', 'S1', 'K1', 'S2', 'K2'], 
                                'freq': [0.997262, 1.0, 1.002738, 2.0, 2.005476]}, 
                         'GW': {'amp': [2.65165669e-08, 6.60019353e-08, 4.62957736e-08, 5.84872627e-07, 6.90948826e-07, 4.52041034e-07, 2.70511113e-08, 2.11415333e-08, 2.33646876e-07, 1.95959477e-07], 
                                'phs': [-0.9056961 ,  2.32349482, -1.94498209,  0.64102506,  2.72597334, -1.19525426,  0.98973575, -2.04675664, -2.87449096, -1.7268479 ], 
                                'comps': ['Q1', 'O1', 'M1', 'P1', 'S1', 'K1', 'N2', 'M2', 'S2', 'K2'], 
                                'freq': [0.893244, 0.929536, 0.966446, 0.997262, 1.0, 1.002738, 1.895982, 1.932274, 2.0, 2.005476]}}}, 
            'Site_C': {'hals': 
                       {'BP': {'amp': [4.94468387e-04, 9.80648608e-04, 4.92825494e-04, 7.11063149e-06, 4.52898606e-06], 
                               'phs': [ 2.66415026, -0.65681186,  2.30896196,  2.98585062, -1.74334083], 
                               'comps': ['P1', 'S1', 'K1', 'S2', 'K2'], 
                               'freq': [0.997262, 1.0, 1.002738, 2.0, 2.005476]}, 
                        'GW': {'amp': [1.26798283e-08, 4.37604695e-08, 5.57754935e-08, 5.39046687e-07, 7.49613985e-07, 5.36668219e-07, 1.95947859e-08, 1.58628403e-08, 1.57152892e-07, 2.14909851e-07], 
                               'phs': [ 0.68999533,  1.92818049, -2.14752126,  0.38076106,  2.28478752, -1.51585643,  0.66528869, -2.18753303,  3.09696833, -1.8898132 ], 
                               'comps': ['Q1', 'O1', 'M1', 'P1', 'S1', 'K1', 'N2', 'M2', 'S2', 'K2'], 
                               'freq': [0.893244, 0.929536, 0.966446, 0.997262, 1.0, 1.002738, 1.895982, 1.932274, 2.0, 2.005476]}}}}
#%%
dict_new = {"Site_A": {'hals': {'BP': {'amp': [0.0, 1.0, 5.0, 1.0, 0]}}},
            "Site_B": {'hals': {'GW': {'amp': [0.0, 1.0, 2.0, 1.0, 0]}}}
            }
dict_update(dict_test,dict_new)
    #%% Define Function for non-valid entries
def non_valid():
    pass
 
#%% Upsampling method
def upsample(df, method = "time"):
   df = df.set_index("datetime")
   df = df.interpolate(method=method).reset_index(drop=True)
   return df

#%% Testing apply function of groupby with multiple arguments
def f_apply_test(group,period=5):
    group['pct']=group['value'].pct_change(periods=period)*100
    return group    
print(data.groupby('location').apply(f_apply_test,period=2))    

#%% backward fill nan based on numpy (Stack Overflow)
def bfill_nan(arr):
    """ Backward-fill NaNs """
    mask = np.isnan(arr)
    idx = np.where(~mask, np.arange(mask.shape[0]), mask.shape[0]-1)
    idx = np.minimum.accumulate(idx[::-1], axis=0)[::-1]
    out = arr[idx]
    return out

#%% Gap mask method prepared for general Tools    
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

#%%  method that splits location into parts if too many consecutive Nan values occure
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

#a  = location_splitter(out,30,3600)
#%% Gap filler method for small and large gaps based on criteria
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

#%% Make regular method for remove all gaps in data by upsampling and splitting of large junks
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

align_out  = BP_align(beta2, inter_max = 3600, method = "backfill", inter_max_total = 10)

#%% Method testing

# Most common frequency (MCF)
mcf = test.copy()
mcf = mcf.hgs.filters.drop_nan # only needed for test data due to the ignore_index in append
#TODO: replace non_valid entries? Dublicates already handled at import
spl_freqs = mcf.hgs.spl_freq_groupby
mcf = mcf.hgs.resample_by_group(spl_freqs)

# gap mask method
mask = mcf.copy()
x = mcf["value"]
mask["value"], counter = gap_mask(x, 12)

# interpolate method with masked data   
inter = mcf[mask["value"]].interpolate(method="backfill")  
inter = inter.reset_index()#[self._obj.columns]
inter = inter.hgs.resample_by_group(spl_freqs) 