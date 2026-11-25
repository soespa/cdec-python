Scene classification (Sentinel-2)
=================================

A map of what every pixel probably shows: vegetation, bare ground, water, cloud, cloud shadow, snow and so on. It is
the *Scene Classification Layer* (SCL) that the other Sentinel-2 downloads use to mask clouds
(:doc:`/reference/scl`). Download it to see **why** pixels are missing in an NDVI or a true-colour image, and to
choose ``scl_classes`` for them.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_scene_classification_map`, short ``download_scl``
   * - Plot function
     - :func:`~cdec.plot_scene_classification_map`, short ``plot_scl``
   * - Source
     - Sentinel-2 Level-2A (collection ``SENTINEL2_L2A``), band SCL
   * - Pixel size
     - 20 m
   * - Result
     - one band of class numbers (0 ... 11) with the colours of the classes attached to the file; 0 means no data
   * - Clouds
     - **all scenes are used** (``max_cloud_cover=100``), because the clouds are what the map should show; no pixel
       is masked
   * - Period
     - the **most recent** observation of every pixel in ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_scl, plot_scl

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_scl("data/scl_bremen.tif", spatial_extent, temporal_extent)
    plot_scl(path)

.. figure:: /_static/figures/scene-classification.png
   :alt: Scene classification of Bremen: vegetation green, not vegetated yellow, water blue, cloud shadows brown, clouds white and grey.
   :width: 100%

   Bremen, most recent observation of every pixel in June 2024. Contains modified Copernicus Sentinel data 2024.

The legend of the plot lists only the classes that occur in the picture. ``cdec.show_scl_classes()`` prints all 12
classes with a hint for each one.

Things to know
--------------

* **No average.** Class numbers have no mean: the average of "vegetation" (4) and "cloud" (9) is not a class. Each
  pixel keeps the class of its most recent observation in the period.
* **One date per pixel, not one date for the picture.** Neighbouring pixels can come from different days. For the
  classification of one day use a period of one day.
* **Use it to choose** ``scl_classes``. If a pixel is missing in your NDVI, look up its class here. A river that is
  missing is class 6 (water), which NDVI drops by default; a patch that is missing in summer is probably cloud
  or cloud shadow (:doc:`/howto/filter-clouds`).
* **It is a guess of a computer program.** The classification is not perfect: thin clouds, haze and cloud edges are
  sometimes labelled as land, and snow is sometimes labelled as cloud (:doc:`/reference/scl`).
* **The colours** are the ones of ``cdec.SCL_COLORS``. The plot takes them from there, not from the colour table
  inside the file, so every file looks the same.
* **Class 0** (no data) is transparent in the plot, as are pixels without any observation.

See also
--------

:doc:`/reference/scl`, :doc:`/howto/filter-clouds`, :doc:`/explanation/clouds-and-masking`, :doc:`land-cover`

Download
--------

.. autofunction:: cdec.download_scene_classification_map

Plot
----

.. autofunction:: cdec.plot_scene_classification_map
