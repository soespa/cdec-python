False-colour infrared image (Sentinel-2)
========================================

The classic picture for vegetation. The near-infrared band is shown as red, the red band as green and the green
band as blue. Healthy plants reflect much near-infrared light, so vegetation looks **red**: the denser and healthier
the plants, the brighter the red. Water absorbs near-infrared light and looks dark blue to black; built-up areas
look grey to blue-grey, and bare soil looks pale brown to grey. Compare it with the
:doc:`true-colour image <true-color>` of the same area to learn the colours.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_false_color_infrared`, short ``download_infrared``
   * - Plot function
     - :func:`~cdec.plot_false_color_infrared`, short ``plot_infrared``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B08 (shown as red), B04 (green) and B03 (blue)
   * - Pixel size
     - 10 m
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

    from cdec import download_infrared, plot_infrared

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_infrared("data/infrared_bremen.tif", spatial_extent, temporal_extent)
    plot_infrared(path)

.. figure:: /_static/figures/false-color-infrared.png
   :alt: Colour-infrared image of Bremen: vegetation bright red, built-up areas grey, rivers and lakes black, white patches without data.
   :width: 100%

   Bremen, June 2024. Red: vegetation, grey: built-up, black: water. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **A fixed stretch.** It is the stretch of the :doc:`false-colour urban image <false-color-urban>`: the
  reflectance 0 to 0.4 becomes 0 to 255, and the brightest values are compressed instead of clipped. No statistics
  of the image are used, so the same reflectance always gets the same colour and images of different dates or
  places can be compared by eye (:doc:`/howto/compare-images`).
* **Do not calculate with the picture.** For differences and thresholds download with ``enhance_contrast=False``
  (:doc:`/howto/calculate-with-reflectance`).
* **Red is not always vegetation.** Dry grass and bare fields reflect less near-infrared light than healthy
  plants and look pink or pale. For a number instead of a colour use the :doc:`ndvi`.
* **Pixels without data** are masked in the file and transparent in the plot, as in the other pictures.

See also
--------

:doc:`true-color`, :doc:`false-color-urban`, :doc:`false-color-swir`, :doc:`/explanation/colours-and-values`,
:doc:`/howto/filter-clouds`

Download
--------

.. autofunction:: cdec.download_false_color_infrared

Plot
----

.. autofunction:: cdec.plot_false_color_infrared
