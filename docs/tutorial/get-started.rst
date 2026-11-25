Get started
===========

In this tutorial you download the vegetation of a small area, look at it, and calculate with it.
You need Python 3.10 or newer and an internet connection. The data is prepared on the servers of the
Copernicus Data Space, so a download takes a while.

The area is the city of Bremen in northern Germany, the period is June 2024. Use your own area
later (see :doc:`/howto/choose-area`).

Step 1: Install the package
---------------------------

.. code-block:: console

    pip install cdec

Step 2: Get an account
----------------------

All data comes from the `Copernicus Data Space <https://dataspace.copernicus.eu/>`_. Register
there for free. You need the account for the first download only: the package opens a login
(a code that you confirm in your browser), stores a token, and later downloads log in silently.

Step 3: Say where and when
--------------------------

Start a Python script or a notebook and describe the area and the period:

.. code-block:: python

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}
    temporal_extent = ["2024-06-01", "2024-07-01"]

The area is a box in degrees of longitude and latitude. The period is a start and an end date.
The end date is *not* included, so this is all of June.

Step 4: Download the NDVI
-------------------------

The NDVI says how green the plants are. Download it:

.. code-block:: python

    from cdec import download_ndvi

    path = download_ndvi("data/ndvi_bremen.tif", spatial_extent, temporal_extent)

The first call opens the login. Then the download runs. The function creates the folder ``data``
if it does not exist, writes the file, and returns its path. It also prints what is in the file
(this is the output of a real download):

.. code-block:: text

    NDVI from Sentinel-2 L2A (mean of the period)
      file      /home/me/data/ndvi_bremen.tif (3.9 MB)
      extent    west 8.7211, south 53.0247, east 8.9047, north 53.1153 (WGS 84), about 12.3 x 10.1 km
      grid      1228 x 1005 pixels of 10 m (EPSG:32632)
      values    -0.6602 to 1.264, mean 0.5496
      unit      no unit (index from -1 to 1)
      no data   26.5 % of the pixels
      period    2024-06-01 to 2024-07-01 (end date not included)
      clouds    scenes with more than 20 % cloud cover are not used
      SCL kept  4 Vegetation, 5 Not vegetated

Read it from top to bottom: a map of 1228 by 1005 pixels, each pixel 10 m wide; the NDVI has a
mean of 0.55; and a quarter of the pixels have no data. Where this comes from is explained in
:doc:`/explanation/clouds-and-masking`.

Step 5: Look at it
------------------

.. code-block:: python

    from cdec import plot_ndvi

    plot_ndvi(path)

A map opens, with a colour bar from red (-1) over yellow to green (1). White areas have no data.

.. image:: /_static/figures/ndvi.png
   :alt: Map of the NDVI of Bremen in June 2024: green fields and parks, lighter yellow-green built-up areas, white patches without data.
   :width: 100%

Step 6: Calculate with it
-------------------------

The file is an ordinary GeoTIFF. Open it with ``rasterio``:

.. code-block:: python

    import rasterio

    with rasterio.open(path) as src:
        ndvi = src.read(1, masked=True)  # masked: pixels without data are left out

    print(f"Mean NDVI of the area: {ndvi.mean():.2f}")
    print(f"Share of pixels with NDVI above 0.6: {(ndvi > 0.6).sum() / ndvi.count():.0%}")

``ndvi`` is an array with one number per pixel. Everything you can do with an array, you can do with it.

Step 7: Add a second picture
----------------------------

Download the true-colour image of the same area and period, and draw both next to each other:

.. code-block:: python

    import matplotlib.pyplot as plt
    from cdec import download_true_color_image, plot_true_color_image, plot_ndvi

    tci_path = download_true_color_image("data/tci_bremen.tif", spatial_extent, temporal_extent)

    fig, (left, right) = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
    plot_true_color_image(tci_path, ax=left)
    plot_ndvi(path, ax=right)
    plt.show()

Passing ``ax=`` tells the plot function where to draw. You decide when ``plt.show()`` opens the figure.

What you have learned
---------------------

* Every data type has a ``download_...`` function and a ``plot_...`` function with the same name.
* A download function takes a file name, an area and a period, and returns the file path.
* The file is a GeoTIFF; you read it with ``rasterio`` and draw it with the ``plot_...`` function.

Where to go next
----------------

* Other kinds of data: :doc:`/data/index`.
* Your own area and period: :doc:`/howto/choose-area`, :doc:`/howto/choose-period`.
* Clouds and holes in the map: :doc:`/howto/filter-clouds`.
