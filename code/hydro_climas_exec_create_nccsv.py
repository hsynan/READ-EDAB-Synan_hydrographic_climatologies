# -*- coding: utf-8 -*-
"""
Created on Mon Jul 27 11:24:37 2026

@author: haley.synan
"""

import os
import pandas as pd
#from NESCAPES_func_interp3D import compare_mtime
from NESCAPES_func_interp3D import create_grid
from NESCAPES_func_interp3D import barnesn
#from NESCAPES_func_interp3D import make_nc
import numpy as np
import xarray as xr
from global_land_mask import globe
from scipy.ndimage import binary_dilation
#from NESCAPES_func_interp3D import match_nearest
#from NESCAPES_func_interp3D import find_closest_pairs
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
if depth == 'surface':
    if loc.__contains__('NECL'):
        source_dir = r'W:\nadata\PROJECTS\NESCAPES\SOURCE_DATA'
        proc_dir = r'W:\nadata\PROJECTS\NESCAPES\PROCESSED_DATA\POINT_MEAN_ABOVEMLD'
    else:
        source_dir = r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/SOURCE_DATA'
        proc_dir = r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/PROCESSED_DATA/POINT_MEAN_ABOVEMLD'
elif depth == 'bottom':
    if loc.__contains__('NECL'):
        source_dir = r'W:\nadata\PROJECTS\NESCAPES\SOURCE_DATA'
        proc_dir = r'W:\nadata\PROJECTS\NESCAPES\PROCESSED_DATA\POINT_MEAN_BOTTOM'
    else:
        source_dir = r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/SOURCE_DATA'
        proc_dir = r'/mnt/EDAB_Archive/nadata/PROJECTS/NESCAPES/PROCESSED_DATA/POINT_MEAN_BOTTOM'

if depth =='bottom':
    df = pd.read_csv(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_{depth}_2000_2024.csv'))
elif depth == 'surface':
    df = pd.read_csv(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_{depth}_2000_2024.csv'))

if depth == 'bottom':
    df['salinity'] = df['salinity'].fillna(-99999)
    df['SA'] = df['SA'].fillna(-99999)
    df.loc[df['salinity'].round(4) == 2.2222, 'SA'] = -99999 #change fill value
    df.loc[df['salinity'].round(4) == 2.2222, 'salinity'] = -99999 #change fill value
    df.loc[df['salinity'] == -99999, 'sal_min'] = -99999 #change fill value
    df.loc[df['salinity'] == -99999, 'sal_max'] = -99999 #change fill value
    df.to_csv(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_data_{depth}_2000_2024.csv'))

    metadata = [
        '*GLOBAL*,project_name,"Surface and Bottom Aggregated In Situ Temperature and Salinity Datasets for the Northwest Atlantic Ocean for 2000-2024"\n',
        '*GLOBAL*,cdm_data_type,"float"\n',
        '*GLOBAL*,institution,"Northeast Fisheries Science Center"\n',
        '*GLOBAL*,creator_name,"Ecosystem Dynamics and Assessment Branch"\n',
        '*GLOBAL*,creator_email,"edab.data@noaa.gov"\n',
        '*GLOBAL*,creator_url,"https://www.fisheries.noaa.gov/contact-directory/northeast-ecosystem-dynamics-assessment"\n',
        '*GLOBAL*,creator_type,"Group"\n',
        '*GLOBAL*,publisher_name,"DOC | NOAA | National Marine Fisheries Service | Northeast Fisheries Science Center"\n',
        '*GLOBAL*,publisher_url,"https://www.fisheries.noaa.gov/about/northeast-fisheries-science-center"\n',
        '*GLOBAL*,DOI,"10.5281/zenodo.22696811"\n',
        '*GLOBAL*,contact_name,"Haley Synan"\n',
        '*GLOBAL*,contact_email,"haley.synan@noaa.gov"\n',
        '*GLOBAL*,contributor_name,"Kimberly Hyde"\n',
        '*GLOBAL*,contributor_email,"kimberly.hyde@noaa.gov"\n',
        '*GLOBAL*,depth,"Bottom"\n',
        '*GLOBAL*,project_url,"https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies"\n',
        '*GLOBAL*,summary,"Aggregated and standardized in situ temperature and salinity datasets for the Northwest Atlantic 2000-2024"\n',
        '*GLOBAL*,history,"Data from multiple sources were split into spatiotemporal surface and bottom bins, collected from differing observation methods, including buoy, flowthrough, and vertical profiles. Buoy data were separated into 1-hour temporal bins to create a quasi-profile. For data collected from a flowthrough system at a fixed intake depth (i.e., TSG), quasi-profiles were created through spatial binning. Vertical profiles were split into up and downcasts. Profiles were matched to a climatological mixed layer depth. Observations above the mixed layer depth were averaged to create a surface mean per profile."\n',
        'profile_uid,units,NaN\n',
        'profile_uid,long_name,Unique profile ID\n',
        'profile_uid,fill_value,nan\n',
        'dataset_id,units,NaN\n',
        'dataset_id,long_name,Unique Dataset ID from raw data\n',
        'dataset_id,fill_value,nan\n',
        'source,units,NaN\n',
        'source,long_name, Source for original data\n',
        'source,fill_value,nan\n',
        'mlotst,units,NaN\n',
        'mlotst,long_name,Climatological mixed layer depth from GLORYS12V1\n',
        'mlotst,fill_value,nan\n',
        'station_id,units,NaN\n',
        'station_id,long_name,Unique station ID from raw data',
        'station_id,fill_value,nan\n',
        'temperature,units,degree_C\n',
        'temperature,long_name,temperature\n',
        'temperature,fill_value,nan\n',
        'salinity,units,PSU\n',
        'salinity,long_name,Salinity\n',
        'salinity,fill_value,-99999\n',
        'CT,units,degree_C\n',
        'CT,long_name,Conservative temperature\n',
        'CT,fill_value,nan\n',
        'SA,units,g/kg\n',
        'SA,long_name,Absolute salinity\n',
        'SA,fill_value,-99999\n',
        'temp_min,units,degrees_C\n',
        'temp_min,long_name,Minimum temperature of observations in depth bin\n',
        'temp_min,fill_value,nan\n',
        'temp_max,units,degrees_C\n',
        'temp_max,long_name,Maximum temperature of observations in depth bin\n',
        'temp_max,fill_value,nan\n',
        'sal_min,units,PSU\n',
        'sal_min,long_name,Minimum salinity of observations in depth bin\n',
        'sal_min,fill_value,-99999\n',
        'sal_max,units,PSU\n',
        'sal_max,long_name,Maximum salinity of observations in depth bin\n',
        'sal_max,fill_value,-99999\n',
        'num_obs,units,NaN\n',
        'num_obs,long_name,Number of observations in average\n',
        'num_obs,fill_value,nan\n',
        'temp_std,units,NaN\n',
        'temp_std,long_name,Standard deviation of temperature observations in depth bin\n',
        'temp_std,fill_value,nan\n',
        'sal_std,units,NaN\n',
        'sal_std,long_name,Standard deviation of salinity observations in depth bin\n',
        'sal_std,fill_value,nan\n',
        '*END_METADATA*\n'
    ]

    with open(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_data_{depth}_2000_2024.csv'), 'r') as infile:
        csv_data = infile.readlines()
    
    with open(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_data_{depth}_2000_2024.csv'), 'w', encoding='utf-8') as outfile:
        outfile.writelines(metadata)
        outfile.writelines(csv_data)
        print('Concatenated nccsv file saved successfully!')
elif depth == 'surface': 
    df = df.drop(['Unnamed: 0','source.1','profile_uid.1',],axis=1)
    metadata = [
        '*GLOBAL*,project_name,"Surface and Bottom Aggregated In Situ Temperature and Salinity Datasets for the Northwest Atlantic Ocean for 2000-2024"\n',
        '*GLOBAL*,cdm_data_type,"float"\n',
        '*GLOBAL*,institution,"Northeast Fisheries Science Center"\n',
        '*GLOBAL*,creator_name,"Ecosystem Dynamics and Assessment Branch"\n',
        '*GLOBAL*,creator_email,"edab.data@noaa.gov"\n',
        '*GLOBAL*,creator_url,"https://www.fisheries.noaa.gov/contact-directory/northeast-ecosystem-dynamics-assessment"\n',
        '*GLOBAL*,creator_type,"Group"\n',
        '*GLOBAL*,publisher_name,"DOC | NOAA | National Marine Fisheries Service | Northeast Fisheries Science Center"\n',
        '*GLOBAL*,publisher_url,"https://www.fisheries.noaa.gov/about/northeast-fisheries-science-center"\n',
        '*GLOBAL*,DOI,"10.5281/zenodo.22696811"\n',
        '*GLOBAL*,contact_name,"Haley Synan"\n',
        '*GLOBAL*,contact_email,"haley.synan@noaa.gov"\n',
        '*GLOBAL*,contributor_name,"Kimberly Hyde"\n',
        '*GLOBAL*,contributor_email,"kimberly.hyde@noaa.gov"\n',
        '*GLOBAL*,depth,"Surfae"\n',
        '*GLOBAL*,project_url,"https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies"\n',
        '*GLOBAL*,summary,"Aggregated and standardized in situ temperature and salinity datasets for the Northwest Atlantic 2000-2024"\n',
        '*GLOBAL*,history,"Data from multiple sources were split into spatiotemporal surface and bottom bins, collected from differing observation methods, including buoy, flowthrough, and vertical profiles. Buoy data were separated into 1-hour temporal bins to create a quasi-profile. For data collected from a flowthrough system at a fixed intake depth (i.e., TSG), quasi-profiles were created through spatial binning. Vertical profiles were split into up and downcasts. Profiles were matched to a climatological mixed layer depth. Observations above the mixed layer depth were averaged to create a surface mean per profile."\n',
        'profile_uid,units,NaN\n',
        'profile_uid,long_name,Unique profile ID\n',
        'profile_uid,fill_value,nan\n',
        'dataset_id,units,NaN\n',
        'dataset_id,long_name,Unique Dataset ID from raw data\n',
        'dataset_id,fill_value,nan\n',
        'source,units,NaN\n',
        'source,long_name, Source for original data\n',
        'source,fill_value,nan\n',
        'mlotst,units,NaN\n',
        'mlotst,long_name,Climatological mixed layer depth from GLORYS12V1\n',
        'mlotst,fill_value,nan\n',
        'station_id,units,NaN\n',
        'station_id,long_name,Unique station ID from raw data',
        'station_id,fill_value,nan\n',
        'temperature,units,degree_C\n',
        'temperature,long_name,temperature\n',
        'temperature,fill_value,nan\n',
        'salinity,units,PSU\n',
        'salinity,long_name,Salinity\n',
        'salinity,fill_value,nan\n',
        'CT,units,degree_C\n',
        'CT,long_name,Conservative temperature\n',
        'CT,fill_value,nan\n',
        'SA,units,g/kg\n',
        'SA,long_name,Absolute salinity\n',
        'SA,fill_value,nan\n',
        'temp_min,units,degrees_C\n',
        'temp_min,long_name,Minimum temperature of observations in depth bin\n',
        'temp_min,fill_value,nan\n',
        'temp_max,units,degrees_C\n',
        'temp_max,long_name,Maximum temperature of observations in depth bin\n',
        'temp_max,fill_value,nan\n',
        'sal_min,units,PSU\n',
        'sal_min,long_name,Minimum salinity of observations in depth bin\n',
        'sal_min,fill_value,nan\n',
        'sal_max,units,PSU\n',
        'sal_max,long_name,Maximum salinity of observations in depth bin\n',
        'sal_max,fill_value,nan\n',
        'num_obs,units,NaN\n',
        'num_obs,long_name,Number of observations in average\n',
        'num_obs,fill_value,nan\n',
        'temp_std,units,NaN\n',
        'temp_std,long_name,Standard deviation of temperature observations in depth bin\n',
        'temp_std,fill_value,nan\n',
        'sal_std,units,NaN\n',
        'sal_std,long_name,Standard deviation of salinity observations in depth bin\n',
        'sal_std,fill_value,nan\n',
        '*END_METADATA*\n'
    ]

    # Read the original CSV data
    with open(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_data_{depth}_2000_2024.csv', 'r') as infile:
        csv_data = infile.readlines()
        
    # Write the metadata and then the data to a new .nccsv file
    with open(os.path.join(proc_dir.rsplit('\\',1)[0],'ALL_POINT_MEAN_ABOVEMLD',f'AGGREGATED_POINT_data_{depth}_2000_2024.csv', 'w', encoding='utf-8') as outfile:
        outfile.writelines(metadata)
        outfile.writelines(csv_data)
