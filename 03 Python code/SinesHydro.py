
import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

class betco: 
    # Define each analysis as a betco object, to which datasets can be 
    # included and methods (i.e. subroutines) can be applied.

    
    class preproc:        
        # Define all pre-processing steps within a subclass here.
        # This is where datasets are added, units are defined, outliers are 
        # removed, gaps are filled, detrending is performed, and equivalent 
        # freshwater head values are calculated.
        
        def __init__(self):
            return

        class import_: 
            # Define data import subroutines as functions contained within 
            # this subclass.    
            
            def __init__(self):
                return

            def Pgw(self, filename):  
                # Function to import groundwater pressure data; need to 
                # specify units, and whether vented or non-vented logger used.
                try:
                    #Pgw = import(filename)
                    return Pgw
                except Exception as error:
                    return error

            def Pba(self, filename): 
                # Function to import barometric pressure data; need to specify 
                # units.
                try:
                    #Pba = import(filename)
                    return Pba
                except Exception as error:
                    return error

            def rainfall(self, filename): 
                # Function to import rainfall data (for mechanical loading 
                # analysis?); # need to specify units
                try:
                    #rfl = import(filename)
                    return rfl
                except Exception as error:
                    return error

            def stage(self, filename): 
                # Function to import surface water stage data (for orthotide 
                # analysis?); need to specify units.
                try:
                    #stg = import(filename)
                    return stg
                except Exception as error:
                    return error

            def extraction(self, filename): 
                # Function to import groundwater extraction data (what for?); 
                # need to specify units.
                try:
                    #ext = import(filename)
                    return ext
                except Exception as error:
                    return error
       
        def remove_outliers(self, dataset, threshold, direction): 
            # Function to remove outliers from input data, belongs to 
            # "preproc" subclass.
            if direction==LT:
                return dataset[dataset<threshold]
            elif direction==GT:
		return dataset[dataset>threshold]
            else:
		return error

        def fill_gaps(self, dataset):
            # Function to fill gaps in input data using linear interpolation;
            # belongs to "preproc" subclass.
            return interpolate(dataset)

        def detrend_linear(self, dataset): 
            # Function to remove linear trend from input data, belongs to 
            # "preproc" subclass.
            # (Could include other detrending methods; e.g. moving average?)
            slope, intercept = regression(dataset)
            return dataset - slope*range(len(dataset))+intercept

        def resample(self, dataset, frequency): 
            # Function to resample input data from one frequency to another, 
            # either up-sampling or down-sampling.
            return

        def match_manual(self, dataset, manual_obs):
            # Function to match logger observations to manual measurements at 
            # specified times.
            return

        def calc_delta(self, dataset): 
            # Function to calculate temporal derivative of input data.
            return diff(dataset)

        def calc_fwhead(): 
            # Function to convert groundwater pressure data to equivalent 
            # freshwater head values.
            # (why?)
            return
 
 
    class proc: 
        # Define all data processing (i.e. analysis) steps within a subclass 
        # here. This is where time domain (i.e. regression deconvolution) and 
        # frequency domain (e.g. DFT) analyses are performed.
        
        def __init__(self):
            return

        class time_domain:
            # Define subclass for all time domain analysis methods.
                
            def __init__(self):
                return

            def calc_linear(self): 
                # Function to estimate linear trend (i.e. slope and intercept) 
                # via linear regression.
                return
                
            def calc_nonlin(self):
                return
            
            def regression_deconvolution(self): 
                # Function to assemble and perform regression deconvolution.
                return

            def extract_fns(self):
                return
                
            def calc_amps(self):
                return

        class freq_domain: 
            # Define subclass for all frequency domain analysis methods.
        
            def __init__(self):
                return

            class dft: 
                # Define subclass containing all discrete Fourier Transform 
                # analyses.
                
                def __init__(self):
                    return

                def calc_amplitude(self): 
                    # Function to calculate amplitudes of all available 
                    # frequencies.
                    return
                
                def calc_phase(self):
                    # Function to calculate phases of all available 
                    # frequencies.
                    return
                
            class cwt: 
                # Define subclass containing all continuous wavelet transform 
                # analyses.
                
                def __init__(self):
                    return

                def calc_amps(self):
                    return
                    

    class postproc:
        # Define all post-processing steps within a subclass here. These 
        # mainly relate to comparisons between outputs, rather than the 
        # generation of outputs.
    
        def __init__(self):
            return

        def estimate_params(self):
            return
            
        def compare_amps(self):
            return
            
        def compare_heads(self):
            return


    class plot: 
        # Define all figure plotting subroutines within a subclass here.
    
        def __init__(self):
            return
           
        def time_pressure(self):
            # Plot pressure (y) versus time (x).
            return

        def frequency_amplitude(self): 
            # Plot amplitude (y) versus frequency (x).
            return

        def frequency_phase(self): 
            # Plot phase (y) versus frequency (x).
            return

        def amplitude_phase(self): 
            # Plot phase (y) versus amplitude (x).
            return
