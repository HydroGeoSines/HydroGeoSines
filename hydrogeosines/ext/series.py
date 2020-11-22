import numpy as np
import pandas as pd

#from ..tools import Tools

class Series(object):
    # define all class attributes here 
    
    def __init__(self, *args, **kwargs):        
        pass  
        #add attributes specific to Processing here
        #self.attribute = variable            
    
    @property
    def df_obj(self):
        """returns df object columns as list"""
        return list(self.select_dtypes(include=['object']).columns)
    
    @property
    def freq_median(self):
        """returns median sample frequency grouped by object-dtype columns, in minutes"""
        df = self[self.value.notnull()]
        return df.groupby(self.df_obj)["datetime"].apply(lambda x: (x.diff(periods=1).dt.seconds.div(60)).median())
    
    @staticmethod                      
    def check_all_equal(arr):
        return print((arr[:] == arr[0]).all(axis=0))
        
    def resample_median(self, freq):
        out = self.groupby(self.df_obj).resample(str(int(freq))+"min", on="datetime").mean()
        return out[self.data_header]

    def resample_median_ind(df,median):
        """resample by median for each location and category individually"""
        out = []
        for i in range(len(med)):
            a = df.loc[:,df_obj(df)] == med.reset_index().loc[i,df_obj(df)]
            a = a.values
            a = (a == a[:, [0]]).all(axis=1)                   
            temp = df.iloc[a].groupby(df_obj(df)).resample(str(int(med[i]))+"min", on="datetime").mean()
            temp.reset_index(inplace=True)
            out.append(temp) 
        out = pd.concat(out,axis=0,ignore_index=True,join="inner",verify_integrity=True)  
        return out[self.data_header] # set to predefined column order


    def dt_pivot(self):
        return self.pivot_table(index=self.datetime,columns=["category", "location"], values="value")
    
    @property
    def is_nan(self):
        return self['value'].isnull().values.any()
    
    # Methods
    def drop_nan(self):              
        return self.dropna(axis=0,how="any",subset=["value"]).reset_index(drop=True)
               
    def remove(self,locs):
        locs = np.array(locs).flatten()
        idx = self.location.isin(locs)   
        return self[~idx].reset_index()         