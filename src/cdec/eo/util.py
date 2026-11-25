"""Shared helpers used by all ``download_*`` functions.

Every download function in this package follows the same recipe:

1. connect to the openEO backend,
2. describe the wanted data as an openEO *data cube* (load, mask, average, ...),
3. hand the cube to :func:`download_raster_cube`, which downloads it and
   writes the final GeoTIFF / Cloud Optimized GeoTIFF.

Steps 1 and 3 live here. Step 2 is deliberately kept inside each
``download_*`` function so that it can be read from top to bottom.
"""

from __future__ import annotations

from datetime import date
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Literal, Sequence, TypeAlias

import openeo
from rio_cogeo.cogeo import cog_translate
from rio_cogeo.profiles import cog_profiles
from shapely.geometry.base import BaseGeometry

from .postprocessing import RasterPostprocess


#: Address of the Copernicus Data Space openEO backend.
BACKEND_URL = "https://openeo.dataspace.copernicus.eu/"

#: Sentinel-2 L2A is stored as integers. Multiplying by this factor gives
#: reflectance between 0 (black) and 1 (perfectly white).
SENTINEL2_REFLECTANCE_SCALE = 0.0001

#: Static data sets (they do not change over time) still need a temporal extent
#: in openEO. This is the acquisition period of the elevation model.
DEFAULT_DEM_TEMPORAL_EXTENT: tuple[str, str] = (
    "2010-12-12T00:00:00Z",
    "2015-01-16T00:00:00Z",
)

SpatialExtent: TypeAlias = dict | BaseGeometry | str | Path
TemporalExtent: TypeAlias = Sequence[str | date] | str | None
OverviewResampling: TypeAlias = Literal[
    "nearest",
    "bilinear",
    "cubic",
    "cubic_spline",
    "lanczos",
    "average",
    "mode",
    "gauss",
    "rms",
]


def get_connection():
    """Connect to the Copernicus Data Space openEO backend and log in.

    The first call opens a login (device code flow). The openEO client stores
    a refresh token, so later calls log in silently.
    """
    return openeo.connect(BACKEND_URL).authenticate_oidc()


def prepare_output_path(file_path: str | Path) -> Path:
    """Return the absolute output path and create missing parent folders."""
    output_path = Path(file_path).expanduser().resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    return output_path


def download_raster_cube(
    cube,
    file_path: str | Path,
    create_cog: bool = True,
    overview_resampling: OverviewResampling = "average",
    postprocess: RasterPostprocess | None = None,
) -> Path:
    """Download an openEO data cube as GeoTIFF and return the final path.

    The cube is first downloaded into a hidden temporary folder next to the
    target file. Only when everything succeeded (download, optional
    ``postprocess``, optional COG conversion) is the finished file moved to
    ``file_path``. A failed download therefore never leaves a half-written
    file behind and never overwrites an existing good file.

    Parameters
    ----------
    cube:
        openEO data cube that already contains the final result.
    file_path:
        Destination path. Missing parent folders are created.
    create_cog:
        If ``True``, convert the download to a Cloud Optimized GeoTIFF.
    overview_resampling:
        Resampling method for the COG overview levels. Use ``"nearest"`` for
        categorical data such as land cover.
    postprocess:
        Optional function that receives the path of the downloaded GeoTIFF and
        rewrites it in place (e.g. colour enhancement).
    """
    output_path = prepare_output_path(file_path)

    with TemporaryDirectory(
        dir=output_path.parent,
        prefix=f".{output_path.stem}_",
    ) as temporary_name:
        temporary_directory = Path(temporary_name)
        source_tif = temporary_directory / "source.tif"

        cube.download(outputfile=source_tif, format="GTiff")

        if postprocess is not None:
            postprocess(source_tif)

        if create_cog:
            cog_tif = temporary_directory / "result_cog.tif"
            cog_translate(
                source=source_tif,
                dst_path=cog_tif,
                dst_kwargs=dict(cog_profiles.get("deflate")),
                overview_resampling=overview_resampling,
                in_memory=False,
                quiet=True,
            )
            result_tif = cog_tif
        else:
            result_tif = source_tif

        result_tif.replace(output_path)

    return output_path
