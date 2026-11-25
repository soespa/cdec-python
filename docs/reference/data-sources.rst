Data sources and credits
========================

All data comes from the `Copernicus Data Space <https://dataspace.copernicus.eu/>`_ through its openEO backend.
Copernicus data is free and open, but you have to name the source when you publish a picture or a result
(a map in a report, a poster, a paper). Check the licence of the collection on the Data Space before you
publish. The usual wording is:

.. list-table::
   :header-rows: 1
   :widths: 25 75

   * - Data type
     - Acknowledgement
   * - Sentinel-2 (:doc:`/data/ndvi`, :doc:`/data/evi`, :doc:`/data/ndwi`, :doc:`/data/ndmi`, :doc:`/data/ndsi`,
       :doc:`/data/true-color`, :doc:`/data/false-color-urban`, :doc:`/data/false-color-infrared`,
       :doc:`/data/false-color-swir`, :doc:`/data/scene-classification`)
     - Contains modified Copernicus Sentinel data (year of the data)
   * - Sentinel-3 (:doc:`/data/land-surface-temperature`)
     - Contains modified Copernicus Sentinel data (year of the data)
   * - ESA WorldCover (:doc:`/data/land-cover`)
     - © ESA WorldCover project 2021 / Contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover
       consortium (licence: CC BY 4.0)
   * - Soil water index (:doc:`/data/soil-water-index`)
     - Generated using European Union's Copernicus Land Monitoring Service information
   * - Copernicus DEM (:doc:`/data/elevation`), Landsat mosaic (:doc:`/data/landsat-ndvi`)
     - see the description of the collection on the Copernicus Data Space

"Modified" is right because the package averages, masks and enhances the data. The pictures in this documentation
show Bremen, made with the functions of this package.
