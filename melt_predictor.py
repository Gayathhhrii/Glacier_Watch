import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import rasterio
import gc

def predict_and_save_melt_map(raw_ndsi, aligned_dem, final_mask, temp_val, out_meta, model_path, output_tiff_path):
    """Trains (or loads) the ML model, predicts melt risk, and saves directly to disk to protect RAM."""
    
    valid_pixels = (final_mask == 1) & ~np.isnan(raw_ndsi) & ~np.isnan(aligned_dem)

    # Force float32 to use 50% less RAM
    X_ndsi = raw_ndsi[valid_pixels].astype(np.float32)
    X_dem = aligned_dem[valid_pixels].astype(np.float32)
    X_temp = np.full(X_ndsi.shape, temp_val, dtype=np.float32) 

    X_full = np.column_stack((X_ndsi, X_dem, X_temp))
    
    # Check if model already exists (Architecture idea from your main.py)
    if os.path.exists(model_path):
        print("    -> Loading existing Random Forest model from disk...")
        rf_model = joblib.load(model_path)
    else:
        print("    -> Training NEW Random Forest model...")
        # Physical glaciology rules for training labels
        y_full = ((X_dem < 5200) & (X_ndsi < 0.6)).astype(np.int8)
        
        # Subsample to 10% to completely prevent Kernel/RAM crashes
        X_train, _, y_train, _ = train_test_split(X_full, y_full, train_size=0.10, random_state=42)
        
        # n_jobs=1 prevents Windows OpenMP threading crashes
        rf_model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=1)
        rf_model.fit(X_train, y_train)
        
        print("    -> Saving model to disk for future use...")
        joblib.dump(rf_model, model_path)
        
        del X_train, y_train
        gc.collect()

    # Predict in chunks to save memory
    print("    -> Predicting melt vulnerability map in safe chunks...")
    melt_probabilities = np.zeros(len(X_full), dtype=np.float32)
    chunk_size = 50000
    
    for i in range(0, len(X_full), chunk_size):
        end = min(i + chunk_size, len(X_full)) 
        melt_probabilities[i:end] = rf_model.predict_proba(X_full[i:end])[:, 1]

    # Reconstruct 2D Map
    melt_map_2d = np.full(raw_ndsi.shape, np.nan, dtype=np.float32)
    melt_map_2d[valid_pixels] = melt_probabilities

    # Save to TIFF instead of drawing with Matplotlib
    print("    -> Saving prediction array directly to GeoTIFF...")
    save_meta = out_meta.copy()
    save_meta.update({"dtype": 'float32', "count": 1, "nodata": np.nan})
    
    with rasterio.open(output_tiff_path, 'w', **save_meta) as dest:
        dest.write(melt_map_2d, 1)
        
    return output_tiff_path