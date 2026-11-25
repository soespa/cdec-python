Helpers for files
=================

Describing a file
-----------------

The download functions print this summary after a download (:doc:`/howto/check-a-file`).

.. autofunction:: cdec.eo.summary.summarize_raster

Colour enhancement
------------------

The true-colour download and the false-colour downloads call these when ``enhance_color=True`` or
``enhance_contrast=True`` (:doc:`/explanation/colours-and-values`). They are not exported by the ``cdec`` package;
import them from ``cdec.eo.postprocessing``. The ``..._raster`` functions rewrite a file *in place*.

.. autofunction:: cdec.eo.postprocessing.enhance_color

.. autofunction:: cdec.eo.postprocessing.enhance_contrast

.. autofunction:: cdec.eo.postprocessing.enhance_color_raster

.. autofunction:: cdec.eo.postprocessing.enhance_contrast_raster
