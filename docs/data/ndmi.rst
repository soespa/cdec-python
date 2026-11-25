NDMI (Sentinel-2)
=================

The **Normalized Difference Moisture Index** shows how much water the vegetation holds. Water in the leaves absorbs
short-wave infrared light, while the structure of the leaves reflects near-infrared light, so
``NDMI = (NIR - SWIR) / (NIR + SWIR)`` is high for moist, leafy vegetation and falls when plants dry out. The result
is one number per pixel, between -1 and 1.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_normalized_difference_moisture_index`, short ``download_ndmi``
   * - Plot function
     - :func:`~cdec.plot_normalized_difference_moisture_index`, short ``plot_ndmi``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B8A (near-infrared) and B11 (short-wave infrared)
   * - Pixel size
     - 20 m
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

    from cdec import download_ndmi, plot_ndmi

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_ndmi("data/ndmi_bremen.tif", spatial_extent, temporal_extent)
    plot_ndmi(path)

.. figure:: /_static/figures/ndmi.png
   :alt: NDMI of Bremen in June 2024: green-blue for moist vegetation, beige for drier surfaces, white patches without data and without water.
   :width: 100%

   Bremen, June 2024. Green-blue: moist, beige: dry. White: no data, and water. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **Both bands have 20 m pixels**, so the file has 20 m pixels, not 10 m like the :doc:`ndvi`.
* **Moisture of the plants, not of the soil.** The index describes the leaves. For the water in the soil use the
  :doc:`soil-water-index`, which is much coarser (1 km).
* **Compare the same kind of vegetation.** A meadow and a forest have different values even when both are healthy.
  The index is most useful for comparing one place at different times, for example a dry and a wet summer
  (:doc:`/howto/compare-images`).
* **Water is empty by default.** The default ``scl_classes`` is ``(4, 5)``. Water has no meaningful moisture value
  here; use ``scl_classes=cdec.SCL_LAND_AND_WATER`` if you want to see it anyway.
* **The name.** The same formula is called NDWI in some books (Gao's index). In this package :doc:`ndwi` is the
  index of McFeeters, made to find open water.
* **The index is calculated from the mean reflectance** of the period, not as the mean of the index of every date.
* **The plot** uses brown-white-blue-green colours and a fixed range of -1 to 1: brown for dry, blue-green for
  moist.

See also
--------

:doc:`ndvi`, :doc:`ndwi`, :doc:`soil-water-index`, :doc:`/howto/filter-clouds`

Download
--------

.. autofunction:: cdec.download_normalized_difference_moisture_index

Plot
----

.. autofunction:: cdec.plot_normalized_difference_moisture_index
