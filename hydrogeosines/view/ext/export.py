# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import pytz

class Export(object):
    
    def __init__(self, *args, **kwargs):
        pass  
        #add attributes specific to Visualize here
        
    #%%
    @staticmethod
    def export_FFT(loc, results, data, folder=False, info=None, **kwargs):
        print("Exporting location: {:s}".format(loc[0]))
        if 'unit' in info:
            unit = info['unit']
        et_unit = ''
        if 'ET_unit' in info:
            et_unit = info['ET_unit']
        filename = ''
        
        if loc[2] in ['GW', 'BP']:
            amp_header = 'Amplitude [{:s}]'.format(unit)
        else:
            amp_header = 'Amplitude [{:s}]'.format(et_unit)
        # the file ...
        file = pd.DataFrame({'Frequency [cpd]': results['freq'],
                 amp_header: np.abs(results['complex']),
                 'Phase [rad]': np.angle(results['complex']), })
    
        # write a file?
        if isinstance(folder, str):
            print(">> Writing file(s) to folder: {}".format(folder))
            filename = folder + "/" + "FFT_" + loc[0] + "_(" + loc[2]  + "," + str(loc[1]) + ").csv"
            file.to_csv(filename, index=False)
        
        return file.copy()
        
    #%%
    @staticmethod
    def export_HALS(loc, results, data, folder=False, info=None, **kwargs):
        print("Exporting location: {:s}".format(loc[0]))
        if 'unit' in info:
            unit = info['unit']
        et_unit = ''
        if 'ET_unit' in info:
            et_unit = info['ET_unit']
        filename = ''

        if loc[2] in ['GW', 'BP']:
            amp_header = 'Amplitude [{:s}]'.format(unit)
        else:
            amp_header = 'Amplitude [{:s}]'.format(et_unit)
        # the file ...
        file = pd.DataFrame({'Frequency [cpd]': results['freq'],
                 'Component': results['component'],
                 amp_header: np.abs(results['complex']),
                 'Phase [rad]': np.angle(results['complex']), })
        
        if isinstance(folder, str):
            print(">> Writing file(s) to folder: {}".format(folder))
            filename = folder + "/" + "HALS_" + loc[0] + "_(" + loc[2]  + "," + str(loc[1]) + ").csv"
            file.to_csv(filename, index=False)
        
        return file.copy()
    
    #%%
    @staticmethod
    def export_GW_correct(loc, results, data, folder=False, info=None, **kwargs):
        print("Exporting location: {:s}".format(loc[0]))
        # search for relevant info ...
        if 'utc_offset' in info:
            datetime = data.index.tz_convert(tz=pytz.FixedOffset(int(60*info['utc_offset']))).tz_localize(None)
            utc_offset = info['utc_offset']
        else:
            datetime = data.index.tz_localize(None)
            utc_offset = 0
        if 'unit' in info:
            unit = info['unit']
        et_unit = ''
        if 'ET_unit' in info:
            et_unit = info['ET_unit']
        
        # assemble the dataset ...
        # check if ET is present ...
        if "ET" in data.columns:
            file1 = pd.DataFrame({'Datetime [UTC{:+.2f}]'.format(utc_offset): datetime, 
                                 "Baro [{:s}]".format(unit): data.BP,
                                 "Earth tides [{:s}]".format(et_unit): data.ET,
                                 loc[0] + " [{:s}]".format(unit): data.GW,
                                 loc[0] + '_corrected [{:s}]'.format(unit): np.around(results['WLc'], 4)})
        else:
            file1 = pd.DataFrame({'Datetime [UTC{:+.2f}]'.format(utc_offset): datetime, 
                                 "Baro [{:s}]".format(unit): data.BP,
                                 loc[0] + " [{:s}]".format(unit): data.GW,
                                 loc[0] + '_corrected [{:s}]'.format(unit): np.around(results['WLc'], 4)})
        # save as CSV
        if 'dt_format' in kwargs:
            dt_format = kwargs['dt_format']
        else:
            dt_format = '%d/%m/%Y %H:%M:%S'
            
        #%% export the additional data ...
        # barometric response function ...
        file2 = pd.DataFrame({'Lag [hours]': results['brf']['lag'],
                             'IRC [-]': results['brf']['irc'],
                             'BRF [-]': results['brf']['brf'], })
        
        if isinstance(folder, str):
            print(">> Writing file(s) to folder: {}".format(folder))
            filename = folder + "/" + "GW_correct_" + loc[0] + "_(" + str(loc[1]) + ").csv"
            file1.to_csv(filename, index=False, date_format=dt_format)
            
            filename = folder + "/" + "GW_correct_BRF_" + loc[0] + "_(" + str(loc[1]) + ").csv"
            file2.to_csv(filename, index=False)
                
        # earth tide response function ...        
        if 'erf' in results:
            # which one ...
            if 'lag' in results['erf']:
                file3 = pd.DataFrame({'Lag [hours]': results['erf']['lag'],
                     'IRC [-]': results['erf']['irc'],
                     'ERF [-]': results['erf']['brf'], })
                
                if isinstance(folder, str):
                    filename = folder + "/"
                    filename += "GW_correct_ERF_" + loc[0] + "_(" + str(loc[1]) + ").csv"
                    file3.to_csv(filename, index=False)
                
            elif 'freq' in results['erf']:
                file3 = pd.DataFrame({'Frequency [cpd]': results['erf']['freq'],
                     'Components': results['erf']['components'],
                     'Amplitude [{:s}]'.format(et_unit): np.abs(results['erf']['complex']),
                     'Phase [rad]': np.angle(results['erf']['complex']), })
                
                if isinstance(folder, str):
                    filename = folder + "/"
                    filename += "GW_correct_ERF_" + loc[0] + "_(" + str(loc[1]) + ").csv"
                    file3.to_csv(filename, index=False)
            else:
                
                raise Warning("Earth tide results could not be exported!")
                    # prepare the filename ...
            
            return file1, file2, file3
        
        else:
            return file1, file2