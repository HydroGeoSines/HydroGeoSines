# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class Plot(object):
    #add attributes specific to Visualize here

    def __init__(self, results_obj):
        self.data = results_obj
    
    #@staticmethod
    #def _validate(obj):
    #    # check if object is of type dict
    #    if not isinstance(obj,dict):
    #        raise AttributeError("Must be a dictionary!") 
        #TODO!: check if object contains valid method keys
    
    @staticmethod    
    def config_grid(ax):
        for i in ['top', 'right']:
            ax.spines[i].set_visible(False)
        ax.grid(which='major', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        ax.grid(which='minor', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
    
    def plot_BE_time(data,method):
        pass
    
    def plot_HALS(self)
    
    def plot_linear_regression(X, Y, slope, intercept):
        '''
            Plot scatterplot of barometric and groundwater pressure data (or derivatives), as well as line of best fit.

            Inputs:
                X - 1-D numpy array. Barometric pressure data,  provided as measured values or as temporal derivatives.
                Y - 1-D numpy array. Groundwater pressure data, provided as measured values or as temporal derivatives.
                slope - scalar. Slope of line of best fit applied to measured.
                intercept - scalar. Intercept of line of best fit applied to data.

            Outputs:
                f,s - matplotlib figure and subplot objects.
        '''
        f,s = plt.subplots(1, 1, figsize=[7.00/2.54, 7.00/2.54])
        s.plot(X, Y, 'o', ms=3, mfc='SteelBlue', mec='none', alpha=0.25)
        xt = np.array([np.min(X), np.max(X)])
        s.plot(xt, slope*xt+intercept, 'k-', lw=1.0)
        s.text(0.1, 0.1, '$\mathit{y = }$'+
                          str('%.3g'% slope).replace('-', '$\endash$')+
                         ' $\mathit{x}$ '+
                         str('%+.3g'% intercept).replace('-', '$\endash$'),
                         transform=s.transAxes, ha='left')
        s.set_xlabel('$\Delta$BP / $\Delta$t')
        s.set_ylabel('$\Delta$GW / $\Delta$t')
        for i in ['top', 'right']:
            s.spines[i].set_visible(False)
        s.grid(which='major', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        s.grid(which='minor', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        plt.tight_layout()
        #plt.savefig('BE_LR.png', dpi=500)
        return f,s

    def plot_Clark(sX, sY, slope, intercept):
        '''
            Plot cumulative sums of temporal derivatives of barometric and pressure data using the Clark method, as well as line of best fit.

            Inputs:
                sX - 1-D numpy array. Cumulative sum of temporal derivatives of barometric pressure data.
                sY - 1-D numpy array. Cumulative sum of temporal derivatives of groundwater pressure data.
                slope - scalar. Slope of line of best fit applied to cumulative data.
                intercept - scalar. Intercept of line of best fit applied to sum data.

            Outputs:
                f,s - matplotlib figure and subplot objects.
        '''
        f,s = plt.subplots(1, 1, figsize=[7.00/2.54, 7.00/2.54])
        s.plot(sX, sY, 'o', ms=3, mfc='SteelBlue', mec='none', alpha=0.25)
        xt = np.array([0., np.max(sX)])
        s.plot(xt, slope*xt+intercept, 'k-', lw=1.0)
        s.set_xlabel('$\Sigma$ ($\Delta$BP / $\Delta$t)')
        s.set_ylabel('$\Sigma$ ($\Delta$GW / $\Delta$t)')
        s.text(0.1, 0.1, '$\mathit{y = }$'+
                          str('%.3g'% slope).replace('-', '$\endash$')+
                          ' $\mathit{x}$ '+
                          ('%+.3g'% intercept).replace('-', '$\endash$'),
                          transform=s.transAxes, ha='left')
        for i in ['top', 'right']:
            s.spines[i].set_visible(False)
        s.grid(which='major', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        s.grid(which='minor', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        plt.tight_layout()
        #plt.savefig('BE_Clark.png', dpi=500)
        return f,s

    def plot_Rahi(sX, sY, slope, intercept):
        '''
            Plot cumulative sums of temporal derivatives of barometric and pressure data using the Rahi method, as well as line of best fit.

            Inputs:
                sX - 1-D numpy array. Cumulative sum of temporal derivatives of barometric pressure data.
                sY - 1-D numpy array. Cumulative sum of temporal derivatives of groundwater pressure data.
                slope - scalar. Slope of line of best fit applied to cumulative data.
                intercept - scalar. Intercept of line of best fit applied to sum data.

            Outputs:
                f,s - matplotlib figure and subplot objects.
        '''
        f,s = plt.subplots(1, 1, figsize=[7.00/2.54, 7.00/2.54])
        s.plot(sX, sY, 'o', ms=3, mfc='SteelBlue', mec='none', alpha=0.25)
        xt = np.array([0., np.max(sX)])
        s.plot(xt, slope*xt+intercept, 'k-', lw=1.0)
        s.set_xlabel('$\Sigma$ ($\Delta$BP / $\Delta$t)')
        s.set_ylabel('$\Sigma$ ($\Delta$GW / $\Delta$t)')
        s.text(0.1, 0.1, '$\mathit{y = }$'+
                          str('%.3g'% slope).replace('-', '$\endash$')+
                          ' $\mathit{x}$ '+
                          ('%+.3g'% intercept).replace('-', '$\endash$'),
                          transform=s.transAxes, ha='left')
        for i in ['top', 'right']:
            s.spines[i].set_visible(False)
        s.grid(which='major', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        s.grid(which='minor', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        plt.tight_layout()
        #plt.savefig('BE_Rahi.png', dpi=500)
        return f,s

    def plot_Rojstaczer(csd_f, csd_p, psd_f, psd_p):
        '''
            Plot the ratio of (a) cross spectral density of barometric and groundwater pressure data to (b) the power spectral density of barometric pressure data.
            Also plot the mean ratio value taken over the full amplitude spectrum.

            Inputs:
                psd_f - 1-D numpy array. Frequency information from the cross spectral density of barometric and groundwater pressure data.
                psd_p - 1-D numpy array. Power information from the power spectral density of barometric pressure data.
                csd_f - 1-D numpy array. Frequencyinformation from the cross spectral density of barometric and groundwater pressure data.
                csd_p - 1-D numpy array. Power information from the power spectral density of barometric pressure data.

            Outputs:
                f,s - matplotlib figure and subplot objects.
        '''
        f,s = plt.subplots(1, 1, figsize=[7.00/2.54, 7.00/2.54])
        s.plot(csd_f, np.abs(csd_p)/psd_p, '-', c='SteelBlue', lw=1.0,
               alpha=0.75)
        s.plot(csd_f, np.mean(np.abs(csd_p)/psd_p)*np.ones(len(csd_f)), 'k-',
               lw=1.0)
        s.text(0.1, 0.1, 'ratio = '+str('%.3f'% result), transform=s.transAxes,
               ha='left')
        s.set_xlabel('Frequency (cpd)')
        s.set_ylabel('Amplitude (m)')
        s.set_ylim(-0.05, 1.05)
        for i in ['top', 'right']:
            s.spines[i].set_visible(False)
        s.grid(which='major', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        s.grid(which='minor', axis='both', c=(194./255., 194./255., 194./255.),
            ls='-', lw=0.5)
        plt.tight_layout()
        #plt.savefig('BE_Rojstaczer.png', dpi=500)
        return f,s
