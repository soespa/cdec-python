Arguments
=========

The three standard arguments
----------------------------

Every download function starts with ``file_path, spatial_extent, temporal_extent``.

``file_path``
    Where to write the file: a string or a :class:`~pathlib.Path`. Missing folders are created.

``SpatialExtent``
    The area: an openEO bounding-box dictionary such as
    ``{"west": 8.7, "south": 53.0, "east": 8.9, "north": 53.1}`` (degrees, WGS 84), a Shapely
    geometry, or the path to a GeoJSON file (:doc:`/howto/choose-area`).

``TemporalExtent``
    The period: ``[start, end]`` as text (``"2024-06-01"``) or :class:`~datetime.date`. The end
    date itself is *not* included, so ``["2024-06-01", "2024-07-01"]`` covers all of June
    (:doc:`/howto/choose-period`). The elevation and land cover functions do not need it.

Options of some data types
--------------------------

.. list-table::
   :header-rows: 1
   :widths: auto

   * - Argument
     - Used by
     - Meaning
   * - ``max_cloud_cover``
     - NDVI, EVI, NDWI, NDMI, NDSI, true colour, false colour (urban, infrared, SWIR), scene classification
     - scenes with more cloud cover (percent) are not used; default 20, but 100 for the scene classification,
       which shows the clouds
   * - ``scl_classes``
     - NDVI, EVI, NDWI, NDMI, NDSI, true colour, false colour (urban, infrared, SWIR)
     - SCL classes to keep; ``None`` switches pixel masking off (:doc:`scl`)
   * - ``enhance_color``
     - true colour
     - ``True``: 8-bit picture; ``False``: reflectance
   * - ``enhance_contrast``
     - false colour (urban, infrared, SWIR)
     - ``True``: 8-bit picture; ``False``: reflectance
   * - ``depth``
     - soil water index
     - characteristic time length *T* in days (2, 5, 10, 15, 20, 40, 60, 100)

Technical options
-----------------

These three are accepted by every download function and must be written with their names
(:doc:`/howto/output-file`).

``create_cog``
    ``True`` (default): write a Cloud Optimized GeoTIFF; ``False``: a plain GeoTIFF.

``overview_resampling``
    How the overview levels of a Cloud Optimized GeoTIFF are calculated. Default ``"average"``
    (``"nearest"`` for land cover and the scene classification). One of ``"nearest"``, ``"bilinear"``, ``"cubic"``, ``"cubic_spline"``,
    ``"lanczos"``, ``"average"``, ``"mode"``, ``"gauss"`` or ``"rms"``.

``verbose``
    ``True`` (default): print a summary of the finished file.
