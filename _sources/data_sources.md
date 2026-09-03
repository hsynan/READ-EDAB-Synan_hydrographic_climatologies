# Data sources
In the data paper, we are standardizing and aggregating data from multiple sources. The data sources used in creating the interpolated dataset are described below.

## Argo
**Location:** ERDDAP <br>
**Link:** https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats.html <br>
**Filetype:** CSV <br>
**Profile type:** Vertical <br>
**DOI:** 10.17882/42182 <br>
**Citation:** <br>
&emsp;Argo. (2025). Argo float measurements [Data set]. Ifremer ERDDAP. Retrieved August 20, 2025, from https://erddap.ifremer.fr/erddap/tabledap/ArgoFloats.csv?fileNumber%2Cdata_type%2Cformat_version%2Chandbook_version%2Creference_date_time%2Cdate_creation%2Cdate_update%2Cplatform_number%2Cproject_name%2Cpi_name%2Ccycle_number%2Cdirection%2Cdata_center%2Cdc_reference%2Cdata_state_indicator%2Cdata_mode%2Cplatform_type%2Cfloat_serial_no%2Cfirmware_version%2Cwmo_inst_type%2Ctime%2Ctime_qc%2Ctime_location%2Clatitude%2Clongitude%2Cposition_qc%2Cpositioning_system%2Cprofile_pres_qc%2Cprofile_temp_qc%2Cprofile_psal_qc%2Cvertical_sampling_scheme%2Cconfig_mission_number%2Cpres%2Cpres_qc%2Cpres_adjusted%2Cpres_adjusted_qc%2Cpres_adjusted_error%2Ctemp%2Ctemp_qc%2Ctemp_adjusted%2Ctemp_adjusted_qc%2Ctemp_adjusted_error%2Cpsal%2Cpsal_qc%2Cpsal_adjusted%2Cpsal_adjusted_qc%2Cpsal_adjusted_error%2Cdoxy%2Cdoxy_qc%2Ctemp_doxy%2Ctemp_doxy_qc%2Cmolar_doxy%2Cmolar_doxy_qc%2Cturbidity%2Cturbidity_qc%2Cchla%2Cchla_qc%2Cnitrate%2Cnitrate_qc&time%3E=2000-01-01T00%3A00%3A00Z&time%3C=2024-12-31T23%3A23%3A20Z

## BCO-DMO
**Location:** ERDDAP <br>
**Link:**  https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_{id} <br>
**Dataset IDs:**
* 916411_v2
* 731502
* 614744
* 807119
<br>
**Filetype:** CSV <br>
**Profile type:** Vertical <br>
**DOI:**  <br>
**Citation:** <br>
&emsp;BCO-DMO. (2026). [AE1913 CTD data] - CTD profiles from R/V Atlantic Explorer cruise AE1913 in
the Sargasso Sea in June of 2019 (Collaborative Research: Direct
Characterization of Adaptive Nutrient Stress Responses in the Sargasso Sea
using Protein Biomarkers and a Biogeochemical AUV) [Data set]. BCO-DMO ERDDAP. Retrieved May 1, 2026, from https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_916411_v2.csv <br>
&emsp;BCO-DMO. (2026). [Binned CTD data] - Temperature and salinity data from binned CTD data
collected during R/V Hugh R. Sharp cruise HRS1414 in the Mid and South-Atlantic
Bight from July to August of 2014 (DANCE project) (Collaborative Research:
Impacts of atmospheric nitrogen deposition on the biogeochemistry of
oligotrophic coastal waters) [Data set]. BCO-DMO ERDDAP. Retrieved May 1, 2026, from https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_731502.csv <br>
&emsp;BCO-DMO. (2026). [CTD - Downcasts] - CTD profile data from 2014-2015 R/V C-HAWK MuLTI-2 project
cruises in the Gulf of Maine, Coastal eastern Maine, from Frenchman Bay to the
Canadian border (An integrated theoretical and empirical approach to across-
shelf mixing and connectivity of mussel populations) [Data set]. BCO-DMO ERDDAP. Retrieved May 1, 2026, from https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_614744.csv <br>
&emsp;BCO-DMO. (2026). [CTD AR29, RB1904 and TN3638] - CTD casts from the SPIROPA project from R/V
Neil Armstrong cruise AR29, Ronald H. Brown cruise RB1904 and R/V Thomas G.
Thompson cruise TN368 to the New England Shelfbreak in 2018 and
2019 (Collaborative Research: Shelfbreak Frontal Dynamics: Mechanisms of
Upwelling, Net Community Production, and Ecological Implications) [Data set]. BCO-DMO ERDDAP. Retrieved May 1, 2026, from https://erddap.bco-dmo.org/erddap/tabledap/bcodmo_dataset_807119.csv <br>
## CFRF/WHOI Shelf Research Fleet 
**Location:** ERDDAP <br>
**Link:**  https://erddap.ondeckdata.com/erddap/tabledap/shelf_fleet_profiles_full_resolution.html <br>
**Filetype:** CSV <br>
**Profile type:** Vertical <br>
**DOI:**  NA <br>
**Citation:** 
&emsp;Commercial Fisheries Research Foundation | Woods Hole Oceanographic Institute. (2026). Shelf fleet profiles full resolution [Data set]. On Deck Data ERDDAP. Retrieved May 1, 2026, from https://erddap.ondeckdata.com/erddap/tabledap/shelf_fleet_profiles_full_resolution.csv
<br>
## EcoMon
**Location:** ERDDAP <br>
**Link:**  https://comet.nefsc.noaa.gov/erddap/tabledap/ocdbs_v_erddap1.html <br>
**Filetype:** CSV <br>
**Profile type:**  Vertical <br>
**DOI:** NA <br>
**Citation:** <br>
&emsp;NOAA | NMFS | NEFSC. (2025).  Hydrographic | NEFSC | Hydrographic Monitoring Program | Temperature,
salinity, dissolved oxygen, PAR and fluorescence profiles | Northeast U.S.
Shelf | 1977-present  [Data set]. On Deck Data ERDDAP. Retrieved August 20, 2025, from https://comet.nefsc.noaa.gov/erddap/tabledap/ocdbs_v_erddap1.csv
<br>

## Department of Fisheries Oceanography Canada 
**Location:** ERDDAP <br>
**Link:** https://cioosatlantic.ca/erddap/tabledap/ <br>
**Dataset IDs:** <br>
*(V) = vertical profile type, (B) = buoy profile type 
* bio_atlantic_zone_off_shelf_monitoring_program_ctd (V)
* bio_historical_offshore_international_ctd (V)
* nafc_multispecies_ctd_profiles (V)
* new_bb1_hyp_level2_binned (V)
* bio_atlantic_zone_monitoring_program_ctd_6d26_7b70_c538 (V)
* bio_maritimes_region_ecosystem_survey_ctd (V)
* bio_historical_coastal_moored_ctd (B)
* bio_rapid_moored_ctd (B) 
* bio_historical_offshore_moored_ctd (B)
* bio_ocean_tracking_network_moored_ctd (B)
* bio_cetacean_moored_ctd (B)

**Filetype:** CSV <br>
**Profile type:** Vertical and buoy <br>
**DOI:** NA <br>
**Citation:** <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Atlantic Zone Off-Shelf Monitoring Program (AZOMP) Rosette
Vertical Profiles [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_atlantic_zone_off_shelf_monitoring_program_ctd.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Historical offshore and international missions Rosette
Vertical Profiles [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_historical_offshore_international_ctd.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Newfoundland and Labrador Region Multi-Species Survey Trawl-Mounted CTD
Profiles [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/nafc_multispecies_ctd_profiles.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Ecosystem Survey Rosette Vertical Profiles [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_maritimes_region_ecosystem_survey_ctd.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Historical Coastal Moored Time Series Data [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_historical_coastal_moored_ctd.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Historical RAPID Climate Change Program Moored Time Series
Data [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_rapid_moored_ctd.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Historical Offshore Moored Time Series Data [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_historical_offshore_moored_ctd.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Cetacean Monitoring Program MicroCAT conductivity,
temperature and pressure time series data [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_cetacean_moored_ctd.csv <br>
&emsp;Regional Association of the Candadian Integrated Ocean Observing System. (2026). Maritimes Region Historical Ocean Tracking Network (OTN) Project Moored Time
Series Data [Data set]. CIOOS Atlantic ERDDAP. Retrieved May 1, 2026, from https://cioosatlantic.ca/erddap/tabledap/bio_ocean_tracking_network_moored_ctd.csv <br>
<br>

## Fishing Industry Shared Bottom Oceanographic Timeseries (FIShBOT)
**Location:** ERDDAP
**Link:** 
&emsp;Current version: https://erddap.ondeckdata.com/erddap/tabledap/fishbot_realtime.html
&emsp;Archived 20 m bottom version: https://zenodo.org/records/22168636
**Filetype:** CSV <br>
**Profile type:** Varied. Data is aggregated from both fisheries dependent and fisheries independent data. Profile types include vertical profiles, fishing trawls, gliders, and flowthrough data.
**DOI:** https://doi.org/10.5281/zenodo.22168636
**Citation:** 
&emsp;Stoltz L., Maynard, G., Morin, M., Salois, S. (2026). FIShBOT Archive 2026-08-30 (V1) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.22168636
&emsp;Linus Stoltz, George Maynard, Michael Morin, Sarah Salois. 2025. Production
of an in-situ bottom water temperature product for the northeast US
continental shelf using oceanographic data collected by fishing vessels . US
Dept Commer Northeast Fish Sci Cent Tech Memo 341. 20 p

<br>

## Maine Department of Marine Resources 
**Location:** Maine DMR Data Portal <br>
**Link:**  https://mainedmr.shinyapps.io/MaineDMR_Trawl_Survey_Portal/ **Requires an account** <br>
**Filetype:** CSV <br>
**Profile type:** Vertical <br>
**DOI:** NA <br>
**Citation:** 
&emsp;Maine - New Hampshire Inshore Trawl Survey. (2025). Retrieved July 25, 2025, from https://mainedmr.shinyapps.io/MaineDMR_Trawl_Survey_Portal/ <br>
<br>
## NEAMAP
**Location:** By request only <br>
**Link:** https://www.neamap.net/neamap-nearshore-trawl/ <br>
**Filetype:** CSV <br>
**Profile type:** Vertical <br>
**DOI:** NA <br>
**Citation:** <br>
&emsp;Virginia Institute of Marine Science’s Multispecies Research Group. (2024). NEAMAP Nearshore Trawl Survey. Accessed November 26, 2024. 
&emsp;Atlantic States Marine Fisheries Commission (2009) Terms of reference and advisory report for the NEAMAP Nearshore Trawl Survey peer review. Report 09-01 of the Atlantic States Marine Fisheries Commission. Alexandria, VA
&emsp;Gartland, J., Gaichas, S.K. and Latour, R.J., 2023. Spatiotemporal patterns in the ecological community of the nearshore Mid-Atlantic Bight. Marine Ecology Progress Series, 704, pp.15-33.

<br>

## NERACOOS
**Location:** ERDDAP <br>
**Link:** https://data.neracoos.org/erddap/tabledap/ <br>
**Dataset IDs:**
* A01_ocean_001m
* B01_ocean_001m
* E01_ocean_001m
* F01_ocean_001m
* I01_ocean_001m
* M01_ocean_001m
* N01_ocean_001m

**Filetype:** CSV <br>
**Profile type:** Buoy <br>
**DOI:** 10.25921/69jq-7135 <br>
**Citation:** <br>
&emsp;Shyka, T., & Northeastern Regional Association of Coastal Ocean Observing System (NERACOOS). (2017). Physical and meteorological data collected from non-federal stations assembled by the Northeastern Regional Association of Coastal Ocean Observing Systems (NERACOOS) [Data set]. NOAA National Centers for Environmental Information. https://doi.org/10.25921/69jq-7135 <br>
&emsp;Physical Oceanography Group, School of Marine Sciences, University of Maine. (2026). A01 Ocean - 1 meter [Data set]. NERACOOS ERDDAP. Retrieved May 1, 2026, from https://data.neracoos.org/erddap/tabledap/A01_ocean_001m.csv <br>
&emsp;Physical Oceanography Group, School of Marine Sciences, University of Maine. (2026). B01 Ocean - 1 meter [Data set]. NERACOOS ERDDAP. Retrieved May 1, 2026, from https://data.neracoos.org/erddap/tabledap/B01_ocean_001m.csv <br>
&emsp;Physical Oceanography Group, School of Marine Sciences, University of Maine. (2026). E01 Ocean - 1 meter [Data set]. NERACOOS ERDDAP. Retrieved May 1, 2026, from https://data.neracoos.org/erddap/tabledap/E01_ocean_001m.csv <br>
&emsp;Physical Oceanography Group, School of Marine Sciences, University of Maine. (2026). I01 Ocean - 1 meter [Data set]. NERACOOS ERDDAP. Retrieved May 1, 2026, from https://data.neracoos.org/erddap/tabledap/I01_ocean_001m.csv <br>
&emsp;Physical Oceanography Group, School of Marine Sciences, University of Maine. (2026). M01 Ocean - 1 meter [Data set]. NERACOOS ERDDAP. Retrieved May 1, 2026, from https://data.neracoos.org/erddap/tabledap/M01_ocean_001m.csv <br>
&emsp;Physical Oceanography Group, School of Marine Sciences, University of Maine. (2026). N01 Ocean - 1 meter [Data set]. NERACOOS ERDDAP. Retrieved May 1, 2026, from https://data.neracoos.org/erddap/tabledap/N01_ocean_001m.csv <br>
<br>
## MARACOOS
**Location:** ERDDAP <br>
**Link:** https://gliders.ioos.us/erddap/tabledap/ <br>
**Dataset IDs:**
* maracoos_02-20210503T1937
* maracoos_02-20210716T1814
* maracoos_02-20210820T1546
* maracoos_02-20211020T1322
* maracoos_02-20220420T2011-delayed
* maracoos_02-20230505T1613
* maracoos_02-20240124T1445
* maracoos_02-20240301T1425-delayed
* maracoos_02-20240502T1359-delayed
* maracoos_04-20221021T1433
* maracoos_04-20230221T1724
* maracoos_04-20241203T1457
* maracoos_05-20240619T1716-delayed
* maracoos_05-20240801T1650-delayed
* maracoos_05-20241011T1741-delayed

**Filetype:** CSV <br>
**Profile type:** Vertical <br>
**DOI:**  10.25921/69jq-7135 <br>
**Citation:** <br>
&emsp;Rutgers University. (2026). maracoos_02-20210503T1937 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20210503T1937.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20210716T1814 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20210716T1814.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20210820T1546 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20210820T1546.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20211020T1322 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20211020T1322.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20220420T2011-delayed [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20220420T2011-delayed.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20230505T1613 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20230505T1613.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20240124T1445 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20240124T1445.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20240301T1425-delayed [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20240301T1425-delayed.csv <br>
&emsp;Rutgers University. (2026). maracoos_02-20240502T1359-delayed [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_02-20240502T1359-delayed.csv <br>
&emsp;Rutgers University. (2026). maracoos_04-20221021T1433 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_04-20221021T1433.csv <br>
&emsp;Rutgers University. (2026). maracoos_04-20230221T1724 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_04-20230221T1724.csv <br>
&emsp;Rutgers University. (2026). maracoos_04-20241203T1457 [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_04-20241203T1457.csv <br>
&emsp;Rutgers University. (2026). maracoos_05-20240619T1716-delayed [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_05-20240619T1716-delayed.csv <br>
&emsp;Rutgers University. (2026). maracoos_05-20240801T1650-delayed [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_05-20240801T1650-delayed.csv <br>
&emsp;Rutgers University. (2026). maracoos_05-20241011T1741-delayed [Data set]. IOOS Gliders ERDDAP. Retrieved May 1, 2026, from https://gliders.ioos.us/erddap/tabledap/maracoos_05-20241011T1741-delayed.csv <br>
<br>
## WOD
**Location:** WOD Select and Search <br>
**Link:** https://www.ncei.noaa.gov/access/world-ocean-database-select/dbsearch.html <br>
**Filetype:** NC <br>
**Data request SOP:**
* Choose search criteria:  
  * Geographic Coordinates
  * Observation Dates - e.g., Year(s), Month(s), Day(s)
  * Dataset - e.g., OSD, CTD, XBT
* Select “Build a query”
* Geographic Coordinates: 
  * Northern edge: 46.362305
  * Southern edge: 34.40918
  * Eastern edge: -63.585942
  * Western edge:-77.681645
* Dates:
  * 01/01/2000 - 2024/12/31
* Datasets:
  * CTD
  * DRB
  * OSD
  * PFL
  * MRB
  * APB
  * UOR
  * GLD 
* Select “get inventory”
* Select “download data”
* Choose format:
  * netCDF format
  * single cast
* Choose level depth
  * Observed level depth (default)
* Choose flag types
  * WOD flags (default)
* Extract data 

**Profile type:** Vertical and buoy <br>
**DOI:** 10.25923/z885-h264 <br>
**Citation:** <br>
&emsp;Mishonov A.V., T. P. Boyer, O. K. Baranova, C. N. Bouchard, S. Cross, H. E. Garcia, R.  A. Locarnini, C. R. Paver, J. R. Reagan, Z. Wang, D. Seidov, A. I. Grodsky, J. G. Beauchamp, (2024): World Ocean Database 2023. C. Bouchard, Technical Ed., NOAA Atlas NESDIS 97, 206 pp., doi.org/10.25923/z885-h264,
## Pioneer Array
**Location:** ERDDAP <br>
**Link:** https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ <br>
**Dataset IDs:**
* ooi-cp10cnsm-rid27-03-ctdbpc000
* ooi-cp10cnsm-mfd37-03-ctdbpc000
* ooi-cp13eapm-sbi01-02-ctdmos011
* ooi-cp14nepm-sbi01-02-ctdmos011
* ooi-cp13nopm-sbi01-02-ctdmos011
* ooi-cp11nosm-rid27-03-ctdbpc000
* ooi-cp11nosm-mfd37-03-ctdbpd000
* ooi-cp14sepm-sbi01-02-ctdmos011
* ooi-cp13sopm-sbi01-02-ctdmos011
* ooi-cp11sosm-rid27-03-ctdbpc000
* ooi-cp11sosm-mfd37-03-ctdbpd000
* ooi-cp01cnsm-rid27-03-ctdbpc000
* ooi-cp01cnsm-mfd37-03-ctdbpd000
* ooi-cp03issm-rid27-03-ctdbpc000
* ooi-cp03issm-mfd37-03-ctdbpd000
* ooi-cp04ossm-rid27-03-ctdbpc000
**Filetype:** CSV <br>
**Profile type:** Buoy <br>
**DOI:** 10.5159/OCCI-PIONEER-ARRAY <br>
**Citation:** <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Central Surface Mooring: Near Surface Instrument Frame:
CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp10cnsm-rid27-03-ctdbpc000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Central Surface Mooring: Seafloor Multi-Function
Node (MFN): CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp10cnsm-mfd37-03-ctdbpc000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Eastern Profiler Mooring: Surface Buoy: CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp13eapm-sbi01-02-ctdmos011.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Coastal Pioneer MAB: Northeastern Profiler Mooring: Surface Buoy: CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp14nepm-sbi01-02-ctdmos011.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Northern Profiler Mooring: Surface Buoy: CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp13nopm-sbi01-02-ctdmos011.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Northern Surface Mooring: Near Surface Instrument Frame:
CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp11nosm-rid27-03-ctdbpc000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Northern Surface Mooring: Seafloor Multi-Function
Node (MFN): CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp11nosm-mfd37-03-ctdbpd000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Southeastern Profiler Mooring: Surface Buoy: CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp14sepm-sbi01-02-ctdmos011.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Southern Profiler Mooring: Surface Buoy: CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp13sopm-sbi01-02-ctdmos011.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Southern Surface Mooring: Near Surface Instrument Frame:
CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp11sosm-rid27-03-ctdbpc000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer MAB: Southern Surface Mooring: Seafloor Multi-Function
Node (MFN): CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp11sosm-mfd37-03-ctdbpd000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer NES: Central Surface Mooring: Near Surface Instrument Frame:
CTD  [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp01cnsm-rid27-03-ctdbpc000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer NES: Central Surface Mooring: Seafloor Multi-Function
Node (MFN): CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp01cnsm-mfd37-03-ctdbpd000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer NES: Inshore Surface Mooring: Near Surface Instrument Frame:
CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp03issm-rid27-03-ctdbpc000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer NES: Inshore Surface Mooring: Seafloor Multi-Function
Node (MFN): CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp03issm-mfd37-03-ctdbpd000.csv <br>
&emsp;Ocean Observatories Initiative (OOI). (2026). Coastal Pioneer NES: Offshore Surface Mooring: Near Surface Instrument Frame:
CTD [Data set]. Ocean Observatories Initiative ERDDAP. Retrieved May 1, 2026, from https://erddap.dataexplorer.oceanobservatories.org/erddap/tabledap/ooi-cp04ossm-rid27-03-ctdbpc000.csv <br>

## SeaBASS
**Location:** SeaBASS file search <br>
**Link:** https://seabass.gsfc.nasa.gov/search <br>
**Data request SOP:** <br>
* Dates: 01/01/2000- 2024/12/31
* Geographic Coordinates: 
  * Northern edge: 46.362305
  * Southern edge: 34.40918
  * Eastern edge: -63.585942
  * Western edge:-77.681645
* Products:
  * "Find files containing any of the selected products"
* Grouped products:
  * CTD
**Filetype:** SB <br>
**Profile type:**  <br>
**DOI:** <br>
**Citation:** <br>
&emsp;Werdell, P. J., & Bailey, S. W. (2002). The SeaWiFS Bio-optical Archive and Storage System (SeaBASS): Current architecture and implementation (NASA Tech. Memo. 2002-211617). NASA Goddard Space Flight Center.
&esmp;Werdell, P. J., Bailey, S. W., Fargion, G. S., Pietras, C., Knobelspiesse, K. D., Feldman, G. C., & McClain, C. R. (2003). Unique data repository facilitates ocean color satellite validation. Eos, Transactions American Geophysical Union, 84(38), 377–381. https://doi.org/10.1029/2003EO380001

## Surface Underway Marine Database (SUMD)
**Location:** Surface Underway Marine Database Portal <br>
**Link:** https://www.ncei.noaa.gov/access/surface-underway-marine-database/ <br>
**Data request SOP:** <br>
* Data parameters:
  * Sea Surface Salinity
  * Sea Surface Temperature - measured by remote temperature sensor
* Dates: 01/01/2000- 2024/12/31
* Geographic Coordinates: 
  * Northern edge: 46.362305
  * Southern edge: 34.40918
  * Eastern edge: -63.585942
  * Western edge:-77.681645
**Filetype:** NC <br>
**Profile type:** flowthrough <br>
**DOI:**  <br>
**Citation:** <br>
&emsp;NOAA National Centers for Environmental Information. (2025). Surface Underway Marine Database (SUMD) [Data set]. NOAA. Retrieved July 29 2025, from https://www.ncei.noaa.gov/access/surface-underway-marine-database/

## NEFSC Passive Acoustics Branch (PAB)
The Virginia (VA/CB) sites are in collaboration with the US Navy/HDR and the Stellwagen (SBNMS) sites are in collaboration with the Office of National Marine Sanctuaries (ONMS).  
**Location:** By request <br>
**Link:**  NA <br>
**Filetype:** CSV <br>
**Profile type:** Buoy <br>
**DOI:**  <br>
**Citation:** <br>
&emsp;NEFSC Passive Acoustics Branch. (2026). Passive acoustic bottom-mounted moorings [Data set]. Accessed April 26 2026. 


## How to set up a new data source for processing
If you wish to add a new dataset and process the raw data into spatiotemporal depth bins (surface and bottom), then you can edit the [FUNC_SOURCE_URLS.py](https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies/blob/main/code/FUNC_SOURCES_URLS.py) file. In this file, edit the ```get_source`` function, following the template outlined below. <br>
*NOTE:* If the data is a buoy or flowthrough, then the unique_id can be left as an empty string. If the profile type is vertical, then you need must provide a column(s) header with a unique id that can separate the data into profiles. 

```'new_data':{'name':'new_data','urls':[os.path.join(local_dir,'newdata.csv')],'filetype':'csv','platform':'float','profiletype':'vertical','unique_id':['station_id','cast_num']}```
                

