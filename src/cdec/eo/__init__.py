"""Download Earth observation data from the Copernicus Data Space openEO backend.

Every data set has a long, readable function name and a short alias. Both names
call exactly the same function::

    long name                                          short alias         data
    -------------------------------------------------  ------------------  -----------------------------
    download_normalized_difference_vegetation_index    download_ndvi       Sentinel-2 NDVI
    download_enhanced_vegetation_index                 download_evi        Sentinel-2 EVI
    download_normalized_difference_water_index         download_ndwi       Sentinel-2 NDWI (water)
    download_normalized_difference_moisture_index      download_ndmi       Sentinel-2 NDMI (moisture)
    download_normalized_difference_snow_index          download_ndsi       Sentinel-2 NDSI (snow)
    download_true_color_image                          download_tci        Sentinel-2 true colour
    download_false_color_urban                         download_urban      Sentinel-2 false colour urban
    download_false_color_infrared                      download_infrared   Sentinel-2 false colour infrared
    download_false_color_swir                          download_swir       Sentinel-2 false colour SWIR
    download_scene_classification_map                  download_scl        Sentinel-2 scene classification
    download_landsat_ndvi                              download_landsat    Landsat NDVI mosaic
    download_land_surface_temperature                  download_lst        Sentinel-3 surface temperature
    download_soil_water_index                          download_swi        Copernicus soil water index
    download_digital_elevation_model                   download_dem        Copernicus elevation model
    download_land_cover                                (no alias)          ESA WorldCover land cover

The Sentinel-2 functions have ``max_cloud_cover`` and ``scl_classes`` as their
first options after the three standard arguments (the scene classification map
has only ``max_cloud_cover``: it *is* the SCL). ``cdec.show_scl_classes()``
explains the SCL classes. Technical options (``create_cog``,
``overview_resampling``) must be passed by keyword. ``help(download_ndvi)``
(or any other function) describes the file that the function writes.
"""

from .dem import download_dem, download_digital_elevation_model
from .evi import download_enhanced_vegetation_index, download_evi
from .false_color_infrared import download_false_color_infrared, download_infrared
from .false_color_swir import download_false_color_swir, download_swir
from .false_color_urban import download_false_color_urban, download_urban
from .landsat import download_landsat, download_landsat_ndvi
from .lst import download_land_surface_temperature, download_lst
from .ndmi import download_ndmi, download_normalized_difference_moisture_index
from .ndsi import download_ndsi, download_normalized_difference_snow_index
from .ndvi import download_ndvi, download_normalized_difference_vegetation_index
from .ndwi import download_ndwi, download_normalized_difference_water_index
from .scene_classification import download_scene_classification_map, download_scl
from .scl import (
    SCL_CLASSES,
    SCL_COLORS,
    SCL_HINTS,
    SCL_LAND,
    SCL_LAND_AND_WATER,
    SCL_LAND_WATER_AND_SNOW,
    show_scl_classes,
)
from .soil_water_index import download_soil_water_index, download_swi
from .tci import download_tci, download_true_color_image
from .worldcover import (
    WORLDCOVER_CLASSES,
    WORLDCOVER_COLORS,
    download_land_cover,
)

__all__ = [
    # long names
    "download_digital_elevation_model",
    "download_enhanced_vegetation_index",
    "download_false_color_infrared",
    "download_false_color_swir",
    "download_false_color_urban",
    "download_land_cover",
    "download_land_surface_temperature",
    "download_landsat_ndvi",
    "download_normalized_difference_moisture_index",
    "download_normalized_difference_snow_index",
    "download_normalized_difference_vegetation_index",
    "download_normalized_difference_water_index",
    "download_scene_classification_map",
    "download_soil_water_index",
    "download_true_color_image",
    # short aliases
    "download_dem",
    "download_evi",
    "download_infrared",
    "download_landsat",
    "download_lst",
    "download_ndmi",
    "download_ndsi",
    "download_ndvi",
    "download_ndwi",
    "download_scl",
    "download_swi",
    "download_swir",
    "download_tci",
    "download_urban",
    # Sentinel-2 Scene Classification Layer
    "SCL_CLASSES",
    "SCL_COLORS",
    "SCL_HINTS",
    "SCL_LAND",
    "SCL_LAND_AND_WATER",
    "SCL_LAND_WATER_AND_SNOW",
    "show_scl_classes",
    # ESA WorldCover legend
    "WORLDCOVER_CLASSES",
    "WORLDCOVER_COLORS",
]
