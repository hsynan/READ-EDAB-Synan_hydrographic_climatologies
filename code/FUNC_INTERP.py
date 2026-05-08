# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 14:51:37 2025

@author: haley.synan

"""

import calendar
import geopandas as gpd
import rioxarray
from shapely.geometry import mapping
def make_nc(data,df,depth=''):
    lats=data.latitude.unique()
    lons=data.longitude.unique()
    cols_to_fix = data.columns.difference(['latitude', 'longitude'])
    is_land = globe.is_land(data.latitude.values, data.longitude.values)
    data.loc[is_land, cols_to_fix] = np.nan
    #stack dataframe into dataarrays for temp and sal 
    for x in range(1,13):
        d=xr.DataArray(data.set_index(['latitude', 'longitude']).to_xarray()[f'CT{calendar.month_name[x]}'], coords={"latitude": lats, "longitude": lons}, dims=["latitude", "longitude"])
        s=xr.DataArray(data.set_index(['latitude', 'longitude']).to_xarray()[f'CT{calendar.month_name[x]}'], coords={"latitude": lats, "longitude": lons}, dims=["latitude", "longitude"])
        if x ==1:
            ts=xr.DataArray(data.set_index(['latitude', 'longitude']).to_xarray()[f'CT{calendar.month_name[1]}'], coords={"latitude": lats, "longitude": lons}, dims=["latitude", "longitude"],name='CT')
            ss=xr.DataArray(data.set_index(['latitude', 'longitude']).to_xarray()[f'CT{calendar.month_name[1]}'], coords={"latitude": lats, "longitude": lons}, dims=["latitude", "longitude"],name='SA')
        else: 
            ts = xr.concat([ts,d],dim='month')
            ss= xr.concat([ss,s],dim='month')
    
    
    std_devs_SA = []
    std_devs_CT=[]
    numobs=[]
    
    for x in range(1, 13):
        sub = df[df.month == x]
        
        xx = np.linspace(34.41, 46.36, 80)
        yy = np.linspace(-77.68, -63.59, 94)
        
        # Define your edges just like before
        dx = xx[1] - xx[0]
        dy = yy[1] - yy[0]
        x_edges = np.concatenate(([xx[0] - dx/2], xx + dx/2))
        y_edges = np.concatenate(([yy[0] - dy/2], yy + dy/2))
        
        # Use binned_statistic_2d instead of histogram2d
        # Replace 'target_column' with the actual column name you want the SD of
        statistic, _, _, _ = binned_statistic_2d(
            sub.latitude.values,
            sub.longitude.values,
            sub.SA.values, 
            statistic='std', 
            bins=[x_edges, y_edges]
        )
        
        std_devs_SA.append(statistic)
        statistic_ct, _, _, _ = binned_statistic_2d(
            sub.latitude.values,
            sub.longitude.values,
            sub.CT.values, 
            statistic='std', 
            bins=[x_edges, y_edges]
        )
        
        std_devs_CT.append(statistic_ct)
        H, _, _ = np.histogram2d(
            sub.latitude.values,
            sub.longitude.values,
            bins=[x_edges, y_edges]
        )
        numobs.append(H)

    std_t = xr.DataArray(std_devs_CT, coords = {'latitude':lats,"longitude":lons}, dims=["month","latitude", "longitude"],name='CT_std')
    std_s = xr.DataArray(std_devs_SA, coords = {'latitude':lats,"longitude":lons}, dims=["month","latitude", "longitude"],name='SA_std')
    no = xr.DataArray(numobs, coords = {'latitude':lats,"longitude":lons}, dims=["month","latitude", "longitude"],name='num_obs')
    
    ds = xr.merge([ts, std_t, ss,std_s,no])
    if depth =='bottom':
        if ds.rio.crs is None:
            ds.rio.write_crs("epsg:4326", inplace=True)
        shp = gpd.read_file(r'https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies/raw/refs/heads/main/data/shapefiles/NES_5REGIONS.zip')
        
        shp['geometry'] = shp.geometry.buffer(0.4)
        shp.crs = "epsg:4326"
        shp = shp.to_crs(ds.rio.crs)
        ds = ds.rio.clip(shp.geometry.apply(mapping), ds.rio.crs, drop=True)
    return ds


import numpy as np
from scipy.ndimage import binary_dilation
from global_land_mask import globe
from scipy.stats import binned_statistic_2d
def outlier_sum_stats(df,border_mask, var='SA',gridsize=1):
    """
    PURPOSE: 
        create standard deviation and standard deviation summary statistics 
    REQUIRED INPUT: 
        df (dataframe)
        border_mask (array): determines whether cell borders land or not
    OPTIONAL INPUT: 
        var (string): name of variable to get statistics on in dataframe
        gridsize (int): size in degrees of equidistant grid.
    HISTORY:
        3/4/26: Function initialized with assistance from google gemini AI 
    """
    #1-D list of lat/lon
    lat_range = np.arange(34, 47, gridsize)   
    lon_range = np.arange(-77, -62, gridsize)  
    lon_grid, lat_grid = np.meshgrid(lon_range, lat_range) #2D grid
    mean_stat, _, _, bin_indices = binned_statistic_2d(
        df['latitude'], df['longitude'], df[var], 
        statistic='mean', bins=[lat_range, lon_range], expand_binnumbers=True
    )
    std_stat, _, _, _ = binned_statistic_2d(
        df['latitude'], df['longitude'], df[var], 
        statistic='std', bins=[lat_range, lon_range]
    )
    row_lat_bins = bin_indices[0] - 1 #bins start at one, index starts at 0 (make bin startat 0)
    row_lon_bins = bin_indices[1] - 1
    df[f'cell_mean_{var}'] = mean_stat[row_lat_bins, row_lon_bins]
    df[f'cell_std_{var}'] = std_stat[row_lat_bins, row_lon_bins]
    df['threshold']=np.where(border_mask[row_lat_bins, row_lon_bins], 5, 3) #if cell borders land, use 5 std, else use 3
    return df

from NESCAPES_func_processraw import get_mtime
def compare_mtime(source_dir, proc_dir):
    """
    PURPOSE: 
        Compare source data directories and processed data directories and compare the last modified time. If there is new source data since the last processing,
        function will process that new data. 
    REQUIRED INPUT: 
        source_dir (path): path to source data
        proc_dir (path): path to processed data
    OPTIONAL INPUT: 
        None
    HISTORY:
        7/30/25: Function initialized
    """
    source_mtime=get_mtime(source_dir)
    proc_mtime = get_mtime(proc_dir)
    for target_substring in list(source_mtime.keys()):
        for key1 in source_mtime:
            if target_substring in key1:
                for key2 in proc_mtime:
                    if target_substring in key2:
                        if source_mtime[key1] > proc_mtime[key2]:
                            print(f'There is new source data since last processing for the {key1} dataset! Processing new data....')
                            from NESCAPES_func_sources_urls import get_source
                            from NESCAPES_func_processraw import get_glorys_mld
                            from NESCAPES_func_processraw import source_tomld
                            glorys_df = get_glorys_mld() #load glorys data 
                            source = get_source() #get all source files 
                            source_tomld(source, key1, proc_dir, glorys_df)
                        else:
                            print(f'No new data for {key1} dataset')
    print('Ready to move on to next steps!')
                            
       
from scipy.spatial import cKDTree
def find_closest_pairs(df1, df2,var,latvar,lonvar,month=None):
    """Finds the closest coordinate pairs between two dataframes."""

    # Create KDTree for efficient nearest neighbor search
    tree = cKDTree(df2[[latvar, lonvar]].values)

    # Query the tree for each point in df1
    distances, indices = tree.query(df1[[latvar, lonvar]].values)

    

    # Create a new dataframe to store the results
    result_df = df1.copy()
    try:
        result_df[str(month)+'_'+var] = df2[var].iloc[indices].values
    except:
        result_df[str(month)+'_'+var]= df2[var].iloc[indices].values
    
    #result_df['closest_lat'] = df2['lat'].iloc[indices].values
    #result_df['closest_lon'] = df2['lon'].iloc[indices].values
    #result_df['distance'] = distances

    return result_df #[str(month)+'_'+var]

def match_nearest(df, ds, var, new_name, date=None):
    try:
        df = df.rename(columns={'lat':'latitude','lon':'longitude'})
    except:
        pass
    try:
        d = []
        for i in range(0, len(df)):
            # Crop the dataset to include data that corresponds to track locations
            cropped_ds = ds[var].sel(time=df.date[i],
                                           latitude=df.latitude[i],
                                           longitude=df.longitude[i],
                                           method='nearest'
                                           )
            d.append(cropped_ds.values)
        df.insert(0,new_name,d)
        return df
    except:
        d = []
        for i in range(0, len(df)):
            # Crop the dataset to include data that corresponds to track locations
            cropped_ds = ds[var].sel(latitude=df.latitude[i],
                                           longitude=df.longitude[i],
                                           method='nearest'
                                           )
            d.append(cropped_ds.values)
        df.insert(0,new_name,d)
        return df

import urllib
import xarray as xr
def create_grid(grid='equidistant'):
    #create grid
    if grid == 'equidistant':
        xx = np.linspace(34.41,46.36,80)
        yy = np.linspace(-77.68,-63.59,94)
        #xx = np.linspace(34.41,46.36,140)
        #yy = np.linspace(-77.68,-63.59,134)
        Xv =(xx,yy) #GRID LOCATIONS
        grid_size = (len(xx),len(yy))
        gridX = np.meshgrid(xx,yy)[0].flatten()
        gridY=np.meshgrid(xx,yy)[1].flatten()
        gridX = np.round(gridX, decimals=2)
        gridY= np.round(gridY, decimals=2)
        print('Equidistant grid created...')
    elif grid == 'sinusoidal':
    
        #get dataset with desirable grid
        url=''.join(['https://www.oceancolour.org/thredds/ncss/CCI_ALL-v6.0-DAILY?var=chlor_a&north=44.36&west=-77.68&east=-63.59&south=34.41&horizStride=1&time_start=2024-07-02T00%3A00%3A00Z&time_end=2024-07-02T00%3A00%3A00Z&timeStride=1&accept=netcdf'])
        file = 'fname.nc'
        urllib.request.urlretrieve(url, file) #download data
        ds = xr.open_dataset(file, decode_cf=True) #open nc file 
        #input_data= ds.to_dataframe().dropna().reset_index()

        #create grid
        Xv =(ds.lat,ds.lon) #GRID LOCATIONS
        gridX ,gridY= np.meshgrid(ds.lat,ds.lon)
        gridX = np.round(gridX.flatten(), decimals=2)
        gridY= np.round(gridY.flatten(), decimals=2)
        grid_size = (len(ds.lat), len(ds.lon))
        print('Sinusoidal grid created...')
    return Xv, gridX, gridY, grid_size


#from sklearn.metrics import mean_squared_error
from math import sqrt
from scipy.interpolate import LinearNDInterpolator
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import cartopy
import warnings
from scipy.spatial.distance import cdist

def calc_Verror(V, Vq, gridX, gridY, Xcell,ii, data): 
    interp = LinearNDInterpolator(list(zip(gridX, gridY)), Vq.flatten())
    interp_v = interp(data.lat,data.lon)
    Verr = V - interp_v 
    rmse=np.nanmean(Verr**2)
    outside =np.where(Verr.isna()==True)
    try:
        Verr[outside] = 0
    except:
        Verr[outside[0]] = 0
    print('Barnes iteration ' + str(ii) + ', average RMS error is ' + str(rmse))
    return rmse, Verr

def parse_inputs(X, V, Xq, Xv,n_interations=3, convergenceparam=0.3, gaussianvariance=float('nan')): 
    params={}
    params['iterations']=n_interations
    params['gaussianvariance']=gaussianvariance
    params['convergenceparameter']=convergenceparam #convergence parameter is to mitigate oversmoothing of data 
    
    if len(X) != len(V):
        raise Exception('The sizes of ''V'' and ''X'' do not match. V must have one value for each row in X')
    
    #remove data points with nan/inf
    remove = np.where(np.isfinite(X)==False)
    X[np.isfinite(X)]
    V[np.isfinite(V)]
    
    #setup parameters, store variable sizes
    params['D'] = X.ndim
    params['nData'] = len(X)
    params['grid_size'] = (len(Xv[0]),len(Xv[1]))
    params['nGrid'] = np.prod(params['grid_size'])
    
    
    A = np.prod(np.max(X, axis=0) - np.min(X,axis=0))
    M = params['nData']
    params['data_spacing'] = sqrt(A)*(1+sqrt(M))/(M-1) #put into dict params
    
    params['optimal_var']=(2*params['data_spacing']/math.pi)**2 * params['convergenceparameter']**(-params['iterations'])
    
    if math.isnan(params['gaussianvariance'])== True:
        params['gaussianvariance'] = params['optimal_var']
    else: 
        raise Exception('Gaussian variance is small. The optimal value is '+str(params['optimal_var']))
    
    params['gaussianstd'] = sqrt(params['gaussianvariance'])


    # Warn if the grid spacing is not appropriate for the data spacing
    #Limits from Koch 1983: 1/3 <= (dn/[grid spacing]) <= 1/2, where dn is the average nearest-neighbor spacing of the data points
    min_grid_spacing = min((np.diff(Xv[0]).min(),np.diff(Xv[1]).min()))
    max_grid_spacing = max((np.diff(Xv[0]).max(),np.diff(Xv[1]).max()))
    if (min_grid_spacing/params['data_spacing']) < 0.333:
        warnings.warn('Grid spacing should be larger than ' + str(params['data_spacing']/3)+ '. Smallest grid spacing: '+ str(min_grid_spacing)+'. Data spacing: '
              + str(params['data_spacing']))
    if (max_grid_spacing/params['data_spacing']) > 0.5: 
        warnings.warn('Note that grid spacing can be smaller than ' + str(params['data_spacing']/2) + '. Largest grid spacing: ' + str(max_grid_spacing) + 
                      '. Data spacing: ' + str(params['data_spacing']))
        
    # Warn if some grid points are far from the data points
    r = np.round(cdist(Xq,X),decimals=4) 
    np.sum(r<=2*params['gaussianstd'])
    
    if any(np.sum(r<=2*params['gaussianstd'],axis=1)<3):
        warnings.warn('Some grid points are far from any data points. Consider modifying the grid.')
    return params, X, V, Xq 

roi1 = []
roi2=[]
roi3=[]


import numpy as np
from scipy.spatial.distance import cdist
def barnesn(X, V, Xv, Xq, data, gridX, gridY, n_interations=3, convergenceparam=0.3, gaussianvariance=float('nan')):
    params, X, V, Vq = parse_inputs(X, V, Xq, Xv,n_interations, convergenceparam, gaussianvariance)
    
    #set up for analysis 
    from scipy.spatial.distance import cdist
    r = np.round(cdist(Xq,X),decimals=4) #matches matlab
    outer_data = [1]*len(data)
    W=[]
    for ii in range(0,params['iterations']):
        w = np.exp(-r**2/params['gaussianvariance']*params['convergenceparameter']**ii)
        sum_w = np.repeat(np.sum(w,axis=1), len(X)).reshape(len(gridX),len(V))
        W.append(w/sum_w) #matches
        if ii==0:
            roi1.append(params['gaussianvariance']/params['convergenceparameter']**ii)
        elif ii == 1:
            roi2.append(params['gaussianvariance']/params['convergenceparameter']**ii)
        elif ii ==2: 
            roi3.append(params['gaussianvariance']/params['convergenceparameter']**ii)
    
    #first pass
    ii = 0
    outer_grid = [1]*len(gridX)
    f = np.tile(V.values, len(outer_grid)).reshape(len(outer_grid),len(V))
    Vq= np.sum(W[ii]*f,axis=1)
    
    #subsequent passes
    Xcell = (data.lat.values,data.lon.values)
    Verr = calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)[1]
    rmse=[]
    rmse.append(calc_Verror(V, Vq, gridX, gridY, Xcell,ii, data)[0])
    for ii in range(1,params['iterations']):
        f = np.tile(Verr.values, len(outer_grid)).reshape(len(outer_grid),len(V))
        Vq = Vq + np.sum(W[ii]*f,axis=1)
        rms,Verr = calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)
        rmse.append( calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)[0])
        
    # ---------------------------------------------------------
    # NEW: Error Propagation and Data Density Calculation
    # ---------------------------------------------------------
    
    # 1. Propagate the standard error using the first pass normalized weights (W[0])
    W_squared = W[0] ** 2

    # 2. Calculate "Data Density" (Sum of unnormalized weights)
    # This tells you how far a grid cell actually is from in situ data
    w_unnorm = np.exp(-r**2 / params['gaussianvariance'])
    dd = np.max(w_unnorm, axis=1).reshape(len(Xv[1]), len(Xv[0]))
        
    Vq = Vq.reshape(len(Xv[1]),len(Xv[0]))
    #Vq = Vq.reshape(grid_size)
    return Vq, params, rmse, roi1,roi2,roi3,dd
'''
def barnesn(X, V, Xv, Xq, data, gridX, gridY, n_interations=3, convergenceparam=0.3, gaussianvariance=float('nan')):
    params, X, V, Vq = parse_inputs(X, V, Xq, Xv,n_interations, convergenceparam, gaussianvariance)
    
    #set up for analysis 
    from scipy.spatial.distance import cdist
    r = np.round(cdist(Xq,X),decimals=4) #matches matlab
    outer_data = [1]*len(data)
    W=[]
    WW = []
    iu_raw_density = np.zeros(len(gridX))
    for ii in range(0,params['iterations']):
        w = np.exp(-r**2/params['gaussianvariance']*params['convergenceparameter']**ii)
        sum_w = np.repeat(np.sum(w,axis=1), len(X)).reshape(len(gridX),len(V))
        current_sum_w = np.sum(w, axis=1)
        sum_w_grid = np.repeat(current_sum_w, len(X)).reshape(len(gridX), len(V))
        WW.append(w/sum_w_grid)
        # Capture the density on the first pass for Uncertainty
        if ii == 0:
            iu_raw_density = current_sum_w
        W.append(w/sum_w) #matches
        if ii==0:
            roi1.append(params['gaussianvariance']/params['convergenceparameter']**ii)
        elif ii == 1:
            roi2.append(params['gaussianvariance']/params['convergenceparameter']**ii)
        elif ii ==2: 
            roi3.append(params['gaussianvariance']/params['convergenceparameter']**ii)
    # --- FIX: Calculate IU safely ---
    if iu_raw_density.max() > 0:
        iu_grid = 1 - (iu_raw_density / iu_raw_density.max())
    else:
        # If no data is found, uncertainty is 1 everywhere
        iu_grid = np.ones(len(gridX))
    
    # Reshape IU to match the 2D grid (Lat x Lon)
    iu_grid = iu_grid.reshape(len(Xv[1]), len(Xv[0]))
    
    #first pass
    ii = 0
    outer_grid = [1]*len(gridX)
    f = np.tile(V.values, len(outer_grid)).reshape(len(outer_grid),len(V))
    Vq= np.sum(W[ii]*f,axis=1)
    
    #subsequent passes
    Xcell = (data.lat.values,data.lon.values)
    Verr = calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)[1]
    rmse=[]
    rmse.append(calc_Verror(V, Vq, gridX, gridY, Xcell,ii, data)[0])
    for ii in range(1,params['iterations']):
        f = np.tile(Verr.values, len(outer_grid)).reshape(len(outer_grid),len(V))
        Vq = Vq + np.sum(W[ii]*f,axis=1)
        rms,Verr = calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)
        rmse.append( calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)[0])
        
    Vq = Vq.reshape(len(Xv[1]),len(Xv[0]))
    #Vq = Vq.reshape(grid_size)
    return Vq, params, rmse, roi1,roi2,roi3,iu_grid
'''

'''
def barnesn(X, V, Xv, Xq, data, gridX, gridY, n_interations=3, convergenceparam=0.3, gaussianvariance=float('nan')):
    params, X, V, Vq = parse_inputs(X, V, Xq, Xv,n_interations, convergenceparam, gaussianvariance)
    
    #set up for analysis 
    from scipy.spatial.distance import cdist
    r = np.round(cdist(Xq,X),decimals=4) #matches matlab
    outer_data = [1]*len(data)
    W=[]
    for ii in range(0,params['iterations']):
        w = np.exp(-r**2/params['gaussianvariance']*params['convergenceparameter']**ii)
        sum_w = np.repeat(np.sum(w,axis=1), len(X)).reshape(len(gridX),len(V))
        W.append(w/sum_w) #matches
        if ii==0:
            roi1.append(params['gaussianvariance']/params['convergenceparameter']**ii)
        elif ii == 1:
            roi2.append(params['gaussianvariance']/params['convergenceparameter']**ii)
        elif ii ==2: 
            roi3.append(params['gaussianvariance']/params['convergenceparameter']**ii)
    
    #first pass
    ii = 0
    outer_grid = [1]*len(gridX)
    f = np.tile(V.values, len(outer_grid)).reshape(len(outer_grid),len(V))
    Vq= np.sum(W[ii]*f,axis=1)
    
    #subsequent passes
    Xcell = (data.lat.values,data.lon.values)
    Verr = calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)[1]
    rmse=[]
    rmse.append(calc_Verror(V, Vq, gridX, gridY, Xcell,ii, data)[0])
    for ii in range(1,params['iterations']):
        f = np.tile(Verr.values, len(outer_grid)).reshape(len(outer_grid),len(V))
        Vq = Vq + np.sum(W[ii]*f,axis=1)
        rms,Verr = calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)
        rmse.append( calc_Verror(V,Vq,gridX, gridY,Xcell,ii,data)[0])
        
    Vq = Vq.reshape(len(Xv[1]),len(Xv[0]))
    #Vq = Vq.reshape(grid_size)
    return Vq, params, rmse, roi1,roi2,roi3
'''
