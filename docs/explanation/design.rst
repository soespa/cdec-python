Why the package looks like this
===============================

The package is written for students who read the code. These decisions follow from that.

**One function per data type.**
  ``download_ndvi``, ``download_tci`` ... each has its own module and reads from top to bottom. A little repetition is
  accepted so that you can read one module and understand it, instead of following a framework.

**Long names and short aliases.**
  ``download_true_color_image`` says what it does, ``download_tci`` is quick to type. They are the same function, and the
  documentation of the long name shows the alias.

**The options worth changing come first.**
  ``max_cloud_cover`` and ``scl_classes`` follow directly after the three standard arguments. Technical options
  (``create_cog``, ``overview_resampling``) must be written with their names, so they cannot be
  confused with the others.

**Functions return a file path.**
  The result is a GeoTIFF, not a Python object. You open it with ``rasterio`` and can use it in QGIS and every
  other program, and nothing in the package stands between you and your data.

**One plot function per data type.**
  A file does not say what its numbers mean. NDVI, EVI, temperature and elevation are all one band of floating-point
  numbers; even NDVI and EVI have the same value range. The colour map and the value range are part of the
  interpretation, so each plot function writes these decisions down (``src/cdec/plot/products.py``: each function is a
  single short call). :func:`~cdec.plot_raster` is the one that only looks at the *format*, for data of your own.

**The docstring says what is in the file.**
  Nothing is printed behind your back. ``help(download_ndvi)`` describes the file that the function writes: the bands,
  the data type, the unit, the no-data value and the pixel size. To see what is really in a file, open it with
  ``rasterio`` (:doc:`/howto/check-a-file`).
