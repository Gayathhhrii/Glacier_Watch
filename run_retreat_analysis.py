import os
import math
import rasterio
import numpy as np
import geopandas as gpd
from rasterio.mask import mask
from skimage.morphology import closing, disk

# ── Paths ──
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
NDSI_JAN = os.path.join(BASE_DIR, "data", "NDSI_Gangotri_Jan2021.tif")
NDSI_OCT = os.path.join(BASE_DIR, "data", "NDSI_Gangotri_Oct2021.tif")
GEOJSON_PATH = os.path.join(BASE_DIR, "data", "glaciers_projected.geojson")

def get_ice_mask_and_area(ndsi_path, geojson_path, threshold=0.4):
    """Generates the ice mask and extracts the physical size of the pixels."""
    glacier_boundary = gpd.read_file(geojson_path)
    
    with rasterio.open(ndsi_path) as src:
        if glacier_boundary.crs != src.crs:
             glacier_boundary = glacier_boundary.to_crs(src.crs)
             
        geometries = glacier_boundary.geometry.values
        out_image, out_transform = mask(src, geometries, crop=True, nodata=np.nan)
        
        pixel_width = abs(out_transform[0])
        pixel_height = abs(out_transform[4])
        
        # --- THE FIX: DEGREE TO METER CONVERSION ---
        if src.crs and src.crs.to_epsg() == 4326:
            lat_center = 30.9 
            meter_per_deg_lat = 111320.0
            meter_per_deg_lon = 111320.0 * math.cos(math.radians(lat_center))
            
            width_m = pixel_width * meter_per_deg_lon
            height_m = pixel_height * meter_per_deg_lat
            pixel_area_m2 = width_m * height_m
        else:
            pixel_area_m2 = pixel_width * pixel_height

    ndsi_array = out_image[0]
    binary_mask = np.where(ndsi_array > threshold, 1, 0).astype(np.uint8)
    clean_mask = closing(binary_mask, disk(3))
    
    total_ice_pixels = np.sum(clean_mask == 1)
    
    return total_ice_pixels, pixel_area_m2

# ── THIS IS THE NEW FUNCTION THAT TALKS TO THE GUI ──
def calculate_retreat_stats():
    """Calculates the retreat and returns a dictionary of the final stats."""
    jan_pixels, pixel_size = get_ice_mask_and_area(NDSI_JAN, GEOJSON_PATH)
    oct_pixels, _ = get_ice_mask_and_area(NDSI_OCT, GEOJSON_PATH)
    
    # --- THE MATH ---
    pixels_lost = jan_pixels - oct_pixels
    area_lost_m2 = pixels_lost * pixel_size
    area_lost_km2 = area_lost_m2 / 1_000_000
    
    # Instead of printing, we PACKAGE the results in a dictionary and RETURN them
    return {
        "jan_pixels": jan_pixels,
        "oct_pixels": oct_pixels,
        "pixels_lost": pixels_lost,
        "area_lost_km2": area_lost_km2
    }

# ── THIS LETS YOU STILL TEST IT IN THE TERMINAL ──
if __name__ == "__main__":
    print("\n🧊 GLACIERWATCH: RETREAT ANALYSIS MODULE 🧊\n")
    print("Calculating stats...")
    
    # Run the new function and print the returned dictionary
    stats = calculate_retreat_stats()
    
    print("\n" + "="*40)
    print("📊 FINAL RETREAT STATISTICS (2021)")
    print("="*40)
    print(f"January Ice Pixels:    {stats['jan_pixels']:,}")
    print(f"October Ice Pixels:    {stats['oct_pixels']:,}")
    print(f"Total Pixels Melted:   {stats['pixels_lost']:,}")
    print("-" * 40)
    print(f"🚨 TOTAL ICE AREA LOST: {stats['area_lost_km2']:.2f} km²")
    print("="*40 + "\n")
    