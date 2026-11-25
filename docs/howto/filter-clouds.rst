Filter clouds
=============

Nine of the Sentinel-2 data types (:doc:`/data/ndvi`, :doc:`/data/evi`, :doc:`/data/ndwi`, :doc:`/data/ndmi`,
:doc:`/data/ndsi`, :doc:`/data/true-color`, :doc:`/data/false-color-urban`, :doc:`/data/false-color-infrared`
and :doc:`/data/false-color-swir`) have two filters. They come right after the three standard arguments,
so they can be given with or without their names:

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Option
     - What it removes
     - Default
   * - ``max_cloud_cover``
     - whole **scenes**: a scene with more than this percent cloud cover is not used at all
     - ``20``
   * - ``scl_classes``
     - single **pixels**: only pixels of these Scene Classification Layer (SCL) classes are **kept**
     - ``(4, 5)`` for NDVI, EVI and NDMI; ``(4, 5, 6)`` for NDWI, true colour and the false-colour images;
       ``(4, 5, 6, 11)`` for NDSI

.. code-block:: python

    import cdec

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    # with the names of the filters, or without them (max_cloud_cover first, then scl_classes)
    cdec.download_ndvi("data/ndvi_clear.tif", spatial_extent, temporal_extent, max_cloud_cover=10, scl_classes=(4, 5, 6))
    cdec.download_ndvi("data/ndvi_clear_2.tif", spatial_extent, temporal_extent, 10, cdec.SCL_LAND_AND_WATER)  # the same
    cdec.download_ndvi("data/ndvi_no_mask.tif", spatial_extent, temporal_extent, scl_classes=None)  # no pixel masking

Fill white holes in the map
---------------------------

A pixel is empty only if *every* observation of the period was removed. Two things help:

* a **longer period**, so that more observations are available;
* a **higher** ``max_cloud_cover`` (for example 50), so that more scenes are used. The pixel mask
  still removes the clouds of those scenes.

Keep water
----------

NDVI, EVI and NDMI drop water by default (class 6 is not in ``(4, 5)``), so rivers and lakes are empty. To keep
them use ``scl_classes=cdec.SCL_LAND_AND_WATER``.

Keep snow
---------

Snow and ice are class 11. Only :doc:`/data/ndsi` keeps them by default. For the other data types add the class:
``scl_classes=cdec.SCL_LAND_WATER_AND_SNOW``. The scene classification sometimes labels snow as cloud, so a snowy area
can stay empty; ``scl_classes=None`` shows what is there.

See why pixels are missing
--------------------------

If a pixel is empty, the :doc:`/data/scene-classification` tells you which class it has. That is the class to add to
``scl_classes``, or the clouds you need a longer period for.

Choose the classes
------------------

``scl_classes`` is the list of the classes you want to **keep**. Look at them with:

.. code-block:: python

    cdec.show_scl_classes()          # all 12 classes with a hint for each one
    cdec.show_scl_classes((4, 5))    # the same table, your selection marked with X

The table is also in the reference: :doc:`/reference/scl`. An invalid class number is reported before the
login, not after.

The other data types
--------------------

:doc:`/data/landsat-ndvi` is already free of clouds. :doc:`/data/land-surface-temperature` has no cloud
filter at all; see its page. The elevation model, the land cover map and the soil water index have no
cloud filter either.
