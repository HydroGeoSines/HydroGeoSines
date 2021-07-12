# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 10:16:33 2021

@author: Daniel
"""

from ..handlers.processing import Processing
from .. import utils

# import additional functionalities
from .ext.export import Export
from .ext.plot import Plot
from .ext.table import Table

class Output(Export,Plot,Table):
    # define all class attributes here 
    #attr = attr
    
    def __init__(self, results_obj):
        self._validate(results_obj)
        self._obj       = results_obj
    
        if isinstance(self._obj, Processing):
            self.results = self._obj.results
        
        if isinstance(self._obj, dict):
            self.results = self._obj
            
    @staticmethod
    def _validate(obj):
        # check if object is of class Processing or a dictionary
        if not isinstance(obj,(Processing,dict)):
            raise AttributeError("Object must either be of Class Processing or Dictonary!")   
            #print(id(Processing)) # test id of class location to compare across package
        # check if entries in results dict exist    
        ## add checks here  
        # check for non valid method entries
        ## add checks here
    
    
    def plot(self, analysis_method="all", **kwargs):
        print("-------------------------------------------------")
        analysis_method = analysis_method.lower()
        # select plotting method based on first key of dict (e.g. HALS, BE_time, BE_freq, etc)
        method_list = utils.method_list(Plot, ID="plot")  
        method_dict = dict(zip([i.replace("plot_", "").lower() for i in method_list], method_list))

        # check for non valid plotting method
        utils.check_affiliation(list(self.results.keys()), method_dict.keys()) #self.results.keys()
        
        # select method            
        if analysis_method.lower() == 'all':
            for method, location in self.results.items():
                plot_method = method_dict[method]
                for loc, results_list in location.items():
                    # extract data for each location
                    results = results_list[0]
                    data    = results_list[1]
                    info    = results_list[2]
                    #info    = results_list[2] #not in use for most methods
                    # use the propper printing function
                    getattr(Plot, plot_method)(loc, results, data, info=info, **kwargs)        
        
        else:
            # check for non valid method 
            utils.check_affiliation(analysis_method, method_dict.keys()) 
            plot_method = method_dict[analysis_method]
            for loc, results_list in self.results[analysis_method].items():
                results = results_list[0]
                data    = results_list[1]
                info    = results_list[2]
                getattr(Plot, plot_method)(loc, results, data, info=info, **kwargs) 


    def export(self, analysis_method="all", folder=None, **kwargs):
        print("-------------------------------------------------")
        analysis_method = analysis_method.lower()
        # select plotting method based on first key of dict (e.g. HALS, BE_time, BE_freq, etc)
        method_list = utils.method_list(Export, ID="export")  
        method_dict = dict(zip([i.replace("export_", "").lower() for i in method_list], method_list))
        
        # check for non valid plotting method
        utils.check_affiliation(list(self.results.keys()), method_dict.keys()) #self.results.keys()
        
        # select method            
        if analysis_method.lower() == 'all':
            for method, location in self.results.items():
                export_method = method_dict[method]
                for loc, results_list in location.items():
                    # extract data for each location
                    results = results_list[0]
                    data    = results_list[1]
                    info    = results_list[2]
                    #info    = results_list[2] #not in use for most methods
                    # use the propper printing function
                    getattr(Export, export_method)(loc, results, data, folder, info=info, **kwargs)        
        
        else:
            # check for non valid method 
            utils.check_affiliation(analysis_method, method_dict.keys()) 
            export_method = method_dict[analysis_method]
            for loc, results_list in self.results[analysis_method].items():
                results = results_list[0]
                data    = results_list[1]
                info    = results_list[2]
                getattr(Plot, export_method)(loc, results, data, folder=None, info=info, **kwargs) 
    
    
    def table(self):
        # select table format
        pass
