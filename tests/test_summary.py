"""Tests of the summary that the download functions print (offline)."""

import re
from datetime import date

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds

from cdec.eo.scl import describe_scl_classes
from cdec.eo.summary import format_period, sentinel2_details, summarize_raster

from .helpers import write_test_raster


def rows(text: str) -> dict[str, str]:
    """The lines of a summary as {label: text}, independent of how the columns are aligned."""
    lines = text.splitlines()[1:]  # the first line is the title
    return dict(re.split(r"\s{2,}", line.strip(), maxsplit=1) for line in lines)


# ----------------------------------------------------------------------------
# What is read from the file
# ----------------------------------------------------------------------------
def test_summary_describes_extent_grid_values_and_no_data(tmp_path):
    path = tmp_path / "ndvi.tif"
    write_test_raster(path, count=1)  # 50 x 40 pixels of 10 m, 10 empty columns = 20 % no data

    text = summarize_raster(path, "NDVI from Sentinel-2", "no unit", {"period": "June 2024"})

    with rasterio.open(path) as raster:
        west, south, east, north = transform_bounds(raster.crs, "EPSG:4326", *raster.bounds)
        values = raster.read(1)
    lines = text.splitlines()
    assert lines[0] == "NDVI from Sentinel-2"
    assert str(path) in text
    assert f"west {west:.4f}, south {south:.4f}, east {east:.4f}, north {north:.4f} (WGS 84)" in text
    assert "50 x 40 pixels of 10 m (EPSG:32632)" in text
    assert f"{np.nanmin(values):.4g} to {np.nanmax(values):.4g}, mean {np.nanmean(values):.4g}" in text
    assert rows(text)["no data"] == "20.0 % of the pixels"
    assert rows(text)["unit"] == "no unit"
    assert list(rows(text))[-1] == "period"  # details come last
    assert rows(text)["period"] == "June 2024"


def test_summary_says_how_big_the_area_is(tmp_path):
    path = tmp_path / "ndvi.tif"
    write_test_raster(path, count=1, width=1000, height=1000)  # 10 km x 10 km

    text = summarize_raster(path)

    width_km, height_km = [float(part) for part in text.split("about ")[1].split(" km")[0].split(" x ")]
    assert width_km == pytest.approx(10 / 1.0, rel=0.05)  # UTM metres vs. degrees: a few percent
    assert height_km == pytest.approx(10, rel=0.05)


def test_summary_gives_the_resolution_in_degrees_for_longitude_latitude_grids(tmp_path):
    path = tmp_path / "lst.tif"
    with rasterio.open(
        path, "w", driver="GTiff", dtype="float32", count=1, width=20, height=10,
        crs="EPSG:4326", transform=from_origin(8.72, 53.11, 0.009, 0.009), nodata=np.nan,
    ) as dst:
        dst.write(np.full((1, 10, 20), 290.0, dtype="float32"))

    text = summarize_raster(path)

    assert "20 x 10 pixels of 0.009 degrees, about 6" in text  # 0.009 deg = about 600 m here
    assert "(EPSG:4326)" in text
    assert rows(text)["no data"] == "none"


def test_summary_counts_nan_as_no_data_even_if_the_file_does_not_declare_it(tmp_path):
    path = tmp_path / "ndvi.tif"
    write_test_raster(path, count=1, declare_nodata=False)

    assert "20.0 % of the pixels" in summarize_raster(path)


def test_summary_lists_the_values_of_class_rasters(tmp_path):
    path = tmp_path / "land_cover.tif"
    write_test_raster(path, count=1, dtype="uint8", class_ids=True, empty_columns=0)

    text = summarize_raster(path)

    assert rows(text)["values"] == "found: 10, 30, 50, 80"


def test_summary_of_a_colour_image_names_the_bands_instead_of_a_value_range(tmp_path):
    path = tmp_path / "tci.tif"
    write_test_raster(path, count=3, dtype="uint8", class_ids=True)

    assert rows(summarize_raster(path))["values"] == "3 bands, uint8"


def test_summary_of_an_empty_raster_does_not_fail(tmp_path):
    path = tmp_path / "empty.tif"
    write_test_raster(path, count=1, empty_columns=50)  # every column is empty

    text = summarize_raster(path)

    assert rows(text)["values"] == "no valid pixels"
    assert rows(text)["no data"] == "100.0 % of the pixels"


def test_summary_works_without_title_unit_and_details(tmp_path):
    path = tmp_path / "ndvi.tif"
    write_test_raster(path, count=1)

    lines = summarize_raster(path).splitlines()

    assert lines[0] == "Downloaded raster"
    assert not any(line.strip().startswith("unit") for line in lines)


# ----------------------------------------------------------------------------
# The lines about the request
# ----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "given, expected",
    [
        (["2024-06-01", "2024-07-01"], "2024-06-01 to 2024-07-01 (end date not included)"),
        (("2024-06-01", "2024-07-01"), "2024-06-01 to 2024-07-01 (end date not included)"),
        ([date(2024, 6, 1), date(2024, 7, 1)], "2024-06-01 to 2024-07-01 (end date not included)"),
        (["2024-06-01", None], "2024-06-01 to open (end date not included)"),
        ("2024", "2024"),
    ],
)
def test_format_period(given, expected):
    assert format_period(given) == expected


def test_describe_scl_classes_uses_the_class_names():
    assert describe_scl_classes([4, 5]) == "4 Vegetation, 5 Not vegetated"
    assert describe_scl_classes([6, 11]) == "6 Water, 11 Snow or ice"
    assert "switched off" in describe_scl_classes(None)


def test_sentinel2_details_contain_period_clouds_and_classes():
    details = sentinel2_details(["2024-06-01", "2024-07-01"], 35, [4, 5, 6])

    assert list(details) == ["period", "clouds", "SCL kept"]
    assert details["period"].startswith("2024-06-01 to 2024-07-01")
    assert "35 %" in details["clouds"]
    assert details["SCL kept"] == "4 Vegetation, 5 Not vegetated, 6 Water"
