import os
import folium
import rasterio
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize

def render_glacier_map(prediction_tiff_path, geojson_path, output_html_path):
    print("    -> Generating interactive Folium map...")

    # Load the Glacier Boundary
    glacier_gdf = gpd.read_file(geojson_path)
    
    # Lat/Lon (EPSG:4326) which Folium requires
    if glacier_gdf.crs and glacier_gdf.crs.to_epsg() != 4326:
        glacier_gdf = glacier_gdf.to_crs(epsg=4326)

    # Clean the data for JSON serialization ---
    # Convert all non-geometry columns to strings so Folium doesn't crash on Timestamps
    for col in glacier_gdf.columns:
        if col != 'geometry':
            glacier_gdf[col] = glacier_gdf[col].astype(str)

    # Use total_bounds to avoid centroid warnings
    # Calculate map center using bounding box instead of centroid
    minx, miny, maxx, maxy = glacier_gdf.total_bounds
    center_lat = (miny + maxy) / 2
    center_lon = (minx + maxx) / 2

    # 2. Initialize the Map (Using Esri High-Res Satellite Imagery)
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Esri Satellite'
    )

    # 3. Add the Glacier Boundary Outline
    folium.GeoJson(
        glacier_gdf,
        name="Official GLIMS Boundary",
        style_function=lambda feature: {
            'fillColor': 'transparent',
            'color': 'white',
            'weight': 2,
            'dashArray': '5, 5'
        }
    ).add_to(m)

    # 4. Load and Colorize the ML Melt Prediction Raster
    with rasterio.open(prediction_tiff_path) as src:
        bounds = src.bounds
        img_bounds = [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

        data = src.read(1)
        masked_data = np.ma.masked_invalid(data)

        # Apply a colormap (coolwarm: Blue = Safe Ice, Red = High Melt Risk)
        cmap = plt.cm.coolwarm
        norm = Normalize(vmin=0, vmax=1)
        
        rgba_img = cmap(norm(masked_data))
        rgba_img[masked_data.mask, 3] = 0 # Transparent background

    # 5. Add the Colorized ML Overlay to the Map
    folium.raster_layers.ImageOverlay(
        image=rgba_img,
        bounds=img_bounds,
        opacity=0.6, 
        name='Melt Vulnerability Prediction (RF Model)',
        interactive=True,
        cross_origin=False,
    ).add_to(m)

    # Add a Layer Control box so the user can toggle layers on/off
    folium.LayerControl().add_to(m)

    # Save the physical HTML file
    m.save(output_html_path)
    return output_html_path
