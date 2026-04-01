================================================================================
GLACIERWATCH: Automated Spatial Data Science Pipeline
================================================================================

PROJECT OVERVIEW
GlacierWatch is a Python-based desktop application designed to track and quantify 
seasonal snow and ice depletion within glacial basins. It fuses multi-spectral 
optical satellite imagery, topographic elevation models, and historical climate 
data into a Random Forest machine learning model to predict melt vulnerability 
and calculate total surface area loss.

Currently configured for the Gangotri Glacier system (2021 Melt Season).

--------------------------------------------------------------------------------
INSTALLATION & SETUP
--------------------------------------------------------------------------------
This project requires Python 3.9+ and Several Spatial Data Science libraries. 
It is highly recommended to run this inside an Anaconda environment.

Required Libraries:
pip install PyQt5 pandas numpy geopandas rasterio scikit-learn folium scikit-image matplotlib pyogrio

--------------------------------------------------------------------------------
HOW TO RUN THE SOFTWARE
--------------------------------------------------------------------------------
You do not need to run every script individually. The entire system is automated 
through a master orchestrator.

1. To launch the full Desktop Application (GUI & Map Generation):
   Open your terminal, navigate to the project folder, and run:
   > python main2.py
   
   From the GUI, simply select your parameters and click "Run Pipeline".

2. To run ONLY the mathematical area-loss calculations (Terminal output only):
   > python run_retreat_analysis.py

--------------------------------------------------------------------------------
PROJECT WORKFLOW & SCRIPT DIRECTORY
--------------------------------------------------------------------------------
The project is divided into distinct modules. When you click "Run" in the GUI, 
the master script (main2.py) triggers the following workflow:

[Root Directory]
* main2.py                  -> The Master Orchestrator. It launches the PyQt5 
                               application and manages the 5-phase pipeline.
* run_retreat_analysis.py   -> The Math Engine. It converts satellite pixels into 
                               square meters to calculate the 33.40 km2 area loss.

[src/gui/]
* main_window.py            -> Builds the PyQt5 desktop dashboard, handles the 
                               button clicks, and runs the background QThread 
                               so the app doesn't freeze during processing.

[src/logic/]
* ndsi_processor.py         -> (Phase 1) Crops the square satellite images down 
                               to the exact historical GLIMS glacier boundary.
* melt_predictor.py         -> (Phase 4) Loads the Random Forest ML model, ingests 
                               the data, and exports the GeoTIFF prediction map.

[src/utils/]
* dem_loader.py             -> (Phase 2) Reprojects and aligns the 30m Digital 
                               Elevation Model to perfectly match the NDSI pixels.
* folium_renderer.py        -> (Phase 5) Translates the GeoTIFF predictions into 
                               an interactive, color-coded HTML web map.

[data/]
Contains all local inputs (NDSI composites, DEMs, GLIMS GeoJSON, Temperature CSVs) 
and is the destination folder for all output maps and predictions.

--------------------------------------------------------------------------------
METHODOLOGY SUMMARY
--------------------------------------------------------------------------------
The pipeline calculates the "Seasonal Ablation Footprint." By masking NDSI data 
to historical bounds, aligning it with elevation and temperature, and applying a 
0.40 frozen-water threshold, the system compares peak winter accumulation (Jan) 
to the end of the summer melt season (Oct) to find the exact footprint of 
seasonal meltwater generation.