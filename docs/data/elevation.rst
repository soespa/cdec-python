Elevation (Copernicus DEM)
==========================

The height of the ground in metres. The Copernicus digital elevation model (DEM) covers the whole world on a
30 m grid. Use it for relief maps, slopes, and to find out which parts of an area lie low.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_digital_elevation_model`, short ``download_dem``
   * - Plot function
     - :func:`~cdec.plot_digital_elevation_model`, short ``plot_dem``
   * - Source
     - Copernicus DEM (collection ``COPERNICUS_30``), band ``DEM``
   * - Pixel size
     - 30 m
   * - Result
     - one band of floating-point numbers in **metres**
   * - Clouds
     - not affected
   * - Period
     - **none needed.** The model is static; ``temporal_extent`` is optional.

Example
-------

.. code-block:: python

    from cdec import download_dem, plot_dem

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen

    path = download_dem("data/dem_bremen.tif", spatial_extent)   # no period needed
    plot_dem(path)

.. figure:: /_static/figures/elevation.png
   :alt: Elevation map of Bremen: low green land along a river, some higher brown spots, heights from about -14 to 43 metres.
   :width: 100%

   Bremen, heights in metres. Copernicus DEM, see :doc:`/reference/data-sources`.

Things to know
--------------

* **No period.** The model was made once (from data of 2010 to 2015). The function uses that period if you do not
  give one, so a recent period would find no data (:doc:`/howto/choose-period`).
* **A surface model.** It shows the top of what the satellite measured, which includes buildings and forest
  canopies, not only the bare ground.
* **Heights** are metres, measured from a model of the sea level (the geoid), so values near the coast can be
  slightly negative. The example area ranges from about -14 to 43 m.
* **The plot** uses terrain colours; they follow the lowest and the highest value of the image. Give two maps the
  same ``vmin`` and ``vmax`` to compare them.
* The file uses longitude and latitude (EPSG:4326).

See also
--------

:doc:`land-cover`, :doc:`/howto/plot-and-save`

Download
--------

.. autofunction:: cdec.download_digital_elevation_model

Plot
----

.. autofunction:: cdec.plot_digital_elevation_model
