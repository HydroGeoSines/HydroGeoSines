import numpy as np
import pandas as pd
import inspect
import re
import pytz
from functools import reduce

from . import _time
from . import _series
from . import _model

#%% the data handling class
class data(_time.time, _series.series):
    def __init__(self, site, BP, GW, ET, results):
        self.site = site
        self.BP = BP
        self.GW = GW
        self.ET = ET
        self.results = results
        self.all = None
        self.method = None
        self.last_return = None
        pass

    #%% import GW data from file
    def import_csv(self, filepath, dt_col='datetime', dt_fmt='excel', bp_col='baro'):
        # self.GW = GW
        # load the csv file into variable
        filedata = pd.read_csv(filepath)
        # read the datetime column
        cols = filedata.columns.values
        # the new container to use
        data = pd.DataFrame()

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
            data['datetime'] = _time.time._excel2dt(filedata[dt_col])
        else:
            data['datetime'] = pd.to_datetime(filedata[dt_col], format=dt_fmt)

        #%% search for baro data
        reg = re.compile('^(baro\s*)\[([a-zA-Z]+)\]', re.IGNORECASE)
        baro_bool = np.array([bool(reg.match(col)) for col in filedata.columns])
        if any(baro_bool):
            baro_col = cols[baro_bool][0]
            if (reg.search(baro_col).group(2).lower() in self.site._pucf):
                pconv = self.site._pucf[reg.search(baro_col).group(2).lower()]
            else:
                raise Exception("Error: The Baro unit '" + reg.search(baro_col).group(2) + "' is unknown.")
        else:
            raise Exception('Error: A baro column and unit must be specific as [xx]!')
        data['{BP}'] = filedata[baro_col]*pconv

        #%% ADD EARTH TIDE COLUMN??
        reg = re.compile('^(et\s*)', re.IGNORECASE)
        et_bool = np.array([bool(reg.match(col)) for col in filedata.columns])
        if any(et_bool):
            et_col = cols[et_bool][0]
            data['{ET}'] = filedata[et_col]
        
        #%% LOAD GW DATA columns
        gw_cols = cols[(~dt_bool & ~baro_bool & ~et_bool)]
        if (len(gw_cols) > 0):
            for i in range(len(gw_cols)):
                wl = re.compile('(.*)\[([a-zA-Z]+)\]', re.IGNORECASE)
                if (wl.search(gw_cols[i]) == None):
                    raise Exception("Error: All data columns in the CSV file must have units, e.g. [mm]")
                else:
                    if (wl.search(gw_cols[i]).group(2).lower() in self.site._pucf):
                        unit = wl.search(gw_cols[i]).group(2).lower()
                        p_factor = self.site._pucf[unit]
                        name = wl.search(gw_cols[i]).group(1).strip()
                        data.loc[:, name] = filedata.loc[:, gw_cols[i]].values*p_factor

        # create index and sort
        data.set_index('datetime', inplace=True)
        data.index = data.index.tz_localize(tz=pytz.FixedOffset(int(60*utc_offset)))
        data.sort_index(inplace=True)
        self.all = data
        # free up some memory
        del data
        return self.all

    #%%
    def combine(self, mode='full', utc_offset=0, et=False):
        if et is True:
            et = self.ET
        if self.BP.main is None:
            raise Exception("Error: Please set the main barometric pressure!")
        print("Try to combine datasets ...")
        # turn datetime to UTC
        datasets = []
        for i, val in enumerate([self.BP.main] + self.GW.data):
            tmp = val.copy()
            tmp.index = tmp.index.tz_convert('UTC')
            datasets.append(tmp)

        if (mode == 'full'):
            self.all = reduce(lambda left,right: pd.merge(left,right,on=['datetime'], how='outer'), datasets)
        elif(mode == 'exact'):
            self.all = reduce(lambda left,right: pd.merge(left,right,on=['datetime'], how='inner'), datasets)
        else:
            raise Exception("Error: The combine method '" + method + "' does not exist!")
        
        # sort the dataframe
        self.all.sort_index(inplace=True)
        # add Earth tides if desired
        if et:
            tmp3 = et.calc(self.all)
            self.all.loc[:, 'et'] = tmp3.values
        # convert to desired time zone
        if (utc_offset != 0):
            self.all.index = self.all.index.tz_convert(tz=pytz.FixedOffset(int(60*utc_offset)))
        del tmp
        return self.all

    #%% This function uses
    def correct_heads(self, locs=None, lag_h=24, et=False, et_method='hals'):
        if locs is None:
            locs = self.gw
        results = pd.DataFrame(index=self.all.index)
        for i, loc in enumerate(locs):
            if not loc in list(self.gw):
                raise Exception("Error: Bore name '" + loc + "' is not in the dataset!")
                
            #%% perform regression deconvolution
            tmp1, tmp2 = _model.model.regress_deconv(self, self.tf, self.all[loc].values, self.all['{BP}'].values, lag_h=lag_h, et=et, et_method=et_method)
            results.loc[:, loc] = np.copy(tmp1)
            self.results.all = results
        return self.results.all
    
    #%%
    def calc_BE(self, locs=None, method='acworth'):
        self.method = {'function': inspect.currentframe().f_code.co_name}
        if locs is None:
            locs = self.gw
        # test that all locations are available
        for i, loc in enumerate(locs):
            if not loc in list(self.gw):
                raise Exception("Error: Bore name '" + loc + "' is not in the dataset!")
        
        #%% ----------------------------------------------------------------------------------------------
        #% Perform BE calculation according to Acworth et al. (2016)
        if method is 'acworth':
            m2_idx = list(self.site._etfqs.keys()).index("M2")
            s2_idx = list(self.site._etfqs.keys()).index("S2")
            # BP data: detrend followed by apes
            bp_detr, tmp = _model.model.lin_window_ovrlp(self, self.tf.values, self.all['{BP}'].values)
            bp_mod, bp_apes = _model.model.hals(self, self.tf.values, bp_detr)
            # ET data: no need to detrend
            # ???????????????????????????
            # here we could use M2 and S2 components from Earth tides only!!!!!
            # ???????????????????????????
            et_mod, et_apes = _model.model.hals(self, self.tf.values, self.all['{ET}'].values)
            BE_val = {}
            for i, loc in enumerate(locs):
                # perform detrend
                gw_detr, tmp = _model.model.lin_window_ovrlp(self, self.tf.values, self.all[loc].values)
                # perform apes
                gw_mod, gw_apes = _model.model.hals(self, self.tf.values, gw_detr)
                # calculate BE from spectral details
                del_phi = et_apes['phi'][s2_idx] -  bp_apes['phi'][s2_idx]
                BE = (gw_apes['alpha'][s2_idx] + et_apes['alpha'][s2_idx]*np.cos(del_phi)*(gw_apes['alpha'][m2_idx]/et_apes['alpha'][m2_idx]))/bp_apes['alpha'][s2_idx]
                # updat ethe results object
                BE_val.update({loc: np.around(BE, 3)})
            return BE_val
            
        elif method is 'MoR':
            pass
        else:
            raise Exception("Error: Be method '" + method + "' is not available!")
        