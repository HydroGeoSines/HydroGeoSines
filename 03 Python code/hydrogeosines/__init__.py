
# This package contains the base class and associated methods

__name__    = 'hydrogeosines'
__author__  = 'Todd Rasmussen, Gabriel Rau and Chris Turnadge'
__version__ = 1.0

import import_data
import preprocess
import process
import postprocess
import plot


class model:

    # Initialise model class
    def __init__(self):
        return
        

#=================================================================
#
# Groundwater pressure subroutines:
    
    # Obtain GW data
    def get_GW(self):
    	self.GW = import_data.get_GW(self)
    
    
    # Print GW data	
    def print_GW(self, number):
        print '%10s%10s'% ('time', 'pressure')
        for t,p in zip(self.GW.t, self.GW.p)[:number]:
	    print '%10.3f%10.3f'% (t,p)


    # Plot GW data (p vs t)	
    def plot_GW(self):
    	plot.plot_GW(self, pname=None)

    
    # Resample GW data
    def resample_GW(self, hours):
        self.GW = preprocess.resample_GW(self.GW, hours)
        
        
#=================================================================
#
# Barometric pressure subroutines:
    
    # Get BA data
    def get_BA(self):
    	self.BA = import_data.get_BA(self)

 
    # Print BA data
    def print_BA(self, number):
        print '%10s%10s'% ('time', 'pressure')
        for t,p in zip(self.BA.t, self.BA.p)[:number]:
	    print '%10.3f%10.3f'% (t,p)

 
    # Plot BA data (p vs t)
    def plot_BA(self):
    	plot.plot_BA(self, pname=None)
    
 
    # Resample BA data
    def resample_BA(self, hours):
        self.BA = preprocess.resample_BA(self.BA, hours)


#=================================================================
#
# DFT subroutines:
    
    # Calculate DFT of GW p data
    def calc_ft_GW(self):
        self.GW.frq, self.GW.amp, self.GW.phs = process.freq_domain.calc_ft_GW(self)
        

    # Calculate DFT of BA p data
    def calc_ft_BA(self):
        self.BA.frq, self.BA.amp, self.BA.phs = process.freq_domain.calc_ft_BA(self)
        
        
    # Plot DFT amplitude spectrum for GW p data         
    def plot_ft_avf_GW(self, pname):
        plot.plot_ft_avf_GW(self, pname)


    # Plot DFT phase versus amplitude for GW p data         
    def plot_ft_pva_GW(self, pname):
        plot.plot_ft_pva_GW(self, pname)


    # Plot DFT amplitude spectrum for BA p data
    def plot_ft_avf_BA(self, pname):
        plot.plot_ft_avf_BA(self, pname)
        
        
    # Plot DFT phase versus amplitude for BA p data         
    def plot_ft_pva_BA(self, pname):
        plot.plot_ft_pva_BA(self, pname)


#=================================================================
#
# Linear regression subroutines: 

    # Calculate linear regression (of GW p vs BA p) 
    def calc_linear_GW(self):
        process.time_domain.calc_linear(self)
        
        
    # Plot linear regression (of GW p vs BA p) 
    def plot_linregress(self, pname):
        plot.plot_linregress(self, pname)
        

#=================================================================
#
# Regression deconvolution subroutines: 

    # Calculate the regression deconvolution (of GW p vs BA p)
    def calc_regress_deconv(self):
	self.lags, self.crf, self.mag, self.phs = process.time_domain.calc_regress_deconv(self)


    # Plot cumulative response function
    def plot_regress_deconv_crf(self, pname):
        plot.plot_regress_deconv_crf(self, pname=None)        


    # Plot amplitude vs phase values (obtained from regression deconvolution)
    def plot_regress_deconv_pva(self, pname):
	plot.plot_regress_deconv_pva(self, pname)


