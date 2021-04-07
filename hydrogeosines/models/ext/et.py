# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import pytz
import datetime as datetime
import os,sys

from pygtide import pygtide as pyg

from scipy.interpolate import interp1d

class ET(object):
    # define all class attributes here 
    #attr = attr
    et_unit = {-1: 'm**2/s**2', 0: 'nm/s**2', 1: 'mas', 2: 'mm', 3: 'mm', 4: 'nstr', 5: 'nstr', 6: 'nstr', 7: 'nstr', 8: 'nstr', 9: 'mm'}
    
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Load here
        #self.attribute = variable            
    
    def add_ET(self, et_comp='pot', et_cat=8, waves=None):
        if (et_comp == 'pot'):
            et_comp_i = -1
        elif(et_comp == 'g'):
            et_comp_i = 0
        else:
            raise Exception("Error: Keyword 'et_comp' must be 'pot' (potential) or 'g' (gravity)!")
        
        if (self.geoloc == None):
            raise Exception('Error: Geo-location (WGS84 longitude, latitude and height) must be set!')
            
        # check if PyGTide is available
        try:            
            # !!!!!!!!!!!!!!! really important !!!!!!!!!!!!!!!
            # change the current directory for PyGTide to work properly
            os.chdir('pygtide')
            # !!!!!!!!!!!!!!!!!
            # create a PyGTide object
            pt = pyg.pygtide()
            # convert to UTC
            dt_utc = self.data.hgs.dt.unique_utc
            # define the start date in UTC
            start = dt_utc.min().tz_localize(None).to_pydatetime()
            duration = ((dt_utc.max() - dt_utc.min()).days + 2)*24
            td = (dt_utc - pd.to_datetime('1899-12-30', utc=True)).dt
            dt_utc_tf = td.days + td.seconds/86400
            dt_utc_s = td.seconds
            # is this correct??
            samplerate = int(np.median(np.diff(dt_utc_s)))
            # set the recommended wave groups
            # as implemented in the wrapper
            if waves is None:
                pt.set_wavegroup()
            else:
                # pt.set_wavegroup(wavedata = np.array([[0.8, 2.2, 1., 0.]]))
                pt.set_wavegroup(wavedata = waves)
            pt.predict(self.geoloc[1], self.geoloc[0], self.geoloc[2], start, duration, samplerate, tidalcompo=et_comp_i, tidalpoten=et_cat)
            # retrieve the results as dataframe
            data = pt.results()
            # !!!!!!!!!!!!!! really important !!!!!!!!!!!!!!!
            # change working directory back to normal ...
            os.chdir('..')
            # print(data.iloc[:30, 0:3])
            # convert time to floating point for matching
            td = (data['UTC'] - pd.to_datetime('1899-12-30', utc=True)).dt
            et_utc_tf = td.days + td.seconds/86400
            # !!! to allow irregular time stamps, interpolate the Earth tide data (cubic spline)
            et_interp = interp1d(et_utc_tf, data.iloc[:, 1].values, kind='cubic')
            et = et_interp(dt_utc_tf)
            
            #######################################################
            # MERGE EARTH TIDES WITH LONG TABLE
            et_data = pd.DataFrame({'datetime': dt_utc, 'value': et})
            et_data['category'] = 'ET'
            et_data['location'] = 'ET'
            et_data['part'] = 'all'
            et_data['unit'] = self.et_unit[et_comp_i]
            # print(et_data.iloc[:30, 0:3])
            # kill existing ET values
            self.data = self.data.drop(self.data[self.data.category == 'ET'].index)
            # add new ET values
            self.data = self.data.append(et_data)
            # sort data in a standard way -> easier to read
            self.data = self.data.sort_values(by=["category","location"])
            # no dublicate indices
            self.data = self.data.reset_index(drop=True)
            # self.data = self.data.hgs.check_dublicates
            print("Earth tide time series were calculated and added ...")
            
            # !!!!!!!!!!!!!!!!!
        except ImportError:
            raise Exception('Error: The PyGTide module was not found!')
        pass
        
    def calc_ET_align(self, et_comp='pot', et_cat=8, waves=None, geoloc:list=None):
        """
        Method for hgs.DataFrame NOT Site as input. Best used on Site.data_regular.

        Parameters
        ----------
        et_comp : TYPE, optional
            DESCRIPTION. The default is 'pot'.
        et_cat : TYPE, optional
            DESCRIPTION. The default is 8.
        waves : TYPE, optional
            DESCRIPTION. The default is None.
        geoloc : list, optional
            DESCRIPTION. The default is None.

        Raises
        ------
        Exception
            DESCRIPTION.

        Returns
        -------
        out : TYPE
            DESCRIPTION.

        """
        if (et_comp == 'pot'):
            et_comp_i = -1
        elif(et_comp == 'g'):
            et_comp_i = 0
        else:
            raise Exception("Error: Keyword 'et_comp' must be 'pot' (potential) or 'g' (gravity)!")
        
        if (geoloc == None):
            raise Exception('Error: Geo-location (WGS84 longitude, latitude and height) must be set!')
        
        # !!!!!!!!!!!!!!! really important !!!!!!!!!!!!!!!
        # change the current directory for PyGTide to work properly
        os.chdir('pygtide')
        # !!!!!!!!!!!!!!!!!
        # create a PyGTide object
        pt = pyg.pygtide()
        # ! Conversion not utc not necessary -> done at import into site object
        # ! better write a check function for processing class whether dt of data is UTC
        # convert to UTC
        dt = self.hgs.pivot.index
        start = dt.min()
        stop  = dt.max()
        start_naive = start.tz_localize(None).to_pydatetime() 
        # get duration in hours
        duration = (dt.max() - dt.min())/pd.Timedelta(hours=1)+48
        td = dt - pd.to_datetime('1899-12-30', utc="UTC")
        #dt_tf = td.days + td.seconds/86400
        dt_s = td.seconds
        # is this correct??
        samplerate = int(np.median(np.diff(dt_s)))
        # set the recommended wave groups as implemented in the wrapper
        if waves is None:
            pt.set_wavegroup()
        else:
            # pt.set_wavegroup(wavedata = np.array([[0.8, 2.2, 1., 0.]]))
            pt.set_wavegroup(wavedata = waves)
        pt.predict(geoloc[1], geoloc[0], geoloc[2], start_naive, duration, samplerate, tidalcompo=et_comp_i, tidalpoten=et_cat)
        # retrieve the results as dataframe
        pt_data = pt.results()
        # !!!!!!!!!!!!!! really important !!!!!!!!!!!!!!!
        # change working directory back to normal ...
        os.chdir('..')
        # interpolate the Earth tide data for non uniform sampling (cubic spline)
        pt_data = pt_data.set_index("UTC")
        pt_data = pt_data.loc[start:stop,:]
        pt_data.iloc[:,1].interpolate(method="cubic", inplace = True)
        #######################################################
        # MERGE EARTH TIDES WITH LONG TABLE
        out = pd.DataFrame({'datetime': pt_data.index.values,
                            'category': "ET",
                            'location': "ET",
                            'part'    : "all",
                            'unit'    : ET.et_unit[et_comp_i],
                            'value'   : pt_data.iloc[:,1].values})
        print("Earth tide time series were calculated and added ...")
        return out
        

        

    
    