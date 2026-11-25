Colours and values
==================

A GeoTIFF holds numbers. Whether you see a picture, a colour map or just numbers is a question of how you display
them. The package keeps the two apart.

Measurements and pictures
-------------------------

**Reflectance** is what the satellite measures: the share of the light that the ground reflects, from 0 (black) to
about 1 (white). It is the right basis for calculations, but as a picture it looks dark and flat, because most of the
land reflects only 5 to 30 % of the light.

**A picture** is made for the eye: reflectance stretched to 0 ... 255 so that it looks like a photograph. It is
right for looking, but the numbers are no longer measurements.

The colour downloads (:doc:`/data/true-color` and the false-colour images :doc:`/data/false-color-urban`,
:doc:`/data/false-color-infrared` and :doc:`/data/false-color-swir`) therefore give you a picture
by default, and the reflectance if you ask for it (``enhance_color=False``, ``enhance_contrast=False``). The index
downloads (NDVI, EVI, NDWI, NDMI, NDSI) are always measurements, and the scene classification is a map of class
numbers.

A fixed stretch
---------------

Most GIS programs stretch the colours of every image between its own smallest and largest value. Then the same colour means different
things in different images, and two images cannot be compared by eye.

The enhancement of the package is **fixed**: it depends only on constants, never on the image. Reflectance 0.1 gets the same
colour in an image of Bremen and of the Alps, in June and in December. The colours of two pictures are therefore comparable.
The price is that the contrast of a very dark or very bright image is not optimised.

Plots follow the same idea
--------------------------

The plot functions use a fixed range wherever the data has a natural one: -1 to 1 for the indices (vegetation, water,
moisture and snow) and 0 to 100 for the soil water index. For temperature and elevation there is no natural range, so the colours follow the
image, and you set ``vmin`` and ``vmax`` yourself to compare (:doc:`/howto/compare-images`).

If you downloaded the reflectance version of a colour image, the plot function enhances the colours *for the picture
only*. The numbers in your file are never changed by plotting.
