Plot and save maps
==================

Every download function has a plot function with the matching name: ``plot_ndvi`` for ``download_ndvi``,
``plot_tci`` for ``download_tci``, and so on. The shared options are described in
:doc:`/reference/plotting`; the data type pages show what each map looks like.

Draw one map
------------

.. code-block:: python

    from cdec import plot_ndvi

    plot_ndvi(path)

A window opens (in a Jupyter notebook the picture appears below the cell).

Draw several maps next to each other
------------------------------------

Every plot function draws into a matplotlib ``Axes`` and returns it. If you pass one with ``ax=``, you
decide when the figure is shown:

.. code-block:: python

    import matplotlib.pyplot as plt
    from cdec import plot_true_color_image, plot_false_color_urban

    fig, (left, right) = plt.subplots(1, 2, figsize=(14, 6), layout="constrained")
    plot_true_color_image(tci_path, ax=left)
    plot_false_color_urban(urban_path, ax=right)
    plt.show()

Save a map as a picture
-----------------------

Use ``show=False`` to draw without opening a window, for example in a loop over many files, and save the figure:

.. code-block:: python

    ax = plot_ndvi(path, show=False)
    ax.figure.savefig("ndvi_bremen.png", dpi=150, bbox_inches="tight")

Change the title or the colours
-------------------------------

``title=`` replaces the title (``title=""`` draws none). The index and measurement plots accept ``cmap=``,
``vmin=`` and ``vmax=``. Because the function returns the ``Axes``, everything else is plain matplotlib:

.. code-block:: python

    ax = plot_lst(path, cmap="coolwarm", vmin=275, vmax=300)
    ax.set_title("Land surface temperature, June 2024 (K)")

Plot any other GeoTIFF
----------------------

:func:`~cdec.plot_raster` draws any GeoTIFF. It decides by the *format* of the file: three 8-bit bands are a
colour picture, everything else is one band of numbers with a colour bar.

.. code-block:: python

    from cdec import plot_raster

    plot_raster("my_file.tif", cmap="viridis", label="my unit")

For a file with several bands choose the band with ``band=`` (``band=1`` is the first). Why there is no
function that finds out the data type by itself is explained in :doc:`/explanation/design`.
