False-colour urban image (Sentinel-2)
=====================================

A picture that uses invisible light. Two short-wave infrared bands and the red band are shown as red, green and
blue, so that surfaces which look alike to the eye get different colours: vegetation, bare soil, built-up areas and
water. In the example below vegetation is green, water is black and the built-up areas of the city are grey.
Compare it with the :doc:`true-colour image <true-color>` of the same area to learn the colours.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_false_color_urban`, short ``download_urban``
   * - Plot function
     - :func:`~cdec.plot_false_color_urban`, short ``plot_urban``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B12 (shown as red), B11 (green) and B04 (blue)
   * - Pixel size
     - 10 m (B11 and B12 have 20 m detail)
   * - Result
     - by default an 8-bit colour picture (three bands, 0 ... 255); with ``enhance_contrast=False`` three bands of
       reflectance (floating point)
   * - Clouds
     - scenes above ``max_cloud_cover`` (20 %) are not used; pixels are masked with ``scl_classes``
       (default: vegetation, not vegetated and water)
   * - Period
     - mean of all observations of ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_urban, plot_urban

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_urban("data/urban_bremen.tif", spatial_extent, temporal_extent)
    plot_urban(path)

.. figure:: /_static/figures/false-color-urban.png
   :alt: False-colour urban image of Bremen: green vegetation, black river and lakes, grey city, white patches without data.
   :width: 100%

   Bremen, June 2024. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **A fixed stretch.** The reflectance 0 to 0.4 becomes 0 to 255, and the brightest values are compressed instead
  of clipped. No statistics of the image are used, so the same reflectance always gets the same colour and images
  of different dates or places can be compared by eye (:doc:`/howto/compare-images`).
* **Do not calculate with the picture.** For differences and thresholds download with ``enhance_contrast=False``
  (:doc:`/howto/calculate-with-reflectance`).
* **Not identical to the Copernicus Browser.** The stretch is the one of the Sentinel Hub "false colour (urban)"
  layer, but that layer shows one acquisition date, and this one the cloud-masked mean of a period.
* **Pixels without data** are masked in the file and transparent in the plot, as in the true-colour image.

See also
--------

:doc:`true-color`, :doc:`/explanation/colours-and-values`, :doc:`/howto/filter-clouds`

Download
--------

.. autofunction:: cdec.download_false_color_urban

Plot
----

.. autofunction:: cdec.plot_false_color_urban
