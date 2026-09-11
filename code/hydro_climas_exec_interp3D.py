# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 11:24:37 2026

@author: haley.synan
@category:
    EXECTUABLE
@purpose: 
    Reads in standardized data and creates climatologies via interpolation
History: 
    7/28/25: Created from existing code
"""

import os
import pandas as pd
from NESCAPES_func_interp3D import compare_mtime
from NESCAPES_func_interp3D import create_grid
from NESCAPES_func_interp3D import barnesn
from NESCAPES_func_interp3D import make_nc
import numpy as np
import xarray as xr
from global_land_mask import globe
from scipy.ndimage import binary_dilation
from NESCAPES_func_interp3D import match_nearest
from NESCAPES_func_interp3D import find_closest_pairs
from NESCAPES_func_interp3D import outlier_sum_stats
from NESCAPES_func_interp3D import calculate_continuous_error
from NESCAPES_func_interp3D import normalize_climatology_errors
from NESCAPES_func_interp3D import calculate_uncertainty
from NESCAPES_func_interp3D import get_stats
from NESCAPES_func_interp3D import get_unc
from NESCAPES_func_interp3D import add_metadata
import geopandas as gpd 
import socket
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("depth",type=str, help="Options include surface or bottom")
args = parser.parse_args()
depth = args.depth

loc = socket.gethostname() #'ip-10-171-25-220.ec2.internal'
#this is set up to read from 2 different potential directories. Currently it is set up to read from locally downloaded data, but the data used here is available on Zenodo and can either be downloaded or read directly from zenodo.
#Directory set up:
#PROJECT_DIR/SOURCE_DATA needs to have subfolders for SHAPEFILES, SOURCE_DATA
#PROJECT_DIR/PROCESSED_DATA needs to have subfolders for POINT_MEAN_ABOVEMLD, POINT_MEAN_BOTTOM
if depth == 'surface':
    if loc.__contains__('NECL'):
        source_dir = r'PROJECT_DIR\SOURCE_DATA'
        proc_dir = r'PROJECT_DIR\PROCESSED_DATA\POINT_MEAN_ABOVEMLD'
    else:
        source_dir = r'PROJECT_DIR/SOURCE_DATA'
        proc_dir = r'PROJECT_DIR/PROCESSED_DATA/POINT_MEAN_ABOVEMLD'
elif depth == 'bottom':
    if loc.__contains__('NECL'):
        source_dir = r'PROJECT_DIR\SOURCE_DATA'
        proc_dir = r'PROJECT_DIR\PROCESSED_DATA/POINT_MEAN_BOTTOM'
    else:
        source_dir = r'PROJECT_DIR/SOURCE_DATA'
        proc_dir = r'PROJECT_DIR/PROCESSED_DATA/POINT_MEAN_BOTTOM'
    
    
#compare_mtime(source_dir, proc_dir) #look for new data since last processing
# LOAD ALL PROCESSED DATA AND CONCATENATE ON SIMILAR VARIABLE NAMES 
ls_dir = os.listdir(proc_dir)#get written out files
files=[]
#file=[]
for df in ls_dir:
    files.append(os.path.join(proc_dir, df))
    #file.append(pd.read_csv(os.path.join(proc_dir, df)))
    
file = sorted(files, key=os.path.getmtime)[:-1] #dont use the one that is currently processing
file= [item for item in file if '.csv' in item]

files = []
for df in file:
    files.append(pd.read_csv(df))
df = pd.concat(files,join='inner', ignore_index=True) #concatenate on similar columns
df = df[(df.temperature>0) & (df.CT>0) & (df.salinity<38)] #clean data
df = df[(df.year >= 2000) & (df.year<=2024)]
print(df.columns)
print('data opened')

#REMOVE DUPLICATES
df = df.drop_duplicates(subset=['latitude','longitude','time','temperature','salinity'])

#REMOVE OUTLIERS 
#get grid CENTERS 
lat_centers = np.arange(34.5, 46.5, 1)
lon_centers = np.arange(-76.5, -62.5, 1)
lon_grid, lat_grid = np.meshgrid(lon_centers, lat_centers)
is_land = globe.is_land(lat_grid, lon_grid)
# Dilate the land mask to find adjacent water cells
dilated_land = binary_dilation(is_land)
border_mask = dilated_land & ~is_land #border mask = true when borders land
out=[]
for x in range(1,13):
    sub=df[df.month==x]
    sub=outlier_sum_stats(sub,border_mask,var='SA')
    sub=outlier_sum_stats(sub,border_mask, var='CT')
    sub['is_outlier'] = (
            (sub['CT'] > sub['cell_mean_CT'] + sub['threshold'] * sub['cell_std_CT']) | 
            (sub['CT'] < sub['cell_mean_CT'] - sub['threshold'] * sub['cell_std_CT']) |
            (sub['SA'] > sub['cell_mean_SA'] + sub['threshold'] * sub['cell_std_SA']) | 
            (sub['SA'] < sub['cell_mean_SA'] - sub['threshold'] * sub['cell_std_SA'])
        )
    out.append(sub[sub['is_outlier']])
print(f'{len(pd.concat(out))} profiles removed during outlier detection')
df_cleaned=df.drop(pd.concat(out).index)   

#manually remove salinity anomalies from offshelf region
#open shapefile for sargasso
shp = gpd.read_file(os.path.join(source_dir,'SHAPEFILES','gssw_edgestudyarea.shp'))
gdf = gpd.GeoDataFrame(
    df_cleaned, geometry=gpd.points_from_xy(df_cleaned.longitude, df_cleaned.latitude), crs="EPSG:4326")
#clip
in_shp = gpd.clip(gdf,shp)
#get values in shapefile
out = df_cleaned[df_cleaned.isin(in_shp)] 
anom=out[out.sal_min<32] #filter anomalies
df_cleaned = df_cleaned.drop(anom.index) #apply to dataset
shp = gpd.read_file(os.path.join(source_dir,'SHAPEFILES','gsmeanpath.shp'))
in_shp = gpd.clip(gdf,shp)
out = df_cleaned[df_cleaned.isin(in_shp)]
anom=out[out.sal_min<32]
df_cleaned = df_cleaned.drop(anom.index) 

if depth =='bottom':
    df_pam = pd.read_csv(os.path.join(proc_dir,'PROCESSED_MEAN_BOTTOM_PAM_PAB_NEFSC_temperature_2018-2024.csv'))
    df_fishbot = pd.read_csv(os.path.join(proc_dir,'PROCESSED_MEAN_BOTTOM_FISHBOT_fishbot_083126_OG20m_filtered.csv'))
    df_cleaned = pd.concat([df_cleaned,df_pam,df_fishbot],join='inner', ignore_index=True) #
    df_cleaned= df_cleaned[df_cleaned.source!='cfrf'] #drop cfrf (duplication with fishbot)
    df_cleaned = df_cleaned[df_cleaned.source!='ecomon'] #drop ecomon (duplication with fishbot)
    print('PAM and fishbot added to bottom temps')
    print('CFRF and ecomon dropped from bottom due to duplication with Fishbot')
    

#SAVE OUT CONCATENATED DATAFRAME (point dataset for DOI)
if os.path.isdir(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD'))==True:
    df_cleaned.to_csv(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_{depth}_2000_2024.csv'))
    print('Concatenated point file saved successfully!')
else: 
    os.mkdir(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD'))
    df_cleaned.to_csv(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_{depth}_2000_2024.csv'))
    print('Concatenated point file saved successfully!')
    
df=df_cleaned
df['latitude'] = df.latitude.astype(float)
df['longitude'] = df.longitude.astype(float)
df['CT'] = df.CT.astype(float)
df['SA'] = df.SA.astype(float)
df['month'] = df.month.astype(float)
print(df)
#initialize empty dataset
Xv, gridX, gridY, grid_size =create_grid(grid='equidistant')
Xq = np.column_stack((gridX, gridY))
months = np.arange(1,13)

ds = xr.Dataset(
    data_vars=dict(
        CT=(['month','latitude','longitude'], np.nan * np.empty((len(months), len(Xv[0]), len(Xv[1]),))),
        SA=(['month','latitude','longitude'], np.nan * np.empty((len(months), len(Xv[0]), len(Xv[1]),))),
        data_density = (['month','latitude','longitude'], np.nan * np.empty((len(months), len(Xv[0]), len(Xv[1]),)))
    ),
    coords=dict(
        latitude=Xv[0],
        longitude=Xv[1],
        month=months
    )
)

varz = ['CT','SA']
rms=[]
for var in varz:
    V = df[var]
    T = df.month.values
    X = df[['latitude','longitude']]
    if depth == 'bottom': #drop na values from SA for bottom salinity (PAM values that have temp but no sal)
        if var == 'SA':
            df = df[df.source!='pam']
            df = df[df.salinity>10] #make sure that erroneous salinity values (with fill value 2.2222) are filtered out 
            df = df.dropna(subset='SA')
            V = df[var]
            T = df.month.values
            X = df[['latitude','longitude']]
            print('Empty salinity values from PAM and fishbot dropped')
    for x in range(1,13):
        target_month = x 
        # Execute the updated barnesn function
        datden = [] 
        Vq, params, rmse, roi1, roi2, roi3, dd, rmse_final = barnesn(
            X=X, 
            V=V, 
            T=T, 
            target_month=target_month, 
            Xv=Xv, 
            Xq=Xq, 
            data=df,         # Pass the full dataframe so calc_Verror can filter by df.month
            gridX=gridX, 
            gridY=gridY, 
            n_interations=3, 
            convergenceparam=0.3, 
            gaussianvariance=.6,#float('nan'), # Let it auto-calculate spatial variance
            temporal_variance=1.0          # L_t^2: penalize distant months moderately
        )
        print(f'Interpolation completed for month {x} for {V}')
        ds[f'{var}'][x-1] = Vq.T
        ds['data_density'][x-1] = dd.T
        rms.append(rmse_final)
        try: 
            pd.DataFrame(rms).to_csv(os.path.join(proc_dir,'final',f'RMSE_{var}_{depth}.csv'))
        except:
            pd.DataFrame(rms).to_csv(os.path.join(proc_dir,'final',f'RMSE_{var}_{depth}.csv'))
        print('Monthly data added to netcdf properly..')
        
ds = get_stats(df,ds) #add std and numobs
ds['CT_se'] = ds.CT_std/np.sqrt(ds.num_obs)
ds['SA_se'] = ds.SA_std/np.sqrt(ds.num_obs)

try: 
    ds.to_netcdf(os.path.join(proc_dir,'final',f'hydrographic_climatology_3D_{depth}_2000_2024_testnans.nc'))
except:
    ds.to_netcdf(os.path.join(proc_dir,'final',f'hydrographic_climatology_3D_{depth}_2000_2024_testnans.nc'))
print('Interpolation as netcdf!')

#remove estuaries
#gdf = gpd.read_file(os.path.join(source_dir,'SHAPEFILES','Atlantic_estuary_shore_dist','Atlantic_estuary_shore_dist.shp'))
#gdf= gdf.to_crs("EPSG:4326") #reproject to match

#remove data from estuaries 
#ds.rio.write_crs("EPSG:4326", inplace=True)
#ds = ds.rio.clip(
#    gdf.geometry, 
#    gdf.crs, 
#    invert=True, 
#    drop=True
#)
gdf = gpd.read_file(os.path.join(source_dir,'SHAPEFILES','Atlantic_estuary_shore_dist','Atlantic_estuary_shore_dist.shp'))
ds = get_unc(ds,depth,gdf) #add uncertainty metric
ds = add_metadata(ds,depth)

try: 
    ds.to_netcdf(os.path.join(proc_dir,'final',f'hydrographic_climatology_3D_{depth}_2000_2024_testnans1.nc'))
except:
    ds.to_netcdf(os.path.join(proc_dir,'final',f'hydrographic_climatology_3D_{depth}_2000_2024_testnans1.nc'))
print('Interpolation and summary stats saved as netcdf!')