"""
Created on Mon Jul 28 14:40:17 2025

@author: haley.synan
"""
import os
import pandas as pd
import urllib
from FUNC_INTERP import compare_mtime
from FUNC_INTERP import create_grid
from FUNC_INTERP import barnesn
from FUNC_INTERP import make_nc
import numpy as np
import xarray as xr
from global_land_mask import globe
from scipy.ndimage import binary_dilation
from FUNC_INTERP import match_nearest
from FUNC_INTERP import find_closest_pairs
from FUNC_INTERP import outlier_sum_stats
import geopandas as gpd 
import socket
import argparse
import pickle
import requests 
import io
from datetime import datetime

parser = argparse.ArgumentParser()
parser.add_argument("depth",type=str, help="Options include surface or bottom")
parser.add_argument("file_path",type=str, help="Absolute path to aggregated point data")
args = parser.parse_args()
depth = args.depth
base_dir = args.file_path

df=pd.read_csv(file_path)
#INTERPOLATE
# GROUP DATA BY MONTH 
al = []
for x in range(0,12):
    al.append(df[df.month==x+1])
    
#check to make sure the column names are lat not latitude (which the barnes function requires)
#and there are no NA values
if 'lat' in al[0].columns:
    for x in range(len(al)):
        al[x] = al[x].dropna(subset=['CT', 'lat','lon'])
elif 'latitude' in al[0].columns:
    for x in range(len(al)):
        al[x].rename(columns={'latitude':'lat','longitude':'lon'},inplace=True)
        al[x] = al[x].dropna(subset=['CT', 'lat','lon'])
    
# INTERPOLATION
Xv, gridX, gridY, grid_size =create_grid(grid='equidistant')

#put back into dataframe format
data = pd.DataFrame({'lat': gridX,
        'lon': gridY})
months = ['January','February','March','April','May','June','July','August','September','October','November','December','x']
dd=[]
var = ['CT','SA']#,'rho']
for v in var:
#set up for interpolation 
    vq=[]
    for x in range(len(al)):
        try:
            al[x]=al[x].drop('level_0',axis=1)
        except:
            pass
        
        month = al[x].reset_index()
        if depth == 'bottom': #drop na values from SA for bottom salinity (PAM values that have temp but no sal)
            if v == 'SA':
                month = month[month.source!='pam']
                month = month.dropna(subset='SA')
            print('Empty salinity values from PAM dropped')
        V = month[v]
        X = []
        for a, b in zip(month.lat, month.lon):
            X.append( [ a, b ] )
        X = np.asarray(X)
        
        Xq = []
        for a, b in zip( gridX, gridY ):
            Xq.append([a, b])
        Xq = np.asarray(Xq)
        
        Vq, params,ve,roi1,roi2,roi3,datden= barnesn(X, V, Xv, Xq, month, gridX, gridY, n_interations=3) #interpolate
        vq.append(Vq.flatten())
        dd.append(datden)
        #ui.append(ui_grid)

    #put into dataframe
    for y in range(len(vq)):
        data[v+months[y]]=vq[y].flatten()
        data['rmse_1'] = [ve[0]]*len(data)
        data['rmse_2'] = [ve[1]]*len(data)
        data['rmse_3'] = [ve[2]]*len(data)
        
data = data.rename(columns={'lat':'latitude','lon':'longitude'})

print('Interpolation complete')
try:
    data.to_csv(os.path.join(os.path.split(file_path)[0],AGGREGATED_POINT_{depth}_2000_2024.csv'))
except: 
    data.to_csv('AGGREGATED_POINT_{depth}_2000_2024.csv')
print('Interpolation data saved as csv!')

ds = make_nc(data,df,depth=depth)
ds['CT_se'] = ds.CT_std/np.sqrt(ds.num_obs)
ds['SA_se'] = ds.SA_std/np.sqrt(ds.num_obs)
data_density =xr.DataArray(np.stack(dd[:12]), coords = {"longitude":data.longitude.unique(),'latitude':data.latitude.unique()}, dims=["month","longitude","latitude"],name='data_density')
ds['data_density'] = data_density
gdf = gpd.read_file(r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/SOURCE_DATA/SHAPEFILES/Atlantic_estuary_shore_dist/Atlantic_estuary_shore_dist.shp')
gdf= gdf.to_crs("EPSG:4326") #reproject to match

#remove data from estuaries 
ds.rio.write_crs("EPSG:4326", inplace=True)
ds = ds.rio.clip(
    gdf.geometry, 
    gdf.crs, 
    invert=True, 
    drop=True
)

#calculate uncertainty 
da_reshaped = ds.data_density.transpose(..., "latitude", "longitude")
err = calculate_continuous_error(ds.CT_std, da_reshaped) #standard error / 
err = normalize_climatology_errors(err)
ds['CT_unc'] = (('month', 'latitude', 'longitude'), err)
err = calculate_continuous_error(ds.SA_std, da_reshaped) #standard error / 
err = normalize_climatology_errors(err)
ds['SA_unc'] = (('month', 'latitude', 'longitude'), err)

if depth == 'bottom': 
    shp = gpd.read_file('https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies/raw/refs/heads/main/data/shapefiles/NES_5REGIONS.zip')
    shp['geometry'] = shp.geometry.buffer(0.4)
    shp.crs = "epsg:4326"
    shp = shp.to_crs(ds.rio.crs)
    ds = ds.rio.clip(shp.geometry.apply(mapping), ds.rio.crs, drop=True)
        

url='https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies/raw/refs/heads/main/data/grid/GRID_4km_sinusoidal.nc'
response= requests.get(url)
grid = xr.open_dataset(io.BytesIO(response.content))
ds = ds.regrid.linear(grid)
ds=ds.sel(latitude=slice(46,34), longitude=slice(-77,-62))
print('Successfully regridded...')

#add metadata
ds.attrs['cdm_data_type'] = 'Grid'
ds.attrs['creator_email'] = 'edab.data@noaa.gov'
ds.attrs['creator_name'] = 'Ecosystem Dynamics and Assesment Branch'
ds.attrs['creator_url'] = 'https://www.fisheries.noaa.gov/contact-directory/northeast-ecosystem-dynamics-assessment'
ds.attrs['geospatial_lat_max'] = float(ds.latitude.max().values)
ds.attrs['geospatial_lat_min'] = float(ds.latitude.min().values)
ds.attrs['geospatial_lat_resolution'] =.04166666666666666666
ds.attrs['geospatial_lat_units'] = 'decimal degrees north'
ds.attrs['geospatial_lon_max'] = float(ds.longitude.max().values)
ds.attrs['geospatial_lon_min'] = float(ds.longitude.min().values)
ds.attrs['geospatial_lon_resolution'] =.04166666666666666666
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
try: 
    ds.to_netcdf(os.path.join(os.path.split(file_path)[0],'hydrographic_climatology_{depth}_2000_2024.nc'))
except:
    ds.to_netcdf('hydrographic_climatology_{depth}_2000_2024.nc')
print('Interpolation and summary stats saved as netcdf!')

        
    
