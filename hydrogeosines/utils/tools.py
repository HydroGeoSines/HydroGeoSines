#import pandas as pd
import numpy as np 
import pandas as pd

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
        return idx.astype(int)
    
    @staticmethod                      
    def check_all_equal(arr):
        return print((arr[:] == arr[0]).all(axis=0))
    
    @staticmethod
    def pi_range(value):
        value = np.array(value)
        idx = (value < np.pi)
        np.add.at(value,idx,2*np.pi)
        idx = (value > np.pi)
        np.add.at(value,idx,-2*np.pi)
        return value
    
    @staticmethod              
    def complex_to_real(n_samples, z):
        amp = 2/len(n_samples)*abs(z)
        phs = np.angle(z)
        return {"amp":amp, "phs":phs}
            
    @staticmethod
    def gap_mask(s:pd.Series, maxgap:int):
        """
        Mask NaN gaps that fall below a maxium gap size and also returns a counter.
    
        Parameters
        ----------
        s : pd.Series
            A Series with null entries
        maxgap : int
            Maximum number of consecutive null entries that are marked as True.
    
        Returns
        -------
        mask: numpy array
            Boolean mask of size s, which is False for all null(NaN) gaps larger then maxgap
        counter: int
            Number of null entries marked as True     
    
        """
        idx = s.isnull().astype(int).groupby(s.notnull().astype(bool).cumsum()).sum()
        sizes = idx[idx > 0] # size of gaps
        start = sizes.index + (sizes.cumsum() - sizes) # get start index
        stop  = start + sizes # get stop index
        gaps = [np.arange(a,b) for a,b in zip(start,stop)] # get indices of each individual gap
        
        ## create a mask for the gap sizes
        mask = np.zeros_like(s)
        for gap in gaps:
            mask[gap] = len(gap)    
    
        return (mask < maxgap) | s.notnull().to_numpy(), np.count_nonzero(np.logical_and(mask > 0, mask < maxgap))