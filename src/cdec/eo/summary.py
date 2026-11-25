"""A short summary of a downloaded raster, printed by the ``download_*`` functions.

The download functions print it when they are called with ``verbose=True``
(the default). Everything about the raster itself (extent, grid, resolution,
values, no data) is read from the finished file, so the summary shows what is
really in it. The caller only adds a title, the unit of the values and a few
lines about the request. The result looks like this::

    NDVI from Sentinel-2 L2A (mean of the period)
      file      /home/me/data/ndvi_bremen.tif (4.1 MB)
      extent    west 8.7218, south 53.0250, east 8.9044, north 53.1150 (WGS 84), about 12.2 x 10.0 km
      grid      1217 x 1006 pixels of 10 m (EPSG:32632)
      values    -0.2113 to 0.9201, mean 0.4538
      unit      no unit (index from -1 to 1)
      no data   6.8 % of the pixels
      period    2024-06-01 to 2024-07-01 (end date not included)
      clouds    scenes with more than 20 % cloud cover are not used
      SCL kept  4 Vegetation, 5 Not vegetated

The same function can describe any raster file, for example one that was
downloaded earlier: ``print(summarize_raster("data/ndvi_bremen.tif"))``.
"""

from __future__ import annotations

from math import cos, radians
from pathlib import Path
from typing import Mapping, Sequence

import numpy as np
import rasterio
from rasterio.warp import transform_bounds

from .scl import describe_scl_classes


# Length of one degree. East-west distances shrink with cos(latitude).
METRES_PER_DEGREE = 111_320

# Integer rasters with at most this many different values (land-cover classes)
# are summarised by listing the values instead of a minimum and a maximum.
MAX_LISTED_VALUES = 15


def format_period(temporal_extent) -> str:
    """Write a temporal extent as text, e.g. ``2024-06-01 to 2024-07-01 (end date not included)``."""
    if isinstance(temporal_extent, (list, tuple)) and len(temporal_extent) == 2:
        start, end = ("open" if value is None else str(value) for value in temporal_extent)
        return f"{start} to {end} (end date not included)"
    return str(temporal_extent)


def describe_cloud_cover(max_cloud_cover: int) -> str:
    """Say which scenes are used: all of them, or only those below the limit."""
    if max_cloud_cover >= 100:
        return "all scenes are used, however cloudy"
    return f"scenes with more than {max_cloud_cover} % cloud cover are not used"


def sentinel2_details(
    temporal_extent,
    max_cloud_cover: int,
    scl_classes: Sequence[int] | None,
) -> dict[str, str]:
    """The lines about the request that the Sentinel-2 functions with SCL masking print."""
    return {
        "period": format_period(temporal_extent),
        "clouds": describe_cloud_cover(max_cloud_cover),
        "SCL kept": describe_scl_classes(scl_classes),
    }


def summarize_raster(
    raster_path: str | Path,
    description: str = "",
    unit: str = "",
    details: Mapping[str, str] | None = None,
) -> str:
    """Return a short text about a raster file, ready to be printed.

    Parameters
    ----------
    raster_path:
        The GeoTIFF to describe.
    description:
        Title line, e.g. ``"NDVI from Sentinel-2 L2A (mean of the period)"``.
    unit:
        What the values mean, e.g. ``"Kelvin"``. Skipped if empty.
    details:
        More lines (label -> text), printed below the lines read from the file.

    Returns
    -------
    str
        The summary, one line per entry. ``print`` it.
    """
    raster_path = Path(raster_path)
    rows = [("file", f"{raster_path} ({_file_size(raster_path)})")]

    with rasterio.open(raster_path) as raster:
        if raster.crs is not None:
            rows += _location_rows(raster)

        band = raster.read(1)
        valid = raster.read_masks(1) > 0
        if band.dtype.kind == "f":
            valid &= np.isfinite(band)  # NaN is "no data", also if the file does not say so

        rows.append(("values", _describe_values(raster.count, raster.dtypes[0], band, valid)))
        if unit:
            rows.append(("unit", unit))

        no_data_percent = 100 * (1 - valid.mean())
        rows.append(("no data", f"{no_data_percent:.1f} % of the pixels" if no_data_percent else "none"))

    rows += list((details or {}).items())

    label_width = max(len(label) for label, _ in rows)
    lines = [description or "Downloaded raster"]
    lines += [f"  {label:<{label_width}}  {text}" for label, text in rows]
    return "\n".join(lines)


def _location_rows(raster) -> list[tuple[str, str]]:
    """Extent (as longitude/latitude) and grid of the raster."""
    west, south, east, north = transform_bounds(raster.crs, "EPSG:4326", *raster.bounds)
    metres_per_degree_east = METRES_PER_DEGREE * cos(radians((south + north) / 2))
    width_km = (east - west) * metres_per_degree_east / 1000
    height_km = (north - south) * METRES_PER_DEGREE / 1000

    x_size, y_size = raster.res
    if raster.crs.is_geographic:
        # The pixel size is an angle, so translate it into metres for orientation.
        resolution = f"{x_size:.6g} degrees, about {x_size * metres_per_degree_east:.0f} m"
    else:
        unit_name = raster.crs.linear_units  # "metre" for UTM
        unit_name = "m" if unit_name == "metre" else unit_name
        resolution = f"{x_size:.6g} {unit_name}"
        if y_size != x_size:
            resolution = f"{x_size:.6g} x {y_size:.6g} {unit_name}"

    epsg = raster.crs.to_epsg()
    crs_name = f"EPSG:{epsg}" if epsg else "custom coordinate system"

    return [
        (
            "extent",
            f"west {west:.4f}, south {south:.4f}, east {east:.4f}, north {north:.4f} "
            f"(WGS 84), about {width_km:.1f} x {height_km:.1f} km",
        ),
        ("grid", f"{raster.width} x {raster.height} pixels of {resolution} ({crs_name})"),
    ]


def _describe_values(band_count: int, dtype: str, band: np.ndarray, valid: np.ndarray) -> str:
    """One line about the values of the first band."""
    if band_count > 1:
        return f"{band_count} bands, {dtype}"
    if not valid.any():
        return "no valid pixels"

    values = band[valid]
    if band.dtype.kind in "iu":
        different = np.unique(values)
        if len(different) <= MAX_LISTED_VALUES:
            return "found: " + ", ".join(str(value) for value in different)
        return f"{values.min()} to {values.max()}, mean {values.mean():.4g}"
    return f"{values.min():.4g} to {values.max():.4g}, mean {values.mean():.4g}"


def _file_size(path: Path) -> str:
    size = path.stat().st_size
    if size < 1024 * 1024:
        return f"{size / 1024:.0f} KB"
    return f"{size / 1024 / 1024:.1f} MB"
