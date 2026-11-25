Sentinel-2 scene classification
===============================

Every Sentinel-2 Level-2A scene comes with an extra band, the *Scene Classification Layer* (SCL). For each 20 m pixel
it contains one number from 0 to 11 that says what the pixel probably shows. The Sentinel-2 download functions
use it to throw away unusable pixels *before* they average the scenes of your period. ``scl_classes`` is the list of
classes you want to **keep**; everything else is treated as no data (:doc:`/howto/filter-clouds`,
:doc:`/explanation/clouds-and-masking`).

.. class-table:: cdec.SCL_CLASSES
   :hints: cdec.SCL_HINTS
   :colors: cdec.SCL_COLORS

The classification is calculated automatically (by ESA's Sen2Cor processor) and is not perfect: thin clouds, haze and
cloud edges are sometimes labelled as land, and snow is sometimes labelled as cloud. The class names follow the Sentinel Hub
and ESA documentation; the hints are written for this package. To see the classes of your own area as a map,
download the :doc:`scene classification </data/scene-classification>`.

.. autofunction:: cdec.show_scl_classes

.. py:data:: cdec.SCL_CLASSES
   :type: dict[int, str]

   The 12 classes of the Sentinel-2 Scene Classification Layer: class number to name.

.. py:data:: cdec.SCL_HINTS
   :type: dict[int, str]

   A short explanation for every class, and whether you usually want to keep it.

.. py:data:: cdec.SCL_LAND
   :type: tuple[int, ...]
   :value: (4, 5)

   Vegetation and not vegetated: the default ``scl_classes`` of NDVI, EVI and NDMI.

.. py:data:: cdec.SCL_LAND_AND_WATER
   :type: tuple[int, ...]
   :value: (4, 5, 6)

   Land and water: the default ``scl_classes`` of NDWI, the true-colour image and the false-colour images
   (urban, infrared and SWIR).

.. py:data:: cdec.SCL_LAND_WATER_AND_SNOW
   :type: tuple[int, ...]
   :value: (4, 5, 6, 11)

   Land, water and snow or ice: the default ``scl_classes`` of NDSI.

.. py:data:: cdec.SCL_COLORS
   :type: dict[int, str]

   The colour of every class as hex code (the colours of the Copernicus Browser layer). This is the colour table
   that :func:`~cdec.download_scene_classification_map` stores in the GeoTIFF, and the colours of
   :func:`~cdec.plot_scene_classification_map`.
