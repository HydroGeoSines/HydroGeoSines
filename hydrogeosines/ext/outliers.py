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

def annotate(data, **kws):
    n = len(data)
    ax = plt.gca()
    ax.text(.1, .6, f"N = {n}", transform=ax.transAxes)

def out_bound(data, **kws):
    data = data.loc[data["variable"] == "perc_change"]
    data_mean, data_std, outliers = out_values(data)    
    ax = plt.gca()
    ax.axhline(data_mean + (data_std * 3),ls="--",c="r")
    ax.axhline(data_mean - (data_std * 3),ls="--",c="r")
    ax.scatter(outliers["datetime"],outliers["value"],c="r",marker="x",s=10)
    
def out_values(data):
    data_mean = data["value"].mean()
    data_std =  data["value"].std()
    outliers = data.loc[data["value"].abs() > data_std*3]
    return data_mean, data_std, outliers
    
def gaps_highlighter(data, **kws):
    if (data["variable"] == "raw").all() == True:
        diff = data["datetime"].diff(periods=1).dt.total_seconds()
        mcf = diff.mode()
        gaps = data.loc[diff > mcf[0]]
        ax = plt.gca()
        ylims = ax.get_ylim()
        ax.scatter(gaps["datetime"], [ylims[0]]*len(gaps),c="green",marker="x",s=10)
        
def percent_change(values):
    # Separate value from all previous values
    last_value = values.iloc[-1]
    previous_values = values.iloc[:-1]
    # Calculate % difference between last values and the mean of all pervious values
    perc_change = (last_value - np.mean(previous_values)) / np.mean(previous_values)
    return perc_change

def find_outliers(df, window = "24H"):
    # drop missing values so % change is only calculated for datetimes with values
    df = df.hgs.filters.drop_nan.reset_index(drop=True)
    df["perc_change"] = df.groupby(df.hgs.filters.obj_col).rolling(window=window, 
                                                             min_periods=1,     
                                                             on = "datetime")["value"].aggregate(percent_change).reset_index()[df.columns]["value"]
    df["ident"] = df["category"] + "_" + df["location"] + "_" + df["part"]
    df.rename(columns={"value":"raw"},inplace=True)
    df = pd.melt(df, id_vars=['ident',"datetime"], value_vars=["raw","perc_change"], value_name='value')
    return df

def inspect_data(df):
    perc_change = df.loc[df["variable"] == "perc_change"]
    outliers = out_values(perc_change)        
    grid = sns.FacetGrid(df, col="ident", row="variable",sharey=False,legend_out = True,height=3,aspect=2)
    #grid.refline(y=(test["value"].mean()+test["value"].std()*3))  #test["value"].mean()
    grid.map_dataframe(sns.scatterplot, "datetime", "value", s=2, color=".1", marker="+") 
    grid.set(xlim=(df.datetime.min(), df.datetime.max()))#, ylim=(0, 12), xticks=[10, 30, 50], yticks=[2, 6, 10])
    grid.map_dataframe(out_bound)
    grid.map_dataframe(gaps_highlighter)
    grid.add_legend() 
    
    for axes in grid.axes.flat:
        _ = axes.set_xticklabels(axes.get_xticklabels(), rotation=45, ha = "right")
    
    grid.tight_layout()  
    return outliers