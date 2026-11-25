from __future__ import annotations

from pathlib import Path
from typing import Sequence

from openeo.processes import array_contains, not_

from .scl import SCL_LAND_WATER_AND_SNOW, check_scl_classes
from .summary import sentinel2_details
from .util import (
    OverviewResampling,
    SpatialExtent,
    SENTINEL2_REFLECTANCE_SCALE,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_normalized_difference_snow_index(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    max_cloud_cover: int = 20,
    scl_classes: Sequence[int] | None = SCL_LAND_WATER_AND_SNOW,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    verbose: bool = True,
) -> Path:
    """Download a Sentinel-2 NDSI (snow index) raster.

    Green and short-wave infrared (B11) reflectance from Sentinel-2 Level-2A
    are masked using the Scene Classification Layer (SCL), then averaged over
    the requested period before calculating the Normalized Difference Snow
    Index:

    ``NDSI = (green - SWIR) / (green + SWIR)``

    Snow is bright in green light and dark in short-wave infrared light, so
    the index is high over snow and ice. The output retains the 10 m
    reflectance grid; B11 and the SCL keep their native 20 m detail.

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
        cloudier are not used at all. This scene filter complements
        ``scl_classes``, which removes single pixels.
    scl_classes:
        Scene Classification Layer (SCL) classes to **keep**, as a tuple of
        class IDs. The default ``SCL_LAND_WATER_AND_SNOW`` = ``(4, 5, 6, 11)``
        keeps vegetation, non-vegetated land, water and snow or ice and drops
        clouds, cirrus, shadows, unclassified and defective pixels. Do not
        remove class ``11``: it is the snow that this index looks for. Use
        ``None`` to switch SCL masking off. Run ``cdec.show_scl_classes()`` to
        see what each class means. Pixels without any retained observation
        remain no data.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels.
    verbose:
        If ``True`` (the default), print a short summary of the downloaded
        file: extent, grid and resolution, value range and the share of
        pixels without data.

    Returns
    -------
    Path
        Absolute path to the downloaded NDSI raster.
    """
    # Check the class IDs before connecting to the backend.
    scl_classes = check_scl_classes(scl_classes)

    connection = get_connection()

    # Load green (B03), short-wave infrared (B11) and optionally SCL together.
    # Loading them together keeps the 10 m grid of B03; B11 detail stays 20 m.
    reflectance_bands = ["B03", "B11"]
    bands_to_load = list(reflectance_bands)
    if scl_classes is not None:
        bands_to_load.append("SCL")

    cube = connection.load_collection(
        collection_id="SENTINEL2_L2A",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=bands_to_load,
        max_cloud_cover=max_cloud_cover,
    )

    if scl_classes is not None:
        # A True mask value removes an observation. Keep only the selected
        # classes; missing SCL values are also excluded by this condition.
        scl = cube.band("SCL")
        mask = scl.apply(lambda value: not_(array_contains(scl_classes, value)))

        # SCL contains class IDs, so remove it before averaging reflectance.
        cube = cube.filter_bands(reflectance_bands)
        cube = cube.mask(mask)

    # Average the retained observations, then scale to reflectance.
    # Masked observations are no data and do not contribute to the mean.
    cube = cube.mean_time()
    cube = cube.apply(lambda value: value * SENTINEL2_REFLECTANCE_SCALE)

    # Calculate NDSI from the mean green and short-wave infrared reflectance.
    green = cube.band("B03")
    swir = cube.band("B11")
    ndsi = (green - swir) / (green + swir)

    return download_raster_cube(
        cube=ndsi,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
        verbose=verbose,
        description="NDSI from Sentinel-2 L2A (mean of the period)",
        unit="no unit (index from -1 to 1)",
        details=sentinel2_details(temporal_extent, max_cloud_cover, scl_classes),
    )


# Short name for the same function, kept for convenience.
download_ndsi = download_normalized_difference_snow_index
