"""Draw the rasters that the ``download_*`` functions write.

* ``plot_raster(file)`` - any GeoTIFF; looks at the format (colour picture or numbers).
* ``plot_ndvi(file)``, ``plot_tci(file)``, ... - one function per data type, with the
  colour map, value range and labels that fit it. They are named like the
  ``download_*`` functions, with the same short aliases.

Every function draws into a matplotlib ``Axes`` and returns it.
See ``products.py`` for the table of names.
"""

from .products import (
    plot_digital_elevation_model,
    plot_enhanced_vegetation_index,
    plot_false_color_infrared,
    plot_false_color_swir,
    plot_false_color_urban,
    plot_land_cover,
    plot_land_surface_temperature,
    plot_landsat_ndvi,
    plot_normalized_difference_moisture_index,
    plot_normalized_difference_snow_index,
    plot_normalized_difference_vegetation_index,
    plot_normalized_difference_water_index,
    plot_scene_classification_map,
    plot_soil_water_index,
    plot_true_color_image,
)
from .products import (
    plot_dem,
    plot_evi,
    plot_infrared,
    plot_landsat,
    plot_lst,
    plot_ndmi,
    plot_ndsi,
    plot_ndvi,
    plot_ndwi,
    plot_scl,
    plot_swi,
    plot_swir,
    plot_tci,
    plot_urban,
)
from .raster import plot_raster

__all__ = [
    # one function per data type
    "plot_normalized_difference_vegetation_index",
    "plot_enhanced_vegetation_index",
    "plot_normalized_difference_water_index",
    "plot_normalized_difference_moisture_index",
    "plot_normalized_difference_snow_index",
    "plot_true_color_image",
    "plot_false_color_urban",
    "plot_false_color_infrared",
    "plot_false_color_swir",
    "plot_scene_classification_map",
    "plot_landsat_ndvi",
    "plot_land_surface_temperature",
    "plot_soil_water_index",
    "plot_digital_elevation_model",
    "plot_land_cover",
    # short aliases
    "plot_ndvi",
    "plot_evi",
    "plot_ndwi",
    "plot_ndmi",
    "plot_ndsi",
    "plot_tci",
    "plot_urban",
    "plot_infrared",
    "plot_swir",
    "plot_scl",
    "plot_landsat",
    "plot_lst",
    "plot_swi",
    "plot_dem",
    # for any other GeoTIFF
    "plot_raster",
]
