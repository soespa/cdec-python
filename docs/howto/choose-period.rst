Choose the period
=================

The third argument, ``temporal_extent``, is the start and the end of the period:

.. code-block:: python

    temporal_extent = ["2024-06-01", "2024-07-01"]

**The end date is not included.** The example is all of June. For a single day write the day and the
next day: ``["2024-06-15", "2024-06-16"]``.

**The result is one image for the whole period.** The download functions average all observations of the
period (see :doc:`/explanation/how-it-works`). A longer period gives a calmer, more complete image;
a shorter period shows the state at that time.

Which period?
-------------

* **Sentinel-2 images and indices:** there is a new observation every few days, but clouds hide many of
  them. A month is a good start. If the map has white holes, use a longer period or a higher
  ``max_cloud_cover`` (:doc:`filter-clouds`).
* **Seasons:** compare the same period of different years (June 2023 and June 2024), not June and December.
* **Landsat NDVI:** the mosaics cover two months each and run from 1997 to 2025
  (:doc:`/data/landsat-ndvi`).
* **Soil water index:** the collection (version 2 of the data) starts on 2025-07-12 at 12:00 UTC. Earlier periods may find no data
  (:doc:`/data/soil-water-index`).

Data that does not change
-------------------------

The elevation model and the land cover map are *static*: they were made once. ``download_dem`` and
``download_land_cover`` do not need a ``temporal_extent``; they use the period of their acquisition. If you
give them a recent period such as June 2024, they find no data.
