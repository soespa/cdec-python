from __future__ import annotations

from pathlib import Path

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
    colormap = {
        value: (*bytes.fromhex(color.removeprefix("#")), 255)
        for value, color in WORLDCOVER_COLORS.items()
    }

    with rasterio.open(raster_path, "r+") as raster:
        raster.write_colormap(1, colormap)


def download_land_cover(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent = WORLDCOVER_TEMPORAL_EXTENT,
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
        Area to download, for example an openEO bounding-box dictionary, a
        Shapely geometry, or a path to a vector file.
    temporal_extent:
        Collection period used for the openEO request. The default covers the
        static 2021 WorldCover product and normally does not need changing.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF. If ``False``, keep a
        regular GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"nearest"``
        preserves categorical class IDs and should normally not be changed.

    Returns
    -------
    Path
        Absolute path to the downloaded land-cover raster.
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
