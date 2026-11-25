from __future__ import annotations

from pathlib import Path
from typing import Sequence

from openeo.processes import array_contains, not_

from .scl import SCL_LAND, check_scl_classes
from .summary import sentinel2_details
from .util import (
    OverviewResampling,
    SpatialExtent,
    SENTINEL2_REFLECTANCE_SCALE,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_enhanced_vegetation_index(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    max_cloud_cover: int = 20,
    scl_classes: Sequence[int] | None = SCL_LAND,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    verbose: bool = True,
) -> Path:
    """Download a Sentinel-2 Enhanced Vegetation Index (EVI) raster.

    Blue, red and near-infrared reflectance from Sentinel-2 Level-2A are
    masked using the Scene Classification Layer (SCL), then averaged over
    the requested period before calculating EVI:

    ``EVI = 2.5 * (NIR - red) / (NIR + 6 * red - 7.5 * blue + 1)``

    The output retains the 10 m reflectance grid; SCL classification detail
    remains 20 m. As with :func:`cdec.download_normalized_difference_vegetation_index`, the index is calculated
    from mean reflectance, rather than averaging indices from individual dates.

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
        class IDs. The default ``SCL_LAND`` = ``(4, 5)`` keeps vegetation and
        non-vegetated land and drops water, clouds, cirrus, shadows, snow/ice,
        unclassified and defective pixels. Use ``SCL_LAND_AND_WATER`` =
        ``(4, 5, 6)`` to also keep water, or ``None`` to switch SCL masking
        off. Run ``cdec.show_scl_classes()`` to see what each class means.
        Pixels without any retained observation remain no data.
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
        Absolute path to the downloaded EVI raster.
    """
    # Check the class IDs before connecting to the backend.
    scl_classes = check_scl_classes(scl_classes)

    connection = get_connection()

    # Load blue (B02), red (B04), near-infrared (B08) and optionally SCL together.
    # The Copernicus backend aligns these bands on the 10 m reflectance grid.
    reflectance_bands = ["B02", "B04", "B08"]
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

    # Average the retained observations. Masked values do not contribute.
    cube = cube.mean_time()

    # Convert digital numbers to reflectance before calculating EVI.
    # This is essential because the formula adds the constant 1.0.
    cube = cube.apply(lambda value: value * SENTINEL2_REFLECTANCE_SCALE)

    blue = cube.band("B02")
    red = cube.band("B04")
    nir = cube.band("B08")
    evi = 2.5 * (nir - red) / (nir + 6.0 * red - 7.5 * blue + 1.0)

    return download_raster_cube(
        cube=evi,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
        verbose=verbose,
        description="EVI from Sentinel-2 L2A (mean of the period)",
        unit="no unit (index)",
        details=sentinel2_details(temporal_extent, max_cloud_cover, scl_classes),
    )


# Short name for the same function, kept for convenience.
download_evi = download_enhanced_vegetation_index
