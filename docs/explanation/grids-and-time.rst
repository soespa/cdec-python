Grids and time
==============

Where is a pixel?
-----------------

A GeoTIFF is a grid of pixels, and the file stores how this grid sits on the Earth: its **coordinate system** and
its **pixel size**.

* The Sentinel-2 downloads come in a *metric* system, UTM. The coordinates are metres (in the example EPSG:32632
  for Bremen) and the pixels are squares of 10 m. The plot labels the axes "Easting (m)" and "Northing (m)".
* The other data types come in *longitude and latitude* (EPSG:4326). The pixel size is then given in degrees. A degree
  of longitude is shorter than a degree of latitude (about 0.6 times as long at the latitude of Bremen), so the plot
  functions correct the shape of the map; without that it would look stretched from east to west.

How to look at the grid of a file is shown in :doc:`/howto/check-a-file`. The edges of the file can differ a little from your box, because the data has its own grid.

The pixel size is not the same as the *detail* of the data. The 10 m grid of Sentinel-2 holds bands of 10 m and 20 m
detail; the scene classification, for example, has 20 m detail only.

When is it?
-----------

The period is ``[start, end]`` and the end date is not included, as in many programming languages: ``["2024-06-01",
"2024-07-01"]`` is all of June. The result is the mean of the period and has no time dimension
(:doc:`how-it-works`).

The data types differ in how often they observe: Sentinel-2 every few days, Sentinel-3 temperature and the soil
water index about daily, the Landsat mosaics every two months. A period shorter than that finds nothing or very little;
static data (elevation, land cover) has no time at all (:doc:`/howto/choose-period`).
