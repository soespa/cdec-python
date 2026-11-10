from __future__ import annotations

from numbers import Integral
from pathlib import Path
from typing import Sequence

from openeo.processes import array_contains, not_

from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_evi(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    max_cloud_cover: int = 20,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    scl_classes: Sequence[int] | None = (4, 5),
) -> Path:
    """Download a Sentinel-2 Enhanced Vegetation Index (EVI) raster.

    Blue, red and near-infrared reflectance from Sentinel-2 Level-2A are
    masked using the Scene Classification Layer (SCL), then averaged over
    the requested period before calculating EVI:

    ``EVI = 2.5 * (NIR - red) / (NIR + 6 * red - 7.5 * blue + 1)``

    The output retains the 10 m reflectance grid; SCL classification detail
    remains 20 m. As with :func:`cdec.download_ndvi`, the index is calculated
    from mean reflectance, rather than averaging indices from individual dates.

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
    max_cloud_cover:
        Maximum scene-level cloud cover in percent.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels.
    scl_classes:
        SCL class IDs to **keep** before averaging. The default ``(4, 5)``
        keeps vegetation and non-vegetated land, excluding water, clouds,
        cirrus, shadows, snow/ice, unclassified and defective pixels.
        Use ``(4, 5, 6)`` to also include water, or ``None`` to disable SCL
        masking. A custom selection must be non-empty and contain integer
        IDs from 0 to 11. Pixels without any retained observations remain
        no data. This pixel filter complements ``max_cloud_cover``.

    Returns
    -------
    Path
        Absolute path to the downloaded EVI raster.
    """
    # Check the class IDs before connecting to the backend.
    if scl_classes is not None:
        scl_classes = tuple(scl_classes)
        if not scl_classes or any(
            isinstance(value, bool)
            or not isinstance(value, Integral)
            or not 0 <= value <= 11
            for value in scl_classes
        ):
            raise ValueError(
                "scl_classes must be a non-empty sequence of integer class IDs "
                "from 0 to 11, or None to disable SCL masking."
            )
        scl_classes = [int(value) for value in scl_classes]

    connection = get_connection()

    # Load blue (B02), red (B04), near-infrared (B08) and optionally SCL together.
    # The Copernicus backend aligns these bands on the 10 m reflectance grid.
    bands = ["B02", "B04", "B08"]
    if scl_classes is not None:
        bands.append("SCL")

    cube = connection.load_collection(
        collection_id="SENTINEL2_L2A",
        spatial_extent=spatial_extent,
        temporal_extent=temporal_extent,
        bands=bands,
        max_cloud_cover=max_cloud_cover,
    )

    if scl_classes is not None:
        # A True mask value removes an observation. Keep only the selected
        # classes; missing SCL values are also excluded by this condition.
        scl = cube.band("SCL")
        mask = scl.apply(lambda value: not_(array_contains(scl_classes, value)))

        # SCL contains class IDs, so remove it before averaging reflectance.
        cube = cube.filter_bands(["B02", "B04", "B08"])
        cube = cube.mask(mask)

    # Average the retained observations. Masked values do not contribute.
    cube = cube.mean_time()

    # Convert digital numbers to reflectance before calculating EVI.
    # This is essential because the formula adds the constant 1.0.
    cube = cube.apply(lambda value: value * 0.0001)

    blue = cube.band("B02")
    red = cube.band("B04")
    nir = cube.band("B08")
    evi = 2.5 * (nir - red) / (nir + 6.0 * red - 7.5 * blue + 1.0)

    return download_raster_cube(
        cube=evi,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
    )
