from __future__ import annotations

from numbers import Integral
from pathlib import Path
from typing import Sequence

from openeo.processes import array_contains, not_

from .postprocessing import enhance_color_raster
from .util import (
    OverviewResampling,
    SpatialExtent,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_tci(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    max_cloud_cover: int = 20,
    enhance_color: bool = True,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    scl_classes: Sequence[int] | None = (4, 5, 6),
) -> Path:
    """Download mean Sentinel-2 true-colour reflectance with SCL masking.

    The output retains the 10 m reflectance grid; SCL classification detail
    remains 20 m.

    Parameters
    ----------
    file_path:
        Destination GeoTIFF path. Missing parent directories are created.
    spatial_extent:
        Area to download, such as an openEO bounding-box dictionary.
    temporal_extent:
        Start and end of the observation period.
    max_cloud_cover:
        Maximum scene-level cloud cover in percent.
    enhance_color:
        If ``True``, enhance reflectance to an 8-bit RGB image.
    create_cog:
        If ``True``, write a Cloud Optimized GeoTIFF.
    overview_resampling:
        Resampling method used to build COG overview levels.
    scl_classes:
        Scene Classification Layer (SCL) class IDs to **keep** before
        averaging. The default ``(4, 5, 6)`` keeps vegetation, non-vegetated
        land and water, excluding clouds, cirrus, shadows, snow/ice,
        unclassified and defective pixels. Add ``11`` to keep snow/ice.
        Use ``None`` to disable SCL masking. A custom selection must be
        non-empty and contain integer IDs from 0 to 11. Pixels without any
        retained observations remain no data, also after colour enhancement.
        This pixel filter complements ``max_cloud_cover``.

    Returns
    -------
    Path
        Absolute path to the downloaded RGB raster.
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

    # Load red (B04), green (B03), blue (B02) and optionally SCL together.
    # The Copernicus backend aligns these bands on the 10 m reflectance grid.
    bands = ["B04", "B03", "B02"]
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
        cube = cube.filter_bands(["B04", "B03", "B02"])
        cube = cube.mask(mask)

    # Average the retained observations, then scale to reflectance.
    # Masked observations are no data and do not contribute to the mean.
    cube = cube.mean_time()
    cube = cube.apply(lambda value: value * 0.0001)

    return download_raster_cube(
        cube=cube,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
        postprocess=enhance_color_raster if enhance_color else None,
    )
