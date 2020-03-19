
# This package contains subroutines for the preprocessing of datasets


'''
Subroutines for future inclusion:

# Resample GW data
def resample_GW(self, hours): 
    print self.GW.p#[self.GW.t%hours==0]
    print self.GW.t#[self.GW.t%hours==0]
    return self.GW


# Resample BA data    
def resample_BA(self, hours): 
    self.BA.p = self.BA.p[self.BA.t%hours==0]
    self.BA.t = self.BA.t[self.BA.t%hours==0]
    return self.BA


# Remove data outliers    
def remove_outliers(self, dataset, threshold, direction): 
    # Function to remove outliers from input data, belongs to 
    # "preproc" subclass.
    if direction==LT:
        return dataset[dataset<threshold]
    elif direction==GT:
	return dataset[dataset>threshold]
    else:
	return error


# Fill data gaps using linear interpolation
def fill_gaps(self, dataset):
    return interpolate(dataset)


# Remove linear trend
def detrend_linear(self, dataset): 
    slope, intercept = regression(dataset)
    return dataset - slope*range(len(dataset))+intercept
    # Could include other detrending methods; e.g. moving average?
    

# Match manual measurements via offsets
def match_manual(self, dataset, manual_obs):
    return


# Calculate temporal derivative of input data
def calc_delta(self, dataset): 
    return diff(dataset)

def calc_fwhead(): 
    # Function to convert groundwater pressure data to equivalent 
    # freshwater head values.
    # (why?)
    return
'''