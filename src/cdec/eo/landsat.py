from __future__ import annotations

from pathlib import Path

from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_landsat(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
) -> Path:
    """Download an NDVI raster from the Landsat bi-monthly mosaic.

    The source collection provides reconstructed, cloud-free Landsat mosaics
    at 30 metre resolution from 1997 through 2024. Red and near-infrared bands are
    averaged over the requested period before calculating NDVI.

    Parameters
    ----------
    file_path:
        Destination path of the GeoTIFF file. Missing parent directories are
        created automatically.
    spatial_extent:
        Area to download, for example an openEO bounding-box dictionary, a
        Shapely geometry, or a path to a vector file.
    temporal_extent:
        Start and end of the observation period.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels.

    Returns
    -------
    Path
        Absolute path to the downloaded NDVI raster.
    """
    connection = get_connection()

    cube = connection.load_collection(
        collection_id="LANDSAT_BIMONTHLY_MOSAIC",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=["B03", "B04"],
    )

    cube = cube.mean_time()
    red = cube.band("B03")
    nir = cube.band("B04")
    ndvi = (nir - red) / (nir + red)

    return download_raster_cube(
        cube=ndvi,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
    )
