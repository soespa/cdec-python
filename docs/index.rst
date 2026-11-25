CDEC
====

CDEC downloads satellite data of a study area from the
`Copernicus Data Space <https://dataspace.copernicus.eu/>`_ and draws it. One function call gives
you one GeoTIFF file that you open with ``rasterio`` or QGIS. The package is made for teaching:
one function per data type, short readable code, and defaults that work.

.. code-block:: python

    from cdec import download_true_color_image, plot_true_color_image

    spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}
    temporal_extent = ["2024-06-01", "2024-07-01"]  # the end date is not included: all of June

    path = download_true_color_image("data/tci_bremen.tif", spatial_extent, temporal_extent)
    plot_true_color_image(path)

The documentation has five parts. Start with the tutorial; come back to the other parts when you
have a question.

.. list-table::
   :widths: 25 75

   * - :doc:`Get started <tutorial/get-started>`
     - **Tutorial.** Your first download, step by step: install, download, look at the result.
   * - :doc:`How-to guides <howto/index>`
     - **Recipes** for a goal: choose the area and period, filter clouds, compare images, plot
       several maps, check a file.
   * - :doc:`Data types <data/index>`
     - **One page for each kind of data:** what it shows, how to download and plot it, and what
       to watch out for.
   * - :doc:`Explanation <explanation/index>`
     - **Background:** how the package works, why clouds need care, what the colours mean.
   * - :doc:`Reference <reference/index>`
     - **Look-up:** all functions, argument types and classes.

.. toctree::
   :hidden:
   :caption: Learn

   tutorial/get-started

.. toctree::
   :hidden:
   :caption: Do

   howto/index

.. toctree::
   :hidden:
   :caption: Data types

   data/index

.. toctree::
   :hidden:
   :caption: Understand

   explanation/index

.. toctree::
   :hidden:
   :caption: Look up

   reference/index

.. toctree::
   :hidden:
   :caption: Project

   contributing
