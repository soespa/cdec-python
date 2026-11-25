Plot functions
==============

The plot function of each data type is documented on the page of the data type (:doc:`functions`). This
page describes what they share, and :func:`~cdec.plot_raster`, which draws any GeoTIFF.

Shared options
--------------

Every plot function takes the file path and keyword options. It draws into a matplotlib ``Axes`` and returns it.

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Option
     - Meaning
     - Available in
   * - ``ax``
     - the ``Axes`` to draw into; without it the function creates a figure
     - all
   * - ``show``
     - ``True``: call ``plt.show()`` afterwards. Default: show only if the function created the figure
     - all
   * - ``title``
     - the title; ``None`` (default) gives the default title of the data type, ``""`` no title
     - all
   * - ``cmap``
     - the matplotlib colour map
     - indices, temperature, soil water index, elevation
   * - ``vmin``, ``vmax``
     - the value range of the colours; the defaults are fixed for the indices (-1 ... 1) and the soil water index
       (0 ... 100) and follow the image for temperature and elevation
     - the same
   * - ``colorbar``
     - ``False`` draws no colour bar
     - the same

What is drawn
-------------

* Pixels without data are transparent.
* The axes show the coordinates of the file: degrees or metres. For longitude and latitude the map is corrected
  for the shorter degrees of longitude (:doc:`/explanation/grids-and-time`).
* A file with the wrong number of bands (for example a true-colour file passed to ``plot_ndvi``) raises a
  ``ValueError`` that names the file and points to ``plot_raster``.

Any GeoTIFF
-----------

.. autofunction:: cdec.plot_raster
