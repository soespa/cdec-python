"""Tests of the colour / contrast enhancement (offline, with made-up rasters)."""

import numpy as np
import pytest
import rasterio

from cdec.eo.postprocessing import (
    enhance_color,
    enhance_color_raster,
    enhance_contrast,
    enhance_contrast_raster,
)

from .helpers import write_test_raster


# ----------------------------------------------------------------------------
# The number crunching on plain arrays
# ----------------------------------------------------------------------------
def gray_ramp(values):
    """Shape (3, 1, n): the same reflectance in red, green and blue."""
    return np.tile(np.array(values, dtype="float32"), (3, 1, 1))


def test_enhance_color_returns_8_bit_rgb():
    result = enhance_color(gray_ramp([0.0, 0.05, 0.1, 0.2, 0.4]))

    assert result.dtype == np.uint8
    assert result.shape == (3, 1, 5)


def test_enhance_color_keeps_black_black_and_gets_brighter_with_reflectance():
    result = enhance_color(gray_ramp([0.0, 0.05, 0.1, 0.2, 0.4]))

    assert (result[:, 0, 0] == 0).all()
    gray_levels = result[0, 0]
    assert (np.diff(gray_levels.astype(int)) > 0).all(), gray_levels


@pytest.mark.parametrize("shape", [(2, 4, 4), (4, 4, 4), (4, 4)])
def test_enhance_color_needs_exactly_three_bands(shape):
    with pytest.raises(ValueError, match="three|3"):
        enhance_color(np.zeros(shape))


def test_enhance_contrast_stretches_linearly_and_compresses_highlights():
    # default stretch is 0 ... 0.4 reflectance; everything above 0.8 is pure white
    values = np.array([-0.1, 0.0, 0.2, 0.36, 0.4, 0.6, 0.8, 5.0], dtype="float32")

    result = enhance_contrast(values)

    assert result[0] == 0 and result[1] == 0  # below the range -> black
    assert result[2] == pytest.approx(0.5)  # linear in the middle
    assert result[3] == pytest.approx(0.9)
    assert 0.92 < result[4] < result[5] < 1.0  # highlights are squeezed, not clipped
    assert result[6] == result[7] == 1.0
    assert (np.diff(result) >= 0).all()


def test_enhance_contrast_does_not_depend_on_the_other_pixels():
    """The stretch is fixed (0..0.4), not adapted to the image: same reflectance, same colour.

    This is what makes false-colour images of different dates or places comparable.
    """
    rng = np.random.default_rng(0)
    dark_scene = rng.uniform(0.0, 0.2, size=(3, 4, 4)).astype("float32")
    bright_scene = rng.uniform(0.2, 0.9, size=(3, 4, 4)).astype("float32")
    probe = np.full((3, 1, 1), 0.15, dtype="float32")  # the same pixel in both scenes

    colours = []
    for scene in (dark_scene, bright_scene):
        scene = scene.copy()
        scene[:, 0, 0] = probe[:, 0, 0]
        colours.append(enhance_contrast(scene)[:, 0, 0])

    assert np.allclose(colours[0], colours[1])
    assert np.allclose(colours[0], enhance_contrast(probe)[:, 0, 0])


def test_enhance_color_does_not_depend_on_the_other_pixels():
    rng = np.random.default_rng(1)
    dark_scene = rng.uniform(0.0, 0.1, size=(3, 4, 4)).astype("float32")
    bright_scene = rng.uniform(0.1, 0.6, size=(3, 4, 4)).astype("float32")
    probe = np.array([0.08, 0.06, 0.04], dtype="float32").reshape(3, 1, 1)

    colours = []
    for scene in (dark_scene, bright_scene):
        scene = scene.copy()
        scene[:, 0, 0] = probe[:, 0, 0]
        colours.append(enhance_color(scene)[:, 0, 0])

    assert np.array_equal(colours[0], colours[1])
    assert np.array_equal(colours[0], enhance_color(probe)[:, 0, 0])


@pytest.mark.parametrize("min_val, max_val", [(0.4, 0.4), (0.5, 0.1), (0.0, np.inf), (np.nan, 1.0)])
def test_enhance_contrast_rejects_a_bad_range(min_val, max_val):
    with pytest.raises(ValueError, match="max_val"):
        enhance_contrast(np.ones((3, 2, 2)), min_val=min_val, max_val=max_val)


# ----------------------------------------------------------------------------
# Rewriting a GeoTIFF file
# ----------------------------------------------------------------------------
RASTER_FUNCTIONS = [enhance_color_raster, enhance_contrast_raster]


@pytest.mark.parametrize("enhance_raster", RASTER_FUNCTIONS)
@pytest.mark.parametrize("declare_nodata", [True, False], ids=["nodata declared", "nodata not declared"])
def test_raster_becomes_rgb_and_keeps_its_empty_pixels(enhance_raster, declare_nodata, tmp_path):
    """Empty pixels (NaN) must stay empty, whether or not the file declares a nodata value."""
    path = tmp_path / "source.tif"
    write_test_raster(path, count=3, empty_columns=10, declare_nodata=declare_nodata)

    enhance_raster(path)

    with rasterio.open(path) as raster:
        assert raster.dtypes == ("uint8", "uint8", "uint8")
        mask = raster.read_masks(1)
        assert (mask[:, :10] == 0).all(), "empty pixels should be marked as no data"
        assert (mask[:, 10:] == 255).all(), "all other pixels should be valid"
        assert (raster.read()[:, :, :10] == 0).all(), "empty pixels should be black"
        assert raster.read()[:, :, 10:].std() > 0, "the picture should not be flat"
    assert list(tmp_path.iterdir()) == [path], "no sidecar or temporary files should be left"


@pytest.mark.parametrize("enhance_raster", RASTER_FUNCTIONS)
def test_raster_without_empty_pixels_is_fully_valid(enhance_raster, tmp_path):
    path = tmp_path / "source.tif"
    write_test_raster(path, count=3, empty_columns=0)

    enhance_raster(path)

    with rasterio.open(path) as raster:
        assert (raster.read_masks(1) == 255).all()


@pytest.mark.parametrize("enhance_raster", RASTER_FUNCTIONS)
@pytest.mark.parametrize("band_count", [1, 2, 4])
def test_raster_needs_exactly_three_bands(enhance_raster, band_count, tmp_path):
    path = tmp_path / "source.tif"
    write_test_raster(path, count=band_count)

    with pytest.raises(ValueError, match="three bands"):
        enhance_raster(path)
