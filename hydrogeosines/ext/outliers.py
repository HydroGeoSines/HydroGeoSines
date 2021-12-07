#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Aug 21 11:16:37 2021

@author: daniel

-Transform data to standardize variance
-Convert data so each point represents a percent change over a previous window
"""
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from matplotlib.dates import DateFormatter

from pandas.tseries.frequencies import to_offset

from .. import utils


def percent_change(values):
    # Separate value from all previous values
    last_value = values.iloc[-1]
    previous_values = values.iloc[:-1]
    # Calculate % difference between last values and the mean of all pervious values
    perc_change = ((last_value - np.mean(previous_values)) / np.mean(previous_values))*100
    return perc_change

def data_stats(series):
    data_mean = series.mean()
    data_std =  series.std()
    data_abs =  series.abs()
    return data_mean, data_std, data_abs

def consecutive_values(df, threshold: int = 1):
    df.index.name = "idx"
    df = df.reset_index()
    #df['value_grp'] = (df["idx"].diff(1) != 1).astype('int').cumsum()
    df['value_grp'] = (df["idx"].diff(1) > threshold).astype('int').cumsum()
    
    out = pd.DataFrame({'StartDate' : df.groupby('value_grp').datetime.first().dt.tz_localize(None), 
              'EndDate' : df.groupby('value_grp').datetime.last().dt.tz_localize(None),
              'Size' : df.groupby('value_grp').size(), 
              'StartIndex' : df.groupby('value_grp')["idx"].first(),
              "AbsChange"  : df.groupby("value_grp")["value"].apply(lambda x:x.max()-x.min())}).reset_index(drop=True)    
    return out

def stationary(df): 
    df = df.hgs.filters.drop_nan.reset_index(drop=True)     
    groups = df.groupby(["location","part"])
    for name, df_grp in groups:
        print(name)
        df_grp = df_grp.set_index("datetime")
        rollmean = df_grp.resample(rule="D").mean()
        rollstd = df_grp.resample(rule= "D").std()
        # resample uses datetime at center of data. offset need to align with df_grp again
        offset = "12h"
        df_grp.index = df_grp.index - to_offset(offset)
        
        fig, axs = plt.subplots(2,1, figsize=(10,5), sharex = True, 
                                    gridspec_kw={'height_ratios': [2,1]})
        axs[0].plot(df_grp["value"], color="blue", label="raw_data")
        axs[0].plot(rollmean, color="red", linestyle="--", label = "rolling_mean")
        axs[1].plot(rollstd, color="black", label= "rolling_std")
        axs[0].set_title(name)
        for ax in axs.reshape(-1):
            ax.legend(loc="best")        
        plt.show()
        
def plot_outliers(df, window = "24H",cat="GW"): 
    """
    Visual examination of outliers in groundwater data.

    Parameters
    ----------
    df : TYPE
        DESCRIPTION.
    window : TYPE, optional
        DESCRIPTION. The default is "24H".
    cat : TYPE, optional
        DESCRIPTION. The default is "GW".

    Returns
    -------
    df_outliers : TYPE
        DESCRIPTION.

    #TODO!: three different types of outliers that need to be distinguished:
        1) extreme values, spikes -> e.g. reading errors 
        2) shifts (often encountered together with a change in sampling rate beforehand (e.g. due to maintainance))
        3) sharp rises or falls (extreme changes in the system) -> e.g. pumping
    """
    
    # user defined style for plot
    with plt.style.context("ggplot"):
        # get category
        df = df.loc[df.category.isin(list(np.array(cat).flatten()))]
        df = df.hgs.filters.drop_nan.reset_index(drop=True)
        #df["value"] = np.ma.masked_where(df["value"] == np.nan,df["value"])
        
        output = {}
        # group by location and part
        groups = df.groupby(["location","part"])
        for name, df_grp in groups:
            print("\nThe data for location '{}', part '{}' is being processed ...".format(name[0],name[1]))
            # calculate percent_change
            df_grp["perc_change"] = df_grp.rolling(window=window, min_periods=1,on="datetime")["value"].aggregate(percent_change)
            
            # calculate mean, std and abs for the percent change data
            perc_mean, perc_std, perc_abs = data_stats(df_grp.perc_change)
            
            # get outliers
            df_outliers =  df_grp.loc[perc_abs > perc_std*3]
            
            # sampling rate
            diff = df_grp["datetime"].diff(periods=1).dt.total_seconds()
            sph = (1/(diff/(60*60)))# samples per hour
            mcf = sph.mode().values # most common sampling frequency
            
            # finds gaps
            gaps = df_grp.loc[diff > mcf[0]]
    
            #ax.scatter(gaps["datetime"], [ylims[0]]*len(gaps),c="green",marker="x",s=10)
            plt_labels = ["value","perc_change"]
            y_labels = ["value [{}]".format(str(df_grp.unit.values[0])),"percent\n change [%]"]
            fig, axs = plt.subplots(len(plt_labels)+1,1, figsize=(12,6), sharex = True, 
                                    gridspec_kw={'height_ratios': [2]*len(plt_labels)+[1]})
            fig.suptitle(utils.join_tuple_string(name)) #,fontsize=16
            for i,var in enumerate(plt_labels):
    
                axs[i].plot(df_grp.datetime,df_grp[var], color="black",linewidth=1)
                axs[i].scatter(df_outliers.datetime,df_outliers[var],marker="x",color="r",s=10)
    
                axs[i].set_ylabel(y_labels[i])
                axs[i].spines[["top","right"]].set_visible(False)
                               
            # plt 3 std around mean
            axs[1].axhline(perc_mean + (perc_std * 3),ls="--",c="r")
            axs[1].axhline(perc_mean - (perc_std * 3),ls="--",c="r")
            
            axs[2].scatter(df_grp["datetime"],sph, color="black",s=10)
            axs[2].axhline(mcf,ls="--",c="g")
            axs[2].set_ylabel("sampling\n rate [s/h]")

            plt.gcf().autofmt_xdate(rotation=30, ha='right')
            plt.tight_layout()
            plt.show()
            
            # find consecutive outliers (clusters)
            grouped_outliers = consecutive_values((df_outliers))
            
            # prompt if user would like to print the table to the console
            while True:
                answer = input("\nWould you like to print the top outliers to the console? (Yes/No) ").lower()
                if answer in ("yes","no"):
                    break
                else:
                    print("That is not a valid answer! Please try again ...")
  
            if answer == "yes":  
                if len(grouped_outliers) < 5:
                    num_entries = len(grouped_outliers)
                    print("\nThese are the {} outlier-clusters sorted by their abs(change_in_value) and size:".format(num_entries))
                else:
                    num_entries = 5
                    print("\nThese are the top 5 outlier-clusters sorted by their abs(change_in_value) and size:")
                print(grouped_outliers.sort_values(by=["AbsChange","Size"],ascending=[False,False]).head(num_entries))
            
            # show clusters of outliers by color in a new plot?
            
            # prompt what to do for a specific range of values
            
            # use "between_dates" of pandas to replace values within a certain time frame
            
            # append output
            result = {name:grouped_outliers}
            output.update(result)
        return output
