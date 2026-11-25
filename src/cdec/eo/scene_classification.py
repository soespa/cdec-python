from __future__ import annotations

from pathlib import Path

import numpy as np
import rasterio

from .scl import SCL_COLORS
from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def _apply_scl_colormap(raster_path: Path) -> None:
    """Attach the colour table of the scene classification map to a class-ID raster.

    A GeoTIFF colour table only works for integer bands. For any other data
    type (for example float32) rasterio would silently skip the colour table,
    so such a raster is converted to ``uint8`` first. That is safe because
    the largest SCL class ID is 11. Class 0 means no data: it is declared as
    the no-data value and is transparent in the colour table.
    """
    colormap = {
        value: (*bytes.fromhex(color.removeprefix("#")), 0 if value == 0 else 255)
        for value, color in SCL_COLORS.items()
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
        raster.nodata = 0  # class 0 = no data, also when the backend delivered integers
        raster.write_colormap(1, colormap)


def download_scene_classification_map(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    max_cloud_cover: int = 100,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "nearest",
) -> Path:
    """Download the Sentinel-2 scene classification map.

    The Scene Classification Layer (SCL) says for every 20 m pixel what it
    probably shows: vegetation, water, cloud, snow and so on (see
    ``cdec.show_scl_classes()``). Class numbers cannot be averaged, so every
    pixel keeps the class of its most recent observation in the requested
    period. The result contains the class IDs 1 to 11; 0 means no data. The
    colour table of the map is attached to the GeoTIFF.

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
        Start and end of the observation period, e.g.
        ``["2024-06-01", "2024-07-01"]``. The end date itself is *not*
        included, so this example covers all of June.
    max_cloud_cover:
        Maximum cloud cover of a whole scene in percent. Scenes that are
        cloudier are not used at all. The default of 100 uses every scene,
        because the clouds are what a classification map should show.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"nearest"``
        keeps the class IDs and should normally not be changed.

    Returns
    -------
    Path
        Absolute path of the GeoTIFF that was written. The file has one band of
        8-bit integers (``uint8``): the SCL class of every pixel, 1 to 11. 0
        means no data and is declared as the no-data value. The colours of the
        classes are stored in the file as a colour table, and
        ``cdec.show_scl_classes()`` explains the numbers. The pixel size is
        10 m, in the UTM zone of the area (EPSG:32632 for Bremen); the classes
        themselves have 20 m detail.
    """
    connection = get_connection()

    cube = connection.load_collection(
        collection_id="SENTINEL2_L2A",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=["SCL"],
        max_cloud_cover=max_cloud_cover,
    )

    # Class numbers have no meaningful average. Keep the most recent observation of every pixel.
    cube = cube.reduce_temporal("last")

    return download_raster_cube(
        cube=cube,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
        postprocess=_apply_scl_colormap,
    )


# Short name for the same function, kept for convenience.
download_scl = download_scene_classification_map
