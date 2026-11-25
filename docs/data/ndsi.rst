NDSI (Sentinel-2)
=================

The **Normalized Difference Snow Index** shows snow and ice. Snow reflects a lot of green light and absorbs
short-wave infrared light, so ``NDSI = (green - SWIR) / (green + SWIR)`` is high for snow and ice and low for most
other surfaces. A value above about 0.4 is a common first guess for snow. The result is one number per pixel, between
-1 and 1.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_normalized_difference_snow_index`, short ``download_ndsi``
   * - Plot function
     - :func:`~cdec.plot_normalized_difference_snow_index`, short ``plot_ndsi``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B03 (green) and B11 (short-wave infrared)
   * - Pixel size
     - 10 m (B11 has 20 m detail)
   * - Result
     - one band of floating-point numbers, no unit, about -1 ... 1
   * - Clouds
     - scenes above ``max_cloud_cover`` (20 %) are not used; pixels are masked with ``scl_classes``
       (default: vegetation, not vegetated, water and snow or ice)
   * - Period
     - mean of all observations of ``temporal_extent``

Example
-------

There is no snow in Bremen in June, so this example looks at the Zugspitze in the Bavarian Alps in winter:

.. code-block:: python

    from cdec import download_ndsi, plot_ndsi

    spatial_extent = {"west": 10.95, "south": 47.38, "east": 11.05, "north": 47.46}  # the Zugspitze
    temporal_extent = ["2024-02-01", "2024-03-01"]  # February 2024, the end date is not included

    path = download_ndsi("data/ndsi_zugspitze.tif", spatial_extent, temporal_extent, max_cloud_cover=50)
    plot_ndsi(path)

.. figure:: /_static/figures/ndsi.png
   :alt: NDSI of the Zugspitze in February 2024: snow-covered slopes in dark blue, snow-free ground in pale blue, white patches without data.
   :width: 100%

   Zugspitze, February 2024. Dark blue: snow or ice. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **Snow or cloud?** Clouds and snow look alike. The scene classification can label snow as cloud and cloud as
  snow, and it removes everything it calls cloud. If a snowy area stays empty, download once with
  ``scl_classes=None`` and compare the result with the :doc:`scene-classification`.
* **Choose a short period.** The mean of a long period mixes days with and without snow, and the result shows
  neither. For snow use a few days to a few weeks, and a higher ``max_cloud_cover`` in the mountains, where the
  weather changes quickly (:doc:`/howto/choose-period`).
* **Snow is kept by default.** The default ``scl_classes`` is ``(4, 5, 6, 11)``: the classes of
  :doc:`ndwi` and the class *snow or ice*. NDVI and EVI drop snow (:doc:`ndvi`).
* **Not every high value is snow.** Thin clouds and some bright surfaces can also reach high values. Look at
  :doc:`true-color` or :doc:`false-color-swir` of the same area to check.
* **Values outside -1 ... 1.** A few pixels can lie outside, in the very dark ones (shadows), where one of the
  reflectances is below zero and the sum in the denominator is close to zero. The example file ranges from -6 to 10.3,
  but only 21 of its about 438,000 pixels are outside -1 ... 1. Treat them as noise or clip them with
  ``numpy.clip(ndsi, -1, 1)``.
* **The index is calculated from the mean reflectance** of the period, not as the mean of the index of every date.
* **The plot** uses white-blue colours and a fixed range of -1 to 1: the darker the blue, the more likely snow.

See also
--------

:doc:`false-color-swir`, :doc:`scene-classification`, :doc:`/howto/filter-clouds`, :doc:`/howto/choose-period`

Download
--------

.. autofunction:: cdec.download_normalized_difference_snow_index

Plot
----

.. autofunction:: cdec.plot_normalized_difference_snow_index
