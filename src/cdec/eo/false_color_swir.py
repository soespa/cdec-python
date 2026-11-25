from __future__ import annotations

from pathlib import Path
from typing import Sequence

from openeo.processes import array_contains, not_

from .postprocessing import enhance_contrast_raster
from .scl import SCL_LAND_AND_WATER, check_scl_classes
from .summary import sentinel2_details
from .util import (
    OverviewResampling,
    SpatialExtent,
    SENTINEL2_REFLECTANCE_SCALE,
    TemporalExtent,
    download_raster_cube,
    get_connection,
)


def download_false_color_swir(
    file_path: str | Path,
    spatial_extent: SpatialExtent,
    temporal_extent: TemporalExtent,
    max_cloud_cover: int = 20,
    scl_classes: Sequence[int] | None = SCL_LAND_AND_WATER,
    enhance_contrast: bool = True,
    *,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    verbose: bool = True,
) -> Path:
    """Download a Sentinel-2 false-colour SWIR composite.

    B12, B8A and B04 are displayed as red, green and blue, respectively.
    Observations are masked using SCL, averaged over the requested period,
    and then enhanced for display by stretching contrast and compressing
    highlights. The output grid is 10 m; B12, B8A and SCL retain their
    native 20 m detail.

    Parameters
    ----------
    file_path:
        Destination GeoTIFF path. Missing parent directories are created.
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
        class IDs. The default ``SCL_LAND_AND_WATER`` = ``(4, 5, 6)`` keeps
        vegetation, non-vegetated land and water and drops clouds, cirrus,
        shadows, snow/ice, unclassified and defective pixels. Add ``11`` to
        keep snow/ice, or use ``None`` to switch SCL masking off. Run
        ``cdec.show_scl_classes()`` to see what each class means. Pixels
        without any retained observation remain no data, also after contrast
        enhancement.
    enhance_contrast:
        If ``True``, create an 8-bit RGB image using a reflectance stretch
        of 0..0.4 with highlight compression. The stretch is fixed: it does
        not look at the values of the image, so the same reflectance always
        gets the same colour, and images of different dates or places can be
        compared by eye. If ``False``, retain the three bands as
        floating-point reflectance values (use this for calculations).
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
        Absolute path to the downloaded SWIR composite.
    """
    # Check the class IDs before connecting to the backend.
    scl_classes = check_scl_classes(scl_classes)

    connection = get_connection()

    # Map short-wave infrared (B12), narrow near-infrared (B8A) and red (B04) to the RGB display channels.
    # Loading them together keeps the 10 m grid of B04; B12 and B8A detail stays 20 m.
    reflectance_bands = ["B12", "B8A", "B04"]
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

    return download_raster_cube(
        cube=cube,
        file_path=file_path,
        create_cog=create_cog,
        overview_resampling=overview_resampling,
        verbose=verbose,
        description="False-colour SWIR composite from Sentinel-2 L2A (B12, B8A, B04 as red, green, blue)",
        unit=(
            "8-bit colour image (0-255), fixed contrast stretch"
            if enhance_contrast
            else "reflectance (0 = black, 1 = white)"
        ),
        details=sentinel2_details(temporal_extent, max_cloud_cover, scl_classes),
        postprocess=enhance_contrast_raster if enhance_contrast else None,
    )


# Short name for the same function, kept for convenience.
download_swir = download_false_color_swir
