How a download works
====================

The satellites do not send you files; they send the Copernicus Data Space petabytes of images. You would not want
to download all of them just to look at one city. CDEC therefore uses **openEO**, a standard way to ask a
server to do the work.

Describe, do not download
-------------------------

A ``download_*`` function does not fetch images. It writes down a recipe for the server, as a *data cube*: a
block of data with the dimensions x, y, time and band. The recipe of the NDVI reads like this:

1. **Load** the red and near-infrared bands (and the scene classification) of your area and period.
2. **Mask** the pixels that you do not want, such as clouds.
3. **Average** over time, so that one value per pixel is left.
4. **Calculate** the index from the averages.
5. **Download** the result as a GeoTIFF.

Only the final result, a few megabytes, travels to your computer. Every module of the package
(``src/cdec/eo/``) is this recipe for one data type; :doc:`design` says why the recipe is not hidden in a
function that all modules share.

Why one image per period
------------------------

The result has no time dimension: it is the *mean* of the period. A single satellite image is always incomplete,
because clouds hide parts of it, and the mean of the usable observations is the simplest way to a complete,
calm picture. The index is calculated from the mean reflectance, not as the mean of daily indices.
If you need to see change, download two periods and compare them.

The login
---------

The Copernicus Data Space asks you to log in. The first time, the package shows a code and a web address; you
confirm the code in your browser. The openEO client stores a token on your computer, so later calls log in
without a question. Every download function connects and logs in again; this is cheap once the token exists.

The file
--------

The function first writes the download into a hidden temporary folder next to the target. Then it applies the
colour enhancement if you asked for one, converts the file to a Cloud Optimized GeoTIFF, and only then moves it
to the name you gave. If something fails on the way, the target file is untouched
(:doc:`/howto/output-file`). At the end the function reads the finished file and prints a summary, so that the
numbers you see are the numbers in the file.

Where to read on
----------------

:doc:`clouds-and-masking` explains the masking step, :doc:`colours-and-values` what happens to the colours, and
:doc:`grids-and-time` what the grid of the result is.
