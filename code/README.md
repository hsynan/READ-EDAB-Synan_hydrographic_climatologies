# Code 
## Naming conventions 
* EXEC_**.py: "executable" files. These files will be run via CLI
* FUNC_**.py: "function" files. These files hold functions that are used in processing and are read in the EXEC files 
## NOTE:
The files are set up to run with locally downloaded files and thus, the directories in the scripts need to be updated when running. Directories are only set once, and subfolders are referenced thereafter, so directory structure must also match.
Inside the project folder there should be 2 subfolders: ```SOURCE_DATA``` and ```PROCESSED_DATA```. Within ```SOURCE_DATA``` there should be subfolders for each data source and one called ```SHAPEFILES``` (which should have [these shapefiles](https://github.com/hsynan/READ-EDAB-Synan_hydrographic_climatologies/tree/main/data/shapefiles) in it). In ```PROCESSED_DATA``` folder, there should be subfolders for ```POINT_MEAN_ABOVEMLD```,  ```POINT_MEAN_BOTTOM```, and ```FINAL```.
## Example CLI 
* hydro_cliams_exec_processraw.py <br>
Example for processing EcoMon data: <br>
```python hydro_climas_exec_process_raw.py ecomon C:\Users\username\Documents\base_dir```
*  hydro_climas_exec_process_raw_bottom.py <br>
```python  hydro_climas_exec_process_raw_bottom.py ecomon C:\Users\username\Documents\base_dir```
* hydro_climas_exec_interp3D.py <br>
```python hydro_climas_exec_interp3D.py surface C:\Users\username\Documents\base_dir```
