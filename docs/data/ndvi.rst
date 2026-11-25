NDVI (Sentinel-2)
=================

The **Normalized Difference Vegetation Index** tells how green and dense the plants are. Healthy plants reflect
much near-infrared light and absorb red light, so ``NDVI = (NIR - red) / (NIR + red)`` is high for them. The result
is one number per pixel: close to 1 for dense green vegetation, around 0.1 to 0.2 for bare soil, and low or
negative for water, built-up surfaces and clouds.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_normalized_difference_vegetation_index`, short ``download_ndvi``
   * - Plot function
     - :func:`~cdec.plot_normalized_difference_vegetation_index`, short ``plot_ndvi``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B04 (red) and B08 (near-infrared)
   * - Pixel size
     - 10 m
   * - Result
     - one band of floating-point numbers, no unit, about -1 ... 1
   * - Clouds
     - scenes above ``max_cloud_cover`` (20 %) are not used; pixels are masked with ``scl_classes``
       (default: vegetation and not vegetated)
   * - Period
     - mean of all observations of ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_ndvi, plot_ndvi

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_ndvi("data/ndvi_bremen.tif", spatial_extent, temporal_extent)
    plot_ndvi(path)

.. figure:: /_static/figures/ndvi.png
   :alt: NDVI of Bremen in June 2024: green fields and parks, yellow-green built-up areas, white patches without data.
   :width: 100%

   Bremen, June 2024. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **The index is calculated from the mean reflectance** of the period, not as the mean of the NDVI of every
  date.
* **Holes.** A pixel without a single usable observation stays empty. In the example about a quarter of the pixels
  are empty. A longer period or a higher ``max_cloud_cover`` fills holes (:doc:`/howto/filter-clouds`).
* **Water is empty by default.** The default ``scl_classes`` is ``(4, 5)``, which keeps vegetation and not vegetated
  pixels only. Use ``scl_classes=cdec.SCL_LAND_AND_WATER`` to keep water.
* **Values outside -1 ... 1.** A few pixels can lie slightly outside, for example when the red reflectance is
  close to zero. The example file ranges from -0.66 to 1.26. Treat them as noise or clip them with
  ``numpy.clip(ndvi, -1, 1)``.
* **The plot** uses red-yellow-green colours and a fixed range of -1 to 1, so the same colour always means the
  same NDVI and two maps can be compared by eye.
* For a longer time series (1997-2024) at a coarser resolution use :doc:`landsat-ndvi`.

See also
--------

:doc:`/howto/filter-clouds`, :doc:`/howto/choose-period`, :doc:`/explanation/clouds-and-masking`

Download
--------

.. autofunction:: cdec.download_normalized_difference_vegetation_index

Plot
----

.. autofunction:: cdec.plot_normalized_difference_vegetation_index
