from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio

from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


WORLDCOVER_TEMPORAL_EXTENT: tuple[str, str] = (
    "2021-01-01T00:00:00Z",
    "2021-12-31T23:59:59Z",
)

WORLDCOVER_CLASSES: dict[int, str] = {
    10: "Tree cover",
    20: "Shrubland",
    30: "Grassland",
    40: "Cropland",
    50: "Built-up",
    60: "Bare / sparse vegetation",
    70: "Snow and ice",
    80: "Permanent water bodies",
    90: "Herbaceous wetland",
    95: "Mangroves",
    100: "Moss and lichen",
}

WORLDCOVER_COLORS: dict[int, str] = {
    10: "#006400",
    20: "#ffbb22",
    30: "#ffff4c",
    40: "#f096ff",
    50: "#fa0000",
    60: "#b4b4b4",
    70: "#f0f0f0",
    80: "#0064c8",
    90: "#0096a0",
    95: "#00cf75",
    100: "#fae6a0",
}


def _apply_worldcover_colormap(raster_path: Path) -> None:
    """Attach the official WorldCover colour table to a class-ID raster.

    A GeoTIFF colour table only works for integer bands. For any other data
    type (for example float32) rasterio would silently skip the colour table,
    so such a raster is converted to ``uint8`` first. That is safe because
    the largest WorldCover class ID is 100.
    """
    colormap = {
        value: (*bytes.fromhex(color.removeprefix("#")), 255)
        for value, color in WORLDCOVER_COLORS.items()
    }

    with rasterio.open(raster_path) as raster:
        data_type = raster.dtypes[0]
        if data_type != "uint8":
            class_ids = raster.read(1)
            profile = raster.profile

    if data_type != "uint8":
        class_ids = np.clip(np.nan_to_num(class_ids, nan=0), 0, 255).astype("uint8")
        profile.update(dtype="uint8", count=1, nodata=0)  # class 0 = no data
        with rasterio.open(raster_path, "w", **profile) as raster:
            raster.write(class_ids, 1)

    with rasterio.open(raster_path, "r+") as raster:
        raster.write_colormap(1, colormap)


def download_land_cover(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent = WORLDCOVER_TEMPORAL_EXTENT,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "nearest",
) -> Path:
    """Download the ESA WorldCover 2021 land-cover map at 10 m resolution.

    The resulting raster contains integer class IDs in its ``MAP`` band. An
    ESA WorldCover color table is attached to the GeoTIFF for visualization.

    Parameters
    ----------
    file_path:
        Destination path of the GeoTIFF file. Missing parent directories are
        created automatically.
    spatial_extent:
        Area to download: an openEO bounding-box dictionary such as
        ``{"west": 8.7, "south": 53.0, "east": 8.9, "north": 53.1}`` (degrees,
        WGS 84), a Shapely geometry, or the path to a GeoJSON file.
    temporal_extent:
        Collection period used for the openEO request. The default covers the
        static 2021 WorldCover product and normally does not need changing.
        Other years find no data in this collection.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF. If ``False``, keep a
        regular GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"nearest"``
        preserves categorical class IDs and should normally not be changed.

    Returns
    -------
    Path
        Absolute path of the GeoTIFF that was written. The file has one band of
        8-bit integers (``uint8``): the WorldCover class of every pixel (10,
        20, ... 100; ``cdec.WORLDCOVER_CLASSES`` has the names). 0 means no
        data and is declared as the no-data value. The colours of the classes
        are stored in the file as a colour table. The coordinate system is
        geographic (EPSG:4326, degrees); the pixel size is 0.000083 degrees,
        about 10 m.
    """
    connection = get_connection()

    cube = connection.load_collection(
        collection_id="ESA_WORLDCOVER_10M_2021_V2",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=["MAP"],
    )
    cube = cube.max_time()

    return download_raster_cube(
        cube=cube,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
        postprocess=_apply_worldcover_colormap,
    )
