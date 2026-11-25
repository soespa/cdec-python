NDVI (Landsat)
==============

The same vegetation index as :doc:`ndvi`, calculated from the Landsat bi-monthly mosaics. They run from 1997 to
2024, so this is the data type for questions about **change over decades**: how did the vegetation of an area
develop since 1997? The price is a coarser pixel (30 m instead of 10 m).

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_landsat_ndvi`, short ``download_landsat``
   * - Plot function
     - :func:`~cdec.plot_landsat_ndvi`, short ``plot_landsat``
   * - Source
     - Landsat bi-monthly mosaic (collection ``LANDSAT_BIMONTHLY_MOSAIC``), bands B03 (red) and B04 (near-infrared)
   * - Pixel size
     - 30 m
   * - Result
     - one band of floating-point numbers, no unit, -1 ... 1
   * - Clouds
     - none needed: the mosaics are reconstructed and cloud-free. There are no ``max_cloud_cover`` and
       ``scl_classes`` options.
   * - Period
     - 1997 to 2024; mean of the mosaics inside ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_landsat, plot_landsat

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_landsat("data/landsat_bremen.tif", spatial_extent, temporal_extent)
    plot_landsat(path)

.. figure:: /_static/figures/landsat-ndvi.png
   :alt: Landsat NDVI of Bremen in June 2024: green fields, a white river, yellow built-up areas.
   :width: 100%

   Bremen, June 2024. White: no data. Landsat data, see :doc:`/reference/data-sources`.

Things to know
--------------

* **Not the same as the Sentinel-2 NDVI.** Different satellites, bands, pixel size and processing give slightly
  different numbers. Compare Landsat with Landsat, and Sentinel-2 with Sentinel-2.
* **Several decades:** use the same months of different years (for example June 1998, 2008, 2018 and 2024) to avoid
  mixing up seasons with change.
* **Empty pixels.** In the example the river is empty; the rest is complete.
* The file uses longitude and latitude (EPSG:4326), so its pixel size is given in degrees. The plot corrects the
  shape of the map for that (:doc:`/explanation/grids-and-time`).
* The plot uses red-yellow-green colours and a fixed range of -1 to 1, like the Sentinel-2 NDVI.

See also
--------

:doc:`ndvi`, :doc:`/howto/choose-period`

Download
--------

.. autofunction:: cdec.download_landsat_ndvi

Plot
----

.. autofunction:: cdec.plot_landsat_ndvi
