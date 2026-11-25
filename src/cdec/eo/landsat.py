from __future__ import annotations

from pathlib import Path

from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_landsat_ndvi(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
) -> Path:
    """Download an NDVI raster from the Landsat bi-monthly mosaic.

    The source collection provides reconstructed, cloud-free Landsat mosaics
    at 30 metre resolution from 1997 through 2025. Red and near-infrared bands are
    averaged over the requested period before calculating NDVI. The mosaics are
    already cloud-free, so there is no cloud-cover or SCL masking here.

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
        included. The mosaics end on 2024-12-31, later dates find no data.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels.

    Returns
    -------
    Path
        Absolute path of the GeoTIFF that was written. The file has one band of
        floating-point numbers (``float32``): the NDVI, a number without unit
        between -1 and 1. Pixels without data are NaN, which the file declares
        as its no-data value. The coordinate system is geographic (EPSG:4326,
        degrees); the pixel size is 0.00025 degrees, about 30 m.
    """
    connection = get_connection()

    cube = connection.load_collection(
        collection_id="LANDSAT_BIMONTHLY_MOSAIC",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=["B03", "B04"],
    )

    # Band numbering of this collection: B03 is red and B04 is near-infrared
    # (Landsat 8 itself uses B04 and B05, so do not mix the two schemes up).
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


# Short name for the same function, kept for convenience.
download_landsat = download_landsat_ndvi
