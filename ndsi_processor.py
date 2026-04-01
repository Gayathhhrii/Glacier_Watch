import os
import numpy as np
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from skimage.morphology import closing, disk

def process_ndsi_and_mask(ndsi_tiff_path, geojson_path, threshold=0.4):
    """Clips the GEE NDSI file to the glacier boundary and generates a clean ice mask."""
    
    glacier_boundary = gpd.read_file(geojson_path)
    geometries = glacier_boundary.geometry.values

    with rasterio.open(ndsi_tiff_path) as src:
        # Auto-reproject boundary if CRS mismatch occurs
        if glacier_boundary.crs != src.crs:
             glacier_boundary = glacier_boundary.to_crs(src.crs)
             geometries = glacier_boundary.geometry.values

        out_image, out_transform = mask(src, geometries, crop=True, nodata=np.nan)
        out_meta = src.meta.copy()
        out_meta.update({
            "driver": "GTiff", 
            "height": out_image.shape[1], 
            "width": out_image.shape[2], 
            "transform": out_transform
        })

    ndsi_array = out_image[0]

    # Generate the binary mask (1 = Ice, 0 = Not Ice)
    binary_mask = np.where(ndsi_array > threshold, 1, 0).astype(np.uint8)
    
    # Clean up the mask (remove false holes/shadows)
    clean_mask = closing(binary_mask, disk(3))

    return ndsi_array, clean_mask, out_meta