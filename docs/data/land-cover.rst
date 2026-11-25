Land cover (ESA WorldCover)
===========================

What covers the ground? The ESA WorldCover map for 2021 sorts every 10 m pixel into one of eleven classes: tree cover,
grassland, cropland, built-up, water and so on. The numbers in the file are **class numbers**, not measurements.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_land_cover` (no short alias)
   * - Plot function
     - :func:`~cdec.plot_land_cover` (no short alias)
   * - Source
     - ESA WorldCover 2021, version 2 (collection ``ESA_WORLDCOVER_10M_2021_V2``), band ``MAP``
   * - Pixel size
     - 10 m
   * - Result
     - one band of 8-bit integers: the class numbers 10, 20, ... 100; 0 is no data. A colour table is stored in the file.
   * - Clouds
     - not affected
   * - Period
     - **none needed.** The map is for the year 2021; ``temporal_extent`` is optional.

Example
-------

.. code-block:: python

    from cdec import download_land_cover, plot_land_cover

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen

    path = download_land_cover("data/land_cover_bremen.tif", spatial_extent)   # no period needed
    plot_land_cover(path)

.. figure:: /_static/figures/land-cover.png
   :alt: Land cover of Bremen: red built-up areas, dark green tree cover, yellow grassland, blue water, with a legend of the classes.
   :width: 100%

   Bremen, 2021. The legend lists the classes that occur in the picture.
   © ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium.

The classes
-----------

.. py:data:: cdec.WORLDCOVER_CLASSES
   :type: dict[int, str]

   The classes of the ESA WorldCover map: class number to name.

.. py:data:: cdec.WORLDCOVER_COLORS
   :type: dict[int, str]

   The official WorldCover colour of every class number, as hex code. This is the colour table that
   :func:`~cdec.download_land_cover` stores in the GeoTIFF and :func:`~cdec.plot_land_cover` uses.

   .. class-table:: cdec.WORLDCOVER_CLASSES
      :colors: cdec.WORLDCOVER_COLORS

Things to know
--------------

* **Count, do not average.** The numbers are labels. The mean of 10 (tree cover) and 50 (built-up) says nothing. Count
  pixels per class instead:

  .. code-block:: python

      import numpy as np
      import rasterio

      with rasterio.open(path) as src:
          classes, counts = np.unique(src.read(1), return_counts=True)

* **Nearest neighbour.** The overview levels of the file are made with ``overview_resampling="nearest"``, so no
  invented in-between classes appear when you zoom out.
* **The colours** are stored in the file as a colour table, so programs that read colour tables, such as QGIS, can
  show the official colours without any setup.
* The map is for the year 2021. It is a classification made by an algorithm: it is not perfect, and fine
  structures can be wrong.
* The file uses longitude and latitude (EPSG:4326).

See also
--------

:doc:`elevation`, :doc:`/reference/data-sources`

Download
--------

.. autofunction:: cdec.download_land_cover

Plot
----

.. autofunction:: cdec.plot_land_cover
