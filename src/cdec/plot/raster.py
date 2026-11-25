"""Draw a downloaded GeoTIFF with rasterio and matplotlib.

``plot_raster`` is the general function. It looks at the *format* of the file
(an 8-bit colour picture, or a band of numbers?) and draws it. It cannot know
what the numbers *mean*, so it uses a neutral colour map and an automatic value
range.

The functions in ``products.py`` (``plot_ndvi``, ``plot_tci``, ...) know what
the numbers mean and add the colour map, value range and labels that fit the
data type. They are short on purpose: read one of them to see how you would
plot your own data.

Everything is drawn into a matplotlib ``Axes``. If you do not pass one, a new
figure is created and shown. If you pass one (for example to put two images
side by side), you decide when to call ``plt.show()``.
"""

from __future__ import annotations

from collections.abc import Callable, Mapping
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import rasterio
from matplotlib.axes import Axes
from matplotlib.colors import to_rgba
from matplotlib.patches import Patch
from matplotlib.ticker import MaxNLocator
from rasterio.plot import plotting_extent, reshape_as_image
from rasterio.plot import show as rasterio_show

from ..eo.postprocessing import _valid_pixels


def plot_raster(
    file_path: str | Path,
    *,
    band: int = 1,
    cmap: str = "viridis",
    vmin: float | None = None,
    vmax: float | None = None,
    label: str | None = None,
    title: str | None = None,
    colorbar: bool = True,
    ax: Axes | None = None,
    show: bool | None = None,
) -> Axes:
    """Draw any GeoTIFF, decided by its format.

    * A file with **three 8-bit bands** is a colour picture (for example the
      true-colour image) and is drawn as it is.
    * Everything else is drawn as **one band of numbers** with a colour bar.

    The function cannot know what the numbers mean. For the data types of this
    package use the matching function (``plot_ndvi``, ``plot_dem``, ...), which
    sets a suitable colour map and value range.

    Parameters
    ----------
    file_path:
        The GeoTIFF to draw, for example the file written by a ``download_*``
        function.
    band:
        Which band to draw (1 is the first). Ignored for colour pictures.
    cmap:
        Name of a matplotlib colour map, see
        https://matplotlib.org/stable/users/explain/colors/colormaps.html
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the band. Fix them (for example ``vmin=-1,
        vmax=1`` for NDVI) to compare several images with the same colours.
    label:
        Text next to the colour bar. Default: the description stored in the
        file, if there is one.
    title:
        Title of the plot.
    colorbar:
        Draw a colour bar.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if the function created it, so a figure that you put together
        yourself is not shown too early.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.
    """
    with rasterio.open(file_path) as src:
        if src.count == 3 and set(src.dtypes) == {"uint8"}:
            return _plot_picture(src, enhance=None, title=title, ax=ax, show=show)

        if label is None:
            label = src.descriptions[band - 1]
        return _plot_band(
            src, band, cmap=cmap, vmin=vmin, vmax=vmax, label=label,
            title=title, colorbar=colorbar, ax=ax, show=show,
        )


# ----------------------------------------------------------------------------
# The three ways to draw: a band of numbers, a colour picture, classes
# ----------------------------------------------------------------------------
def _plot_band(src, band, *, cmap, vmin, vmax, label, title, colorbar, ax, show) -> Axes:
    """One band of numbers, coloured with a colour map."""
    ax, created = _get_axes(ax)

    # masked=True: pixels without data are not drawn (and do not change the colour range)
    data = src.read(band, masked=True)
    rasterio_show(data, transform=src.transform, ax=ax, cmap=cmap, vmin=vmin, vmax=vmax)

    if colorbar:
        ax.figure.colorbar(ax.images[-1], ax=ax, label=label, shrink=0.8)
    return _finish(ax, src, title, show, created)


def _plot_picture(src, *, enhance, title, ax, show) -> Axes:
    """Three bands as a colour picture. Pixels without data are transparent.

    ``enhance`` is None for a file that already is an 8-bit picture. For a file
    with reflectance (downloaded with ``enhance_*=False``) it is the function that
    turns reflectance into 8-bit colours; this happens in memory only and the
    file is not changed.
    """
    ax, created = _get_axes(ax)

    data = src.read(masked=True)  # shape (3, height, width)
    valid = _valid_pixels(data)
    colors = np.ma.getdata(data)
    if enhance is not None:
        colors = enhance(np.where(valid, colors, 0.0).astype(np.float32))

    # matplotlib wants (height, width, channels); the 4th channel is the transparency
    alpha = np.where(valid, 255, 0).astype(np.uint8)
    picture = np.dstack([reshape_as_image(colors), alpha])
    ax.imshow(picture, extent=plotting_extent(src))
    return _finish(ax, src, title, show, created)


def _plot_classes(
    src,
    colors: Mapping[int, str],
    names: Mapping[int, str],
    *,
    legend_title: str,
    title,
    ax,
    show,
) -> Axes:
    """Class IDs, each class in its own colour, with a legend of the classes found."""
    ax, created = _get_axes(ax)

    data = src.read(1, masked=True)
    class_ids = np.ma.getdata(data)
    valid = ~np.ma.getmaskarray(data)

    picture = np.zeros((*class_ids.shape, 4), dtype=np.float32)  # transparent
    legend_entries = []
    for class_id, color in colors.items():
        pixels = valid & (class_ids == class_id)
        if pixels.any():
            picture[pixels] = to_rgba(color)
            legend_entries.append(Patch(facecolor=color, edgecolor="grey", label=f"{class_id}  {names[class_id]}"))

    ax.imshow(picture, extent=plotting_extent(src))
    ax.legend(
        handles=legend_entries, title=legend_title, loc="upper left",
        bbox_to_anchor=(1.02, 1.0), borderaxespad=0, frameon=False,
    )
    return _finish(ax, src, title, show, created)


# ----------------------------------------------------------------------------
# Plumbing shared by the three
# ----------------------------------------------------------------------------
def _get_axes(ax: Axes | None) -> tuple[Axes, bool]:
    """Use the axes of the caller, or create a figure. Also say which of the two happened."""
    if ax is not None:
        return ax, False
    _, ax = plt.subplots(figsize=(8, 6), layout="constrained")
    return ax, True


def _finish(ax: Axes, src, title: str | None, show: bool | None, created: bool) -> Axes:
    """Axis labels, title, and ``plt.show()`` if wanted."""
    _label_axes(ax, src)
    if title:
        ax.set_title(title)
    if show is None:
        show = created
    if show:
        plt.show()
    return ax


def _label_axes(ax: Axes, src) -> None:
    """Write the coordinate system on the axes: degrees or metres, and keep the shapes right."""
    if src.crs is None:
        return
    ax.ticklabel_format(useOffset=False, style="plain")  # 5880000 and not 5.88e6

    if src.crs.is_geographic:
        ax.set_xlabel("Longitude (degrees)")
        ax.set_ylabel("Latitude (degrees)")
        # One degree of longitude is shorter than one degree of latitude (by cos(latitude)).
        # Without this correction the picture would look stretched in east-west direction.
        middle_latitude = (src.bounds.bottom + src.bounds.top) / 2
        ax.set_aspect(1 / np.cos(np.radians(middle_latitude)))
    else:
        unit = src.crs.linear_units
        unit = "m" if unit in ("metre", "meter") else unit
        ax.set_xlabel(f"Easting ({unit})")
        ax.set_ylabel(f"Northing ({unit})")
        # Coordinates such as 482000 are wide: fewer ticks, so the labels do not run into each other.
        ax.xaxis.set_major_locator(MaxNLocator(nbins=4))


def _choose_title(title: str | None, default_title: str) -> str:
    """The title of the caller. ``None`` means the default title; ``""`` means no title."""
    return default_title if title is None else title


def _file_name(src) -> str:
    return Path(src.name).name


def _check_bands(src, expected: int, function_name: str, hint: str) -> None:
    """A clear message if a file of another data type is passed to a plot function."""
    if src.count != expected:
        raise ValueError(
            f"{function_name} needs a file with {expected} band(s), but "
            f"'{_file_name(src)}' has {src.count}. {hint}"
        )


def _plot_one_band_file(
    file_path, function_name, *, default_title, label, title, cmap, vmin, vmax, colorbar, ax, show
) -> Axes:
    """Open a file that must have one band and draw it. Used by the ``plot_*`` data type functions."""
    with rasterio.open(file_path) as src:
        _check_bands(src, 1, function_name, "Is this the file of another data type? Try plot_raster(file_path).")
        return _plot_band(
            src, 1, cmap=cmap, vmin=vmin, vmax=vmax, label=label,
            title=_choose_title(title, default_title), colorbar=colorbar, ax=ax, show=show,
        )


def _plot_picture_file(
    file_path, function_name, enhance: Callable[[np.ndarray], np.ndarray] | None, *, default_title, title, ax, show
) -> Axes:
    """Open a three-band file and draw it as a picture. Used by the ``plot_*`` data type functions."""
    with rasterio.open(file_path) as src:
        _check_bands(src, 3, function_name, "A colour picture has three bands (red, green, blue).")

        data_type = np.dtype(src.dtypes[0])
        if data_type == np.uint8:
            enhance = None  # the file already holds colours
        elif data_type.kind != "f":
            raise ValueError(
                f"{function_name} needs 8-bit colours or floating-point reflectance, "
                f"but '{_file_name(src)}' has the data type {data_type.name}."
            )
        return _plot_picture(src, enhance=enhance, title=_choose_title(title, default_title), ax=ax, show=show)


def _plot_class_file(
    file_path, function_name, colors, names, *, legend_title, default_title, title, ax, show
) -> Axes:
    """Open a file with class IDs and draw it. Used by ``plot_land_cover``."""
    with rasterio.open(file_path) as src:
        _check_bands(src, 1, function_name, "Class IDs are stored in a single band.")
        return _plot_classes(
            src, colors, names, legend_title=legend_title, title=_choose_title(title, default_title), ax=ax, show=show,
        )
