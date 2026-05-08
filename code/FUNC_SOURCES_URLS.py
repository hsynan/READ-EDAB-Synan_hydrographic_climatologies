# -*- coding: utf-8 -*-
"""
Created on Mon Jul 28 12:54:55 2025

@title: NESCAPES_func_sources_urls
@author: haley.synan
@category:
    FUNCTIONS 
@purpose: 
    Get URL locations for all the source data used in the NEScapes product
History: 
    7/28/25: Created from existing code
"""

import os 
def neracoos_urls(stations  = ['A','B','E','F','I','M','N']):
    urls = []
    for sta in stations: 
        urls.append('https://data.neracoos.org/erddap/tabledap/'+sta+'01_ocean_001m.csv')
    return urls

def maracoos_urls(datasetid= ['maracoos_02-20210503T1937','maracoos_02-20210716T1814','maracoos_02-20210820T1546','maracoos_02-20211020T1322',
            'maracoos_02-20220420T2011-delayed','maracoos_02-20230505T1613','maracoos_02-20240124T1445','maracoos_02-20240301T1425-delayed',
            'maracoos_02-20240502T1359-delayed','maracoos_04-20221021T1433','maracoos_04-20230221T1724','maracoos_04-20241203T1457',
            'maracoos_05-20240619T1716-delayed','maracoos_05-20240801T1650-delayed','maracoos_05-20241011T1741-delayed']):
    urls=[]
    for id in datasetid: 
        urls.append(f'https://gliders.ioos.us/erddap/tabledap/{id}.csv')
    return urls


#cast,CTD_cast, cruiseid and cast
def bcodmo_urls(datasetid= ['916411_v2','731502','614744','807119']):
    urls=[]
    for id in datasetid: 
        urls.append(f'https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_{id}.csv')
    return urls

#'ooi-cp13eapm-wfp01-03-ctdpfk000','ooi-cp14nepm-wfp01-03-ctdpfk000','ooi-cp13nopm-wfp01-03-ctdpfk000',ooi-cp14sepm-wfp01-03-ctdpfk000,'ooi-cp13sopm-wfp01-03-ctdpfk000',
#ooi-cp02pmci-wfp01-03-ctdpfk000','ooi-cp02pmco-wfp01-03-ctdpfk000','ooi-cp01cnpm-wfp01-03-ctdpfk000','ooi-cp01cnsp-sp001-08-ctdpfj000',
#'ooi-cp03ispm-wfp01-03-ctdpfk000','ooi-cp03issp-sp001-08-ctdpfj000','ooi-cp04ospm-wfp01-03-ctdpfk000',
#only vert
def ooi_urls_prof(datasetid=['ooi-cp13eapm-wfp01-03-ctdpfk000','ooi-cp14nepm-wfp01-03-ctdpfk000','ooi-cp13nopm-wfp01-03-ctdpfk000','ooi-cp14sepm-wfp01-03-ctdpfk000','ooi-cp13sopm-wfp01-03-ctdpfk000'
                           ,'ooi-cp02pmci-wfp01-03-ctdpfk000','ooi-cp02pmco-wfp01-03-ctdpfk000','ooi-cp01cnpm-wfp01-03-ctdpfk000','ooi-cp01cnsp-sp001-08-ctdpfj000',
                           'ooi-cp03ispm-wfp01-03-ctdpfk000','ooi-cp03issp-sp001-08-ctdpfj000','ooi-cp04ospm-wfp01-03-ctdpfk000',]):
    urls=[]
    for id in datasetid: 
        urls.append(f'https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/{id}.csv')
    return urls

#only buoys
def ooi_urls(datasetid= ['ooi-cp10cnsm-rid27-03-ctdbpc000','ooi-cp10cnsm-mfd37-03-ctdbpc000','ooi-cp13eapm-sbi01-02-ctdmos011',
                        'ooi-cp14nepm-sbi01-02-ctdmos011','ooi-cp13nopm-sbi01-02-ctdmos011',
                        'ooi-cp11nosm-rid27-03-ctdbpc000','ooi-cp11nosm-mfd37-03-ctdbpd000','ooi-cp14sepm-sbi01-02-ctdmos011',
                        'ooi-cp13sopm-sbi01-02-ctdmos011','ooi-cp11sosm-rid27-03-ctdbpc000','ooi-cp11sosm-mfd37-03-ctdbpd000',
                        'ooi-cp01cnsm-rid27-03-ctdbpc000',
                        'ooi-cp01cnsm-mfd37-03-ctdbpd000','ooi-cp03issm-rid27-03-ctdbpc000',
                        'ooi-cp03issm-mfd37-03-ctdbpd000','ooi-cp04ossm-rid27-03-ctdbpc000',]):
    urls=[]
    for id in datasetid: 
        urls.append(f'https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/{id}.csv')
    return urls


def seabass_files(local_dir):
    file_list = []
    for root, _, files in os.walk(os.path.join(local_dir,'SeaBASS','requested_files')):
        for file in files:
            if file.endswith('.sb'):
                file_list.append(os.path.join(root, file))

    return file_list

def sumd_files(local_dir):
    files=[]
    for file in os.listdir(os.path.join(local_dir,'SUMD')):
        files.append(os.path.join(local_dir,'SUMD',f'{file}'))
    return files

def wod_files(local_dir, data_source):
    files = []
    for file in os.listdir(os.path.join(local_dir,'WOD',data_source)):
        files.append(os.path.join(local_dir,'WOD',data_source,file))
    return files 

def dfo_urls(datasetid= [
        'bio_atlantic_zone_off_shelf_monitoring_program_ctd',
                            'bio_historical_offshore_international_ctd',
                            'nafc_multispecies_ctd_profiles','new_bb1_hyp_level2_binned','bio_atlantic_zone_monitoring_program_ctd_6d26_7b70_c538','bio_maritimes_region_ecosystem_survey_ctd',
                            ]):
    #'nafc_bulk_unsorted_ctd_profiles',
    urls=[]
    for id in datasetid: 
        urls.append(f'https://cioosatlantic.ca/erddap/tabledap/{id}.csv')
    return urls

def dfo_urls_buoys(datasetid= [
                             'bio_historical_coastal_moored_ctd',
        'bio_rapid_moored_ctd','bio_historical_offshore_moored_ctd',
                           'bio_ocean_tracking_network_moored_ctd',
                            'bio_cetacean_moored_ctd',]):
    #'nafc_bulk_unsorted_ctd_profiles',
    urls=[]
    for id in datasetid: 
        urls.append(f'https://cioosatlantic.ca/erddap/tabledap/{id}.csv')
    return urls

def get_source(local_dir=os.path.join('W:','nadata','PROJECTS','NESCAPES','SOURCE_DATA')):
    source = {#'argo':{'name':'argo','urls':['https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats.csv?fileNumber%2Cdata_type%2Cformat_version%2Chandbook_version%2Creference_date_time%2Cdate_creation%2Cdate_update%2Cplatform_number%2Cproject_name%2Cpi_name%2Ccycle_number%2Cdirection%2Cdata_center%2Cdc_reference%2Cdata_state_indicator%2Cdata_mode%2Cplatform_type%2Cfloat_serial_no%2Cfirmware_version%2Cwmo_inst_type%2Ctime%2Ctime_qc%2Ctime_location%2Clatitude%2Clongitude%2Cposition_qc%2Cpositioning_system%2Cprofile_pres_qc%2Cprofile_temp_qc%2Cprofile_psal_qc%2Cvertical_sampling_scheme%2Cconfig_mission_number%2Cpres%2Cpres_qc%2Cpres_adjusted%2Cpres_adjusted_qc%2Cpres_adjusted_error%2Ctemp%2Ctemp_qc%2Ctemp_adjusted%2Ctemp_adjusted_qc%2Ctemp_adjusted_error%2Cpsal%2Cpsal_qc%2Cpsal_adjusted%2Cpsal_adjusted_qc%2Cpsal_adjusted_error%2Cdoxy%2Cdoxy_qc%2Ctemp_doxy%2Ctemp_doxy_qc%2Cmolar_doxy%2Cmolar_doxy_qc%2Cturbidity%2Cturbidity_qc%2Cchla%2Cchla_qc%2Cnitrate%2Cnitrate_qc&time%3E=2000-01-01T00%3A00%3A00Z&time%3C=2024-12-31T23%3A23%3A20Z'],'filetype':'csv',
              #      'platform':'argo_float'},
              'argo':{'name':'argo','urls':[os.path.join(local_dir,'ARGO','ArgoFloats_fb94_d389_bb8e.csv')],'filetype':'csv',
                              'platform':'argo_float','profiletype':'vertical','unique_id':['station_id','cast_num']},
              'bcodmo':{'name':'bcodmo','urls':bcodmo_urls(),'filetype':'csv',
                       'platform':'nan','profiletype':'vertical','unique_id':['station_id']},
              'cfrf':{'name':'cfrf','urls':['https://erddap.ondeckdata.com/erddap/tabledap/shelf_fleet_profiles_full_resolution.csv'],'filetype':'csv',
                     'platform':'RBR ctd','profiletype':'vertical','unique_id':['station_id']},
              #'ecomon': {'name':'ecomon','urls':['https://comet.nefsc.noaa.gov/erddap/tabledap/ocdbs_v_erddap1.csv'],'filetype':'csv',
              #          'platform':'gear_type'}, 
              'dfo':{'name':'dfo','urls':dfo_urls(),
                     'filetype':'csv','platform':'platform_id','profiletype':'vertical', 'unique_id':['station_id', 'cruise_name']},
              'dfo_buoys':{'name':'dfo_buoys','urls':dfo_urls_buoys(),
                     'filetype':'csv','platform':'platform_id','profiletype':'buoy','station_id':['latitude','longitude','mooring_number'] },
              #['station_id','id',"profile_id",'station']
              'ecomon': {'name':'ecomon','urls':[os.path.join(local_dir,'ECOMON','ocdbs_v_erddap1_a9d0_559d_4954.csv')],'filetype':'csv',
                        'platform':'gear_type','profiletype':'vertical','unique_id':['station_id','cast_num']}, 
              'metrawl':{'name':'metrawl','urls':[os.path.join(local_dir,'ME_DMR','MaineDMR_Trawl_Survey_Tow_Data_2025-07-14.csv')],'filetype':'csv',
                        'platform':'nan','profiletype':'vertical','unique_id':['station_id','cast_num']},
              'neamap':{'name':'neamap','urls':[os.path.join(local_dir, 'NEAMAP','NEAMAP_HydroData.csv')],'filetype':'csv',
                        'platform':'nan','profiletype':'vertical','unique_id':['station_id']},
              'neracoos':{'name':'neracoos','urls':neracoos_urls(),'filetype':'csv',
                         'platform':'buoy','profiletype':'buoy'},
              'maracoos':{'name':'maracoos','urls':maracoos_urls(),'filetype':'csv',
                         'platform':'glider','profiletype':'vertical', 'unique_id':['station_id']},
              'wod_apb': {'name':'wod','urls':wod_files(local_dir,'APB'),'filetype':'nc','platform':'','profiletype':''},
              'wod_ctd': {'name':'wod','urls':wod_files(local_dir,'CTD'),'filetype':'nc','platform':'','profiletype':''},
              'wod_drb': {'name':'wod','urls':wod_files(local_dir,'DRB'),'filetype':'nc','platform':'','profiletype':''},
              'wod_gld': {'name':'wod','urls':wod_files(local_dir,'GLD'),'filetype':'nc','platform':'','profiletype':''},
              'wod_mrb': {'name':'wod','urls':wod_files(local_dir,'MRB'),'filetype':'nc','platform':'','profiletype':''},
              'wod_osd': {'name':'wod','urls': wod_files(local_dir,'OSD'),'filetype':'nc','platform':'','profiletype':''},
              'wod_pfl': {'name':'wod','urls': wod_files(local_dir,'PFL'),'filetype':'nc','platform':'','profiletype':''},
              'wod_uor': {'name':'wod','urls': wod_files(local_dir,'UOR'),'filetype':'nc','platform':'','profiletype':''},
              'seabass':{'name':'seabass','urls':seabass_files(local_dir),'filetype':'sb','profiletype':'', 'unique_id':['station_id']},
              'pioneerarray':{'name':'pioneerarray','urls':ooi_urls(),'filetype':'csv','profiletype':'buoy'},
              'pioneerarray_prof':{'name':'pioneerarray_prof','urls':ooi_urls_prof(),'filetype':'csv','profiletype':'vertical','unique_id':[]},
              'sumd':{'name':'sumd','urls':sumd_files(local_dir),'filetype':'nc','profiletype':''},
              'pam':{'name':'pam','urls':[os.path.join(local_dir,'PAM','PAB_NEFSC_temperature_2018-2024.csv')],'filetype':'csv','profiletype':'buoy'}
                }
    return source



