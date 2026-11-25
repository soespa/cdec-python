Developer reference
===================

Every ``download_*`` function follows the same recipe: connect, describe the data as an openEO
data cube, hand the cube to :func:`~cdec.eo.util.download_raster_cube`. These are the helpers
behind it. They are not meant to be called by users of the package.

Shared helpers
--------------

.. automodule:: cdec.eo.util
   :members: get_connection, prepare_output_path, download_raster_cube

.. autodata:: cdec.eo.util.BACKEND_URL

.. autodata:: cdec.eo.util.SENTINEL2_REFLECTANCE_SCALE

.. autodata:: cdec.eo.util.DEFAULT_DEM_TEMPORAL_EXTENT

Scene classification helpers
----------------------------

.. automodule:: cdec.eo.scl
   :members: check_scl_classes, describe_scl_classes

Summary helpers
---------------

.. automodule:: cdec.eo.summary
   :members: format_period, sentinel2_details
