# Climate Data Entrepreneurial Club (CDEC)

[![PyPI - Version](https://img.shields.io/pypi/v/cdec.svg)](https://pypi.org/project/cdec)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cdec.svg)](https://pypi.org/project/cdec)

`cdec` downloads satellite data for a study area from the
[Copernicus Data Space](https://dataspace.copernicus.eu/) and draws it. You call one function, you get one
(Cloud Optimized) GeoTIFF that you can open with `rasterio` or QGIS. The package is written for teaching:
one function per data type, short readable code, and defaults that work.

It covers fifteen data types: the vegetation, water, moisture and snow indices NDVI, EVI, NDWI, NDMI and NDSI
(Sentinel-2), true-colour and false-colour images (urban, infrared and SWIR; Sentinel-2), the Sentinel-2 scene
classification, NDVI from the Landsat mosaic, land surface temperature (Sentinel-3), soil water index, elevation
and land cover.

## Installation

Python 3.10 or newer is required.

```console
pip install cdec
```

For development (editable install with the test and documentation tools):

```console
pip install -e ".[test,docs]"
```

## Quick start

You need a free [Copernicus Data Space account](https://dataspace.copernicus.eu/). The first download opens a login
(device code), later downloads reuse the stored token.

```python
from cdec import download_ndvi, plot_ndvi

spatial_extent = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}
temporal_extent = ["2024-06-01", "2024-07-01"]  # the end date is NOT included: this is all of June

path = download_ndvi("data/ndvi_bremen.tif", spatial_extent, temporal_extent)
plot_ndvi(path)  # right colours, fixed range -1 ... 1, colour bar
```

`download_ndvi` returns the path of the file and prints a summary of what is in it
(this is the output of a real download for Bremen; `verbose=False` switches the summary off):

```text
NDVI from Sentinel-2 L2A (mean of the period)
  file      /home/me/data/ndvi_bremen.tif (3.9 MB)
  extent    west 8.7211, south 53.0247, east 8.9047, north 53.1153 (WGS 84), about 12.3 x 10.1 km
  grid      1228 x 1005 pixels of 10 m (EPSG:32632)
  values    -0.6602 to 1.264, mean 0.5496
  unit      no unit (index from -1 to 1)
  no data   26.5 % of the pixels
  period    2024-06-01 to 2024-07-01 (end date not included)
  clouds    scenes with more than 20 % cloud cover are not used
  SCL kept  4 Vegetation, 5 Not vegetated
```

Every download function has a plot function with the matching name, and a short alias:
`download_true_color_image` / `download_tci` and `plot_true_color_image` / `plot_tci` are the same functions.
The documentation (the `docs/` folder, a [Sphinx](https://www.sphinx-doc.org) site) has a get-started tutorial,
how-to guides, a page for each data type and the full reference.

## License

`cdec` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
