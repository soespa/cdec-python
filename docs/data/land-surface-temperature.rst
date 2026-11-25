Land surface temperature (Sentinel-3)
=====================================

How hot is the ground? The land surface temperature (LST) is the temperature of the surface that the satellite
sees: roofs, asphalt, soil and the tops of plants. It is *not* the air temperature that a weather report
gives, and it can be much higher than the air in the sun and lower at night.

.. list-table:: At a glance
   :widths: 28 72
   :stub-columns: 1

   * - Download function
     - :func:`~cdec.download_land_surface_temperature`, short ``download_lst``
   * - Plot function
     - :func:`~cdec.plot_land_surface_temperature`, short ``plot_lst``
   * - Source
     - Sentinel-3 SLSTR Level-2 (collection ``SENTINEL3_SLSTR_L2_LST``), band ``LST``
   * - Pixel size
     - 1 km
   * - Result
     - one band of floating-point numbers in **Kelvin** (subtract 273.15 for degrees Celsius)
   * - Clouds
     - **no cloud masking**: the mean contains every observation that the backend delivers
   * - Period
     - mean of all observations of ``temporal_extent``

Example
-------

.. code-block:: python

    from cdec import download_lst, plot_lst

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen
    temporal_extent = ["2024-06-01", "2024-07-01"]  # June 2024, the end date is not included

    path = download_lst("data/lst_bremen.tif", spatial_extent, temporal_extent)
    plot_lst(path)

.. figure:: /_static/figures/land-surface-temperature.png
   :alt: Land surface temperature of Bremen in June 2024 as large blocks, between 279 and 283 Kelvin, warmer in the city centre.
   :width: 100%

   Bremen, June 2024, in Kelvin. Contains modified Copernicus Sentinel data 2024.

Things to know
--------------

* **A coarse grid.** One pixel is about 1 km wide. The area of the example (12 by 10 km) has only 21 by 11 pixels,
  and the plot shows them as blocks. This data type is meant for large areas and regional patterns, not for
  single streets.
* **Check the numbers.** The example has a mean of 281 K, which is 8 degrees Celsius. That is cold for a June day.
  Because nothing is masked, the mean may include cloudy observations (the cloud top is cold) and night-time
  observations. Do not read the result as the air temperature of a June day.
* **Same range for comparisons.** The plot colours follow the smallest and largest value of the image. To compare two
  maps give both the same ``vmin`` and ``vmax`` in Kelvin (:doc:`/howto/compare-images`).
* The file uses longitude and latitude (EPSG:4326).

See also
--------

:doc:`/explanation/clouds-and-masking`, :doc:`/howto/choose-period`

Download
--------

.. autofunction:: cdec.download_land_surface_temperature

Plot
----

.. autofunction:: cdec.plot_land_surface_temperature
