#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jan  5 19:36:18 2019

@author: Meesum
"""
#Importing required libraries
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os
#Checking current working directory
os.getcwd()

# lsOfFileNames => will contain all file names and lsDataFramesForHist => will contain all data frames
lsOfFileNames = []
lsDataFramesForHist = []
lsDataFramesForTimeSeries = {}
    
#Iterate over folder and append filenames in list declared above. 
for files in os.walk("./AI_WaseemHaider/set-a/"):#Make sure to give relative or absolute path to set-a folder
    for filename in files:
        lsOfFileNames.append(filename)
# print(lsOfFileNames)
# Actual filenames start from 2nd index
lsOfFileNames = lsOfFileNames[2]

##################################################################################
def getTimeSeries(filename, paramName):
    ''' This function takes filename i.e. patient record id 
    and the parameter of which time series is needed 
    and returns time series along with unique parameters of that patient record 
    '''
    
    # If record is missing from list of data frames then return
    if (filename + '.txt') not in lsDataFramesForTimeSeries.keys():
        return
    
    # Reading relevant data frame
    tdf = lsDataFramesForTimeSeries[filename + '.txt']
    # Extracting unique parameters
    params = tdf.Parameter.unique()
#    print(params)
    # if parameter passed in argument is not availabble then return
    if paramName not in params:
        return
    # converting time column from string to date time type
    tdf.Time = pd.to_datetime(tdf.Time,format= '%H:%M:%S').dt.time
    # Grouping dataframe on parameters
    groups = tdf.groupby('Parameter')
#    tdf.describe()
    # fetching required group based on parameter name provided in argument
    ts = groups.get_group(paramName)
    # Making Time as index
    ts.set_index(ts.Time, inplace=False)
    # Dropping irrelevant columns
    ts = ts.drop(columns=['Time','Parameter'])
    # returning time series and unique parameters
    return ts,params.tolist()
##################################################################################
    
##################################################################################
def getParams(filename):
    ''' This function takes filename i.e. patient record id 
    and returns unique parameters of that patient record 
    '''
    if (filename + '.txt') not in lsDataFramesForTimeSeries.keys():
        return
    
    tdf = lsDataFramesForTimeSeries[filename + '.txt']
    return tdf.Parameter.unique().tolist()
##################################################################################

##################################################################################
# importing numpy for calculating slopes via polyfit
import numpy as np
def getSlopes(recordID):
    # fetching unique parameters of Patient record
    args = getParams(recordID)
    slopes = {}
    # iterating over each parameter except record id
    for a in args:
        if a == "RecordID":
            continue
        # fetching time series against each parameter
        time_series, p = getTimeSeries(recordID,a)
        # increasing index by 1 to avoid divide by zero exception
        time_series.index = time_series.index + 1
        # calculating slopes via polyfit
        slopes[a+"_slope"] = time_series.apply(lambda x: np.polyfit(time_series.index, x, 1)[0])
#    print(slopes)
    return slopes
##################################################################################

# Iterate over each filename and read the data frame. 
# drop Time col as it is not needed in plotting histograms.
# Group the dataframe WRT Parameter and aggregate Value col.
# Append the transpose of grouped dataframe to dataframes list.
for filename in lsOfFileNames:
    # read patient record as dataframe
    d = pd.read_csv("./AI_WaseemHaider/set-a/" + filename)
    # reformating time column
    d.Time = d.Time.map(lambda x: "00:"+x)
    # appending dataframe against patient record id
    lsDataFramesForTimeSeries[filename] = d
    
#    params = d.Parameter.unique().tolist()
#    d.Time = pd.to_datetime(d.Time,format= '%H:%M:%S').dt.time
#    groups = d.groupby('Parameter')
#    ts = groups.get_group(paramName)
#    ts.set_index(ts.Time, inplace=False)
#    ts = ts.drop(columns=['Time','Parameter'])
    recordId = filename.strip(".txt")
    # fetching slopes of each parameter
    slopes_df = pd.DataFrame(getSlopes(recordId))
    d = d.drop(columns=['Time'])
    d = d[d.Parameter != "RecordID"]
    # Grouping by aggregates
    # creating new features from existing ones
    groups = d.groupby(['Parameter'])
    e_med = groups.agg({'Value':'median'}).T
    e_max = groups.agg({'Value':'max'}).T
    e_min = groups.agg({'Value':'min'}).T
    e_first = groups.agg({'Value':'first'}).T
    e_last = groups.agg({'Value':'last'}).T
    e_std = groups.agg({'Value':'std'}).T
    e_mode = groups.agg(lambda x:x.value_counts().index[0]).T

    # Renaming columns accordingly
    e_med.columns = [str(col) + '_med' for col in e_med.columns]
    e_max.columns = [str(col) + '_max' for col in e_max.columns]
    e_min.columns = [str(col) + '_min' for col in e_min.columns]
    e_first.columns = [str(col) + '_first' for col in e_first.columns]
    e_last.columns = [str(col) + '_last' for col in e_last.columns]
    e_std.columns = [str(col) + '_std' for col in e_std.columns]
    e_mode.columns = [str(col) + '_mode' for col in e_mode.columns]

    # Concatenated Dataframe
    df_con = pd.concat([e_med,e_mode,e_max,e_min,e_first,e_last,e_std,slopes_df], axis = 1)
    df_con['RecordID'] = recordId
    # Making list of concatenated dataframes
    lsDataFramesForHist.append(df_con)
    print(recordId)
    
# reading outcome file as dataframe
outcome = pd.read_csv("./AI_WaseemHaider/Outcomes-a.txt",sep=',')   
outcome['RecordID'] = outcome['RecordID'].astype(str)


# Concatenate all dataframes in list into single dataframe
DfForHistogram = pd.concat(lsDataFramesForHist)

# Fill NaN values with median
DfForHistogram = DfForHistogram.fillna(DfForHistogram.median())
# merge outcome dataframe with patients records
df_outer = pd.merge(DfForHistogram, outcome, on='RecordID', how='outer')
# saving finat data frame as csv
df_outer.to_csv("Final_Dataset.csv")

#
#df_inner = pd.merge(DfForHistogram, outcome, on='RecordID', how='inner')
#
#
#df_max = lsDataFramesForTimeSeries['138298.txt'].groupby(['Parameter']).agg({'Value':'max'}).T
#df_max.columns = [str(col) + '_max' for col in df_max.columns]
#df_median = lsDataFramesForTimeSeries['138298.txt'].groupby(['Parameter']).agg({'Value':'median'}).T
#df_median.columns = [str(col) + '_median' for col in df_median.columns]
#df_mode = lsDataFramesForTimeSeries['138298.txt'].groupby(['Parameter']).agg(lambda x:x.value_counts().index[0])
#
#df = lsDataFramesForTimeSeries['138298.txt'].groupby(['Parameter']).agg({'Value':'std'}).T
#
#l = pd.concat([df_max,df_median], axis = 1)
#grps = df.groups
#
## plot histograms of each col with figsize of your choice
#DfForHistogram.hist(figsize=(20,20))
#
#
#sns.set(color_codes=True)
#sns.kdeplot(DfForHistogram.Age,DfForHistogram.RecordID, shade=True);
#
#def plotTimeSeries():
#    while True:
#        FileName = input("Enter Patient ID: ")
#        if (FileName + '.txt') in lsDataFramesForTimeSeries.keys():
#            break
#    tdf = lsDataFramesForTimeSeries[FileName + '.txt']
#    params = tdf.Parameter.unique()
#    print(params)
#    t = True
#    while t:
#        Param = input("Enter Parameter To Plot: ")
#        if Param in params:
#            break    
#    
#    tdf.Time = pd.to_datetime(tdf.Time,format= '%H:%M:%S').dt.time
#    groups = tdf.groupby('Parameter')
#    tdf.describe()
#    ts = groups.get_group(Param)
#    ts.set_index(ts.Time, inplace=True)
#    ts = ts.drop(columns=['Time','Parameter'])
#    ts.plot(figsize=(20,10), linewidth=5, fontsize=20)
#    plt.xlabel('Time', fontsize=20);plt.ylabel(Param,fontsize=20)
#    
#
#
#p1tshr, p1params = getTimeSeries('132539','Mg')
#p1tshr.columns = ['HR_P1']
#p2tshr = getTimeSeries('136723','pH')
#p2tshr.columns = ['HR_P2']
#
#tscat = pd.concat([p1tshr,p2tshr], axis=1)
#tscat['HR_P2'] = tscat['HR_P2'].fillna(tscat['HR_P2'].mean())
#tscat['HR_P1'] = tscat['HR_P1'].fillna(tscat['HR_P1'].mean())
#
#tscat.hist()
#
#plt.figure(figsize=(10,10))
#plt.hist(tscat['HR_P2'])
#plt.hist(tscat['HR_P1'])
#
#points = plt.scatter(tscat.HR, tscat.RespRate,
#                     c=tscat.RespRate, s=100, cmap="Spectral") #set style options
##add a color bar
#plt.colorbar(points)
##sns.pointplot(x=tshr.HR, y=tsrr.RespRate)
#sns.regplot('HR','RespRate',data=tscat, scatter=False)
#
#plotTimeSeries()

