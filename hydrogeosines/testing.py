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
        
        for attr in ['gw', 'bp']:
             setattr(self, f'{attr}_data', self.__func(attr))    
             
    @property
    def name(self):
        return 'nah'      

    #self.name2 = name 
    @staticmethod
    def __func(cat):
        @property
        def inner():
            return cat
        return inner    