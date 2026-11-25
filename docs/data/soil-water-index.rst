Soil water index
================

How wet is the soil? The Soil Water Index (SWI) of the Copernicus Land Monitoring Service describes the soil
moisture in percent: 0 is dry, 100 is saturated. It is calculated from radar data and available for Europe on
a 1 km grid, every day.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_soil_water_index`, short ``download_swi``
   * - Plot function
     - :func:`~cdec.plot_soil_water_index`, short ``plot_swi``
   * - Source
     - Copernicus Land Monitoring Service (collection ``CLMS_SWI_EUROPE_1KM_DAILY_V2``, daily, Europe)
   * - Pixel size
     - 1 km
   * - Result
     - one band of floating-point numbers in percent, 0 ... 100
   * - Clouds
     - not affected (it is a modelled product)
   * - Period
     - mean of all days of ``temporal_extent``. **Version 2 starts on 2025-07-13.**

Example
-------

.. code-block:: python

    from cdec import download_swi, plot_swi

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2025-08-01", "2025-09-01"]  # August 2025, the end date is not included

    path = download_swi("data/swi_bremen.tif", spatial_extent, temporal_extent, depth=20)
    plot_swi(path)

.. figure:: /_static/figures/soil-water-index.png
   :alt: Soil water index of Bremen in August 2025 as large blocks between 17 and 34 percent, some blocks empty.
   :width: 100%

   Bremen, August 2025, ``depth=20``. White: no data. Generated using European Union's Copernicus Land Monitoring Service information.

Things to know
--------------

* **Check the dates first.** CLMS publishes version 2 of the 1 km SWI from 2025-07-13 onwards; version 1 covers 2015
  up to 2025-07-12. An earlier period (such as June 2024) may find no data in this collection. The Copernicus Data
  Space also labels its CLMS collections as experimental.
* **The depth.** The ``depth`` argument is the characteristic time length *T* of the index in days: 2, 5, 10, 15, 20, 40,
  60 or 100. A small *T* follows recent rain and describes the topsoil; a large *T* is slow and describes deeper
  layers. The default is 2.
* **Empty blocks.** In the example about a third of the pixels have no value.
* **The plot** uses white-to-blue colours and a fixed range of 0 to 100, so the same colour always means the same
  moisture.
* The file uses longitude and latitude (EPSG:4326).

See also
--------

:doc:`/howto/choose-period`

Download
--------

.. autofunction:: cdec.download_soil_water_index

Plot
----

.. autofunction:: cdec.plot_soil_water_index
