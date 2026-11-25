"""Tests of the shared helper functions in ``cdec.eo.util`` (offline)."""

import pytest
import rasterio

from cdec.eo.util import download_raster_cube, prepare_output_path

from .helpers import write_test_raster


# ----------------------------------------------------------------------------
# prepare_output_path
# ----------------------------------------------------------------------------
def test_prepare_output_path_creates_folders_and_returns_absolute_path(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)

    result = prepare_output_path("a/b/result.tif")  # relative path

    assert result == (tmp_path / "a" / "b" / "result.tif").resolve()
    assert result.parent.is_dir()
    assert not result.exists()  # only the folders are created


def test_prepare_output_path_expands_the_home_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))

    result = prepare_output_path("~/downloads/result.tif")

    assert result == (tmp_path / "downloads" / "result.tif").resolve()


# ----------------------------------------------------------------------------
# download_raster_cube
# ----------------------------------------------------------------------------
class WorkingCube:
    """Minimal stand-in for an openEO data cube: 'downloads' a made-up GeoTIFF."""

    def download(self, outputfile, format):
        assert format == "GTiff"
        write_test_raster(outputfile, count=1, empty_columns=0)


class BrokenCube:
    """A cube whose download fails, as when the connection drops."""

    def download(self, outputfile, format):
        write_test_raster(outputfile, count=1)  # a half-finished file is on disk ...
        raise ConnectionError("connection lost")  # ... when the error happens


@pytest.mark.parametrize("create_cog", [True, False])
def test_download_raster_cube_leaves_only_the_result(tmp_path, create_cog):
    target = tmp_path / "result.tif"

    returned = download_raster_cube(WorkingCube(), target, create_cog=create_cog)

    assert returned == target
    assert list(tmp_path.iterdir()) == [target]


def test_failed_download_leaves_no_partial_file(tmp_path):
    target = tmp_path / "result.tif"

    with pytest.raises(ConnectionError):
        download_raster_cube(BrokenCube(), target)

    assert list(tmp_path.iterdir()) == []


def test_failed_download_keeps_an_existing_good_file(tmp_path):
    target = tmp_path / "result.tif"
    write_test_raster(target, count=1, empty_columns=0)
    size_before = target.stat().st_size

    with pytest.raises(ConnectionError):
        download_raster_cube(BrokenCube(), target)

    assert target.stat().st_size == size_before
    with rasterio.open(target) as raster:  # still readable
        assert raster.count == 1
    assert list(tmp_path.iterdir()) == [target]


def test_postprocess_function_runs_before_the_cog_is_made(tmp_path):
    def make_two_bands(path):
        write_test_raster(path, count=2, empty_columns=0)

    result = download_raster_cube(WorkingCube(), tmp_path / "result.tif", postprocess=make_two_bands)

    with rasterio.open(result) as raster:
        assert raster.count == 2
        assert raster.profile["tiled"] is True  # COG conversion came afterwards
