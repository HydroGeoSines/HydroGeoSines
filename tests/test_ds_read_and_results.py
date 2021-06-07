# -*- coding: utf-8 -*-
"""
Created on Tue Apr 13 08:46:25 2021

@author: Daniel
"""
import numpy as np
## generally accessible constants
const = {}

# pressure conversion constants
const['_pucf'] = {'m': 1.0, 'dm': 0.1, 'cm': 0.01, 'mm': 0.001, 'pa': 0.00010197442889221, 'hpa': 0.010197442889221, 'kpa': 0.10197442889221, \
         'mbar': 0.010197442889221, 'bar': 10.197442889221, 'mmhg': 0.013595475598539, 'psi': 0.70308890742557, 'ft': 1200/3937, 'yd': 3600/3937, 'inch': 0.0254}

# plausible Earth tide units
const['_etunit'] = ['m**2/s**2', 'm/s**2', 'nm/s**2', 'str', 'nstr']

# the most common Earth tide frequencies found in groundwater pressure (Merritt, 2004; McMillan et al., 2019)
const['_etfqs'] = {'Q1': 0.893244, 'O1': 0.929536, 'M1': 0.966446, 'P1': 0.997262, 'S1': 1.0, 'K1': 1.002738, 'N2': 1.895982, 'M2': 1.932274, 'S2': 2.0, 'K2': 2.005476}
# the most common atmospheric tide frequencies (McMillan et al., 2019)
const['_atfqs'] = {'P1': 0.997262, 'S1': 1.0, 'K1': 1.002738, 'S2': 2.0, 'K2': 2.005476}

# Check if this is BE_Method state in DS_Development_V2    

#%%
input_category= ["GW","BP","ET"]
unit=["m","m","nstr"]

if any(cat in input_category for cat in ("GW","BP")):
    print(True)
    idx = [ic for ic, e in enumerate(np.array(input_category).flatten()) if e in ("GW","BP")]
    hgs.utils.check_affiliation([u.lower() for u in np.array(unit).flatten()[idx]], const['_pucf'].keys())
    print(idx)
#%%    
if "ET" in input_category:
    print(True)
    idx = [i for i, e in enumerate(input_category) if e == "ET"]
    hgs.utils.check_affiliation([u.lower() for u in np.array(unit).flatten()[idx]], const['_etunit'])
    print(idx)    
    
#%%
def unit_converter_vec(df,unit_dict : dict):  
        # adjust values based on a unit conversion factor dictionary
        return df.value*np.vectorize(unit_dict.__getitem__)(df.unit.str.lower())
    
def pucf_converter_vec(df,unit_dict : dict): # using vectorization        
    # convert pressure units for GW and BP into SI unit meter        
    idx     = df.category.isin(["GW","BP"]) & (df.unit != "m")
    df.loc[idx,"value"] = unit_converter_vec(df[idx],unit_dict) 
    unit    = np.where(idx, "m", df.unit) 
    return val, unit

#%%
out = pucf_converter_vec(data,unit_dict = const["_pucf"])
#%%    
idx = data.category.isin(["GW","BP"]) & (data.unit != "m")    
val = np.where(idx.values, data.hgs.unit_converter_vec(const['_pucf']),data.value) 
unit    = np.where(idx, "m", data.unit)

#%%
locs = [i[:-1] for i in list(comps.keys())]
unique_loc = [tuple(i) for i in np.unique(locs, axis=0)]

for abc in comps.keys():
    #print(abc)
    if unique_loc[0][0] in abc:
        print(abc)
        
#%%
out = [comps[i][0] for i in comps.keys()]
new_dict= dict.fromkeys(comps)
for key,val in zip(comps.keys(),out):
    new_dict[key] = val
    
test = pd.DataFrame.from_dict(new_dict,orient="index").reset_index().rename(columns={"level_0":"location","level_1":"part","level_2":"category"})
grouped = test.groupby(by=(["location","part"]))
for group, val in grouped:
    print(group)
    print(val)
    new = val[val["category"] == "BP"]
    
        