"""Soil Water Index (SWI) from the Copernicus Land Monitoring Service (CLMS)."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from .summary import format_period
from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


SWI_COLLECTION_ID = "CLMS_SWI_EUROPE_1KM_DAILY_V2"

# Characteristic time lengths T (in days) of the SWI bands "swi002" ... "swi100".
# A small T reacts quickly to rain (topsoil), a large T describes deeper soil.
SWI_DEPTHS: tuple[int, ...] = (2, 5, 10, 15, 20, 40, 60, 100)


def download_soil_water_index(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    depth: Literal[2, 5, 10, 15, 20, 40, 60, 100] = 2,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    verbose: bool = True,
) -> Path:
    """Download the mean Soil Water Index (SWI) of a period.

    The function loads one SWI band from the ``CLMS_SWI_EUROPE_1KM_DAILY_V2``
    openEO collection (Europe, 1 km, daily) and calculates the temporal mean
    for the requested period. The SWI describes soil moisture in percent
    (0 = dry, 100 = saturated) according to the CLMS product description.

    Check the dates before you use this function: CLMS publishes *version 2*
    of the 1 km SWI from 2025-07-13 onwards, while version 1 covers 2015 up to
    2025-07-12. Earlier periods may therefore find no data in this collection.
    CDSE also labels its openEO CLMS collections as experimental.

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
        ``["2025-08-01", "2025-09-01"]``. The end date itself is *not*
        included, so this example covers all of August.
    depth:
        Characteristic time length T of the SWI in days. One of
        2, 5, 10, 15, 20, 40, 60 or 100. Small values describe the topsoil,
        large values the deeper and slower soil layers.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF. If ``False``, keep a
        regular GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels. ``"average"``
        is a suitable default for continuous data.
    verbose:
        If ``True`` (the default), print a short summary of the downloaded
        file: extent, grid and resolution, value range and the share of
        pixels without data.

    Returns
    -------
    Path
        Absolute path to the downloaded SWI raster.

    Raises
    ------
    ValueError
        If ``depth`` is not one of the available values. This is checked
        before connecting to the backend.
    """
    # Check the depth before connecting to the backend.
    if depth not in SWI_DEPTHS:
        raise ValueError(f"depth must be one of {SWI_DEPTHS}, got {depth!r}.")

    connection = get_connection()

    # The bands are called swi002, swi005, ... swi100.
    band = f"swi{int(depth):03d}"

    cube = connection.load_collection(
        collection_id=SWI_COLLECTION_ID,
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=[band],
    )

    cube = cube.mean_time()

    return download_raster_cube(
        cube=cube,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
        verbose=verbose,
        description="Soil Water Index from CLMS (mean of the period)",
        unit="percent (0 = dry, 100 = saturated)",
        details={
            "period": format_period(temporal_extent),
            "depth": f"T = {depth} days (small T: topsoil, large T: deeper soil)",
        },
    )


# Short name for the same function, kept for convenience.
download_swi = download_soil_water_index
