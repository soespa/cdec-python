Check a downloaded file
=======================

A download function returns the path of the file it wrote. What the file *should* contain is written in the
documentation of the function: ``help(download_ndvi)``, or the page of the data type (:doc:`/data/index`).
To see what is *really* in a file, open it with ``rasterio``:

.. code-block:: python

    import rasterio

    with rasterio.open("data/ndvi_bremen.tif") as src:
        print(src.crs, src.res, src.bounds)   # coordinate system, pixel size, extent
        print(src.count, src.dtypes)          # number of bands, data type
        ndvi = src.read(1, masked=True)       # first band; pixels without data are masked

    print(f"values from {ndvi.min():.2f} to {ndvi.max():.2f}, mean {ndvi.mean():.2f}")
    print(f"no data: {1 - ndvi.count() / ndvi.size:.1%} of the pixels")

For the NDVI of Bremen in June 2024 this prints something like:

.. code-block:: text

    EPSG:32632 (10.0, 10.0) BoundingBox(left=481330.0, bottom=5875050.0, right=493610.0, top=5885100.0)
    1 ('float32',)
    values from -0.66 to 1.26, mean 0.55
    no data: 26.5% of the pixels

What to look at
---------------

**The no data share.**
  A large share is normal for Sentinel-2 data of a short period (clouds). If it is very large, use a longer
  period or relax the filters (:doc:`filter-clouds`).

**The value range.**
  Compare it with the data type page. NDVI should be between -1 and 1, apart from a few dark pixels
  (:doc:`/data/ndvi`); temperature in Kelvin should be around 250 to 320 (:doc:`/data/land-surface-temperature`).

**The grid.**
  The pixel size should be the one of the data type (10 m, 30 m or 1 km), and the extent should be your area.
  The edges can differ a little from your box, because the data has its own grid (:doc:`/explanation/grids-and-time`).

And draw it: :doc:`plot-and-save`.
