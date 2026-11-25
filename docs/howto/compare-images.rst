Compare images
==============

You want to compare two dates, two places, or two data types. These rules keep the comparison fair.

**Compare like with like.**
  Use the same period length (the mean of a week is noisier than the mean of a month), the same
  ``max_cloud_cover`` and the same ``scl_classes``. Changing ``scl_classes`` changes which pixels are kept at all.

**Use the same colours.**
  :doc:`/data/ndvi`, :doc:`/data/evi`, :doc:`/data/ndwi`, :doc:`/data/ndmi`, :doc:`/data/ndsi`,
  :doc:`/data/landsat-ndvi` and :doc:`/data/soil-water-index` are drawn with a fixed value range, so the same colour always means the same value. For
  :doc:`/data/land-surface-temperature` and :doc:`/data/elevation` the colours follow the image. Give
  both images the same range:

  .. code-block:: python

      plot_lst(june_path, vmin=275, vmax=300)
      plot_lst(august_path, vmin=275, vmax=300)

**Colour pictures are comparable by eye.**
  :doc:`/data/true-color` and the false-colour images (:doc:`/data/false-color-urban`,
  :doc:`/data/false-color-infrared`, :doc:`/data/false-color-swir`) use a fixed stretch. No statistics of the image
  are used, so the same reflectance always gets the same colour, whatever else is in the image. This is not
  true for the automatic min/max stretch of many GIS programs. See :doc:`/explanation/colours-and-values`.

**Do not calculate with the pictures.**
  The 8-bit pictures are for the eye: bright values are compressed and saturate. For differences,
  statistics or thresholds use reflectance: :doc:`calculate-with-reflectance`.

**Copernicus Browser.**
  The stretch of the false-colour urban image (0 to 0.4, bands B12/B11/B04) is the one of the Sentinel Hub
  "false colour (urban)" layer; the infrared and SWIR images use the same stretch. That layer shows *one* acquisition date, while this package shows the
  cloud-masked *mean* of a period, and the highlight compression is re-implemented with NumPy (not compared
  pixel by pixel). Expect similar colours, not identical pixels.
