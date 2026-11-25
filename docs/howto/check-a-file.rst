Check a downloaded file
=======================

After a download the function prints a summary of the file it wrote (unless you pass ``verbose=False``).
To get the same summary for a file you downloaded earlier, use :func:`~cdec.eo.summary.summarize_raster`:

.. code-block:: python

    from cdec.eo.summary import summarize_raster

    print(summarize_raster("data/ndvi_bremen.tif"))

The summary is read from the file itself, so it shows what is really in it: extent, grid and resolution, the
smallest, largest and mean value, and the share of pixels without data. For a file that was not written by
a ``download_*`` function the title, the unit and the lines about period and clouds are simply missing; you can
pass your own with ``description=``, ``unit=`` and ``details=``.

What to look at
---------------

**The no data share.**
  A large share is normal for Sentinel-2 data of a short period (clouds). If it is very large, use a longer
  period or relax the filters (:doc:`filter-clouds`).

**The value range.**
  Compare it with the data type page. NDVI should be between -1 and 1 (:doc:`/data/ndvi`); temperature in Kelvin
  should be around 250 to 320 (:doc:`/data/land-surface-temperature`).

**The grid.**
  The pixel size should be the one of the data type (10 m, 30 m or 1 km), and the extent should be your area.

Look at the file with rasterio
------------------------------

.. code-block:: python

    import rasterio

    with rasterio.open(path) as src:
        print(src.crs, src.res, src.bounds)   # coordinate system, pixel size, extent
        print(src.count, src.dtypes)          # number of bands, data type
        data = src.read(1, masked=True)       # first band; pixels without data are masked

And draw it: :doc:`plot-and-save`.
