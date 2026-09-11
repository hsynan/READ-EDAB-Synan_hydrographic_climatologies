# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 11:22:55 2026
@title: hydro_climas_func_interp3D.py
@author: haley.synan
@category:
    FUNCTIONS 
@purpose: 
    Functions to interpolate formatted data 
History: 
    7/28/25: Created from existing code
    8/26: Updated uncertainty function
"""

from math import sqrt
from scipy.interpolate import LinearNDInterpolator
import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt
import cartopy
import warnings
from scipy.spatial.distance import cdist
import numpy as np
import pandas as pd
import math
from math import sqrt
from scipy.interpolate import LinearNDInterpolator
from scipy.spatial.distance import cdist
import warnings

from scipy.interpolate import RegularGridInterpolator
rms = {}
def calc_Verror(V, Vq, gridX, gridY, Xcell, ii, data, target_month, Xv): 
    # Handle pandas series vs numpy array
    if isinstance(V, pd.Series):
        V_vals = V.values
    else:
        V_vals = V
        
    # 1. Reshape Vq back to 2D (meshgrid default shape is len(y), len(x))
    grid_shape = (len(Xv[1]), len(Xv[0]))
    Vq_2d = Vq.reshape(grid_shape)
    
    # 2. Use RegularGridInterpolator (Instant interpolation)
    # Note: Xv[1] is yy (longitude/y-axis), Xv[0] is xx (latitude/x-axis)
    interp = RegularGridInterpolator((Xv[1], Xv[0]), Vq_2d, bounds_error=False, fill_value=np.nan)
    
    # Interpolate at the station locations
    interp_v = interp(list(zip(data.longitude, data.latitude)))
        
    Verr = V_vals - interp_v 
    #Verr = np.nan_to_num(Verr, nan=0.0) #NEW ADDITION
    
    # Isolate target month data
    is_target_month = (data.month == target_month)
    
    # Calculate RMSE ONLY for the target month's data points
    rmse = np.nanmean(Verr[is_target_month]**2)
    
    # Force the residual of all other months to 0 
    Verr[~is_target_month] = 0
    
    # Handle NaNs from interpolating outside the grid
    if hasattr(Verr, 'isna'):
        outside = np.where(Verr.isna() == True)
    else:
        outside = np.where(np.isnan(Verr))
        
    try:
        Verr[outside] = 0
    except:
        if len(outside[0]) > 0:
            Verr[outside[0]] = 0
            
    #rms.update({ii: rmse})
    #Verr[~is_target_month] = 0
    
    # NEW: Catch NaNs AND Infinities
    #Verr = np.nan_to_num(Verr, nan=0.0, posinf=0.0, neginf=0.0) 
        
    rms.update({ii: rmse})
    print(f'Barnes iteration {ii+1} (Month {target_month}): average RMSE error is {rmse:.4f}')
    print(f'Barnes iteration {ii+1} (Month {target_month}): average RMSE error is {rmse:.4f}')
    
    return rmse, Verr


def parse_inputs(X, V, T, Xq, Xv, n_interations=3, convergenceparam=0.3, gaussianvariance=float('nan'), temporal_variance=1.0): 
    params = {}
    params['iterations'] = n_interations
    params['gaussianvariance'] = gaussianvariance
    params['convergenceparameter'] = convergenceparam 
    params['temporal_variance'] = temporal_variance 
    
    if len(X) != len(V) or len(X) != len(T): 
        raise Exception('The sizes of V, X, and T do not match.')
    
    # Remove data points with nan/inf
    valid_mask = np.isfinite(X).all(axis=1) & np.isfinite(V) & np.isfinite(T) 
    X = X[valid_mask]
    V = V[valid_mask]
    T = np.array(T)[valid_mask] 
    
    # Setup parameters, store variable sizes
    params['D'] = X.ndim
    params['nData'] = len(X)
    params['grid_size'] = (len(Xv[0]), len(Xv[1]))
    params['nGrid'] = np.prod(params['grid_size'])
    
    A = np.prod(np.max(X, axis=0) - np.min(X, axis=0))
    M = params['nData'] /12
    params['data_spacing'] = sqrt(A)*(1+sqrt(M))/(M-1) 
    
    params['optimal_var'] = (2*params['data_spacing']/math.pi)**2 * params['convergenceparameter']**(-params['iterations'])
    print(f'The gaussian variance is {params["optimal_var"]}')
    
    if math.isnan(params['gaussianvariance']):
        params['gaussianvariance'] = params['optimal_var']
    elif params['gaussianvariance'] < params['optimal_var']/10: # Just a soft warning threshold now
        warnings.warn('Gaussian variance might be too small. The optimal theoretical value is '+str(params['optimal_var']))
    
    params['gaussianstd'] = sqrt(params['gaussianvariance'])

    min_grid_spacing = min((np.diff(Xv[0]).min(), np.diff(Xv[1]).min()))
    max_grid_spacing = max((np.diff(Xv[0]).max(), np.diff(Xv[1]).max()))
    if (min_grid_spacing/params['data_spacing']) < 0.333:
        warnings.warn('Grid spacing should be larger than ' + str(params['data_spacing']/3))
    if (max_grid_spacing/params['data_spacing']) > 0.5: 
        warnings.warn('Note that grid spacing can be smaller than ' + str(params['data_spacing']/2))
        
    # NOTE: The memory-crashing cdist() warning check has been removed from here.
    
    return params, X, V, T, Xq 

def barnesn(X, V, T, target_month, Xv, Xq, data, gridX, gridY, n_interations=3, convergenceparam=0.3, gaussianvariance=float('nan'), temporal_variance=1.0):
    params, X, V, T, Xq = parse_inputs(X, V, T, Xq, Xv, n_interations, convergenceparam, gaussianvariance, temporal_variance)
    
    # 1. Temporal Math
    dt_raw = np.abs(T - target_month) 
    dt = np.minimum(dt_raw, 12 - dt_raw) # Circular distance
    dt_squared_scaled = dt**2 / params['temporal_variance']
    is_target = (T == target_month) # Boolean mask for Pass 2+
    
    # 2. Pre-allocate arrays
    Vq = np.zeros(len(Xq))
    dd = np.zeros(len(Xq))
    rmse_dict = {}
    
    roi1, roi2, roi3 = [], [], []
    
    if isinstance(V, pd.Series):
        V_vals = V.values
    else:
        V_vals = V
        
    Xcell = (data.latitude.values, data.longitude.values)
    chunk_size = 400 # Memory cap (~2GB max RAM usage)

    print("Pre-calculating distance matrix...")
    r_chunks_sq = []
    for start_idx in range(0, len(Xq), chunk_size):
        end_idx = min(start_idx + chunk_size, len(Xq))
        # Calculate distance, square it immediately, and save to memory
        r_dist = np.round(cdist(Xq[start_idx:end_idx], X), decimals=4)
        r_chunks_sq.append(r_dist**2)
    print('Done calculating distance matrix..')
    # ==========================================
    
    # 3. Successive Correction Loop
    for ii in range(params['iterations']):
        print('Starting corrections..')
        Vq_pass = np.zeros(len(Xq))
        
        # Calculate and print the true Radius of Influence
        current_spatial_var = params['gaussianvariance'] * (params['convergenceparameter']**ii)
        current_temporal_var = params['temporal_variance'] * (params['convergenceparameter']**ii)
        
        spatial_roi = math.sqrt(current_spatial_var)
        temporal_roi = math.sqrt(current_temporal_var)
        
        print(f"--- Pass {ii+1} ---")
        if ii == 0: 
            print(f"Temporal ROI: {temporal_roi:.3f} months")
        print(f"Spatial ROI: {spatial_roi:.3f} degrees")
        
        # Determine values to interpolate
        if ii == 0:
            f_vals = V_vals
            roi1.append(params['gaussianvariance'] / params['convergenceparameter']**ii)
        else:
            f_vals = Verr.values if hasattr(Verr, 'values') else Verr
            if ii == 1:
                roi2.append(params['gaussianvariance'] / params['convergenceparameter']**ii)
            elif ii == 2:
                roi3.append(params['gaussianvariance'] / params['convergenceparameter']**ii)      
                
        chunk_idx = 0 # Track which chunk we are on
        
        # Loop through grid points in memory-safe batches
        for start_idx in range(0, len(Xq), chunk_size):
            end_idx = min(start_idx + chunk_size, len(Xq))
            
            # Grab the pre-calculated squared distances
            dist_sq_chunk = r_chunks_sq[chunk_idx]
            chunk_idx += 1
            
            # Spatiotemporal penalty
            spatio_temporal_penalty = (dist_sq_chunk / params['gaussianvariance']) + dt_squared_scaled
            
            # Apply convergence parameter to shrink the radius
            w_chunk = np.exp(-spatio_temporal_penalty / (params['convergenceparameter']**ii))
            
            # Save Data Density on first pass
            #if ii == 2:
            #    dd[start_idx:end_idx] = np.max(w_chunk, axis=1)
            if ii == 2:
                w_for_density = w_chunk[:, is_target] 
                if w_for_density.shape[1] > 0: #if its is in the target month then proceed
                    dd[start_idx:end_idx] = np.max(w_for_density, axis=1)
                else:
                    dd[start_idx:end_idx] = 0.0
                
            # Filter weights and data based on the pass
            if ii == 0:
                # Pass 1: Use all months to build the seasonal background
                w_active = w_chunk
                f_active = f_vals
            else:
                # Pass 2+: ONLY use the target month's data to apply corrections
                w_active = w_chunk[:, is_target]
                f_active = f_vals[is_target]
                
            sum_w_active = np.sum(w_active, axis=1)
            valid = sum_w_active > 1e-10 # Prevent divide-by-zero in empty regions
            
            chunk_result = np.zeros(end_idx - start_idx)
            chunk_result[valid] = np.dot(w_active[valid, :], f_active) / sum_w_active[valid]
            
            # Apply to grid
            if ii == 0:
                Vq_pass[start_idx:end_idx] = chunk_result
            else:
                Vq_pass[start_idx:end_idx] = Vq[start_idx:end_idx] + chunk_result
                
        # Update our primary grid for this pass
        Vq = Vq_pass
        #Vq = np.nan_to_num(Vq, nan=0.0) #NEW ADDITION
        
        # Calculate errors at the station locations
        # NEW: Xv is passed at the end for the RegularGridInterpolator fix
        rms_val, Verr = calc_Verror(V, Vq, gridX, gridY, Xcell, ii, data, target_month, Xv)
        rmse_dict[ii] = rms_val
        
    # 4. Final reshaping to match grid axes
    Vq = Vq.reshape(len(Xv[1]), len(Xv[0]))
    dd = dd.reshape(len(Xv[1]), len(Xv[0]))
    #Vq = np.nan_to_num(Vq, nan=0.0, posinf=0.0, neginf=0.0) #NEW
    #dd = np.nan_to_num(dd, nan=0.0, posinf=0.0, neginf=0.0) #NEW
    
    return Vq, params, rmse_dict, roi1, roi2, roi3, dd, rmse_dict

import urllib
import xarray as xr
def create_grid(grid='equidistant'):
    #create grid
    if grid == 'equidistant':
        #xx = np.linspace(34.41,46.36,80)
        #yy = np.linspace(-77.68,-63.59,94)
        step = 1/12
        xx = np.arange(34.41, 46.36 + step / 2, step)
        yy = np.arange(-77.68, -63.59 + step / 2, step)
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


from scipy.stats import binned_statistic_2d
def get_stats(df,ds): 
    std_devs_SA = []
    std_devs_CT=[]
    numobs=[]
    lats=ds.latitude.values
    lons=ds.longitude.values
    
    for x in range(1, 13):
        sub = df[df.month == x]
        step = 1/12
        xx = np.arange(34.41, 46.36 + step / 2, step)
        yy = np.arange(-77.68, -63.59 + step / 2, step)
        
        #xx = np.linspace(34.41, 46.36, 80)
        #yy = np.linspace(-77.68, -63.59, 94)
        
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
    ds['CT_std'] = std_t
    ds['SA_std'] = std_s
    ds['num_obs'] = no
    return ds

import calendar
import geopandas as gpd
import rioxarray
from shapely.geometry import mapping

def calculate_continuous_error(grid_std, data_density):
    # Prevent division by absolute zero
    epsilon = 1e-6
    
    # Cap density at minimum to prevent zero-division
    # NOTE: Remove a_max=1.0 if data_density is raw point counts (N)
    safe_density = np.nan_to_num(data_density, nan=0.0)
    effective_density = np.clip(data_density, a_min=epsilon, a_max=None)
    
    # Replaces 0.0/0.0 NaNs with the average grid error
    baseline_error = np.nanmean(grid_std)
    safe_grid_std = np.where(np.isnan(grid_std), baseline_error, grid_std)
    worst_real_error = np.nanpercentile(grid_std, 99)
    # Set the cap to 1.5x or 2.0x that value
    dynamic_cap = worst_real_error * 2.0
    # Inflate the error 
    inflated_se = safe_grid_std / np.sqrt(effective_density)
    
    # Cap the maximum error
    inflated_se = np.clip(inflated_se, a_min=0, a_max=dynamic_cap)
    
    return inflated_se

def normalize_climatology_errors(monthly_error_grids):
    """
    Normalizes a stack of monthly error grids to a global 0.0 - 1.0 scale.
    
    Parameters:
    monthly_error_grids : ndarray or list
        A 3D array of shape (12, len(Y), len(X)) containing the 
        inflated_se output for each of the 12 months.
        
    Returns:
    normalized_grids : ndarray
        The same 3D array, scaled from 0.0 to 1.0.
    """
    # Convert list to array if necessary
    error_stack = np.asarray(monthly_error_grids)
    
    # 1. Find the absolute minimum and maximum across the ENTIRE year
    # Using nanmin/nanmax safely ignores any remaining NaNs
    global_min = np.nanmin(error_stack)
    global_max = np.nanmax(error_stack)
    
    # 2. Apply the Min-Max formula to the entire 3D stack at once
    normalized_grids = (error_stack - global_min) / (global_max - global_min)
    
    return normalized_grids

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
        df['latitude'].astype(float), df['longitude'].astype(float), df[var].astype(float), 
        statistic='mean', bins=[lat_range, lon_range], expand_binnumbers=True
    )
    std_stat, _, _, _ = binned_statistic_2d(
        df['latitude'].astype(float), df['longitude'].astype(float), df[var].astype(float), 
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
    
    
def calculate_uncertainty(ds):
    unc_CT = []
    unc_SA = []
    for x in range(12):
        t=calculate_continuous_error(ds.CT[x], ds.data_density[x])
        tt = t=calculate_continuous_error(ds.SA[x], ds.data_density[x])
        unc_CT.append(normalize_climatology_errors(t))
        unc_SA.append(normalize_climatology_errors(tt))
    unc_CT = np.stack(unc_CT, axis=0)
    unc_SA = np.stack(unc_SA, axis=0)
    ds['CT_unc'] = (('month', 'latitude', 'longitude'), unc_CT)
    ds['SA_unc'] = (('month', 'latitude', 'longitude'), unc_SA)
    return ds


def get_unc(ds,depth,gdf):
    gdf= gdf.to_crs("EPSG:4326") #reproject to match
    ds.rio.write_crs("EPSG:4326", inplace=True)
    ds=ds.rio.clip(
        gdf.geometry, 
        gdf.crs, 
        invert=True, 
        drop=True
    )
    lon2d, lat2d = np.meshgrid(ds.longitude, ds.latitude)
    # 3. Get the global land mask boolean array (True if land, False if ocean/sea)
    is_land_2d = globe.is_land(lat2d, lon2d)
    # 4. Wrap the mask into an xarray DataArray with matching coordinates
    land_mask_da = xr.DataArray(is_land_2d, coords={"latitude": ds.latitude, "longitude": ds.longitude})
    # 5. Mask out land values by setting them to NaN (keep values where is_land is False)
    ds= ds.where(~land_mask_da)
    da_reshaped = ds.data_density.transpose(..., "latitude", "longitude")
    #err = calculate_continuous_error(ds.CT_std, da_reshaped) #standard error / 
    ds['CT_unc']=calculate_uncertainty(ds.CT_std, da_reshaped)
    ds['SA_unc']=calculate_uncertainty(ds.SA_std, da_reshaped)
        
    if depth == 'bottom': 
        shp = gpd.read_file(r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/SOURCE_DATA/SHAPEFILES/NES_5REGIONS.shp')
        ds = ds.rio.write_crs("EPSG:4326")
        shp['geometry'] = shp.geometry.buffer(0.4)
        shp.crs = "epsg:4326"
        shp = shp.to_crs(ds.rio.crs)
        ds = ds.rio.clip(shp.geometry.apply(mapping), ds.rio.crs, drop=True)
    return ds 


def add_metadata(ds,depth):
    ds.attrs['cdm_data_type'] = 'Grid'
    ds.attrs['creator_email'] = 'edab.data@noaa.gov'
    ds.attrs['creator_name'] = 'Ecosystem Dynamics and Assesment Branch'
    ds.attrs['create_type'] = 'group'
    ds.attrs['creator_url'] = 'https://www.fisheries.noaa.gov/contact-directory/northeast-ecosystem-dynamics-assessment'
    ds.attrs['publisher_name'] = 'DOC | NOAA | National Marine Fisheries Service | Northeast Fisheries Science Center'
    ds.attrs['publisher_url'] = 'https://www.fisheries.noaa.gov/about/northeast-fisheries-science-center'
    ds.attrs['contact_name'] = 'Haley Synan'
    ds.attrs['contact_email'] = 'haley.synan@noaa.gov'
    ds.attrs['DOI'] = '10.5281/zenodo.20183495'
    ds.attrs['contributor_name'] = 'Kimberly Hyde'
    ds.attrs['contributr_email'] = 'kimberly.hyde@noaa.gov'
    ds.attrs['depth'] = depth
    ds.attrs['project_url'] = 'https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies'
    ds.attrs['summary'] = 'Interpolated climatologies created using aggregated in situ temperature and salinity datasets.'
    ds.attrs['title'] = f'In situ derived temperature and salinity {depth} climatologies (2000-2024)'
    if depth == 'bottom':
        ds.attrs['history'] = 'In situ datasets from multiple instruments and deployment methods were aggregated and standardized into a bottom (observations within 10 m of the bathymetric bottom) depth bin before employing 3-D Barnes Objective Analysis to create climatologies.'
    elif depth =='surface':
        ds.attrs['history'] = 'In situ Datasets from multiple instruments and deployment methods were aggregated and standardized into a surface (observations above the climatological mixed layer depth) depth bin before employing 3-D Barnes Objective Analysis to create climatologies.'

    ds.attrs['geospatial_lat_max'] = float(ds.latitude.max().values)
    ds.attrs['geospatial_lat_min'] = float(ds.latitude.min().values)
    ds.attrs['geospatial_lat_resolution'] ='.0833°'
    ds.attrs['geospatial_lat_units'] = 'decimal degrees north'
    ds.attrs['geospatial_lon_max'] = float(ds.longitude.max().values)
    ds.attrs['geospatial_lon_min'] = float(ds.longitude.min().values)
    ds.attrs['geospatial_lon_resolution'] ='.0833°'
    ds.attrs['geospatial_lon_units'] = 'decimal degrees east'
    ds.attrs['geospatial_vertical_max'] = 0.0
    ds.attrs['geospatial_vertical_min']=0.0
    ds.attrs['keywords'] = 'hydrographic, climatology, temperature, salinity, in situ'
    ds.attrs['creation_date'] = str(pd.to_datetime(datetime.now()))
    ds.attrs['start_date'] = '2000-01-01'
    ds.attrs['end_date'] = '2024-12-31'
    
    
    ds.CT.attrs['long_name'] = 'Climatological conservative temperature for the reference years of 2000 through 2024 generated using interpolation of hydrographic point data'
    ds.CT.attrs['depth_bin'] = f'{depth}' 
    ds.CT.attrs['units'] = 'Degrees celsius'
    ds.CT.attrs['ancillary_variables'] = 'CT_std, CT_unc'
    
    ds.CT_std.attrs['long_name'] = 'Standard deviation of the point temperature data per grid cell (pre-interpolation)'
    ds.CT_std.attrs['depth_bin'] = f'{depth}' 
    ds.CT_std.attrs['units'] = 'Degrees celsius'
    ds.CT_std.attrs['ancillary_variables'] = 'CT, CT_unc'
    
    ds.SA.attrs['long_name'] = 'Climatological absolute salinity for the reference years of 2000 through 2024 generated using interpolation of hydrographic point data'
    ds.SA.attrs['depth_bin'] = f'{depth}' 
    ds.SA.attrs['units'] = 'Grams per kilogram'
    ds.SA.attrs['ancillary_variables'] = 'SA_std, SA_unc'
    
    ds.SA_std.attrs['long_name'] = 'Standard deviation of the point salinity data per grid cell (pre-interpolation)'
    ds.SA_std.attrs['depth_bin'] = f'{depth}' 
    ds.SA_std.attrs['units'] = 'Grams per kilogram'
    ds.SA_std.attrs['ancillary_variables'] = 'SA, SA_unc'
    
    ds.num_obs.attrs['long_name'] = 'Number of point observations per grid cell (pre-interpolation)'
    ds.num_obs.attrs['depth_bin'] = f'{depth}' 
    ds.num_obs.attrs['units'] = 'Grams per kilogram'
    ds.num_obs.attrs['ancillary_variables'] = 'SA, CT'
    
    ds.CT_se.attrs['long_name'] = 'Standard error of conservative temperature'
    ds.CT_se.attrs['depth_bin'] = f'{depth}' 
    ds.CT_se.attrs['units'] = 'Degrees celcius'
    ds.CT_se.attrs['ancillary_variables'] = 'CT, CT_unc'
    
    ds.SA_se.attrs['long_name'] = 'Standard error of absolute slainity'
    ds.SA_se.attrs['depth_bin'] = f'{depth}' 
    ds.SA_se.attrs['units'] = 'Grams per kilogram'
    ds.SA_se.attrs['ancillary_variables'] = 'SA, SA_unc'
    
    ds.data_density.attrs['long_name'] = 'Sum of unnormalized weights, which tells you how far a grid cell actually is from in situ data'
    ds.data_density.attrs['depth_bin'] = f'{depth}' 
    ds.data_density.attrs['units'] = ''
    
    ds.CT_unc.attrs['long_name'] = 'Uncertainty in interpolated climatological value per grid cell'
    ds.CT_unc.attrs['depth_bin'] = f'{depth}' 
    ds.CT_unc.attrs['units'] = '0-1'
    ds.CT_unc.attrs['ancillary_variables'] = 'CT, CT_std'
    
    ds.SA_unc.attrs['long_name'] = 'Uncertainty in interpolated climatological value per grid cell'
    ds.SA_unc.attrs['depth_bin'] = f'{depth}' 
    ds.SA_unc.attrs['units'] = '0-1'
    ds.SA_unc.attrs['ancillary_variables'] = 'SA, SA_std'
    
    print('metadata added...')
    return ds