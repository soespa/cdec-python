Control the output file
=======================

All download functions share these keyword options. They must be written with their names
(``create_cog=False``), so they cannot be mixed up with the options that are worth changing.

**File name and folder.**
  ``file_path`` is a string or a :class:`~pathlib.Path`. Missing folders are created. The function returns the
  absolute path of the finished file, so ``plot_ndvi(download_ndvi(...))`` works.

**Plain GeoTIFF instead of Cloud Optimized GeoTIFF.**
  By default the result is a Cloud Optimized GeoTIFF (COG): a normal GeoTIFF with a layout that allows fast
  partial reads, and overview levels for fast zooming. Every GIS and ``rasterio`` can read it. If you want a
  plain GeoTIFF, pass ``create_cog=False``.

**Overview levels.**
  ``overview_resampling`` sets how the smaller overview levels of a COG are calculated. The default ``"average"``
  suits measurements. The land cover download uses ``"nearest"``, because averaging class numbers makes no sense.

**No printed summary.**
  ``verbose=False`` switches the summary off.

**A failed download does no harm.**
  The data is first written to a hidden temporary folder next to the target file. Only when everything succeeded
  (download, colour enhancement, COG conversion) it replaces ``file_path``. A failed download never leaves a
  half-written file and never overwrites an existing good file. A successful download replaces an existing file
  of the same name.
