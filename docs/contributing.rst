Contributing
============

This page is for people who change the package: how the code is organised, how to run the tests, how to build this
documentation, and what to do when you add a data type.

Set up
------

.. code-block:: console

    pip install -e ".[test,docs]"

How the code is organised
-------------------------

.. code-block:: text

    src/cdec/eo/
        ndvi.py, evi.py, tci.py, ...   one module per data type, one download_* function each
        scl.py                         Sentinel-2 SCL classes: names, hints, ready-made selections
        summary.py                     the summary that the download functions print
        util.py                        login, download + Cloud Optimized GeoTIFF
        postprocessing.py              colour / contrast enhancement of RGB composites
    src/cdec/plot/
        products.py                    one plot_* function per data type (colour map, range, labels)
        raster.py                      the drawing itself, and plot_raster for any GeoTIFF
    docs/                              this documentation (conf.py, *.rst, _ext/ for the class tables)

Every ``download_*`` function reads from top to bottom in the same way: check the arguments, connect, describe the
data as an openEO data cube (``load_collection`` -> mask -> ``mean_time`` -> index), then hand the cube to
``download_raster_cube`` (:doc:`/explanation/how-it-works`). Start with ``ndvi.py``; the other modules are
variations of it. The short alias of each function is the last line of its module. The helpers are in the
:doc:`developer reference </reference/internals>`.

Run the tests
-------------

.. code-block:: console

    pytest              # offline tests only, a few seconds: no internet, no login
    pytest --live       # additionally download every data type for real
    pytest --live -k ndvi

.. list-table::
   :header-rows: 1
   :widths: auto

   * - File
     - What it tests
   * - ``tests/test_download_offline.py``
     - what every ``download_*`` function asks openEO for, and what it does with the file (a fake backend replaces openEO)
   * - ``tests/test_postprocessing.py``, ``test_scl.py``, ``test_summary.py``, ``test_util.py``, ``test_package.py``
     - colour enhancement (including: same reflectance, same colour), SCL table and validation, the printed summary,
       helper functions, the public interface (aliases, argument order)
   * - ``tests/test_plot.py``
     - the plot functions: colour maps and ranges, no-data pixels, colour pictures from reflectance, land-cover legend,
       axes in degrees or metres, ``plt.show()`` behaviour, the whole way from download to plot
   * - ``tests/test_docs.py``
     - the documentation: every public name is documented, every data type has a page, the pages build without
       a warning (the build tests are skipped if Sphinx is not installed)
   * - ``tests/test_download_live.py``
     - **real downloads** of every data type for Bremen (see ``tests/conftest.py``), with checks of the files and of
       the values

The live tests need internet and a Copernicus Data Space account. The first run asks you to log in. The downloaded
rasters are kept in ``tests/output/`` (ignored by git) so you can open them in QGIS.

Look at the plots
-----------------

``tests/plot_gallery.py`` is not a test. It draws all plot functions into one picture so that you can look at them
(and check a change of a plot function with your own eyes):

.. code-block:: console

    python tests/plot_gallery.py            # a made-up landscape, works offline
    python tests/plot_gallery.py --real     # the files that `pytest --live` downloaded to tests/output/
    python tests/plot_gallery.py --no-show  # do not open a window, only write tests/output/plot_gallery_*.png

Build this documentation
------------------------

.. code-block:: console

    python docs/_scripts/build_docs.py

This builds the English and the German version into ``docs/_build/html/en`` and ``docs/_build/html/de``. Then open
``docs/_build/html/index.html`` in a browser: it forwards you to the language of your browser (``docs/_build/`` is
ignored by git). Every build uses ``-W``, which turns every warning into an error. ``hatch run docs:build`` does the
same. While you write, one language is quicker:

.. code-block:: console

    sphinx-build -W --keep-going -b html docs docs/_build/html/en
    sphinx-build -W --keep-going -b html -D language=de docs docs/_build/html/de

The pages follow the `Diátaxis <https://diataxis.fr/>`_ scheme: ``tutorial/`` (learning), ``howto/`` (goals),
``explanation/`` (understanding) and ``reference/`` (look-up), plus one page for each data type in ``data/``.

The pictures on the data type pages are real data. They are made from the files in ``tests/output/`` (after a
``pytest --live`` run) and saved in ``docs/_static/figures/``. After a change of a plot function make them again and
commit them:

.. code-block:: console

    python docs/_scripts/make_figures.py

The code examples on the data type pages and the how-to pages are complete: each one defines the
``spatial_extent`` and the ``temporal_extent`` it uses (Bremen, June 2024), so that a student can copy it into an empty
file and run it. ``tests/test_docs.py`` checks this, and runs the example of every data type page with the made-up
backend. Keep it that way when you write a new page.

Translate the documentation
---------------------------

The pages are written in English and translated with Sphinx's gettext system: the German texts are in
``docs/locale/de/LC_MESSAGES/*.po`` (one file for each folder of ``docs/``). The ``.rst`` files exist only once, so
both languages have the same pages, the same pictures and the same code. The ``.po`` files also translate the
documentation of the functions (their docstrings); the docstrings in the code stay English.

When you change an English text, the German page shows the new English text until you translate it. To find the
texts that changed:

.. code-block:: console

    pip install sphinx-intl
    sphinx-build -b gettext docs docs/_build/gettext
    sphinx-intl -c docs/conf.py update -p docs/_build/gettext -l de

Open the ``.po`` files in a text editor or in Poedit and fill in every ``msgstr`` that is empty or marked ``#, fuzzy``
(remove the ``fuzzy`` line when the translation is right). Do not translate code between double back-ticks and keep
the roles such as ``:doc:`` and ``:func:``: Sphinx warns about broken markup, and ``tests/test_docs.py`` compares the
code and the roles of every German text with the English one. It also fails while a German text is missing.

For a third language add its code to ``LANGUAGES`` in ``docs/conf.py`` and run ``sphinx-intl update`` with ``-l`` and
that code.

Add a data type
---------------

1. Write ``src/cdec/eo/<name>.py`` with the ``download_<long_name>`` function and a short alias as its last line;
   copy ``ndvi.py`` and change what is different. Export both names in ``src/cdec/eo/__init__.py``.
2. Write the matching ``plot_<long_name>`` function in ``src/cdec/plot/products.py`` and export it in
   ``src/cdec/plot/__init__.py``.
3. Add the page ``docs/data/<name>.rst`` (copy a page of a similar data type) with a line
   ``.. autofunction:: cdec.download_<long_name>`` and ``.. autofunction:: cdec.plot_<long_name>``, and list it in
   ``docs/data/index.rst`` and ``docs/reference/functions.rst``. The short alias needs no line: the documentation of the
   long name shows it automatically.
4. Add the function to the tests (``tests/test_download_offline.py``, ``tests/test_plot.py``,
   ``tests/test_package.py``) and to the live tests. ``tests/test_docs.py`` fails until the documentation is complete.
5. Translate the new texts of the page and of the docstrings into German (see above).

Make a release
--------------

.. code-block:: console

    uv build                    # or: python -m build
    twine check dist/*

Raise ``__version__`` in ``src/cdec/__about__.py`` first.
