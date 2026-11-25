"""Make downloaded Sentinel-2 composites look good on screen.

The ``download_*`` functions deliver *reflectance* (numbers between 0 and
about 1). That is correct for analysis, but looks dark and flat when shown as
a picture. The functions in this module turn three reflectance bands into an
8-bit RGB image:

* :func:`enhance_color`    - "true colour" look for red/green/blue bands
* :func:`enhance_contrast` - linear stretch with soft highlights (false colour)

The ``*_raster`` functions apply this to a GeoTIFF file on disk. They are
passed as ``postprocess=`` to ``download_raster_cube``.
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import rasterio


RasterPostprocess = Callable[[Path], None]


def enhance_color(data: np.ndarray) -> np.ndarray:
    """
    Apply the Sentinel-2 true-color enhancement to RGB reflectance data.

    Parameters
    ----------
    data:
        Array with shape ``(3, height, width)`` containing red, green, and
        blue reflectance values.

    Returns
    -------
    numpy.ndarray
        The enhanced image as 8-bit values (0 to 255), same shape as ``data``.

    Raises
    ------
    ValueError
        If ``data`` does not have the shape ``(3, height, width)``.
    """
    data = np.asarray(data, dtype=np.float32)
    if data.ndim != 3 or data.shape[0] != 3:
        raise ValueError(
            "enhance_color expects an array of shape (3, height, width) "
            "holding red, green and blue reflectance."
        )

    r, g, b = data[:3]

    maxR = 3.0
    midR = 0.13
    sat = 1.2
    gamma = 1.8

    gOff = 0.01
    gOffPow = np.power(gOff, gamma)
    gOffRange = np.power(1 + gOff, gamma) - gOffPow

    def clip(values):
        return np.clip(values, 0, 1)

    def sRGB(channel):
        return np.where(
            channel <= 0.0031308,
            12.92 * channel,
            1.055 * np.power(channel, 1 / 2.4) - 0.055,
        )

    def adjGamma(channel):
        return (np.power(channel + gOff, gamma) - gOffPow) / gOffRange

    def adj(channel, tx, ty, maxC):
        scaled = clip(channel / maxC)
        return scaled * (scaled * (tx / maxC + ty - 1) - ty) / (
            scaled * (2 * tx / maxC - 1) - tx / maxC
        )

    def sAdj(channel):
        return adjGamma(adj(channel, midR, 1, maxR))

    def satEnh(red, green, blue):
        avgS = (red + green + blue) / 3.0 * (1 - sat)
        return (
            clip(avgS + red * sat),
            clip(avgS + green * sat),
            clip(avgS + blue * sat),
        )

    r_adj = sAdj(r)
    g_adj = sAdj(g)
    b_adj = sAdj(b)
    rgb_linear = satEnh(r_adj, g_adj, b_adj)

    rgb = np.stack(
        [
            sRGB(rgb_linear[0]),
            sRGB(rgb_linear[1]),
            sRGB(rgb_linear[2]),
        ],
        axis=0,
    )

    return np.clip(rgb * 255, 0, 255).astype(np.uint8)


def enhance_contrast(
    data: np.ndarray,
    min_val: float = 0.0,
    max_val: float = 0.4,
) -> np.ndarray:
    """
    Stretch reflectance contrast while compressing bright highlights.

    This is a NumPy approximation of Sentinel Hub's HighlightCompressVisualizer.
    Input values are reflectance, typically in the range 0..1. The result
    contains display intensities in the range 0..1. The default stretch
    uses 0..0.4, as in the Sentinel-2 false-colour urban visualization.

    The stretch is fixed: it depends only on ``min_val`` and ``max_val``, never
    on the values in ``data``, so the same reflectance always gives the same
    intensity.

    Parameters
    ----------
    data:
        Array of reflectance values, any shape.
    min_val:
        Reflectance that is displayed as black (0).
    max_val:
        Reflectance at the top of the linear stretch, displayed at about 93 %
        brightness. Brighter values are compressed instead of clipped;
        a reflectance of ``2 * max_val - min_val`` and above is white (1).

    Returns
    -------
    numpy.ndarray
        Display intensities from 0 to 1, same shape as ``data``.

    Raises
    ------
    ValueError
        If ``max_val`` is not greater than ``min_val``, or if one of them is
        not finite.
    """
    if not np.isfinite(min_val) or not np.isfinite(max_val) or max_val <= min_val:
        raise ValueError("max_val must be greater than min_val, and both must be finite.")

    data = np.asarray(data, dtype=np.float32)
    t = (data - min_val) / (max_val - min_val)

    # Stretch dark and mid-range values linearly. Compress the highlights
    # into the last 8% of the display range instead of clipping them early.
    return np.where(
        t <= 0.0,
        0.0,
        np.where(
            t <= 0.92,
            t,
            np.where(
                t < 2.0,
                0.92 + (t - 0.92) * (0.08 / 1.08),
                1.0,
            ),
        ),
    )


def _valid_pixels(data: np.ma.MaskedArray) -> np.ndarray:
    """Return a ``(height, width)`` array that is True where every band has a usable value.

    A pixel counts as "without data" if the file flags it as nodata *or* if one
    of its values is NaN/infinite (a backend does not always declare a nodata
    value). ``data`` is what ``rasterio`` returns for ``read(masked=True)``.
    """
    values = np.ma.getdata(data)
    return ~np.ma.getmaskarray(data).any(axis=0) & np.isfinite(values).all(axis=0)


def _enhance_contrast_8bit(data: np.ndarray) -> np.ndarray:
    """:func:`enhance_contrast` with the result as 8-bit values (0 to 255), like a picture file."""
    return np.clip(enhance_contrast(data) * 255, 0, 255).astype(np.uint8)


def _rewrite_as_rgb(
    raster_path: str | Path,
    enhance: Callable[[np.ndarray], np.ndarray],
) -> None:
    """Rewrite a three-band reflectance GeoTIFF in place as an 8-bit RGB GeoTIFF.

    ``enhance`` receives the reflectance as a float array of shape
    ``(3, height, width)`` and returns the display values as ``uint8`` with the
    same shape.

    Pixels without data stay without data: they are black in the picture and
    marked as invalid in a mask that is stored inside the TIFF. A pixel counts
    as "without data" if the file flags it as nodata *or* if one of its values
    is NaN/infinite (a backend does not always declare a nodata value).
    """
    raster_path = Path(raster_path)
    temporary_output = raster_path.with_name(f"{raster_path.stem}_enhanced.tif")

    with rasterio.open(raster_path) as src:
        if src.count != 3:
            raise ValueError(
                f"Expected exactly three bands (red, green, blue), found {src.count}."
            )
        data = src.read(masked=True).astype(np.float32)
        profile = src.profile.copy()

    values = np.ma.getdata(data)
    valid_mask = _valid_pixels(data)

    # Enhance with a harmless 0.0 in the empty pixels, then paint them black.
    rgb = enhance(np.where(valid_mask, values, 0.0))
    rgb[:, ~valid_mask] = 0

    profile.update(dtype=rasterio.uint8, count=3, nodata=None, photometric="RGB")

    # Store the mask inside the TIFF so it stays attached when the file is moved.
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
        with rasterio.open(temporary_output, "w", **profile) as dst:
            dst.write(rgb)
            dst.write_mask(valid_mask.astype(np.uint8) * 255)

    temporary_output.replace(raster_path)


def enhance_color_raster(raster_path: str | Path) -> None:
    """Rewrite a red/green/blue reflectance GeoTIFF in place as enhanced 8-bit RGB.

    Uses :func:`enhance_color`. The bands must be ordered red, green, blue.
    Pixels without data stay without data (black, with a mask stored inside
    the file).

    This changes the file itself and the original reflectance values are lost.
    Normally you do not call it yourself: ``download_true_color_image`` does
    it for you when ``enhance_color=True``.

    Parameters
    ----------
    raster_path:
        Three-band GeoTIFF with red, green and blue reflectance. It is
        overwritten with an 8-bit RGB GeoTIFF.

    Raises
    ------
    ValueError
        If the file does not have exactly three bands.
    """
    _rewrite_as_rgb(raster_path, enhance_color)


def enhance_contrast_raster(raster_path: str | Path) -> None:
    """Rewrite a three-band reflectance GeoTIFF in place as contrast-enhanced 8-bit RGB.

    Uses :func:`enhance_contrast`. The bands must already be ordered as the
    intended red, green and blue display channels. Pixels without data stay
    without data (black, with a mask stored inside the file).

    This changes the file itself and the original reflectance values are lost.
    Normally you do not call it yourself: ``download_false_color_urban`` does
    it for you when ``enhance_contrast=True``.

    Parameters
    ----------
    raster_path:
        Three-band GeoTIFF with reflectance in the order of the display
        channels (red, green, blue). It is overwritten with an 8-bit RGB
        GeoTIFF.

    Raises
    ------
    ValueError
        If the file does not have exactly three bands.
    """
    _rewrite_as_rgb(raster_path, _enhance_contrast_8bit)
