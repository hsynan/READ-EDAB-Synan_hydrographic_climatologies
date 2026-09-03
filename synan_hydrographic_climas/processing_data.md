
# Data processing 

Data are split into spatiotemporal surface and bottom bins based on data source type, either buoy, vertical, or flowthrough. <br>
**Profile types:**
* Buoy: averaged into 1 hour bins 
* Vertical: split into directional casts. Upcasts are retained (when available) and a unique profile identifier, like a station ID or coordinates, was assigned to split into separate profiles.  
* Flowthrough: data were put onto a regular grid and averaged into hourly spatial bins 

**Depth bins:**
* Surface: averaged observations above climatological mixed layer depth (per profile)
* Bottom: averaged observations 10 meters above bathymetric seafloor 