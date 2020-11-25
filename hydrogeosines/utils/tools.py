import pandas as pd
import numpy as np 

class Tools(object):
    # define all class attributes here 
    #attr = attr
            
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Processing here
        #self.attribute = variable             
    
    @staticmethod
    def check_affiliation(values,valid):
            if not all(x in valid for x in np.array([values]).flatten()):
                raise ValueError("%r contains values that are not part of %r." % (values,valid))                 
    
    @staticmethod                              
    def zip_formatter(arg1,*args):
        args = list(args)
        valid = (str,float,int)
        # check for single string arguments
        if (any(isinstance(a,valid) for a in args)):         
            idx = np.where([isinstance(a,valid) for a in args])[0]
            args_list = [[args[i]]*len(arg1) for i in idx]
            # check if there are any non string arguements left
            check = [x for x in args if x not in [args[i] for i in idx]]
            if check != []:
                #print("A list of values remains")
                args_list.extend(check)    
        else:
            args_list = args
        return list(zip(arg1,*args_list)) 
    
    @staticmethod
    def find_nearest_idx(array,value):
        # find index nearest to value
        idx = np.argmin(np.array(np.abs(array-value)))
        return idx