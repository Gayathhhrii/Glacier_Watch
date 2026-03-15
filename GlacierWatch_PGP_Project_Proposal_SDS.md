**PROJECT PROPOSAL**

**GlacierWatch: Himalayan Glacier Retreat Detection and Melt
Prediction**

**Group Name:** FrostByte ❄️💻

**Members:** Diljeeth Santhosh, Anurag Borah, Chennu Gayathri

**Project Working Title:** GlacierWatch: Satellite NDSI and Random
Forest Based Glacier Retreat Detection and Melt Probability Prediction
for Uttarakhand Himalayas

**1. Problem Statement**

**What is the Spatial Problem?**

Uttarakhand's Himalayan glaciers --- including Gangotri, Pindari,
Chorabari, and Milam --- are retreating at accelerating rates due to
climate change. Gangotri alone has lost several kilometres of ice over
the past century. The real issue is that no accessible tool currently
exists which allows researchers, planners, or the public to see the
current snow and ice extent of these glaciers, compare it against
historical baselines, or understand where melt pressure is concentrated
right now. Anyone who wants this information today has to manually
download raw satellite files, write their own processing code, and
assemble results from scratch --- which is impractical for disaster
planners, hydrologists, or students who need answers quickly.

GlacierWatch processes free Landsat 8 multispectral satellite imagery
from USGS EarthData to compute the Normalized Difference Snow Index,
written as NDSI = (Band 3 − Band 6) / (Band 3 + Band 6), for any
Uttarakhand glacier bounding box. A Scikit-learn Random Forest
classifier, trained on NDSI values combined with SRTM elevation and
Open-Meteo temperature features, predicts per-pixel melt probability.
The output is an interactive Folium map showing the current ice extent,
the retreat boundary over time, and a melt-probability surface ---
updated whenever new Landsat imagery is available, approximately every
16 days.

**Target User**

-   Wadia Institute of Himalayan Geology researchers monitoring glacier
    mass balance and ice volume changes over time.

-   NDMA and SDMA Uttarakhand disaster planners assessing glacial lake
    outburst flood risk in downstream valleys.

-   Jal Shakti Ministry hydrologists modelling downstream river flow
    that depends on glacial meltwater contribution.

-   Climate scientists and students at HNB Garhwal University who need
    accessible and reproducible glacier analysis tools without writing
    satellite processing code from scratch.

**2. Technical Stack & Libraries**

The table below identifies every library and its specific role in the
pipeline. This project simultaneously satisfies the Image Processing
track (Rasterio + Scikit-image NDSI processing) and the Machine Learning
track (Scikit-learn Random Forest) --- two rubric tracks in one unified
pipeline.

  -----------------------------------------------------------------------
  **Layer**        **Library**         **Purpose**
  ---------------- ------------------- ----------------------------------
  GUI Framework    PyQt6               Main application window, glacier
                                       selector dropdown, NDSI threshold
                                       slider, QWebEngineView map panel,
                                       and Matplotlib histogram sidebar.

  Satellite        Rasterio + NumPy    Read Landsat 8 GeoTIFF Band 3 and
  Imagery                              Band 6 into NumPy arrays. Compute
                                       NDSI = (B3 − B6) / (B3 + B6) per
                                       pixel using vectorised array
                                       operations.

  Image Processing Scikit-image        Morphological thresholding and
                                       closing operations on the binary
                                       snow and ice mask to remove edge
                                       noise and fill small holes caused
                                       by crevasses or shadows.

  Machine Learning Scikit-learn        Train a Random Forest classifier
                   (Random Forest)     on three per-pixel features: NDSI
                                       value, SRTM elevation in metres,
                                       and daily mean temperature. Output
                                       is a melt probability score
                                       between 0 and 1 per pixel.

  Elevation Data   Rasterio + SRTM DEM Load the 30 metre resolution SRTM
                   (NASA)              digital elevation model and
                                       resample it to match the Landsat
                                       pixel grid. Used as the elevation
                                       feature in the Random Forest
                                       model.

  Live Weather     Requests +          Fetch free daily mean temperature
                   Open-Meteo API      and precipitation data for the
                                       glacier bounding box centroid. No
                                       API key required. Used as the
                                       temperature feature in the Random
                                       Forest model.

  Core Geospatial  GeoPandas + Shapely Convert per-pixel binary ice masks
                                       to vector polygons. Compute
                                       polygon difference between two
                                       acquisition dates to produce the
                                       retreat boundary. Calculate
                                       retreat area in square kilometres.

  Visualization    Folium + Matplotlib Generate the interactive
                   (embedded)          Leaflet.js map HTML showing ice
                                       extent in blue-white and melt
                                       probability surface in amber-red
                                       gradient. Matplotlib draws the
                                       NDSI histogram panel in the PyQt6
                                       sidebar.
  -----------------------------------------------------------------------

**The \"Advanced\" Component --- Image Processing Track + ML Track (Both
Simultaneously)**

-   **Image Processing:** Rasterio reads Landsat 8 GeoTIFF bands 3
    (Green, 0.53--0.59 µm) and 6 (SWIR, 1.57--1.65 µm). NumPy computes
    NDSI = (B3 − B6) / (B3 + B6) per pixel. NDSI \> 0.4 indicates
    glacier ice and NDSI \> 0.6 indicates fresh snow. Scikit-image
    morphological operations clean the binary ice mask by filling holes
    and removing noise.

-   **Machine Learning:** A Random Forest classifier (Scikit-learn) is
    trained on three features per pixel: NDSI value, SRTM elevation in
    metres, and Open-Meteo daily mean temperature in degrees Celsius.
    The model predicts a melt probability score between 0 and 1 per
    pixel. Pixels with high NDSI but rising temperature and low
    elevation are flagged as the highest melt risk zones.

-   **Temporal Spatial Analysis:** Multi-date Landsat composites,
    pre-downloaded for at least two dates and bundled in the data
    directory, enable a temporal retreat map showing the ice boundary
    shift between dates as a GeoPandas polygon difference operation. The
    area of ice lost is calculated in square kilometres.

**Data Sources**

-   Landsat 8 Collection 2 Level-2 imagery --- USGS EarthData
    (earthdata.nasa.gov), free, requires one-time account registration.
    Pre-downloaded scene tiles for Gangotri and Pindari are bundled in
    the data directory for offline demonstration.

-   SRTM 1 Arc-Second DEM --- NASA EarthData, free download, bundled in
    the repository as dehradun_region_dem.tif.

-   Open-Meteo Historical and Forecast API --- open-meteo.com,
    completely free, no API key required, returns daily temperature for
    any glacier bounding box centroid coordinate.

-   Glacier boundary polygons --- GLIMS (Global Land Ice Measurements
    from Space) database at glims.org, free GeoJSON download, bundled in
    the data directory.

**3. Proposed GUI Architecture**

**Input Section**

-   Glacier selector dropdown (Gangotri / Pindari / Chorabari / Custom
    bbox) --- pre-loads bundled scene tiles and DEM subset automatically
    on selection, or triggers a live Earthaccess download for new
    scenes.

-   Date range picker --- two calendar inputs letting the user select
    which two Landsat acquisition dates to compare. Controls which scene
    tiles are loaded and defines the temporal period for retreat
    boundary calculation.

-   NDSI threshold slider (default 0.4) --- adjusts the ice and snow
    classification boundary live. Moving the slider immediately updates
    the ice mask visualisation without requiring a full reprocessing
    run.

-   \"Process Imagery\" button --- triggers the full pipeline: NDSI
    computation, morphological cleaning, DEM alignment, temperature
    fetching, Random Forest melt prediction, polygon differencing, and
    Folium map generation.

-   Offline Demo toggle --- forces the application to use only the
    bundled data directory without any network requests, ensuring the
    tool works in environments without internet access during a
    demonstration.

**Processing Section (triggered on button click)**

-   Load selected Landsat Band 3 and Band 6 GeoTIFF tiles via Rasterio →
    NumPy arrays, preserving coordinate reference system and spatial
    transform for all downstream geospatial operations.

-   Compute NDSI per pixel using NumPy vectorised operations. Apply
    Scikit-image morphological closing to the binary ice mask to fill
    crevasse holes and remove edge noise → clean binary ice mask.

-   Load SRTM DEM for the same bounding box via Rasterio → resample to
    Landsat 30 metre resolution using bilinear interpolation for
    pixel-accurate feature alignment.

-   Fetch Open-Meteo daily mean temperature for the glacier centroid
    latitude and longitude across the selected date range via the
    Requests library.

-   Assemble per-pixel feature matrix \[NDSI, elevation, temperature\] →
    run the pre-trained Random Forest predictor → output melt
    probability raster of the same spatial shape as the input bands.

-   Compute polygon difference between the two-date binary ice masks
    using GeoPandas → produce a retreat boundary GeoDataFrame with area
    calculated in square kilometres.

-   Export NDSI raster + melt probability surface + retreat boundary
    polygon → Folium animated map → HTML file loaded into PyQt6
    QWebEngineView for interactive display.

**Output / Visualization**

-   Folium animated choropleth embedded in PyQt6 QWebEngineView --- ice
    extent displayed in blue-white colour gradient, melt probability
    surface overlaid in amber-to-red gradient where red marks highest
    melt risk zones.

-   Retreat boundary overlay --- a distinct vector polygon showing the
    exact ice area lost between the two selected acquisition dates, with
    total area lost in km² shown in the application status bar.

-   Matplotlib NDSI histogram panel embedded in the PyQt6 right sidebar
    --- shows the frequency distribution of pixel NDSI values for the
    selected scene so users can assess the overall glacier condition at
    a glance.

-   Export button --- saves the current melt probability map and retreat
    boundary as a GeoJSON file and a PNG image suitable for use in
    research reports, presentations, or disaster assessment documents.

**4. GitHub Repository Setup**

**Repo URL:** https://github.com/Gayathhhrii/Glacier_Watch/blob/main/GlacierWatch_PGP_Project_Proposal_SDS.md

**Initial Folder Structure**

+-----------------------------------------------------------------------+
| glacierwatch/                                                         |
|                                                                       |
| ├── data/                                                             |
|                                                                       |
| │ ├── gangotri_B3.tif \# Landsat 8 Band 3 for Gangotri                |
|                                                                       |
| │ ├── gangotri_B6.tif \# Landsat 8 Band 6 for Gangotri                |
|                                                                       |
| │ ├── pindari_B3.tif \# Landsat 8 Band 3 for Pindari                  |
|                                                                       |
| │ ├── pindari_B6.tif \# Landsat 8 Band 6 for Pindari                  |
|                                                                       |
| │ ├── dehradun_region_dem.tif \# SRTM elevation model                 |
|                                                                       |
| │ └── glims_boundaries.geojson \# Glacier outline polygons            |
|                                                                       |
| ├── src/                                                              |
|                                                                       |
| │ ├── ndsi_processor.py \# Rasterio + NumPy + Scikit-image pipeline   |
|                                                                       |
| │ ├── melt_predictor.py \# Scikit-learn Random Forest training and    |
| prediction                                                            |
|                                                                       |
| │ ├── main_window.py \# PyQt6 application window and controls         |
|                                                                       |
| │ ├── folium_renderer.py \# Folium map generation and HTML export     |
|                                                                       |
| │ └── data_utils.py \# API calls, DEM loading, Earthaccess            |
| integration                                                           |
|                                                                       |
| ├── models/                                                           |
|                                                                       |
| │ └── rf_melt_model.pkl \# Serialised trained Random Forest model     |
|                                                                       |
| ├── outputs/ \# Generated maps and exports (gitignored)               |
|                                                                       |
| ├── tests/ \# Unit tests for each module                              |
|                                                                       |
| ├── requirements.txt \# All Python dependencies with version pins     |
|                                                                       |
| ├── README.md \# Setup instructions and usage guide                   |
|                                                                       |
| └── .gitignore \# Excludes outputs, pycache, and model cache          |
+-----------------------------------------------------------------------+

**5. Preliminary Task Distribution**

This project is being executed by a group of 3 members. The workload has
been distributed so that each member owns a complete, independently
testable module. Diljeeth Santhosh handles all satellite image
processing and glacier retreat measurement. Anurag Borah handles the
full GUI layer, all API and data utilities, and offline demo
preparation. Chennu Gayathri handles the machine learning pipeline and
all Git and integration responsibilities.

  -----------------------------------------------------------------------
  **Member      **Primary Responsibility**     **Secondary
  Name**                                       Responsibility**
  ------------- ------------------------------ --------------------------
  Diljeeth      ndsi_processor.py --- Rasterio Bundled offline data
  Santhosh      band loading, NumPy NDSI       preparation for the data
                computation, Scikit-image      directory. Unit tests
                morphological cleaning, SRTM   confirming NDSI output
                DEM alignment, GeoPandas       stays within the
                retreat boundary polygon and   physically valid range of
                km² area calculation.          −1 to +1.

  Anurag Borah  main_window.py --- PyQt6       README.md setup and usage
                application layout, glacier    guide. requirements.txt
                selector, date picker, NDSI    with all pinned Python
                slider, QWebEngineView map     dependencies.
                panel, Matplotlib histogram    
                sidebar, export button.        
                data_utils.py --- Open-Meteo   
                API integration, Earthaccess   
                Landsat downloads, offline     
                demo toggle logic.             

  Chennu        melt_predictor.py --- feature  Git lead --- repository
  Gayathri      matrix assembly from NDSI,     setup, branch management,
                elevation, and temperature;    pull request merging,
                Random Forest training,        final end-to-end
                cross-validation, and          integration tests, and
                hyperparameter tuning; model   architecture diagram for
                serialisation to               the docs directory.
                rf_melt_model.pkl.             
                folium_renderer.py --- Folium  
                HTML map generation with ice   
                extent, melt probability, and  
                retreat boundary layers.       
  -----------------------------------------------------------------------

\-\--x\-\--
