# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 16:13:00 2020

@author: Daniel
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

class Plot(object):
    #add attributes specific to Visualize here

    def __init__(self, *args, **kwargs):
        pass
        #add attributes specific to Load here
        #self.attribute = variable
    
    @staticmethod
    def plot_BE_time(loc, results, data):
        pass
    
    @staticmethod
    def plot_BE_freq(loc, results, data):
        pass
    
    @staticmethod
    def plot_HALS(loc, results, data):  
        fig = plt.figure()
        sns.scatterplot(x= results["phs"],y= results["amp"], hue = results["comps"])
        plt.xlabel("phs")
        plt.ylabel("amp")
        plt.title(loc)
    
    @staticmethod
    def plot_FFT(loc, results, data):
        pass
    
    @staticmethod
    def plot_GW_correct(loc, results, data):
        pass
    
    
    
        
        
 