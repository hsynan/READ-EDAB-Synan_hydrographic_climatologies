# -*- coding: utf-8 -*-
"""
Created on Wed Feb 25 08:39:39 2026
@author: haley.synan
"""


from NESCAPES_func_processraw import *
from NESCAPES_func_sources_urls import get_source
import socket
import os 
import argparse

#OUTDATED
#base_dir=os.path.join('W:','nadata','PROJECTS','NESCAPES')
#data_source='sumd'

# command line input of data source
parser = argparse.ArgumentParser()
parser.add_argument("data_source",type=str, help="The name of the data source. Options include: argo, bcodmo,cfrf,dfo,ecomon,metrawl,neamap,neracoos,maracoos,wod_apb,wod_ctd,wod_drb,wod_gld,wod_osd,wod_mrb,wod_uor,wod_pfl,seabass,pioneerarray,sumd")
args = parser.parse_args()
data_source = args.data_source

# autodetect file locations 
loc = socket.gethostname()
if loc=='NECL04740467':
    base_dir=os.path.join('W:','nadata','PROJECTS','NESCAPES')
else: 
    base_dir = os.path.join('/','mnt','EDAB_Archive','nadata','PROJECTS','NESCAPES')

# load trees and source dictionary
source = get_source(local_dir=os.path.join(base_dir,'SOURCE_DATA')) 
glorys_trees, glorys_month_data = load_glorys_trees()


file_dir=os.path.join(base_dir,'PROCESSED_DATA','POINT_MEAN_ABOVEMLD')
#starting pipeline 
print(f'Starting pipeline for {data_source}.....')
if source[data_source]['filetype'] == 'csv':
    for fname in source[data_source]['urls']:
        #LOAD DATA
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        df = pd.read_csv(fname, storage_options=headers)
        #PREPROCESSING
        df = format_headernames(df, data_source) #rename headers to be consistent
        df=df.loc[:, ~df.columns.duplicated()] #drop duplicate columns
        if source[data_source]['name']=='dfo':
            df = df[1:]
        else: 
            if (isinstance(df.latitude.iloc[0], str) & isinstance(df.time.iloc[0], str) & isinstance(df.pressure.iloc[0], str)) == True:
                df =df.drop(0)
        df = check_format(df) #check formatting 
        df = df.dropna(subset=['temperature','salinity'])
        df = subset(df) #spatially subset to study region of NWA 
        if df is None:
            continue
        else:
            dataset_id = re.split(r'[/\\]+', fname)[-1].split('.')[0]
            df['time'] = pd.to_datetime(df.time)
            df['day'] = pd.to_numeric(df.time.dt.day)
            df['year'] = pd.to_numeric(df.time.dt.year)
            df['month'] = pd.to_numeric(df.time.dt.month)
            df['dataset_id'] =dataset_id
            print(df.columns)
            #QA/QC
            if data_source=='argo': #more qa/qc to filter out bad data
                df = df[
                    (df['temp_qc'] == '1') | (df['temp_qc'] == 1) & 
                    (df['psal_qc'] == '1') | (df['psal_qc'] == 1) & 
                    (df['pres_qc'] == '1') | (df['pres_qc'] == 1)
                ]
            elif data_source=='pioneerarray': #more qa/qc filters specific for pioneer array
                qc_cols = df.filter(like='qc', axis=1)
                sal_qc=qc_cols.filter(like='sal',axis=1)
                temp_qc=qc_cols.filter(like='temp',axis=1)
                df = df[
                    (df[temp_qc.filter(like='agg',axis=1).columns[0]] == '1') | (df[temp_qc.filter(like='agg',axis=1).columns[0]] == 1) & 
                    (df[sal_qc.filter(like='agg',axis=1).columns[0]] == '1') | (df[sal_qc.filter(like='agg',axis=1).columns[0]] == 1) 
                ]
            valid_mask = (
                (df['temperature'].between(-2, 35)) & 
                (df['salinity'].between(2, 40)) &
                (df['pressure'] >= 0)
            )
            df = df[valid_mask].copy()
            print(f'{len(df[~valid_mask])} observations flagged out during QA/QC')
            #CONVERSIONS
            df = gsw_conversions(df) #gsw conversions (SA and CT) 
            print('Preprocessing complete... moving on to averaging profiles above the MLD')
            if source[data_source]['profiletype']=='vertical':
                print(f'Processing {data_source} as vertical profiles')
                #MATCH OBS TO MLD, GROUP BY PROFILE, AND AVERAGE 
                #SPLIT INTO up and down cast
                if data_source=='argo': #argo already has a direction column 
                    pass
                else: 
                    df['p_max_so_far'] = df.groupby(source[data_source]['unique_id'])['pressure'].cummax()
                    df['direction'] = np.where(df['pressure'] >= df['p_max_so_far'], 'down', 'up')
                # Create a unique ID for each profile based on the grouping columns AND up/down cast (splits up and down into 2 separate profiles)
                source[data_source]['unique_id'].append('direction')
                if data_source =='pioneerarray_prof': #note that the pioneer array profilers dont have a unique id, they can only be separated by time so they dont have a station_id to create unique profiles
                    df['profile_uid'] = df.groupby([df.time.dt.year,df.time.dt.month,df.time.dt.day,df.time.dt.hour]).ngroups
                else: 
                    df['profile_uid'] = df.groupby(source[data_source]['unique_id']).ngroup()
                # Sort by profile_uid and pressure to ensure calculations are depth-ordered
                df = df.sort_values(['profile_uid', 'pressure']).reset_index(drop=True)
                df = match_mld(df,glorys_month_data,glorys_trees)
                print('MLD matched..')
                print(df.columns)
                proc = avg_mld_vert(df)
                new_fname = 'PROCESSED_MEAN_ABOVEMLD_'+data_source.upper()+'_'+dataset_id+'.csv'
                proc.to_csv(os.path.join(file_dir,new_fname))
                #print(f'Processing for {source[data_source]['name']} complete')
                try:
                    source[data_source]['unique_id'].remove('direction')
                except:
                    pass
            elif source[data_source]['profiletype']=='buoy':
                #Create unique ID 
                df['hour_bin'] = df['time'].dt.floor('1h')
                df['profile_uid'] = (
                    df['station_id'].astype(str) + "_" + 
                    df['hour_bin'].dt.strftime('%Y%m%d_%H')
                )
            
                df = match_mld(df,glorys_month_data,glorys_trees)
                #print(df.columns)
                print('MLD matched')
                #print(df.columns)
                proc = avg_mld_buoy(df)
                new_fname = 'PROCESSED_MEAN_ABOVEMLD_'+data_source.upper()+'_'+dataset_id+'.csv'
                proc.to_csv(os.path.join(file_dir,new_fname))
                #assumes stationary 
                print(f'Processing {data_source} as buoys')
            elif source[data_source]['profiletype']=='drifter':
                print(f'Processing {data_source} as glider/drifter profiles')
            else: 
                print('No profile type defined. Please go into the source dictionary (found in NESCAPES_func_sources_urls.py) to update.')
if source[data_source]['filetype'] == 'nc':
    all_urls = source[data_source]['urls'] #get all urls 
    batches = [all_urls[i:i + 5000] for i in range(0, len(all_urls), 5000)] #define batches 
    for x in range(len(batches)):
        file_list=batches[x]
        batch_dfs = []
        # 1. Load files in the batch
        for fname in file_list:
            with xr.open_dataset(fname) as ds:
                # Standardize all data variable names to lowercase
                ds = ds.rename({var: var.lower() for var in ds.data_vars})
                ds = ds.rename({coord: coord.lower() for coord in ds.coords})
                if 'wod' in data_source:
                    if 'temperature' not in ds.data_vars or 'salinity' not in ds.data_vars:
                        print(f"Skipping {fname}: Missing T or S")
                        continue
                elif data_source=='sumd':
                    if 'sea_surface_temperature' not in ds.data_vars or 'sea_surface_salinity' not in ds.data_vars:
                        print(f"Skipping {fname}: Missing T or S")
                        continue
                if data_source=='sumd':
                    print('good sumd file')
                    dff=ds.to_dataframe().reset_index().drop_duplicates('obs')
                else: 
                    dff = ds.to_dataframe().reset_index()
                # Select only required variables to save memory
                #df = ds[['temperature', 'salinity', 'pressure', 'lat', 'lon', 'time','wod_cruise_identifier','wod_unique_cast']].to_dataframe().reset_index()
                batch_dfs.append(dff)
        df=pd.concat(batch_dfs)
        df = format_headernames(df, data_source) #rename headers to be consistent
        if data_source=='sumd':
            df['pressure'] = 10 #setting standardized 10 m
            df['time']=pd.to_datetime([t.strftime() for t in df.time]) #convert datetime
        else: 
            df['time'] = pd.to_datetime(df.time)
        if (isinstance(df.latitude.iloc[0], str) & isinstance(df.time.iloc[0], str) & isinstance(df.pressure.iloc[0], str)) == True:
            df =df.drop(0)
        df = check_format(df) #check formatting 
        df = df.dropna(subset=['temperature','salinity'])
        df = subset(df) #spatially subset to study region of NWA 
        dataset_id = re.split(r'[/\\]+', fname)[-1].split('.')[0]
        df['dataset_id'] = dataset_id
        df['day'] = pd.to_numeric(df.time.dt.day)
        df['year'] = pd.to_numeric(df.time.dt.year)
        df['month'] = pd.to_numeric(df.time.dt.month)
        if 'wod' in data_source:
            df['dataset_id'] =df.wod_cruise_identifier
            df['profile_uid']=df.wod_unique_cast
        elif data_source=='sumd':
            #create spatial bins
            lat_bins = np.linspace(34.41,46.36,80) #use same grid as interpolation grid
            lon_bins= np.linspace(-77.68,-63.59,94)
            df['lat_bin'] = pd.cut(df['latitude'], bins=lat_bins)
            df['lon_bin'] = pd.cut(df['longitude'], bins=lon_bins)
            df['day'] = pd.to_numeric(df.time.dt.day)
            df['year'] = pd.to_numeric(df.time.dt.year)
            df['month'] = pd.to_numeric(df.time.dt.month)
            df=df.dropna(subset=['lat_bin','lon_bin'])
            df['profile_uid'] = df.groupby(['lat_bin', 'lon_bin','day','month','year']).ngroup()   
        #QA/QC
        valid_mask = (
            (df['temperature'].between(-2, 35)) & 
            (df['salinity'].between(2, 40)) &
            (df['pressure'] >= 0)
        )
        df = df[valid_mask].copy()
        print(f'{len(df[~valid_mask])} observations flagged out during QA/QC')
        if data_source=='sumd':
            df = df.where((df.sea_surface_temperature_qc == 1) & (df.sea_surface_salinity_qc==1)) #SUMD specific qa/qc
        #CONVERSIONS
        df = gsw_conversions(df) #gsw conversions (SA and CT) 
        print('Preprocessing complete... moving on to averaging profiles above the MLD')
        df = match_mld(df,glorys_month_data,glorys_trees)
        proc=avg_mld_vert(df)
        batch_name = f"PROCESSED_MEAN_ABOVEMLD_{data_source}_batch_{x}.csv"
        proc.to_csv(os.path.join(file_dir,batch_name))
        print(f'Processing completed for batch {x} of {len(batches)}')
elif source[data_source]['filetype'] == 'sb':
    for fname in source[data_source]['urls']:
        sb = readSB(filename=fname, mask_missing=False,no_warn=True)
        try: 
            df = pd.DataFrame.from_dict(sb.data)  
            df = format_headernames(df, data_source) #rename headers to be consistent
            print(df.columns)
            if {'temperature','salinity'}.issubset(df.columns)==False:
                print('Missing T or S... Skipping')
            else: 
                df=df.loc[:, ~df.columns.duplicated()] #drop duplicate columns
                if 'year' in df.columns:
                    if 'month' in df.columns:
                        if 'day' in df.columns:
                            if 'hour' in df.columns:
                                if 'minute' in df.columns:
                                    if 'second' in df.columns:
                                        df['time'] = [datetime.strptime(str(df.year[x])+str(df.month[x]).zfill(2)+str(df.day[x]).zfill(2)+str(df.hour[x]).zfill(2)+str(df.minute[x]).zfill(2)+str(df.second[x]).zfill(2),'%Y%m%d%H%M%S') for x in range(len(df))] 
                                    else:
                                        df['time'] = [datetime.strptime(str(df.year[x])+str(df.month[x]).zfill(2)+str(df.day[x]).zfill(2)+str(df.hour[x]).zfill(2)+str(df.minute[x]).zfill(2),'%Y%m%d%H%M') for x in range(len(df))] 
                                        
                if 'date' in df.columns:
                    if 'time' in df.columns:
                        df['time'] = [datetime.strptime(str(df.date[x])+str(df.time[x]),'%Y%m%d%H:%M:%S') for x in range(len(df))]
                if 'time' not in df.columns:
                    print('Skipping.. no time available')
                else: 
                    try:
                        df = check_format(df) #check formatting 
                        datatype='vertical'
                    except AttributeError:
                        print('No pressure detected. Data is flowthrough. Setting default to 10m depth')
                        df['pressure'] = 10
                        datatype='flowthrough'
                    df = df.dropna(subset=['temperature','salinity'])
                    #df = subset(df) #spatially subset to study region of NWA 
                    dataset_id = re.split(r'[/\\]+', fname)[-1].split('.')[0]
                    df['time'] = pd.to_datetime(df.time)
                    df['day'] = pd.to_numeric(df.time.dt.day)
                    df['year'] = pd.to_numeric(df.time.dt.year)
                    df['month'] = pd.to_numeric(df.time.dt.month)
                    df['day'] = pd.to_numeric(df.time.dt.day)
                    df['hour'] =pd.to_numeric(df.time.dt.hour)
                    df['dataset_id'] =dataset_id
                    #QA/QA
                    valid_mask = (
                        (df['temperature'].between(-2, 35)) & 
                        (df['salinity'].between(2, 40)) &
                        (df['pressure'] >= 0)
                    )
                    df = df[valid_mask].copy()
                    print(f'{len(df[~valid_mask])} observations flagged out during QA/QC')
                    #CONVERSIONS
                    if 'direction' in source[data_source]['unique_id']:
                        source[data_source]['unique_id'].remove('direction')
                    df = gsw_conversions(df) #gsw conversions (SA and CT) 
                    if datatype=='flowthrough':
                        #spatially subset
                        lat_bins = np.linspace(34.41,46.36,80) #use same grid as interpolation grid
                        lon_bins= np.linspace(-77.68,-63.59,94)
                        df['lat_bin'] = pd.cut(df['latitude'], bins=lat_bins)
                        df['lon_bin'] = pd.cut(df['longitude'], bins=lon_bins)
                        df=df.dropna(subset=['lat_bin','lon_bin'])
                        df['profile_uid'] = df.groupby(['lat_bin', 'lon_bin','day','month','year','day','hour']).ngroup() 
                    elif datatype=='vertical':
                        #trad profile
                        df['p_max_so_far'] = df.groupby(source[data_source]['unique_id'])['pressure'].cummax()
                        df['direction'] = np.where(df['pressure'] >= df['p_max_so_far'], 'down', 'up')
                        print(df.columns)
                        # Create a unique ID for each profile based on the grouping columns AND up/down cast (splits up and down into 2 separate profiles)
                        source[data_source]['unique_id'].append('direction')
                        df['profile_uid'] = df[['latitude','longitude','date']].groupby(['latitude','longitude','date']).ngroup()
                        #df['profile_uid'] = df.groupby(source[data_source]['unique_id']).ngroup()
                        # Sort by profile_uid and pressure to ensure calculations are depth-ordered
                        df = df.sort_values(['profile_uid', 'pressure']).reset_index(drop=True)
                    if len(df)!=0:
                        df = match_mld(df,glorys_month_data,glorys_trees)
                        proc=avg_mld_vert(df)
                        new_fname = 'PROCESSED_MEAN_ABOVEMLD_'+data_source.upper()+'_'+dataset_id+'.csv'
                        proc.to_csv(os.path.join(file_dir,new_fname))
                    # print(f'Processing for {source[data_source]['name']} complete')
        except ValueError:
            print('unable to convert sb file to dataframe due to issue with length of data... moving on')
            pass
            