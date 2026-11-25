Data types
==========

CDEC downloads fifteen kinds of data. Each has a page that shows what the data is, how to download and plot it,
what the numbers mean, and what to watch out for. The pages all have the same layout:

1. a short description and a table *At a glance*,
2. an example that you can copy and run as it is, with its picture,
3. things to know,
4. the reference of the download function and of the plot function.

Every download function has a long name, a short alias (the same function) and a plot function with the
matching name. Every function is called as ``download_xxx(file_path, spatial_extent, temporal_extent, ...)``
and returns the absolute path of the file.

Vegetation
----------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Data type
     - Functions
     - Source
     - Pixel size
     - Result
   * - :doc:`ndvi`
     - ``download_ndvi``, ``plot_ndvi``
     - Sentinel-2
     - 10 m
     - number, -1 ... 1
   * - :doc:`evi`
     - ``download_evi``, ``plot_evi``
     - Sentinel-2
     - 10 m
     - number
   * - :doc:`landsat-ndvi`
     - ``download_landsat``, ``plot_landsat``
     - Landsat mosaic, 1997-2025
     - 30 m
     - number, -1 ... 1

Water, moisture and snow
------------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Data type
     - Functions
     - Source
     - Pixel size
     - Result
   * - :doc:`ndwi`
     - ``download_ndwi``, ``plot_ndwi``
     - Sentinel-2
     - 10 m
     - number, -1 ... 1
   * - :doc:`ndmi`
     - ``download_ndmi``, ``plot_ndmi``
     - Sentinel-2
     - 10 m
     - number, -1 ... 1
   * - :doc:`ndsi`
     - ``download_ndsi``, ``plot_ndsi``
     - Sentinel-2
     - 10 m
     - number, -1 ... 1

Pictures
--------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Data type
     - Functions
     - Source
     - Pixel size
     - Result
   * - :doc:`true-color`
     - ``download_tci``, ``plot_tci``
     - Sentinel-2
     - 10 m
     - 8-bit colour picture (or reflectance)
   * - :doc:`false-color-urban`
     - ``download_urban``, ``plot_urban``
     - Sentinel-2
     - 10 m
     - 8-bit colour picture (or reflectance)
   * - :doc:`false-color-infrared`
     - ``download_infrared``, ``plot_infrared``
     - Sentinel-2
     - 10 m
     - 8-bit colour picture (or reflectance)
   * - :doc:`false-color-swir`
     - ``download_swir``, ``plot_swir``
     - Sentinel-2
     - 10 m
     - 8-bit colour picture (or reflectance)

Temperature and soil moisture
-----------------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Data type
     - Functions
     - Source
     - Pixel size
     - Result
   * - :doc:`land-surface-temperature`
     - ``download_lst``, ``plot_lst``
     - Sentinel-3
     - 1 km
     - Kelvin
   * - :doc:`soil-water-index`
     - ``download_swi``, ``plot_swi``
     - Copernicus Land Monitoring Service
     - 1 km
     - percent, 0 ... 100

Terrain and land cover
----------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Data type
     - Functions
     - Source
     - Pixel size
     - Result
   * - :doc:`elevation`
     - ``download_dem``, ``plot_dem``
     - Copernicus DEM
     - 30 m
     - metres
   * - :doc:`land-cover`
     - ``download_land_cover``, ``plot_land_cover``
     - ESA WorldCover 2021
     - 10 m
     - class numbers
   * - :doc:`scene-classification`
     - ``download_scl``, ``plot_scl``
     - Sentinel-2
     - 10 m
     - class numbers

The pictures on these pages show the area of the tutorial (Bremen, Germany), made from real downloads.
See :doc:`/reference/data-sources` for the credits of the data.

.. toctree::
   :hidden:

   ndvi
   evi
   landsat-ndvi
   ndwi
   ndmi
   ndsi
   true-color
   false-color-urban
   false-color-infrared
   false-color-swir
   land-surface-temperature
   soil-water-index
   elevation
   land-cover
   scene-classification
