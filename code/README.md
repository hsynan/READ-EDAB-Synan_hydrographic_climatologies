# Code 
## Naming conventions 
* EXEC_**.py: "executable" files. These files will be run via CLI
* FUNC_**.py: "function" files. These files hold functions that are used in processing and are read in the EXEC files 

## Example CLI 
* EXEC_PROCESS_RAW_SURFACE.py <br>
Example for processing EcoMon data: <br>
```python EXEC_PROCESS_RAW_SURFACE.py ecomon C:\Users\username\Documents\base_dir```
* EXEC_PROCESS_RAW_BOTTOM.py <br>
```python EXEC_PROCESS_RAW_BOTTOM.py ecomon C:\Users\username\Documents\base_dir```
* EXEC_INTERP.py <br>
```python EXEC_INTERP.py surface C:\Users\username\Documents\base_dir```
