# -*- coding: utf-8 -*-
"""
Created on Wed Nov  4 21:13:29 2020

@author: Daniel
"""

VALID_CATEGORY = {"ET", "BP", "GW"}

class Site():
    "Optional class documentation string, can be accessed via Site.__doc__"   
    
    # define all class attributes here 
    data_header = f'xxx{2*4}'
    
    
    def __init__(self,*args, **kwargs):
        
        for attr in VALID_CATEGORY:
             setattr(self,f'get_{attr.lower()}_data', self.func(attr))    
             
    @property
    def name(self):
        return 'nah'      

    #self.name2 = name 
    #@staticmethod
    def func(self,cat): 
        @property
        def inner():
            return self.__get_data(cat)
        return inner    
    
    #@property
    #def gw_data(self):
    #    # return self.data[self.data['category'] == 'GW'].pivot(index='datetime', columns='location', values='value')
#        return self.__get_data('GW')
    @property
    def location(self,category):
        pass
        #return self.f"get_{category}_data'
    
    
site = Site()    