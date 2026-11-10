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


BACKEND_URL = "https://openeo.dataspace.copernicus.eu/"

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
    return openeo.connect(BACKEND_URL).authenticate_oidc()


def prepare_output_path(file_path: str | Path) -> Path:
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
    output_path = prepare_output_path(file_path)

    if not create_cog and postprocess is None:
        cube.download(outputfile=output_path, format="GTiff")
        return output_path

    with TemporaryDirectory(
        dir=output_path.parent,
        prefix=f".{output_path.stem}_",
    ) as temporary_directory:
        temporary_directory = Path(temporary_directory)
        source_tif = temporary_directory / "source.tif"
        temporary_cog = temporary_directory / "result_cog.tif"

        cube.download(outputfile=source_tif, format="GTiff")

        if postprocess is not None:
            postprocess(source_tif)

        if not create_cog:
            source_tif.replace(output_path)
            return output_path

        cog_profile = cog_profiles.get("deflate")
        if cog_profile is None:
            raise RuntimeError("COG profile 'deflate' konnte nicht geladen werden.")

        cog_translate(
            source=source_tif,
            dst_path=temporary_cog,
            dst_kwargs=dict(cog_profile),
            overview_resampling=overview_resampling,
            in_memory=False,
            quiet=True,
        )

        temporary_cog.replace(output_path)

    return output_path


def resolve_spatial_extent():
    pass
