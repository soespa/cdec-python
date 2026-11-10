from __future__ import annotations

from pathlib import Path
from typing import Literal

from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_swi(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    depth: Literal[2, 5, 10, 15, 20, 40, 60, 100] = 2,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
) -> Path:

    connection = get_connection()

    platform = "CLMS_SWI_EUROPE_1KM_DAILY_V2"
    band = f'swi{str(depth).zfill(3)}'

    cube = connection.load_collection(
        collection_id=platform,
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
    )
