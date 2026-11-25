from __future__ import annotations

from pathlib import Path

from .summary import format_period
from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_land_surface_temperature(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    verbose: bool = True,
) -> Path:
    """Download mean land surface temperature data from Sentinel-3.

    The function loads the ``LST`` band from the
    ``SENTINEL3_SLSTR_L2_LST`` openEO collection and calculates the temporal
    mean for the requested period. Values in the resulting raster are stored
    in Kelvin. No cloud masking is applied: the mean contains every observation
    the backend delivers.

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
        Start and end of the requested period, e.g.
        ``["2024-06-01", "2024-07-01"]``. The end date itself is *not*
        included, so this example covers all of June.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF. If ``False``, keep a
        regular GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"average"``
        is a suitable default for continuous temperature data.
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
        verbose=verbose,
        description="Land surface temperature from Sentinel-3 SLSTR (mean of the period)",
        unit="Kelvin (subtract 273.15 for degrees Celsius)",
        details={
            "period": format_period(temporal_extent),
            "clouds": "no cloud masking",
        },
    )


# Short name for the same function, kept for convenience.
download_lst = download_land_surface_temperature
