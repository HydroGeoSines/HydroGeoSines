#%% hydrogeoscience under development
from types import MethodType
import numpy as np
import datetime as dt
import pandas as pd
import inspect
import re
import pytz

# import other sub-classes
from . import _time
from . import _BP
from . import _GW
from . import _ET
from . import _data
from . import _results
from . import _method

from . import _const
const = _const.const

# from . import models
# https://code.activestate.com/recipes/577504/

class site(object):

    def __init__(self, name, geoloc=None, *args, **kwargs):
        super(site, self).__init__(*args, **kwargs)

        # the site name
        self.name = name
        
        if geoloc is not None:
            if not isinstance(geoloc, (list, np.ndarray)):
                raise Exception("Error: Input 'geoloc' must be a list with 3 values: Longitude, latitude, height in WGS84!")
            if (geoloc[0] < -180) or (geoloc[0] > 180) or (geoloc[1] < -90) or (geoloc[1] > 90) or (geoloc[2] < -1000) or (geoloc[2] > 8500):
                raise Exception("Error: Input 'geoloc' must contain valid geo-coordinates in WGS84!")
            self.geoloc = geoloc
        else:
            self.geoloc = None
        
        # load the data object into the class
        self.data = _data.data()
        
        self.results = _results.results()
        
        self.brf = pd.DataFrame()
        self.erf = pd.DataFrame()
    
    #%% import GW data from file
    def import_csv(self, filepath, dt_col='datetime', dt_fmt='excel', bp_col='baro'):        
        # clear dataframe if not empty
        # this avoids issues with overriding
        if not self.data.empty:
            self.data = _data.data()
        
        # load the csv file into variable
        filedata = pd.read_csv(filepath)
        # read the datetime column
        cols = filedata.columns.values
        # the new container to use
        
        #%% check for valid datetime column
        reg = re.compile('^datetime\s*\[UTC([\+\-0-9\.]+)\]', re.IGNORECASE)
        dt_bool = np.array([bool(reg.match(col)) for col in filedata.columns])
        if any(dt_bool):
            dt_col = cols[dt_bool][0]
            utc_offset = float(reg.search(dt_col).group(1))
        else:
            raise Exception('Error: Datetime column must exist and contain UTC offset specified as [UTC+\-hh]!')
        # decide on the date time format
        if (dt_fmt == 'excel'):
            self.data['datetime'] = _time.time._excel2dt(filedata[dt_col])
        else:
            self.data['datetime'] = pd.to_datetime(filedata[dt_col], format=dt_fmt)

        #%% search for baro data
        reg = re.compile('^(baro\s*)\[([a-zA-Z]+)\]', re.IGNORECASE)
        baro_bool = np.array([bool(reg.match(col)) for col in filedata.columns])
        if any(baro_bool):
            baro_col = cols[baro_bool][0]
            if (reg.search(baro_col).group(2).lower() in const['_pucf']):
                pconv = const['_pucf'][reg.search(baro_col).group(2).lower()]
            else:
                raise Exception("Error: The Baro unit '" + reg.search(baro_col).group(2) + "' is unknown.")
        else:
            raise Exception('Error: A baro column and unit must be specific as [xx]!')
        self.data['{BP}'] = filedata[baro_col]*pconv

        #%% ADD EARTH TIDE COLUMN??
        reg = re.compile('^(et\s*)\[([a-zAZ0-9\/\^\+\-\*]+)\]', re.IGNORECASE)
        et_bool = np.array([bool(reg.match(col)) for col in filedata.columns])
        if any(et_bool):
            et_col = cols[et_bool][0]
            self.data['{ET}'] = filedata[et_col]
            # print(reg.match(et_col).group(2))
            self.data.ET_unit = reg.match(et_col).group(2)
        
        #%% LOAD GW DATA columns
        gw_cols = cols[(~dt_bool & ~baro_bool & ~et_bool)]
        if (len(gw_cols) > 0):
            for i in range(len(gw_cols)):
                wl = re.compile('(.*)\[([a-zA-Z]+)\]', re.IGNORECASE)
                if (wl.search(gw_cols[i]) == None):
                    raise Exception("Error: All data columns in the CSV file must have units, e.g. [mm]")
                else:
                    if (wl.search(gw_cols[i]).group(2).lower() in const['_pucf']):
                        unit = wl.search(gw_cols[i]).group(2).lower()
                        p_factor = const['_pucf'][unit]
                        name = wl.search(gw_cols[i]).group(1).strip()
                        self.data.loc[:, name] = filedata.loc[:, gw_cols[i]].values*p_factor

        # create index and sort
        self.data.set_index('datetime', inplace=True)
        self.data.index = self.data.index.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset)))
        self.data.sort_index(inplace=True)
        return self.data

    #%% This function uses
    def correct(self, locs=None, lag_h=24, et=False, et_method='ts'):
        if locs is None:
            locs = self.data.gw_names
        
        for i, loc in enumerate(locs):
            if not loc in list(self.data.gw_names):
                raise Exception("Error: Bore name '" + loc + "' is not in the dataset!")
        
        ET = None
        if (et_method == 'ts'):
            if ('{ET}' in self.data.columns):
                ET = self.data.et
            else:
                et_emthod = 'hals'
            
        #%% prepare the new dataframe
        # clear dataframe if not empty
        # this avoids issues with overriding
        if not self.results.empty:
            self.results = _results.results()
        
        self.results['datetime'] = self.data.index
        self.results.set_index('datetime', drop=True, inplace=True)
        
        #%% perform regression deconvolution
        for i, loc in enumerate(locs):
            tmp1, tmp2 = _method.method.regress_deconv(self, self.data.tf, self.data[loc].values, self.data.bp.values, ET=ET, lag_h=lag_h, et=et, et_method=et_method)
            self.results.loc[:, loc] = np.copy(tmp1)
            
            #%% store the BRF results
            if 'Lag_time[h]' not in self.brf:
                self.brf.loc[:, 'Lag_time[h]'] = tmp2['brf']['lag']
            self.brf.loc[:, loc] = tmp2['brf']['crf']
            self.brf.loc[:, loc + '_std'] = tmp2['brf']['crf_stdev']
            
            #%% store the ET results
            if et:
                # the time series results
                if et_method == 'ts':
                    if 'Lag_time[h]' not in self.erf:
                        self.erf.loc[:, 'Lag_time[h]'] = tmp2['erf']['lag']
                    self.erf.loc[:, loc] = tmp2['erf']['crf']
                    self.erf.loc[:, loc + '_std'] = tmp2['erf']['crf_stdev']
                    pass
                # the harmonic results
                elif et_method == 'hals':
                    if 'Freq[cpd]' not in self.erf:
                        self.erf.loc[:, 'Freq[cpd]'] = tmp2['erf']['freq']
                    
                    # match ET names from inbuilt dirctionary, if possible
                    self.erf.loc[:, 'ET_name'] = ''
                    et_vals = const['_etfqs'].values()
                    for i, row in self.erf.iterrows():
                        for j in const['_etfqs']:
                            if row['Freq[cpd]'] == const['_etfqs'][j]:
                                self.erf.loc[i, 'ET_name'] = j
                    # set the results
                    self.erf.loc[:, loc + '_amp'] = np.abs(tmp2['erf']['comp'])
                    self.erf.loc[:, loc + '_phi'] = np.angle(tmp2['erf']['comp'])
                else:
                    raise Exception("Error: Earth tide method '" + etmethod + "' does not exist!")
                
        return self.results
    
    #%%
    def calc_BE(self, locs=None, method='acworth'):
        self.method = {'function': inspect.currentframe().f_code.co_name}
        if locs is None:
            locs = self.data.gw_names
        # test that all locations are available
        for i, loc in enumerate(locs):
            if not loc in list(self.data.gw_names):
                raise Exception("Error: Bore name '" + loc + "' is not in the dataset!")
        
        #%% ----------------------------------------------------------------------------------------------
        #% Perform BE calculation according to Acworth et al. (2016)
        if method == 'acworth':
            m2_idx = list(const['_etfqs'].keys()).index("M2")
            s2_idx = list(const['_etfqs'].keys()).index("S2")
            # BP data: detrend followed by hals
            bp_detr, tmp = _method.method.lin_window_ovrlp(self, self.data.tf.values, self.data.bp.values)
            bp_mod, bp_hals = _method.method.hals(self, self.data.tf.values, bp_detr)
            et_mod, et_hals = _method.method.hals(self, self.data.tf.values, self.data.et.values)
            BE_val = {}
            for i, loc in enumerate(locs):
                # perform detrend
                gw_detr, tmp = _method.method.lin_window_ovrlp(self, self.data.tf.values, self.data[loc].values)
                # perform hals
                gw_mod, gw_hals = _method.method.hals(self, self.data.tf.values, gw_detr)
                # calculate BE from harmonic components
                del_phi = np.angle(et_hals['comp'][s2_idx]) -  np.angle(bp_hals['comp'][s2_idx])
                BE = (np.abs(gw_hals['comp'][s2_idx]) + np.abs(et_hals['comp'][s2_idx])*np.cos(del_phi)*(np.abs(gw_hals['comp'][m2_idx])/np.abs(et_hals['comp'][m2_idx])))/np.abs(bp_hals['comp'][s2_idx])
                # updat ethe results object
                BE_val.update({loc: np.around(BE, 3)})
            return BE_val
        
        #%% ----------------------------------------------------------------------------------------------
        #% Perform BE calculation according to Acworth et al. (2016)
        if method == 'rau':
            m2_idx = list(const['_etfqs'].keys()).index("M2")
            s2_idx = list(const['_etfqs'].keys()).index("S2")
            # BP data: detrend followed by hals
            bp_detr, tmp = _method.method.lin_window_ovrlp(self, self.data.tf.values, self.data.bp.values)
            bp_mod, bp_hals = _method.method.hals(self, self.data.tf.values, bp_detr)
            et_mod, et_hals = _method.method.hals(self, self.data.tf.values, self.data.et.values)
            BE_val = {}
            for i, loc in enumerate(locs):
                # perform detrend
                gw_detr, tmp = _method.method.lin_window_ovrlp(self, self.data.tf.values, self.data[loc].values)
                # perform hals
                gw_mod, gw_hals = _method.method.hals(self, self.data.tf.values, gw_detr)
                # calculate BE from harmonic components
                gw_et_s2 = (gw_hals['comp'][m2_idx]/et_hals['comp'][m2_idx])*et_hals['comp'][s2_idx]
                gw_at_s2 = gw_hals['comp'][s2_idx] - gw_et_s2
                BE = np.abs(gw_at_s2/bp_hals['comp'][s2_idx])
                # updat ethe results object
                BE_val.update({loc: np.around(BE, 3)})
            return BE_val
        elif method == 'MoR':
            pass
        else:
            raise Exception("Error: Be method '" + method + "' is not available!")

    #%% export to CSV
    def export_results(self, filename, utc=False, et=False, bp=False, bp_unit='m', gw_unit='m', digits=4):
        if filename is None:
            raise Exception("Error: Export must have a valid filename!")
        bp_unit = bp_unit.lower()
        if bp_unit not in const['_pucf']:
            raise Exception("Error: Barometric pressure unit must be valid!")
        gw_unit = gw_unit.lower()
        if gw_unit not in const['_pucf']:
            raise Exception("Error: Groundwater pressure unit must be valid!")
        
        #%% prepare the dataset
        if self.results.empty:
            raise Exception("Error: Results have not been calculated!")
        else:
            tmp = self.results.copy()
            # rename GW columns
            locs = self.results.columns
            for i, loc in enumerate(locs):
                if gw_unit != 'm':
                    tmp.loc[:, loc] /= const['_pucf'][gw_unit]
                tmp.rename(columns={loc: loc + '[' + gw_unit + ']'}, inplace=True)
    
            # export barometric pressure?
            if bp:
                tmp.loc[:, '{BP}'] = self.data.bp
                # rename barometric pressure column
                if '{BP}' in tmp:
                    if bp_unit != 'm':
                        tmp.loc[:, '{BP}'] /= const['_pucf'][bp_unit]
                    tmp.rename(columns={'{BP}': 'BP[' + bp_unit + ']'}, inplace=True)
            
            # export earth tides?
            if et:
                tmp.loc[:, '{ET}'] = self.data.et
                # rename barometric pressure column
                if '{ET}' in tmp:
                    tmp.rename(columns={'{ET}': 'ET[' + self.data.ET_unit + ']'}, inplace=True)
                
            # add the datetime column to the results
            if utc:
                tmp.insert(0, 'Datetime[UTC]', self.data.time_str(utc=True).values)
            else:
                tmp.insert(0, 'Datetime[UTC{:+.1f}]'.format(self.data.dt_utc), self.data.ts.values)
                
            # write to file
            if digits is None:
                tmp.to_csv(filename, index=False)
            else:
                tmp.to_csv(filename, index=False, float_format='%.' + str(digits) + 'f')
            # del tmp
            return tmp
    
    #%% export to CSV
    def export_data(self, filename, utc=False, et=True, bp=True, bp_unit='m', gw_unit='m', digits=None):
        if filename is None:
            raise Exception("Error: Export must have a valid filename!")
        bp_unit = bp_unit.lower()
        if bp_unit not in const['_pucf']:
            raise Exception("Error: Barometric pressure unit must be valid!")
        gw_unit = gw_unit.lower()
        if gw_unit not in const['_pucf']:
            raise Exception("Error: Groundwater pressure unit must be valid!")
        
        #%% prepare the dataset
        tmp = self.data.copy()
        # rename GW columns
        locs = self.data.gw_names
        for i, loc in enumerate(locs):
            if gw_unit != 'm':
                tmp.loc[:, loc] /= const['_pucf'][gw_unit]
            tmp.rename(columns={loc: loc + '[' + gw_unit + ']'}, inplace=True)
        
        # export barometric pressure?
        if bp:
            # rename barometric pressure column
            if '{BP}' in tmp:
                if bp_unit != 'm':
                    tmp.loc[:, '{BP}'] /= const['_pucf'][bp_unit]
                tmp.rename(columns={'{BP}': 'BP[' + bp_unit + ']'}, inplace=True)
        else:
            tmp.drop('{BP}', 1, inplace=True)
        
        # export earth tides?
        if et:
            # rename barometric pressure column
            if '{ET}' in tmp:
                tmp.rename(columns={'{ET}': 'ET[' + self.data.ET_unit + ']'}, inplace=True)
        else:
            tmp.drop('{ET}', 1, inplace=True)
            
        # add the datetime column to the results
        if utc:
            tmp.insert(0, 'Datetime[UTC]', self.data.time_str(utc=True).values)
        else:
            tmp.insert(0, 'Datetime[UTC{:+.1f}]'.format(self.data.dt_utc), self.data.ts.values)
            
        # write to file
        if digits is None:
            tmp.to_csv(filename, index=False)
        else:
            tmp.to_csv(filename, index=False, float_format='%.' + str(digits) + 'f')
        # del tmp
        return tmp
    