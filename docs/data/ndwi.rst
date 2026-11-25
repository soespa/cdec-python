NDWI (Sentinel-2)
=================

The **Normalized Difference Water Index** shows open water. Water reflects more green light than near-infrared
light, while plants and soil do the opposite, so ``NDWI = (green - NIR) / (green + NIR)`` is above 0 for water and
below 0 for most land. The result is one number per pixel, between -1 and 1.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_normalized_difference_water_index`, short ``download_ndwi``
   * - Plot function
     - :func:`~cdec.plot_normalized_difference_water_index`, short ``plot_ndwi``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B03 (green) and B08 (near-infrared)
   * - Pixel size
     - 10 m
   * - Result
     - one band of floating-point numbers, no unit, -1 ... 1
   * - Clouds
     - scenes above ``max_cloud_cover`` (20 %) are not used; pixels are masked with ``scl_classes``
       (default: vegetation, not vegetated and water)
   * - Period
     - mean of all observations of ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_ndwi, plot_ndwi

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_ndwi("data/ndwi_bremen.tif", spatial_extent, temporal_extent)
    plot_ndwi(path)

.. figure:: /_static/figures/ndwi.png
   :alt: NDWI of Bremen in June 2024: rivers and lakes in blue, fields and built-up areas in red, white patches without data.
   :width: 100%

   Bremen, June 2024. Blue: water, red: land. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **Two indices are called NDWI.** This page is the index of McFeeters (green and near-infrared), made to find
  open water. Gao's index (near-infrared and short-wave infrared) measures the water in leaves; this package calls
  it :doc:`NDMI <ndmi>`. Check which one a book or a paper means.
* **Water is kept by default.** The default ``scl_classes`` is ``(4, 5, 6)``, because a water index without water is
  useless. NDVI and EVI drop water instead (:doc:`ndvi`).
* **Above 0 is a first guess, not a water map.** Built-up areas and shadows can also have values close to 0 or
  slightly above. For a water mask combine the index with the scene classification (class 6,
  :doc:`scene-classification`) or the :doc:`land cover map <land-cover>`.
* **The index is calculated from the mean reflectance** of the period, not as the mean of the index of every date.
* **The plot** uses red-white-blue colours and a fixed range of -1 to 1: red for land, blue for water, so the same
  colour always means the same NDWI and two maps can be compared by eye.

See also
--------

:doc:`ndmi`, :doc:`scene-classification`, :doc:`/howto/filter-clouds`, :doc:`/explanation/clouds-and-masking`

Download
--------

.. autofunction:: cdec.download_normalized_difference_water_index

Plot
----

.. autofunction:: cdec.plot_normalized_difference_water_index
