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
    """
    data = np.asarray(data, dtype=np.float32)
    if data.ndim != 3 or data.shape[0] < 3:
        raise ValueError("enhance_color erwartet ein Array mit drei RGB-Baendern.")

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


def enhance_color_raster(raster_path: str | Path) -> None:
    """
    Rewrite a raster in place with the Sentinel-2 true-color enhancement.
    """
    raster_path = Path(raster_path)
    temporary_output = raster_path.with_name(f"{raster_path.stem}_enhanced.tif")

    with rasterio.open(raster_path) as src:
        if src.count < 3:
            raise ValueError("Zur Farbverbesserung werden mindestens drei Baender benoetigt.")

        data = src.read(indexes=(1, 2, 3), masked=True).astype(np.float32)
        valid_mask = ~np.any(np.ma.getmaskarray(data), axis=0)
        profile = src.profile.copy()

    enhanced = enhance_color(np.ma.filled(data, 0.0))
    enhanced[:, ~valid_mask] = 0

    profile.update(dtype=rasterio.uint8, count=3, nodata=None, photometric="RGB")

    with rasterio.open(temporary_output, "w", **profile) as dst:
        dst.write(enhanced)
        dst.write_mask(valid_mask.astype(np.uint8) * 255)

    temporary_output.replace(raster_path)


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


def enhance_contrast_raster(raster_path: str | Path) -> None:
    """Convert a three-band reflectance composite to a contrast-enhanced RGB TIFF.

    Bands must already be ordered as the intended red, green and blue display
    channels. The output uses 8-bit values and preserves the input data mask.
    """
    raster_path = Path(raster_path)
    temporary_output = raster_path.with_name(f"{raster_path.stem}_enhanced.tif")

    with rasterio.open(raster_path) as src:
        if src.count != 3:
            raise ValueError("Contrast enhancement requires exactly three display bands.")

        data = src.read(masked=True).astype(np.float32)
        valid_mask = ~np.any(np.ma.getmaskarray(data), axis=0)
        profile = src.profile.copy()

    enhanced = enhance_contrast(np.ma.filled(data, 0.0))
    enhanced = np.clip(enhanced * 255, 0, 255).astype(np.uint8)
    enhanced[:, ~valid_mask] = 0

    profile.update(dtype=rasterio.uint8, count=3, nodata=None, photometric="RGB")

    # Store the mask inside the TIFF so it stays attached when the file is moved.
    with rasterio.Env(GDAL_TIFF_INTERNAL_MASK=True):
        with rasterio.open(temporary_output, "w", **profile) as dst:
            dst.write(enhanced)
            dst.write_mask(valid_mask.astype(np.uint8) * 255)

    temporary_output.replace(raster_path)
