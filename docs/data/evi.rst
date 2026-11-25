EVI (Sentinel-2)
================

The **Enhanced Vegetation Index** is a second vegetation index. It uses the blue band to correct for the
atmosphere and does not level off as quickly as the NDVI over very dense vegetation. The formula is
``EVI = 2.5 * (NIR - red) / (NIR + 6 * red - 7.5 * blue + 1)``.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_enhanced_vegetation_index`, short ``download_evi``
   * - Plot function
     - :func:`~cdec.plot_enhanced_vegetation_index`, short ``plot_evi``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B02 (blue), B04 (red) and B08 (near-infrared)
   * - Pixel size
     - 10 m
   * - Result
     - one band of floating-point numbers, no unit, typically 0 ... 1 for vegetation
   * - Clouds
     - scenes above ``max_cloud_cover`` (20 %) are not used; pixels are masked with ``scl_classes``
       (default: vegetation and not vegetated)
   * - Period
     - mean of all observations of ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_evi, plot_evi

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_evi("data/evi_bremen.tif", spatial_extent, temporal_extent)
    plot_evi(path)

.. figure:: /_static/figures/evi.png
   :alt: EVI of Bremen in June 2024: similar to the NDVI map, with lower values.
   :width: 100%

   Bremen, June 2024. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **Extreme values.** The denominator of the formula can come close to zero, and then the result explodes. The
  example file ranges from -52 to 263, although its median is 0.39 and 99 % of its pixels lie between 0.01 and 0.83.
  Before you calculate statistics, clip the values or use percentiles instead of the maximum:
  ``numpy.clip(evi, -1, 1)``.
* **The plot** uses a fixed range of -1 to 1. Pixels outside the range get the colour of the nearest end of the
  colour bar.
* Like the NDVI, the index is calculated from the mean reflectance of the period, water is empty by default,
  and holes can be filled with a longer period (:doc:`ndvi`, :doc:`/howto/filter-clouds`).

See also
--------

:doc:`ndvi`, :doc:`/howto/filter-clouds`, :doc:`/explanation/clouds-and-masking`

Download
--------

.. autofunction:: cdec.download_enhanced_vegetation_index

Plot
----

.. autofunction:: cdec.plot_enhanced_vegetation_index
