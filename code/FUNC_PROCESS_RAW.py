# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 13:18:51 2025

@title: FUNC_PROCESS_RAW
@author: haley.synan
@category:
    FUNCTIONS 
@purpose: 
    Functions to process the raw data to NEScapes formatted data 
History: 
    7/28/25: Created from existing code
    2/25/26: Updated functions 
"""

import numpy as np
from scipy.spatial import cKDTree
import os
import time
import gsw
import copernicusmarine
import pandas as pd
from datetime import datetime
import numpy as np
import re
from SB_support import readSB
import xarray as xr

def match_bathy(grid, b,bathy_tree):
    #using ckdtree instead of sel, method=nearest because I need to subset and get rid of positive bathymetry values
    #tested against match_nearest methods and results are the same except for getting rid of the postiive values
    target_coords = np.column_stack((grid.latitude, grid.longitude))
    distances, indices = bathy_tree.query(target_coords, k=1)  # k=1 for nearest valid
    grid['bathy'] = b.z[indices].values
    grid['bathy'] = grid.bathy.abs()
    return grid

def avg_bot_vert(indata, data_source):
    """
    Purpose:
        Vectorized function to average all values above a mixed layer depth per profile (based on unique profile id)
    Required input: 
        indata (df): dataframe with profiles and mld values
    Returns: 
         processed_data (df): dataframe with average values and statistics (ie min temp, max temp, num observations above mld, etc)
    History:
        2/22/26: Function initialized  
    """
    # Create a mask for all observations above the Mixed Layer Depth
    if data_source == 'argo':
        bot_mask = indata['pressure'] > (np.abs(indata['bathy'])-100)
    else: 
        bot_mask = indata['pressure'] > (np.abs(indata['bathy'])-10)
    # Filter the og dataframe to only data above the MLD
    filtered_df = indata[bot_mask].copy()
    # Identify profiles that have NO data above the MLD 
    valid_profiles = filtered_df['profile_uid'].unique()
    # Define which columns need to be averaged (floats) and which kept as is (strings, values that dont change, etc)
    float_cols = ['temperature', 'salinity', 'SA', 'CT', 'rho', 'alpha', 'beta', 'spiciness', 'pressure']
    meta_cols = ['latitude', 'longitude', 'time', 'dataset_id', 'source', 'month', 'profile_uid','bathy','year','day','source','station_id']
    
    # Group by profile ID on the filtered dataframe and average 
    means = filtered_df.groupby('profile_uid')[float_cols].mean()
    # Get metadata to match
    metadata = filtered_df.groupby('profile_uid')[meta_cols].first()
    # Calculate stats 
    profile_stats = indata.groupby('profile_uid').agg(
        min_prof_temp=('temperature', 'min'),
        max_prof_temp=('temperature', 'max'),
        min_prof_sal=('salinity', 'min'),
        max_prof_sal=('salinity', 'max'),
        prof_total_num_obs=('pressure', 'count') # Count from filtered_df instead? Use separate agg
    )
    profile_stats['num_obs_bot']=filtered_df.groupby('profile_uid').agg(num_obs_bot=('pressure', 'count'))
    # put back together 
    processed_data = metadata.join(means, rsuffix='_mean').join(profile_stats)
    return processed_data

def match_mld(indata,glorys_month_data,glorys_trees):
    """
    Purpose:
        Match rows of dataframe to a mixed layer depth cKDTree
    Required input: 
        indata (df): dataframe with coordinates to use for matching
        glorys_month_data (dict): dictionary of dataframes of mixed layer depth values by month
        glorys_trees (dict): dictionary of cKDTrees 
    Returns: 
         indata with matched mld values 
    History:
        2/22/26: Function initialized  
    """
    for m in range(1, 13):
        mask = indata['month'] == m
        if mask.any():
            distances, indices = glorys_trees[m].query(indata.loc[mask, ['latitude', 'longitude']].values)
            indata.loc[mask, 'mlotst'] = glorys_month_data[m]['mlotst'].iloc[indices].values
    return indata

def avg_mld_vert(indata):
    """
    Purpose:
        Vectorized function to average all values above a mixed layer depth per profile (based on unique profile id)
    Required input: 
        indata (df): dataframe with profiles and mld values
    Returns: 
         processed_data (df): dataframe with average values and statistics (ie min temp, max temp, num observations above mld, etc)
    History:
        2/22/26: Function initialized  
    """
    # Create a mask for all observations above the Mixed Layer Depth
    above_mld_mask = indata['pressure'] < indata['mlotst']
    # Filter the og dataframe to only data above the MLD
    filtered_df = indata[above_mld_mask].copy()
    # Identify profiles that have NO data above the MLD 
    valid_profiles = filtered_df['profile_uid'].unique()
    # Define which columns need to be averaged (floats) and which kept as is (strings, values that dont change, etc)
    float_cols = ['temperature', 'salinity', 'SA', 'CT', 'rho', 'alpha', 'beta', 'spiciness', 'pressure']
    meta_cols = ['latitude', 'longitude', 'time', 'dataset_id', 'source', 'month', 'profile_uid','mlotst','year','day','source','station_id']
    
    # Group by profile ID on the filtered dataframe and average 
    means = filtered_df.groupby('profile_uid')[float_cols].mean()
    # Get metadata to match
    metadata = filtered_df.groupby('profile_uid')[meta_cols].first()
    # Calculate stats 
    profile_stats = indata.groupby('profile_uid').agg(
        min_prof_temp=('temperature', 'min'),
        max_prof_temp=('temperature', 'max'),
        min_prof_sal=('salinity', 'min'),
        max_prof_sal=('salinity', 'max'),
        prof_total_num_obs=('pressure', 'count') # Count from filtered_df instead? Use separate agg
    )
    profile_stats['num_obs_above_mld']=filtered_df.groupby('profile_uid').agg(num_obs_above_mld=('pressure', 'count'))
    # put back together 
    processed_data = metadata.join(means, rsuffix='_mean').join(profile_stats)
    return processed_data

#create a dictionary of possible names for each column 
all_vars = {
    'temperature': ['sea_surface_temperature','temperature', 't090c','temp','surface_watertemp_degc','wt', 'sea_water_temperature', 'sea_water_temperature_profiler_depth_enabled','temppr01','temps901','temp_c'],
    'salinity':    ['sea_surface_salinity','sal00','sal','salinity','practical_salinity','surface_salinity','sa', 'psal', 'sea_water_practical_salinity', 'sea_water_practical_salinity_profiler_depth_enabled','psalst01','sea_water_salinity',
                    'psltzz01'],
    'latitude':    ['latitude','start_latitude','lat','latitude_start','deployment_latitude'],
    'longitude':   ['longitude','start_longitude','lon','longitude_start','deployment_longitude'],
    'time':        ['time','date_string','date_utc','towbegin','start_date','utc_datetime','datetime_utc'],
    'pressure':    ['prespr01','depth','press','pres','sea_pressure','z','sample_depth','deployment_water_depth_m'],
    'station_id':  ['cruise_id','station_id','cast','cruiseid','profile_id','survey','station','platform_number','id','sta','file_name','Station_Id','CTD_cast','platform_number','deployment_code'],
    'cast_num':    ['cast_number','townumber','tow_number','cycle_number']
}

def format_headernames(df, data_source):
    """
    Purpose:
        Find matching variable names (ie temp, or t0191c, etc) and rename to standardized variable names (ie temperature)
    Required input: 
        df (dataframe): dataframe containing original variable names
        data_source (str): name of data source (ie:'wod','bcodmo')
    Returns: 
         df (dataframe): original dataframe, but with standardized variable names (for temperature, latitude, salinity, longitude, time, and pressure)
    History:
        7/25: Created function from existing code 
        2/26: Updated to make more streamlined
    """
    df.columns = map(str.lower, df.columns) #change all be lowercase
    # 1. Build a renaming dictionary by checking which mapping keys exist in the DF
    vars_torename = {}
    for var_std, var_opt in all_vars.items():
        # Find the first alias that actually exists in the dataframe columns
        match = next((col for col in var_opt if col in df.columns), None)
        if match:
            vars_torename[match] = var_std
    df = df.rename(columns=vars_torename) #rename columns as needed 
    if 'station_id' not in df.columns:
        df['station_id'] = np.nan
    df['source'] = data_source #add column 

    print(f'Variable names for {data_source} detected and formatted.')
    return df


def avg_mld_buoy(indata):
    """
    Purpose:
        Vectorized function to average quasi-profiles temporally
    Required input: 
        indata (df): dataframe with profiles and mld values
    Returns: 
        processed_data (df): dataframe with average values and statistics (ie min temp, max temp, num observations above mld, etc)
    History:
        2/22/26: Function initialized  
    """
    # Create a mask for all observations above the Mixed Layer Depth
    above_mld_mask = indata['pressure'] < indata['mlotst']
    # Filter the og dataframe to only data above the MLD
    filtered_df = indata[above_mld_mask].copy()
    # Identify profiles that have NO data above the MLD 
    valid_profiles = filtered_df['profile_uid'].unique()
    # Define which columns need to be averaged (floats) and which kept as is (strings, values that dont change, etc)
    float_cols = ['temperature', 'salinity', 'SA', 'CT', 'rho', 'alpha', 'beta', 'spiciness', 'pressure']
    meta_cols = ['latitude', 'longitude', 'time', 'dataset_id', 'source', 'month', 'profile_uid','mlotst','year','day','source','station_id']
    
    # Group by profile ID on the filtered dataframe and average 
    means = filtered_df.groupby('profile_uid')[float_cols].mean()
    # Get metadata to match
    metadata = filtered_df.groupby('profile_uid')[meta_cols].first()
    # Calculate stats 
    profile_stats = indata.groupby('profile_uid').agg(
        min_prof_temp=('temperature', 'min'),
        max_prof_temp=('temperature', 'max'),
        min_prof_sal=('salinity', 'min'),
        max_prof_sal=('salinity', 'max'),
        prof_total_num_obs=('pressure', 'count') # Count from filtered_df instead? Use separate agg
    )
    profile_stats['num_obs_above_mld']=filtered_df.groupby('profile_uid').agg(num_obs_above_mld=('pressure', 'count'))
    # put back together 
    processed_data = metadata.join(means, rsuffix='_mean').join(profile_stats)
    return processed_data

def avg_mld_buoy_bot(indata):
    """
    Purpose:
        Vectorized function to average quasi-profiles temporally
    Required input: 
        indata (df): dataframe with profiles and mld values
    Returns: 
        processed_data (df): dataframe with average values and statistics (ie min temp, max temp, num observations above mld, etc)
    History:
        2/22/26: Function initialized  
    """
    # Create a mask for all observations above the Mixed Layer Depth
    bot_mask = indata['pressure'] > indata['bathy']
    # Filter the og dataframe to only data above the MLD
    filtered_df = indata[bot_mask].copy()
    # Identify profiles that have NO data above the MLD 
    valid_profiles = filtered_df['profile_uid'].unique()
    # Define which columns need to be averaged (floats) and which kept as is (strings, values that dont change, etc)
    float_cols = ['temperature', 'salinity', 'SA', 'CT', 'rho', 'alpha', 'beta', 'spiciness', 'pressure']
    meta_cols = ['latitude', 'longitude', 'time', 'dataset_id', 'source', 'month', 'profile_uid','bathy','year','day','source','station_id']
    
    # Group by profile ID on the filtered dataframe and average 
    means = filtered_df.groupby('profile_uid')[float_cols].mean()
    # Get metadata to match
    metadata = filtered_df.groupby('profile_uid')[meta_cols].first()
    # Calculate stats 
    profile_stats = indata.groupby('profile_uid').agg(
        min_prof_temp=('temperature', 'min'),
        max_prof_temp=('temperature', 'max'),
        min_prof_sal=('salinity', 'min'),
        max_prof_sal=('salinity', 'max'),
        prof_total_num_obs=('pressure', 'count') # Count from filtered_df instead? Use separate agg
    )
    profile_stats['num_obs_above_mld']=filtered_df.groupby('profile_uid').agg(num_obs_above_mld=('pressure', 'count'))
    # put back together 
    processed_data = metadata.join(means, rsuffix='_mean').join(profile_stats)
    return processed_data


def load_glorys_trees():
    """
    Purpose:
        Wrapper function to load MLD glorys nearest neighbor trees
    Required input: 
        na
    Returns: 
        glorys trees and glorys_month_data
    History:
        2/22/26: Function initialized  
    """
    # Load the GLORYS data once
    glorys_df = get_glorys_mld() 
    # Build 12 separate trees for nearest neighbor look up (1 for each month)
    # Create a dictionary to hold 12 trees
    glorys_trees = {}
    glorys_month_data = {}
    for m in range(1, 13):
        # Subset glorys data for that specific month
        month_subset = glorys_df[glorys_df['month'] == m].copy()
        glorys_month_data[m] = month_subset
        # Build and store the tree for this month's grid
        glorys_trees[m] = cKDTree(month_subset[['latitude', 'longitude']].values)
    return glorys_trees, glorys_month_data

def get_glorys_mld():
    """
    Purpose:
        Load dataframe of climatological mixed layer depth values from GLORYS. Tries to read locally first, if unable to find using the copernicusmarine package
    Required input: 
        None
    Returns: 
        glorys_df (dataframe) - contains gridded coordinates, month, and corresponding MLD values 
    History:
        7/25: Created function from existing code 
    """
    try: 
        glorys_df = pd.read_csv(r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/SOURCE_DATA/GLORYS/glorys_clima_mld.csv')
        print('Glorys MLD file found locally.')
    except FileNotFoundError:
        print('Glorys MLD file NOT found locally. Using copernicus marine package')
        datasetID = 'cmems_mod_glo_phy_my_0.083deg-climatology_P1M-m'
        ds = copernicusmarine.open_dataset(dataset_id = datasetID,
                                           minimum_longitude=-77, maximum_longitude=-63,
                                           minimum_latitude=34,maximum_latitude=46,)
        #subset to NWA
        ds = ds.where((ds.latitude > 34.40918) & (ds.latitude < 46.362305) & (-63>ds.longitude) & (-77< ds.longitude),drop=True) #define spatial bounds 
        glorys_df = ds.to_dataframe().reset_index()
        glorys_df.insert(2,'month',pd.to_datetime(glorys_df.time).dt.month)
        glorys_df.mlotst[np.isnan(glorys_df.mlotst)]=10 #IF MLD CLIMA IS NAN, MAKE 10 M THE DEFAULT
    return glorys_df

def get_varname(df, var_str):
    """
    Purpose:
        Return variable name from dataframe from list of options
    Required input: 
        df (dataframe): dataframe containing original variable names
        var_str (list): list of possible variable names to search for
    Returns: 
         var_opt (list): the variable name from the dataframe of a variable (ie temperature name is "temp" in dataframe)
    History:
        7/25: Created function from existing code 
    """
    df.columns = map(str.lower, df.columns) #change all be lowercase
    pattern = '|'.join(var_str)
    var_opt = df.loc[:, df.columns.str.contains(pattern)].columns.values #search for list of substrings 
    if len(var_opt)>1:
        var_opt = [t for t in df.columns if t in var_str]
        if len(var_opt)>1:
            var_opt = [[v] for v in var_opt] #turn each into list 
            var_opt = var_opt[0] #get first element 
    return list(var_opt)


import time   
def get_mtime(fname):
    """
    PURPOSE: 
        Return list of mtime(s) of file(s). 
    REQUIRED INPUT: 
        fname (str or list): single filename (or path) or list of filenames. 
    OPTIONAL INPUT: 
        None
    HISTORY:
        6/3/25: Function initialized
    """
    old_dir = os.getcwd()
    mts ={}
    if os.path.isdir(fname):
        os.chdir(fname)
        file = os.listdir()
        mt = [mts.update({f:time.ctime(os.path.getmtime(f))}) for f in file]
        os.chdir(old_dir)
        return mts

def add_monthvar(df):
    """
    Purpose:
        Add month variable to dataframe using time variable
    Required input: 
        df (dataframe): dataframe 
    Returns: 
         df (dataframe): input dataframe updated to have a column for month 
    History:
        7/25: Created function from existing code 
    """
    try: 
        df['month'] = pd.to_datetime(df.time).dt.month #add month var
    except: 
        df['month'] = [int(str(d).split('-')[1]) for d in df.time] #if formatted as a yyyy-mm-dd, remove mm and add to dataframe 
    print('Month variable added to dataframe')
    return df 

def gsw_conversions(df):
    """
    Purpose:
        Conversions (SA, CT, rho, spiciness, alpha, beta) using the GSW package
    Required input: 
        df (dataframe): dataframe
    Returns: 
         df (dataframe): original input dataframe but with columns for newly created variables 
    History:
        7/25: Created function from existing code 
    """
    df['SA'] = gsw.SA_from_SP(df.salinity.astype(float), df.pressure.astype(float), df.longitude.astype(float), df.latitude.astype(float))
    df['CT'] = gsw.CT_from_t(df.SA.astype(float), df.temperature.astype(float), df.pressure.astype(float))
    df['rho'] = gsw.rho(df.SA.astype(float), df.CT.astype(float), df.pressure.astype(float))
    df['alpha'] = gsw.alpha(df.SA.astype(float), df.CT.astype(float), df.pressure.astype(float))
    df['beta'] = gsw.beta(df.SA.astype(float), df.CT.astype(float), df.pressure.astype(float))
    df['spiciness'] = gsw.spiciness0(df.SA.astype(float),df.CT.astype(float)) 
    print('Successfully finished GSW conversions')
    return df

def check_format(df):
    """
    Purpose:
        Check formatting to ensure columns in dataframe exist and are the correct dtype
    Required input: 
        df (dataframe): dataframe
    Returns: 
         df (dataframe)
    History:
        7/25: Created function from existing code 
    """
    df['latitude'] = df.latitude.astype(float)
    df['longitude'] = df.longitude.astype(float)
    df['temperature'] = df.temperature.astype(float)
    df['salinity'] = df.salinity.astype(float)
    df['pressure'] = df.pressure.astype(float)
    df= df.loc[:, ~df.columns.duplicated()]
    return df

from datetime import datetime
def subset(df, start_year = 2000, end_year = 2024, minlat=33, maxlat=46, minlon=-77, maxlon=-63):
    """
    Purpose:
        subset dataframe to defined temporal and spatial bounds
    Required input: 
        df (dataframe): dataframe
        start_year (int, optional): default 2000
        end_year (int, optional): default 2024
        minlat (int/float, optional): default 33
        maxlat (int/float, optional): default is 46
        minlon (int/float, optional): default is -77
        maxlon (int/float, optional): default is -63 
    Returns: 
         
    History:
        7/25: Created function from existing code 
    """
    if df.time.dtype == 'int64': 
        if len(str(df.time[0])) == 8: 
            print('Datetime formatting detected as yyyymmdd.. converting..')
            df['time'] = [pd.to_datetime(str(x)) for x in df.time]
    #add year check 2000-2024
    
    df = df[(pd.to_datetime(df.time).dt.year > (start_year-1)) & (pd.to_datetime(df.time).dt.year < (end_year+1))]
    #subset by location
    df = df[(df.latitude > minlat) & (df.latitude < maxlat) & (df.longitude > minlon) & (df.longitude < maxlon)].reset_index()
    if len(df) == 0:
        print('Data not in study area. Skipping...')
        return None
    print('Spatial (NWA) and temporal (2000-2024) subsetting successfully completed')
    return df 
