from __future__ import annotations

from pathlib import Path

from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_lst(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
) -> Path:
    """Download mean land surface temperature data from Sentinel-3.

    The function loads the ``LST`` band from the
    ``SENTINEL3_SLSTR_L2_LST`` openEO collection and calculates the temporal
    mean for the requested period. Values in the resulting raster are stored
    in Kelvin.

    Parameters
    ----------
    file_path:
        Destination path of the GeoTIFF file. Missing parent directories are
        created automatically.
    spatial_extent:
        Area to download, for example an openEO bounding-box dictionary, a
        Shapely geometry, or a path to a vector file.
    temporal_extent:
        Start and end of the requested period, for example
        ``["2024-06-01", "2024-08-31"]``.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF. If ``False``, keep a
        regular GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"average"``
        is a suitable default for continuous temperature data.

    Returns
    -------
    Path
        Absolute path to the downloaded raster file.
    """

    connection = get_connection()

    cube = connection.load_collection(
        collection_id="SENTINEL3_SLSTR_L2_LST",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=["LST"],
    )

    cube = cube.mean_time()

    return download_raster_cube(
        cube=cube,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
    )
