"""Live tests: really download every type of satellite data.

These tests talk to the Copernicus Data Space openEO backend, so they

* need internet and a free Copernicus Data Space account,
* take a few minutes in total,
* are skipped unless you ask for them with ``--live``.

    pytest --live                       # run all of them
    pytest --live -k ndvi               # run only the NDVI test
    pytest --live -k "dem or land_cover"

The first run prints a web address and a code: open it in your browser and log
in. The openEO client stores a token on your computer, so later runs do not
ask again. The downloaded files stay in ``tests/output/`` - open them in QGIS
to look at them.

Every test downloads the same area (around Bremen) and, where the data changes
over time, the same period (June 2024), see ``conftest.py``. Each test then
checks the file (valid Cloud Optimized GeoTIFF, right area, right number of
bands) and whether the values make sense for Bremen in June. The value limits
below come from the product descriptions; if one of them fails, look at the
numbers in the message first - the limit may simply need adjusting.

If a Sentinel-2 test fails with "NoDataAvailable", no scene was clear enough:
try a larger ``max_cloud_cover``.
"""

import numpy as np
import pytest
import rasterio

from cdec import (
    SCL_CLASSES,
    SCL_COLORS,
    WORLDCOVER_CLASSES,
    WORLDCOVER_COLORS,
    download_dem,
    download_evi,
    download_infrared,
    download_land_cover,
    download_landsat,
    download_lst,
    download_ndmi,
    download_ndsi,
    download_ndvi,
    download_ndwi,
    download_scl,
    download_swi,
    download_swir,
    download_tci,
    download_urban,
)

from .helpers import assert_covers_extent, assert_index_in_range, assert_valid_cog, read_valid_values


pytestmark = [pytest.mark.live, pytest.mark.usefixtures("openeo_login")]


def check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind=None):
    """The checks that every download has to pass, whatever the data type."""
    assert path == output_tif, "the function should return the path it was given"
    assert path.is_file() and path.stat().st_size > 0
    assert_valid_cog(path)
    assert_covers_extent(path, spatial_extent)

    with rasterio.open(path) as raster:
        assert raster.crs is not None
        assert raster.count == band_count
        if dtype_kind is not None:  # "f" = float, "u" = unsigned integer
            assert {np.dtype(dtype).kind for dtype in raster.dtypes} == {dtype_kind}


# ----------------------------------------------------------------------------
# Sentinel-2 (10 m)
# ----------------------------------------------------------------------------
def test_ndvi(output_tif, spatial_extent, temporal_extent):
    path = download_ndvi(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    ndvi, pixel_count = read_valid_values(path)
    assert len(ndvi) > 0.5 * pixel_count, "more than half of the pixels should have data"
    assert_index_in_range(ndvi, "NDVI")
    assert np.median(ndvi) > 0.2, f"median NDVI {np.median(ndvi):.2f}: Bremen is green in June"


def test_evi(output_tif, spatial_extent, temporal_extent):
    path = download_evi(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    evi, pixel_count = read_valid_values(path)
    assert len(evi) > 0.5 * pixel_count
    low, high = np.percentile(evi, [1, 99])
    # Without the 0.0001 scaling EVI would be around 2.5, so this also guards the scaling.
    assert -1 <= low and high <= 1.5, f"EVI 1%..99% range {low:.2f} ... {high:.2f}"
    assert 0 < np.median(evi) < 1, f"median EVI {np.median(evi):.2f}"


def test_ndwi(output_tif, spatial_extent, temporal_extent):
    path = download_ndwi(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    ndwi, pixel_count = read_valid_values(path)
    assert len(ndwi) > 0.5 * pixel_count
    assert_index_in_range(ndwi, "NDWI")
    assert np.median(ndwi) < 0, f"median NDWI {np.median(ndwi):.2f}: most of Bremen is land"
    assert ndwi.max() > 0, "the Weser should show up as water (NDWI above 0)"


def test_ndmi(output_tif, spatial_extent, temporal_extent):
    path = download_ndmi(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    ndmi, pixel_count = read_valid_values(path)
    assert len(ndmi) > 0.5 * pixel_count
    assert_index_in_range(ndmi, "NDMI")
    assert np.median(ndmi) > 0, f"median NDMI {np.median(ndmi):.2f}: Bremen is green in June"


def test_ndsi(output_tif, spatial_extent, temporal_extent):
    path = download_ndsi(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    ndsi, pixel_count = read_valid_values(path)
    assert len(ndsi) > 0.5 * pixel_count
    assert_index_in_range(ndsi, "NDSI")
    assert np.median(ndsi) < 0, f"median NDSI {np.median(ndsi):.2f}: there is no snow in Bremen in June"


def test_ndsi_zugspitze(output_tif):
    """Bremen has no snow in June, so snow is tested where it is: the Zugspitze in winter.

    The documentation page of the NDSI shows this file. If it fails with "NoDataAvailable", the weather was
    bad: try a longer period or a higher ``max_cloud_cover``.
    """
    zugspitze = {"west": 10.95, "south": 47.38, "east": 11.05, "north": 47.46}
    path = download_ndsi(output_tif, zugspitze, ["2024-02-01", "2024-03-01"], max_cloud_cover=50)

    check_raster_file(path, output_tif, zugspitze, band_count=1, dtype_kind="f")
    ndsi, pixel_count = read_valid_values(path)
    assert len(ndsi) > 0.3 * pixel_count
    assert_index_in_range(ndsi, "NDSI")
    assert ndsi.max() > 0.4, f"highest NDSI {ndsi.max():.2f}: there should be snow on the Zugspitze in February"


def test_tci(output_tif, spatial_extent, temporal_extent):
    path = download_tci(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=3, dtype_kind="u")
    for band in (1, 2, 3):
        values, pixel_count = read_valid_values(path, band)
        assert len(values) > 0.5 * pixel_count
        assert values.std() > 5, f"band {band} looks flat"
        assert 10 < values.mean() < 245, f"band {band} mean {values.mean():.0f}: too dark or bright"


def test_tci_without_color_enhancement(output_tif, spatial_extent, temporal_extent):
    path = download_tci(output_tif, spatial_extent, temporal_extent, enhance_color=False)

    check_raster_file(path, output_tif, spatial_extent, band_count=3, dtype_kind="f")
    red, pixel_count = read_valid_values(path, 1)
    assert len(red) > 0.5 * pixel_count
    assert 0 <= red.min() and red.max() < 1.5, f"reflectance {red.min()} ... {red.max()}"
    assert 0.01 < np.median(red) < 0.5


def test_urban(output_tif, spatial_extent, temporal_extent):
    path = download_urban(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=3, dtype_kind="u")
    for band in (1, 2, 3):
        values, pixel_count = read_valid_values(path, band)
        assert len(values) > 0.5 * pixel_count
        assert values.std() > 5, f"band {band} looks flat"


def check_false_color_image(path, output_tif, spatial_extent):
    check_raster_file(path, output_tif, spatial_extent, band_count=3, dtype_kind="u")
    for band in (1, 2, 3):
        values, pixel_count = read_valid_values(path, band)
        assert len(values) > 0.5 * pixel_count
        assert values.std() > 5, f"band {band} looks flat"


def test_infrared(output_tif, spatial_extent, temporal_extent):
    path = download_infrared(output_tif, spatial_extent, temporal_extent)

    check_false_color_image(path, output_tif, spatial_extent)


def test_swir(output_tif, spatial_extent, temporal_extent):
    path = download_swir(output_tif, spatial_extent, temporal_extent)

    check_false_color_image(path, output_tif, spatial_extent)


def test_scl(output_tif, spatial_extent, temporal_extent):
    path = download_scl(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="u")
    class_ids, pixel_count = read_valid_values(path)
    found = set(np.unique(class_ids).tolist())
    assert len(class_ids) > 0.5 * pixel_count
    assert found <= set(SCL_CLASSES), f"unknown class IDs: {found - set(SCL_CLASSES)}"
    assert 4 in found, "Bremen has vegetation in June"
    assert 6 in found, "the Weser is water"

    with rasterio.open(path) as raster:  # the SCL colour table is attached
        colormap = raster.colormap(1)
    for class_id, color in SCL_COLORS.items():
        assert colormap[class_id][:3] == tuple(bytes.fromhex(color.removeprefix("#")))


# ----------------------------------------------------------------------------
# Landsat (30 m)
# ----------------------------------------------------------------------------
def test_landsat(output_tif, spatial_extent, temporal_extent):
    path = download_landsat(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    ndvi, pixel_count = read_valid_values(path)
    assert len(ndvi) > 0.5 * pixel_count
    assert ndvi.min() >= -1 and ndvi.max() <= 1, f"NDVI range {ndvi.min()} ... {ndvi.max()}"
    assert np.median(ndvi) > 0.1, f"median NDVI {np.median(ndvi):.2f}"


# ----------------------------------------------------------------------------
# Sentinel-3 land surface temperature (1 km)
# ----------------------------------------------------------------------------
def test_lst(output_tif, spatial_extent, temporal_extent):
    path = download_lst(output_tif, spatial_extent, temporal_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    lst, pixel_count = read_valid_values(path)
    assert len(lst) > 0.5 * pixel_count
    # The docstring promises Kelvin: ~20 would mean degrees Celsius, ~15000 raw counts.
    assert 270 < lst.mean() < 330, f"mean LST {lst.mean():.1f}: is this really Kelvin?"


# ----------------------------------------------------------------------------
# Static data sets (no temporal extent needed: the functions use their default)
# ----------------------------------------------------------------------------
def test_dem(output_tif, spatial_extent):
    path = download_dem(output_tif, spatial_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1)
    elevation, pixel_count = read_valid_values(path)
    assert len(elevation) > 0.95 * pixel_count
    # Bremen is flat: about 0-30 m, a little more where buildings are in the surface model.
    assert -20 < elevation.min() and elevation.max() < 150, (
        f"elevation {elevation.min()} ... {elevation.max()} m"
    )


def test_dem_without_cog(output_tif, spatial_extent):
    path = download_dem(output_tif, spatial_extent, create_cog=False)

    assert path == output_tif and path.is_file()
    with rasterio.open(path) as raster:  # a plain GeoTIFF, but readable
        assert raster.count == 1
    elevation, pixel_count = read_valid_values(path)
    assert len(elevation) > 0.95 * pixel_count


def test_land_cover(output_tif, spatial_extent):
    path = download_land_cover(output_tif, spatial_extent)

    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="u")
    class_ids, pixel_count = read_valid_values(path)
    found = set(np.unique(class_ids).tolist())
    assert len(class_ids) > 0.95 * pixel_count
    assert found <= set(WORLDCOVER_CLASSES) | {0}, f"unknown class IDs: {found - set(WORLDCOVER_CLASSES)}"
    assert 50 in found, "a city like Bremen must contain 'Built-up'"

    with rasterio.open(path) as raster:  # the ESA colour table is attached
        colormap = raster.colormap(1)
    for class_id, color in WORLDCOVER_COLORS.items():
        assert colormap[class_id][:3] == tuple(bytes.fromhex(color.removeprefix("#")))


# ----------------------------------------------------------------------------
# Copernicus Land Monitoring Service: Soil Water Index (1 km)
# ----------------------------------------------------------------------------
def check_swi(path, output_tif, spatial_extent):
    check_raster_file(path, output_tif, spatial_extent, band_count=1, dtype_kind="f")
    swi, pixel_count = read_valid_values(path)
    assert len(swi) > 0.5 * pixel_count
    # The SWI is a percentage. 0 ... 200 would mean the raw, unscaled values.
    assert 0 <= swi.min() and swi.max() <= 100, f"SWI range {swi.min()} ... {swi.max()}"


def test_swi_for_the_standard_test_period(output_tif, spatial_extent, temporal_extent):
    """June 2024. Expected to FAIL with 'no data' if the collection starts later.

    The collection with version 2 of the 1 km Soil Water Index starts on
    2025-07-12 at 12:00 UTC (version 1 covers the years before). The next test shows whether the
    function itself works.
    """
    path = download_swi(output_tif, spatial_extent, temporal_extent)

    check_swi(path, output_tif, spatial_extent)


def test_swi_for_a_period_covered_by_version_2(output_tif, spatial_extent):
    path = download_swi(output_tif, spatial_extent, ["2025-08-01", "2025-09-01"], depth=20)

    check_swi(path, output_tif, spatial_extent)
