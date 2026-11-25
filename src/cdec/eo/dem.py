from __future__ import annotations

from pathlib import Path

from .summary import format_period
from .util import (
    DEFAULT_DEM_TEMPORAL_EXTENT,
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_digital_elevation_model(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent = DEFAULT_DEM_TEMPORAL_EXTENT,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    verbose: bool = True,
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
        Area to download: an openEO bounding-box dictionary such as
        ``{"west": 8.7, "south": 53.0, "east": 8.9, "north": 53.1}`` (degrees,
        WGS 84), a Shapely geometry, or the path to a GeoJSON file.
    temporal_extent:
        Collection period used for the openEO request. The default covers the
        acquisition period of the Copernicus DEM and normally does not need to
        be changed: the DEM is a static data set, so a recent period such as
        June 2024 is outside of it and normally finds no data.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF. If ``False``, keep a
        regular GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"average"``
        is a suitable default for continuous elevation data.
    verbose:
        If ``True`` (the default), print a short summary of the downloaded
        file: extent, grid and resolution, value range and the share of
        pixels without data.

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
        verbose=verbose,
        description="Copernicus digital elevation model (30 m)",
        unit="metres",
        details={"period": format_period(temporal_extent)},
    )


# Short name for the same function, kept for convenience.
download_dem = download_digital_elevation_model
