All functions
=============

Download and plot functions
---------------------------

Every function has a long name and a short alias. Both names call the same function. Click a name to
open its documentation on the page of the data type.

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Data type
     - Download (long name)
     - Download (alias)
     - Plot (long name)
     - Plot (alias)
   * - :doc:`/data/ndvi`
     - :func:`~cdec.download_normalized_difference_vegetation_index`
     - ``download_ndvi``
     - :func:`~cdec.plot_normalized_difference_vegetation_index`
     - ``plot_ndvi``
   * - :doc:`/data/evi`
     - :func:`~cdec.download_enhanced_vegetation_index`
     - ``download_evi``
     - :func:`~cdec.plot_enhanced_vegetation_index`
     - ``plot_evi``
   * - :doc:`/data/landsat-ndvi`
     - :func:`~cdec.download_landsat_ndvi`
     - ``download_landsat``
     - :func:`~cdec.plot_landsat_ndvi`
     - ``plot_landsat``
   * - :doc:`/data/ndwi`
     - :func:`~cdec.download_normalized_difference_water_index`
     - ``download_ndwi``
     - :func:`~cdec.plot_normalized_difference_water_index`
     - ``plot_ndwi``
   * - :doc:`/data/ndmi`
     - :func:`~cdec.download_normalized_difference_moisture_index`
     - ``download_ndmi``
     - :func:`~cdec.plot_normalized_difference_moisture_index`
     - ``plot_ndmi``
   * - :doc:`/data/ndsi`
     - :func:`~cdec.download_normalized_difference_snow_index`
     - ``download_ndsi``
     - :func:`~cdec.plot_normalized_difference_snow_index`
     - ``plot_ndsi``
   * - :doc:`/data/true-color`
     - :func:`~cdec.download_true_color_image`
     - ``download_tci``
     - :func:`~cdec.plot_true_color_image`
     - ``plot_tci``
   * - :doc:`/data/false-color-urban`
     - :func:`~cdec.download_false_color_urban`
     - ``download_urban``
     - :func:`~cdec.plot_false_color_urban`
     - ``plot_urban``
   * - :doc:`/data/false-color-infrared`
     - :func:`~cdec.download_false_color_infrared`
     - ``download_infrared``
     - :func:`~cdec.plot_false_color_infrared`
     - ``plot_infrared``
   * - :doc:`/data/false-color-swir`
     - :func:`~cdec.download_false_color_swir`
     - ``download_swir``
     - :func:`~cdec.plot_false_color_swir`
     - ``plot_swir``
   * - :doc:`/data/land-surface-temperature`
     - :func:`~cdec.download_land_surface_temperature`
     - ``download_lst``
     - :func:`~cdec.plot_land_surface_temperature`
     - ``plot_lst``
   * - :doc:`/data/soil-water-index`
     - :func:`~cdec.download_soil_water_index`
     - ``download_swi``
     - :func:`~cdec.plot_soil_water_index`
     - ``plot_swi``
   * - :doc:`/data/elevation`
     - :func:`~cdec.download_digital_elevation_model`
     - ``download_dem``
     - :func:`~cdec.plot_digital_elevation_model`
     - ``plot_dem``
   * - :doc:`/data/land-cover`
     - :func:`~cdec.download_land_cover`
     - (none)
     - :func:`~cdec.plot_land_cover`
     - (none)
   * - :doc:`/data/scene-classification`
     - :func:`~cdec.download_scene_classification_map`
     - ``download_scl``
     - :func:`~cdec.plot_scene_classification_map`
     - ``plot_scl``

Other functions
---------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Function
     - What it does
     - Page
   * - :func:`~cdec.plot_raster`
     - draws any GeoTIFF
     - :doc:`plotting`
   * - :func:`~cdec.show_scl_classes`
     - prints the Sentinel-2 SCL classes with a hint for each
     - :doc:`scl`
   * - :func:`~cdec.eo.postprocessing.enhance_color`, :func:`~cdec.eo.postprocessing.enhance_contrast`
     - turn reflectance into colours
     - :doc:`files`

Constants
---------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Name
     - Content
     - Page
   * - ``cdec.SCL_CLASSES``, ``cdec.SCL_HINTS``, ``cdec.SCL_COLORS``
     - the 12 SCL classes, a hint for each and their colours
     - :doc:`scl`
   * - ``cdec.SCL_LAND``, ``cdec.SCL_LAND_AND_WATER``, ``cdec.SCL_LAND_WATER_AND_SNOW``
     - ready-made selections ``(4, 5)``, ``(4, 5, 6)`` and ``(4, 5, 6, 11)``
     - :doc:`scl`
   * - ``cdec.WORLDCOVER_CLASSES``, ``cdec.WORLDCOVER_COLORS``
     - names and colours of the land cover classes
     - :doc:`/data/land-cover`
