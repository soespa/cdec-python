True-colour image (Sentinel-2)
==============================

A picture of the area as the eye would see it: red, green and blue light. The image is the *mean* of all
cloud-free observations of the period, not a photo of one day, so it looks calmer than a single satellite
image, and clouds are replaced by the data of other days.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_true_color_image`, short ``download_tci``
   * - Plot function
     - :func:`~cdec.plot_true_color_image`, short ``plot_tci``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), bands B04 (red), B03 (green) and B02 (blue)
   * - Pixel size
     - 10 m
   * - Result
     - by default an 8-bit colour picture (three bands, 0 ... 255); with ``enhance_color=False`` three bands of
       reflectance (floating point, about 0 ... 1)
   * - Clouds
     - scenes above ``max_cloud_cover`` (20 %) are not used; pixels are masked with ``scl_classes``
       (default: vegetation, not vegetated and water)
   * - Period
     - mean of all observations of ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_tci, plot_tci

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_tci("data/tci_bremen.tif", spatial_extent, temporal_extent)
    plot_tci(path)

.. figure:: /_static/figures/true-color.png
   :alt: True-colour image of Bremen in June 2024: green fields, grey roads and buildings, a dark river, white patches without data.
   :width: 100%

   Bremen, June 2024. White: no data. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **A picture, not a measurement.** The default file holds colours for the eye. The reflectance is recalculated
  into 0 ... 255 with a fixed brightness, saturation and gamma curve. For calculations download with
  ``enhance_color=False`` (:doc:`/howto/calculate-with-reflectance`).
* **Comparable colours.** The curve does not look at the image, so the same reflectance always gets the same
  colour, in every image (:doc:`/explanation/colours-and-values`).
* **Pixels without data** are black in the numbers, but the file stores a mask. GIS programs and the plot function
  show them as transparent.
* **Water is kept** by default (``scl_classes=(4, 5, 6)``), clouds and shadows are removed. Pixels that stay empty
  are the ones where every observation of the period was removed.
* The reflectance version can contain a few values above 1 (the example up to 1.8): bright clouds or snow that
  were not masked.
* Plot a reflectance file with :func:`~cdec.plot_true_color_image` as well: it enhances the colours *for the
  picture only*.

See also
--------

:doc:`false-color-urban`, :doc:`/howto/compare-images`, :doc:`/howto/filter-clouds`

Download
--------

.. autofunction:: cdec.download_true_color_image

Plot
----

.. autofunction:: cdec.plot_true_color_image
