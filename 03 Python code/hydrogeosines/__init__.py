
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
    def plot_GW(self, pname):
    	plot.plot_GW(self, pname)

    
    # Resample GW data
    def resample_GW(self, hours):
        self.GW = preprocess.resample_GW(self.GW, hours)

    
    # Calculate temporal derivatives of GW data 
    def calc_delta_GW(self):
        self.GW.dp = preprocess.calc_delta_GW(self)
           
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
    def plot_BA(self, pname):
    	plot.plot_BA(self, pname)
    
 
    # Resample BA data
    def resample_BA(self, hours):
        self.BA = preprocess.resample_BA(self.BA, hours)


    # Calculate temporal derivatives of BA data 
    def calc_delta_BA(self):
        self.BA.dp = preprocess.calc_delta_BA(self)
        
#=================================================================
#
# Time domain analysis subroutines:

    # Calculate linear regression (of GW p vs BA p) 
    def calc_linear_GW(self):
        process.time_domain.calc_linear(self)
        
        
    # Plot linear regression (of GW p vs BA p) 
    def plot_linregress(self, pname):
        plot.plot_linregress(self, pname)
        

    # Calculate BE using average-of-ratios method
    def calc_BE_AoR(self):
        self.BE_AoR, self.BE_AoR_all, self.BE_AoR_ratios = process.time_domain.calc_BE_AoR(self)


    # Calculate BE using median-of-ratios method
    def calc_BE_MoR(self):
        self.BE_MoR, self.BE_MoR_all = process.time_domain.calc_BE_MoR(self)


    # Calculate BE using linear regression method
    def calc_BE_LR(self):
        self.BE_LR, self.BE_LR_all = process.time_domain.calc_BE_LR(self)


    # Calculate BE using Clark (1967) method
    def calc_BE_Clark(self):
        self.BE_Clk, self.BE_Clk_all = process.time_domain.calc_BE_Clark(self)


    # Calculate BE using Rahi (2010) method
    def calc_BE_Rahi(self):
        self.BE_Rah, self.BE_Rah_all = process.time_domain.calc_BE_Rahi(self)


    # Plot Convergence of time domain BE metrics over time
    def plot_BE_vs_time(self, pname):
        plot.plot_BE_vs_time(self, pname)


    # Calculate the regression deconvolution (of GW p vs BA p)
    def calc_regress_deconv(self):
	self.lags, self.crf, self.mag, self.phs = process.time_domain.calc_regress_deconv(self)


    # Plot cumulative response function
    def plot_regress_deconv_crf(self, pname):
        plot.plot_regress_deconv_crf(self, pname)        


    # Plot amplitude vs phase values (obtained from regression deconvolution)
    def plot_regress_deconv_pva(self, pname):
	plot.plot_regress_deconv_pva(self, pname)

#=================================================================
#
# Frequency domain analysis subroutines:
    
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


