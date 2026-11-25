False-colour SWIR image (Sentinel-2)
====================================

A picture made of invisible light that separates snow, clouds, water and vegetation. A short-wave infrared band is
shown as red, a near-infrared band as green and the red band as blue. Vegetation looks **green**, bare soil and
built-up areas look brown to orange, and water looks black. Snow and ice absorb short-wave infrared light and look
cyan (light blue), while clouds stay white. Compare it with the :doc:`true-colour image <true-color>` of the same
area to learn the colours.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_false_color_swir`, short ``download_swir``
   * - Plot function
     - :func:`~cdec.plot_false_color_swir`, short ``plot_swir``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B12 (shown as red), B8A (green) and B04 (blue)
   * - Pixel size
     - 10 m (B12 and B8A have 20 m detail)
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

    from cdec import download_swir, plot_swir

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_swir("data/swir_bremen.tif", spatial_extent, temporal_extent)
    plot_swir(path)

.. figure:: /_static/figures/false-color-swir.png
   :alt: Short-wave infrared image of Bremen: vegetation bright green, built-up areas brown and grey, rivers and lakes black, white patches without data.
   :width: 100%

   Bremen, June 2024. Green: vegetation, brown and grey: built-up, black: water. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **Clouds and snow are removed by default**, so you do not see the colours that tell them apart. To see snow
  use ``scl_classes=(4, 5, 6, 11)``; to see clouds next to it use ``scl_classes=None``. Choose a short period, so
  that the picture is not a mean of days with and without snow (:doc:`/howto/filter-clouds`, :doc:`ndsi`).
* **A fixed stretch.** It is the stretch of the :doc:`false-colour urban image <false-color-urban>`: the
  reflectance 0 to 0.4 becomes 0 to 255, and the brightest values are compressed instead of clipped. The same
  reflectance always gets the same colour, so images can be compared by eye (:doc:`/howto/compare-images`).
* **Do not calculate with the picture.** For differences and thresholds download with ``enhance_contrast=False``
  (:doc:`/howto/calculate-with-reflectance`).
* **Similar to the urban image.** Both use short-wave infrared bands. The urban image shows vegetation in green
  and the city in grey; this one has brown built-up areas and separates snow from cloud.
* **Pixels without data** are masked in the file and transparent in the plot, as in the other pictures.

See also
--------

:doc:`true-color`, :doc:`false-color-urban`, :doc:`false-color-infrared`, :doc:`ndsi`,
:doc:`/explanation/colours-and-values`

Download
--------

.. autofunction:: cdec.download_false_color_swir

Plot
----

.. autofunction:: cdec.plot_false_color_swir
