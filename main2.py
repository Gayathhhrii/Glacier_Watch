import os
import pandas as pd

# Import our custom modules
from src.logic.ndsi_processor import process_ndsi_and_mask
from src.utils.dem_loader import load_and_align_dem
from src.logic.melt_predictor import predict_and_save_melt_map
from src.utils.folium_renderer import render_glacier_map

# ── Paths ──
# ── Remove the hardcoded paths from the top of your file ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "data", "rf_model_jan.joblib") 
GEOJSON_PATH = os.path.join(BASE_DIR, "data", "glaciers_projected.geojson")
DEM_PATH = os.path.join(BASE_DIR, "data", "output_SRTMGL1.tif")

def get_monthly_temperature(csv_path, target_month):
    # ... (Keep this function exactly the same) ...
    try:
        df = pd.read_csv(csv_path)
        df['date'] = df['date'].astype(str)
        month_data = df[df['date'].str.startswith(target_month)]
        if not month_data.empty:
            return month_data['temperature_2m_mean_C'].mean()
    except Exception as e:
        print(f"  [!] Weather warning: {e}")
    return -5.0 

# ── Update this function to accept a month! ──
def run_pipeline(month_num="01"):
    month_prefix = "Jan" if month_num == "01" else "Oct"
    month_word = "january" if month_num == "01" else "october"
    
    print(f"\n🚀 STARTING GLACIERWATCH ML PIPELINE ({month_word.upper()}) 🚀\n")

    # Dynamically set the paths for this specific month
    NDSI_PATH = os.path.join(BASE_DIR, "data", f"NDSI_Gangotri_{month_prefix}2021.tif")
    TEMP_CSV = os.path.join(BASE_DIR, "data", "Temperature_data", f"gangotri_temp_2021_{month_num}.csv")
    OUTPUT_TIF = os.path.join(BASE_DIR, "data", f"melt_prediction_2021_{month_num}.tif")
    HTML_OUTPUT = os.path.join(BASE_DIR, "data", f"glacier_map_{month_word}.html")

    print(f"[1/5] Processing NDSI and generating boundaries...")
    raw_ndsi, final_mask, ndsi_meta = process_ndsi_and_mask(NDSI_PATH, GEOJSON_PATH)
    
    print(f"\n[2/5] Loading and aligning Digital Elevation Model...")
    aligned_dem = load_and_align_dem(DEM_PATH, GEOJSON_PATH, ndsi_meta)
    
    print(f"\n[3/5] Fetching historical weather composites...")
    mean_temp = get_monthly_temperature(TEMP_CSV, f"2021-{month_num}")
    
    print(f"\n[4/5] Executing Machine Learning Module...")
    out_file = predict_and_save_melt_map(
        raw_ndsi, aligned_dem, final_mask, mean_temp, 
        ndsi_meta, MODEL_PATH, OUTPUT_TIF
    )
    
    print(f"\n[5/5] Rendering Interactive Map...")
    html_file = render_glacier_map(OUTPUT_TIF, GEOJSON_PATH, HTML_OUTPUT)
    
    print(f"\n✅ PIPELINE COMPLETE FOR {month_word.upper()}!\n")
    return html_file # Return the map path so the GUI can display it


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from src.gui.main_window import GlacierWatchWindow
    
    # Initialize the Desktop Application
    app = QApplication(sys.argv)
    
    # Create and show the main window
    window = GlacierWatchWindow()
    window.show()
    
    # Run the application loop (Note the underscore in exec_ for PyQt5)
    sys.exit(app.exec_())