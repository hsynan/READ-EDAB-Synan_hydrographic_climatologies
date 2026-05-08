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

parser = argparse.ArgumentParser()
parser.add_argument("depth",type=str, help="Options include surface or bottom")
parser.add_argument("base_dir",type=str, help="Base directory with subfolders for data and code")
args = parser.parse_args()
depth = args.depth
base_dir = args.base_dir
if depth =='surface':
    source_dir = os.path.join(base_dir, 'SOURCE_DATA')
    proc_dir = os.path.join(base_dir,'PROCESSED_DATA','POINT_MEAN_ABOVEMLD')
elif depth == 'bottom': 
    source_dir = os.path.join(base_dir, 'SOURCE_DATA')
    proc_dir = os.path.join(base_dir,'PROCESSED_DATA','POINT_MEAN_BOTTOM')
else: 
    print('No depth bin defined')

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
df = df[(df.temperature>0) & (df.CT>0) & (df.SA>0) & (df.salinity>0) & (df.salinity<38)] #clean data
df = df[(df.year >= 2000) & (df.year<=2024)]
###df = pd.read_csv(r'C:\Users\haley.synan\Documents\DATA\above_mld_within_2std.csv')



#REMOVE DUPLICATES
#df = df.drop_duplicates(subset=['latitude','longitude','month','CT','SA']).reset_index()
df = df.drop_duplicates(subset=['latitude','longitude','time','temperature','salinity'])
#df = df[(df.SA<40) & (df.SA>5) & (df.CT>0) & (df.CT<40)] #clean

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
anom=out[out.min_prof_sal<30] #filter anomalies
df_cleaned = df_cleaned.drop(anom.index) #apply to dataset
shp = gpd.read_file(os.path.join(source_dir,'SHAPEFILES','gsmeanpath.shp'))
in_shp = gpd.clip(gdf,shp)
out = df_cleaned[df_cleaned.isin(in_shp)]
anom=out[out.min_prof_sal<30]
df_cleaned = df_cleaned.drop(anom.index) 

if depth =='bottom':
    df_pam = pd.read_csv(os.path.join(proc_dir,'PROCESSED_MEAN_BOTTOM_PAM_PAB_NEFSC_temperature_2018-2024.csv'))
    df_cleaned = pd.concat([df_cleaned,df_pam],join='inner', ignore_index=True) #
    print('PAM added to bottom temps')
    

#SAVE OUT CONCATENATED DATAFRAME (point dataset for DOI)
if os.path.isdir(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD'))==True:
    df_cleaned.to_csv(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD','PROCESSED_MEAN_ABOVEMLD_ALL.csv'))
    print('Concatenated point file saved successfully!')
else: 
    os.mkdir(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD'))
    df_cleaned.to_csv(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD','PROCESSED_MEAN_ABOVEMLD_ALL.csv'))
    print('Concatenated point file saved successfully!')
    
#READ THIS to read in already concatenated data
#df = pd.read_csv(os.path.join(proc_dir,'ALL_POINT_MEAN_ABOVEMLD','PROCESSED_MEAN_ABOVEMLD_ALL_nooutliers_medianfilt_clean.csv'))   
#df=df[df.source!='sumd'] #REMOVE SUMD UNTIL DATES ARE FIXED

# ADD MEDIAN FILT FOR CLEANING????

df=df_cleaned
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
    data.to_csv(os.path.join(r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/PROCESSED_DATA','final',f'formatted_equigrid_all_finer{depth}.csv'))
except:
    data.to_csv(os.path.join(r'W:\nadata\PROJECTS\NESCAPES\PROCESSED_DATA','final',f'formatted_equigrid_all_finer{depth}.csv'))
    
print('Interpolation data saved as csv!')

import os


# Define the folder and filename
#folder_name = r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/PROCESSED_DATA/final'
#file_name = 'ui.pkl'

# Ensure the directory exists (optional, but recommended)
#if not os.path.exists(folder_name):
#    os.makedirs(folder_name)

# Construct the full file path using os.path.join
#file_path = os.path.join(folder_name, file_name)

# Save the object to the specified path
#with open(file_path, 'wb') as file:
#    pickle.dump(ui, file)

#print(f"Object saved at: {os.path.abspath(file_path)}")




ds = make_nc(data,df,depth=depth)
#se = ds.CT_std/np.sqrt(ds.num_obs)
#se = (se - se.min()) / (se.max() - se.min())
#ds = make_nc(data,df,depth='bottom')
#ds['ui']=xr.DataArray(data=np.stack(ui[:12]),dims=('month','longitude','latitude'),coords={'month':range(1,13),'latitude':data.latitude.unique(),'longitude':data.longitude.unique()})
se = ds.CT_std/np.sqrt(ds.num_obs)
ds['se'] = ds.CT_std/np.sqrt(ds.num_obs)
data_density =xr.DataArray(np.stack(dd[:12]), coords = {"longitude":data.longitude.unique(),'latitude':data.latitude.unique()}, dims=["month","longitude","latitude"],name='data_density')
ds['data_density_CT'] = data_density
#tot=np.sqrt(se**2 + ds.ui**2)
#ds['u_final'] = (tot - tot.min()) / (tot.max() - tot.min())
try: 
    ds.to_netcdf(os.path.join(r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/PROCESSED_DATA','final',f'formatted_equigrid_all_finer{depth}.nc'))
except:
    ds.to_netcdf(os.path.join(r'W:\nadata\PROJECTS\NESCAPES\PROCESSED_DATA','final',f'formatted_equigrid_all_finer{depth}.nc'))
print('Interpolation and summary stats saved as netcdf!')




# ADD VARIABLES 
print('Adding other input variables...')
#BATHYMETRY 
url=''.join(['https://hfr.marine.rutgers.edu/erddap/griddap/bathymetry_srtm15_v24.nc?z%5B(34):1:(46)%5D%5B(-77):1:(-63)%5D'])
file = os.path.join(proc_dir,'srtm3.nc')
urllib.request.urlretrieve(url,file) #download data
srtm = xr.open_dataset(file)
var ='z'
data = match_nearest(data, srtm, 'z','STRM_bathymetry')
print('Bathymetry added successfully.')

month = ['x','January','February','March','April','May','June','July','August','September','October','November','December']
#match chlorophyll 
xr_chla = xr.open_dataset(r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/PROCESSED_DATA/CLIMATOLOGIES.nc')
xr_chla = xr_chla.rename({"lat": "latitude", "lon": "longitude"})
land_mask=globe.is_land(np.meshgrid(xr_chla.longitude,xr_chla.latitude)[1], np.meshgrid(xr_chla.longitude,xr_chla.latitude)[0])
xr_chla['land_mask']= (('latitude','longitude'),land_mask) #add to dataset
masked = xr_chla.where(xr_chla.land_mask==False, drop=True)
#mask estuaries 

masked = masked.to_dataframe().dropna().reset_index()
months= ['x','January','February','March','April','May','June','July','August','September','October','November','December']
for x in range(1,13):
    chla= xr_chla.sel(month=x)
    data = match_nearest(data, chla, 'chlor_a','chla'+month[x])

    chla = masked[masked.month==x].reset_index()
    data = find_closest_pairs(data,chla,'chlor_a','latitude','longitude',months[x])

#for x in range(1,13):
#    chla = masked[masked.month==x].reset_index()
#    data = find_closest_pairs(data,chla,'chlor_a','latitude','longitude',months[x])
    

print('Chlorophyll added successfully')
data.to_csv(os.path.join(r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/PROCESSED_DATA','final','formatted_equigrid_all_finer.csv'))
print("Formatted dataset saved. Ready to input to model!")


#interpolation, removing estuaries/buffering from coastline
#add variables (bathymetry and chla)
#save out this dataframe as a gridded dataset for DOI
#remove duplicates
#check alignment





#SINCE DATA DENSITY IS DIFFERENT ... on shore and offshore weights????



        
    
