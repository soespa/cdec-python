Clouds and masking
==================

Optical satellites like Sentinel-2 cannot see through clouds. On a typical day a large part of central Europe is
covered, and the shadows of clouds are dark patches that look like water. If you average images without caring,
the clouds end up in your NDVI as low values, and your forest looks sick.

Two filters
-----------

The Sentinel-2 download functions remove clouds in two steps:

``max_cloud_cover``: whole scenes
  Every scene (a tile of about 100 by 100 km) has an estimate of its cloud cover in percent. Scenes above the limit
  (default 20) are not used at all. This is fast and cheap but coarse: a scene with 15 % clouds is used, clouds
  included.

``scl_classes``: single pixels
  Every scene comes with a *Scene Classification Layer* (SCL): for each 20 m pixel a number from 0 to 11 says what the
  pixel probably shows (vegetation, water, cloud, shadow, snow ...). You list the classes you want to **keep**; every other
  pixel is treated as no data (:doc:`/reference/scl`).

Why a list to keep and not a list to drop? It is the safer way round: a class you forgot is removed, not silently
kept.

The mean of what is left
------------------------

Masked pixels are no data, and the average over time ignores no data. A pixel therefore uses only the observations
that were clear. A pixel stays empty only when *every* observation of the period was masked: the white patches in
the maps of :doc:`/data/ndvi` and :doc:`/data/true-color`. A longer period is the best cure.

The limits
----------

The classification is calculated automatically (by ESA's Sen2Cor processor) and is not perfect. Thin clouds, haze and
cloud edges are sometimes labelled as land; snow is sometimes labelled as cloud. Look at your result before you
trust it.

Other data types
----------------

* The **Landsat** mosaic is already reconstructed to be free of clouds.
* **Land surface temperature** has *no* masking, and its mean can include cloudy observations
  (:doc:`/data/land-surface-temperature`).
* The **soil water index**, the **elevation model** and the **land cover map** do not depend on clouds.
