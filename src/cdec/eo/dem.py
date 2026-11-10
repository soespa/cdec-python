from __future__ import annotations

from pathlib import Path

from .util import (
    DEFAULT_DEM_TEMPORAL_EXTENT,
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_dem(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent = DEFAULT_DEM_TEMPORAL_EXTENT,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
) -> Path:
    """Download a Copernicus digital elevation model.

    The function loads the ``DEM`` band from the static ``COPERNICUS_30``
    openEO collection and reduces its time dimension to one elevation raster.
    The collection's known acquisition period is used by default, so users do
    not have to provide a temporal extent.

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
        available Copernicus DEM data and normally does not need to be changed.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF. If ``False``, keep a
        regular GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"average"``
        is a suitable default for continuous elevation data.

    Returns
    -------
    Path
        Absolute path to the downloaded raster file.
    """

    connection = get_connection()

    cube = connection.load_collection(
        collection_id="COPERNICUS_30",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=["DEM"],
    )

    cube = cube.mean_time()

    return download_raster_cube(
        cube=cube,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
    )
