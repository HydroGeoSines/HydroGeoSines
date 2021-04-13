# -*- coding: utf-8 -*-
"""
Created on Thu Apr  8 10:17:38 2021

@author: Daniel
"""

# Function for conversion of nested dictionaries

def flatten(object):
    for item in object:
        if isinstance(item, (list, tuple, set)):
            yield from flatten(item)
        else:
            yield item

def dict_depth(dic, level = 1):      
    if not isinstance(dic, dict) or not dic:
        return level
    return max(dict_depth(dic[key], level + 1)
                               for key in dic)

def nested_dict_to_tuple_key(d):
    d = {tuple(flatten((i,j))): d[i][j] 
     for i in d.keys() 
     for j in d[i].keys()}
    #print([(a, *rest) for a, rest in d.keys()])
    depth = dict_depth(d)
    #print("dict depth = ",depth)
    if depth == 2:
        return d
    else:
        return nested_dict_to_tuple_key(d) 
    
def dict_reform(nested_dict):
    '''    Works for two level nested dict. Result can be converted to MultiIndex DataFrame   '''
    reformed_dict = {}
    for outerKey, innerDict in nested_dict.items():
    	for innerKey, values in innerDict.items():
    		reformed_dict[(outerKey,
    					innerKey)] = values
    return reformed_dict      