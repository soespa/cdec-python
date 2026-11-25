Calculate with reflectance
==========================

The true-colour download and the false-colour downloads (urban, infrared, SWIR) are *pictures* by default: 8-bit numbers from 0 to 255
that look good on screen. To calculate with them (differences, thresholds, statistics) you want the
measurement behind the picture: the **reflectance**, a number between 0 (black) and about 1 (white).

Download the image without the enhancement:

.. code-block:: python

    from cdec import download_true_color_image

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}  # Bremen

    june = download_true_color_image(
        "data/tci_june.tif", spatial_extent, ["2024-06-01", "2024-07-01"], enhance_color=False
    )
    august = download_true_color_image(
        "data/tci_august.tif", spatial_extent, ["2024-08-01", "2024-09-01"], enhance_color=False
    )

(for the false-colour composites the option is called ``enhance_contrast=False``). The files now have three
floating-point bands, in the order red, green, blue. Read them with ``rasterio``:

.. code-block:: python

    import rasterio

    with rasterio.open(june) as a, rasterio.open(august) as b:
        change_in_red = b.read(1, masked=True) - a.read(1, masked=True)

Both files have the same area, so they have the same grid and the arrays fit together.

Good to know
------------

* Reflectance is not strictly limited to 0 ... 1. A few pixels are slightly below 0 or above 1 (bright clouds
  or snow that were not masked).
* You can still look at such a file: :func:`~cdec.plot_true_color_image` applies the colour enhancement
  **for the picture only** and leaves the file unchanged (:doc:`/explanation/colours-and-values`).
* The index data types (NDVI, EVI, NDWI, NDMI, NDSI) are always numbers; they have no picture version.
