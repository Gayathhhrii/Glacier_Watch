import numpy as np
import rasterio
from rasterio.mask import mask
from rasterio.enums import Resampling
from rasterio.vrt import WarpedVRT
import geopandas as gpd

def load_and_align_dem(dem_path, geojson_path, ndsi_metadata):
    """Virtually resamples and clips the 30m DEM to match the NDSI resolution perfectly."""
    
    glacier_boundary = gpd.read_file(geojson_path)
    
    target_crs = ndsi_metadata['crs']
    target_transform = ndsi_metadata['transform']
    target_height = ndsi_metadata['height']
    target_width = ndsi_metadata['width']

    if glacier_boundary.crs != target_crs:
        glacier_boundary = glacier_boundary.to_crs(target_crs)
    geometries = glacier_boundary.geometry.values

    with rasterio.open(dem_path) as src:
        vrt_options = {
            'resampling': Resampling.bilinear,
            'crs': target_crs,
            'transform': target_transform,
            'height': target_height,
            'width': target_width
        }
        
        with WarpedVRT(src, **vrt_options) as vrt:
            # We use -9999 to prevent float-to-integer crashing during the mask
            out_image, out_transform = mask(vrt, geometries, crop=True, nodata=-9999)
            
    # Convert immediately to float32 to save memory and restore np.nan
    dem_array = out_image[0].astype(np.float32)
    dem_array[dem_array == -9999.0] = np.nan
    
    return dem_array