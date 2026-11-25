"""Small helper functions shared by the test files."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio.warp import transform_bounds
from rio_cogeo.cogeo import cog_validate


def write_test_raster(
    path: str | Path,
    count: int = 3,
    dtype: str = "float32",
    class_ids: bool = False,
    empty_columns: int = 10,
    declare_nodata: bool = False,
    width: int = 50,
    height: int = 40,
    crs: str = "EPSG:32632",
) -> None:
    """Write a small GeoTIFF with made-up values, for tests that run offline.

    The ``empty_columns`` columns on the left side have no data (NaN for float
    rasters, 0 for integer rasters). By default the file does *not* declare a
    nodata value, which is the harder case for the package.

    With ``class_ids=True`` the values are land-cover class IDs (10, 30, 50, 80),
    otherwise they look like reflectance (0.02 ... 0.3).

    ``crs`` is UTM zone 32 (metres) by default. With a geographic system such as
    ``"EPSG:4326"`` the pixels are 0.001 degrees large, near Bremen.
    """
    rng = np.random.default_rng(seed=42)
    if class_ids:
        data = rng.choice([10, 30, 50, 80], size=(count, height, width))
    else:
        data = rng.uniform(0.02, 0.3, size=(count, height, width))
    data = data.astype(dtype)
    data[:, :, :empty_columns] = np.nan if np.dtype(dtype).kind == "f" else 0

    if rasterio.crs.CRS.from_string(crs).is_geographic:
        transform = from_origin(8.72, 53.115, 0.001, 0.001)
    else:
        transform = from_origin(480000, 5880000, 10, 10)

    nodata = None
    if declare_nodata:
        nodata = np.nan if np.dtype(dtype).kind == "f" else 0

    with rasterio.open(
        path,
        "w",
        driver="GTiff",
        dtype=dtype,
        count=count,
        width=width,
        height=height,
        crs=crs,
        transform=transform,
        nodata=nodata,
    ) as dst:
        dst.write(data)


def find_processes(graph, process_id: str) -> list[dict]:
    """Return the arguments of every openEO process called ``process_id``.

    Looks through the whole process graph, including the callbacks inside
    ``apply`` and ``reduce_dimension``. An empty list means: not used.
    """
    found = []
    if isinstance(graph, dict):
        if graph.get("process_id") == process_id:
            found.append(graph["arguments"])
        for value in graph.values():
            found += find_processes(value, process_id)
    elif isinstance(graph, list):
        for item in graph:
            found += find_processes(item, process_id)
    return found


def find_numbers(graph) -> set[float]:
    """Return all numbers that appear in an openEO process graph."""
    numbers = set()
    if isinstance(graph, dict):
        for value in graph.values():
            numbers |= find_numbers(value)
    elif isinstance(graph, list):
        for item in graph:
            numbers |= find_numbers(item)
    elif isinstance(graph, (int, float)) and not isinstance(graph, bool):
        numbers.add(float(graph))
    return numbers


def assert_valid_cog(path: str | Path) -> None:
    """Fail if ``path`` is not a valid Cloud Optimized GeoTIFF."""
    is_valid, errors, _warnings = cog_validate(path, quiet=True)
    assert is_valid, f"{path} is not a valid Cloud Optimized GeoTIFF: {errors}"


def assert_covers_extent(path: str | Path, spatial_extent: dict, tolerance_pixels: int = 2) -> None:
    """Fail if the raster does not cover the requested bounding box.

    openEO snaps the area to the pixel grid, so the raster may be a little
    smaller or larger than the request. ``tolerance_pixels`` allows for that.
    """
    with rasterio.open(path) as raster:
        west, south, east, north = transform_bounds(raster.crs, "EPSG:4326", *raster.bounds)
        pixel_size_in_degrees = (east - west) / raster.width

    tolerance = max(tolerance_pixels * pixel_size_in_degrees, 0.002)
    covered = (
        west <= spatial_extent["west"] + tolerance
        and south <= spatial_extent["south"] + tolerance
        and east >= spatial_extent["east"] - tolerance
        and north >= spatial_extent["north"] - tolerance
    )
    assert covered, (
        f"Raster covers lon {west:.4f}..{east:.4f}, lat {south:.4f}..{north:.4f}, "
        f"but lon {spatial_extent['west']}..{spatial_extent['east']}, "
        f"lat {spatial_extent['south']}..{spatial_extent['north']} was requested."
    )


def read_valid_values(path: str | Path, band: int = 1) -> tuple[np.ndarray, int]:
    """Read one band; return its valid values (no nodata, no NaN) and the pixel count."""
    with rasterio.open(path) as raster:
        data = raster.read(band, masked=True)
    values = data.compressed()
    values = values[np.isfinite(values)]
    return values, data.size


def assert_index_in_range(values: np.ndarray, name: str, max_share: float = 0.001) -> None:
    """Check that a normalised-difference index stays in -1 ... 1, apart from a few dark pixels.

    The index can leave -1 ... 1 only where one of the two reflectances is below zero, which happens in the darkest
    pixels (shadows, water). The documentation says so, so a tiny share of such pixels is no error. In the
    example downloads it is below 0.01 %; a share above ``max_share`` (0.1 %) means something is wrong.
    """
    share = float(np.mean((values < -1) | (values > 1)))
    assert share <= max_share, (
        f"{name}: {100 * share:.3f} % of the pixels are outside -1 ... 1 (range {values.min():.2f} ... {values.max():.2f})"
    )
