"""One plot function per data type, named like the matching ``download_*`` function.

===============================================  ==================  =======================
Long name                                        Short alias         Draws the file of
===============================================  ==================  =======================
``plot_normalized_difference_vegetation_index``  ``plot_ndvi``       ``download_ndvi``
``plot_enhanced_vegetation_index``               ``plot_evi``        ``download_evi``
``plot_normalized_difference_water_index``       ``plot_ndwi``       ``download_ndwi``
``plot_normalized_difference_moisture_index``    ``plot_ndmi``       ``download_ndmi``
``plot_normalized_difference_snow_index``        ``plot_ndsi``       ``download_ndsi``
``plot_true_color_image``                        ``plot_tci``        ``download_tci``
``plot_false_color_urban``                       ``plot_urban``      ``download_urban``
``plot_false_color_infrared``                    ``plot_infrared``   ``download_infrared``
``plot_false_color_swir``                        ``plot_swir``       ``download_swir``
``plot_scene_classification_map``                ``plot_scl``        ``download_scl``
``plot_landsat_ndvi``                            ``plot_landsat``    ``download_landsat``
``plot_land_surface_temperature``                ``plot_lst``        ``download_lst``
``plot_soil_water_index``                        ``plot_swi``        ``download_swi``
``plot_digital_elevation_model``                 ``plot_dem``        ``download_dem``
``plot_land_cover``                              -                   ``download_land_cover``
===============================================  ==================  =======================

Every function reads like a recipe: *which colour map, which value range, which
label* are right for this data type. The drawing itself is in ``raster.py``.
To plot data of your own, call ``plot_raster`` and choose these yourself.

The short alias is the last line of this module, as in the ``download_*`` modules.
"""

from __future__ import annotations

from pathlib import Path

from matplotlib.axes import Axes

from ..eo.postprocessing import _enhance_contrast_8bit, enhance_color
from ..eo.scl import SCL_CLASSES, SCL_COLORS
from ..eo.worldcover import WORLDCOVER_CLASSES, WORLDCOVER_COLORS
from .raster import _plot_class_file, _plot_one_band_file, _plot_picture_file


# ----------------------------------------------------------------------------
# Indices with a fixed range: NDVI, EVI (Sentinel-2), NDVI (Landsat)
# ----------------------------------------------------------------------------
def plot_normalized_difference_vegetation_index(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "RdYlGn",
    vmin: float | None = -1.0,
    vmax: float | None = 1.0,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the NDVI of ``download_normalized_difference_vegetation_index``.

    NDVI lies between -1 and 1: water and bare ground are around or below 0,
    dense green vegetation is above 0.6. The colour map goes from red (low)
    over yellow to green (high). The range is fixed to -1 ... 1, so two images
    always have the same colours and can be compared.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_ndvi``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "NDVI (Sentinel-2)". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the image instead.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_normalized_difference_vegetation_index",
        default_title="NDVI (Sentinel-2)", label="NDVI",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


def plot_enhanced_vegetation_index(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "RdYlGn",
    vmin: float | None = -1.0,
    vmax: float | None = 1.0,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the EVI of ``download_enhanced_vegetation_index``.

    EVI is read like NDVI but reacts less to the atmosphere and does not
    saturate as early over dense vegetation. It uses the same colour map and
    the same fixed range (-1 ... 1) as :func:`plot_normalized_difference_vegetation_index`,
    so NDVI and EVI of the same area can be compared by eye.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_evi``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "EVI (Sentinel-2)". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the image instead.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_enhanced_vegetation_index",
        default_title="EVI (Sentinel-2)", label="EVI",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


def plot_landsat_ndvi(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "RdYlGn",
    vmin: float | None = -1.0,
    vmax: float | None = 1.0,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the NDVI of ``download_landsat_ndvi``.

    Same colour map and range as :func:`plot_normalized_difference_vegetation_index`.
    Landsat pixels are larger than Sentinel-2 pixels, so the same area looks coarser.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_landsat``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "NDVI (Landsat)". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the image instead.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_landsat_ndvi",
        default_title="NDVI (Landsat)", label="NDVI",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


# ----------------------------------------------------------------------------
# Measurements without a natural range: the colours follow the values of the image


def plot_normalized_difference_water_index(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "RdBu",
    vmin: float | None = -1.0,
    vmax: float | None = 1.0,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the NDWI of ``download_normalized_difference_water_index``.

    NDWI lies between -1 and 1: open water is above 0, land is below 0. The
    colour map goes from red (land) over white to blue (water). The range is
    fixed to -1 ... 1, so two images always have the same colours and can be
    compared.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_ndwi``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "NDWI (Sentinel-2)". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the image instead.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_normalized_difference_water_index",
        default_title="NDWI (Sentinel-2)", label="NDWI",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


def plot_normalized_difference_moisture_index(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "BrBG",
    vmin: float | None = -1.0,
    vmax: float | None = 1.0,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the NDMI of ``download_normalized_difference_moisture_index``.

    NDMI lies between -1 and 1: dry vegetation and bare ground are low,
    vegetation that holds much water is high. The colour map goes from brown
    (dry) over white to blue-green (moist). The range is fixed to -1 ... 1, so
    two images always have the same colours and can be compared.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_ndmi``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "NDMI (Sentinel-2)". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the image instead.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_normalized_difference_moisture_index",
        default_title="NDMI (Sentinel-2)", label="NDMI",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


def plot_normalized_difference_snow_index(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "PuBu",
    vmin: float | None = -1.0,
    vmax: float | None = 1.0,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the NDSI of ``download_normalized_difference_snow_index``.

    NDSI lies between -1 and 1: snow and ice are high (usually above 0.4),
    land and water are low. The colour map goes from white (low) to dark blue
    (high). The range is fixed to -1 ... 1, so two images always have the same
    colours and can be compared.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_ndsi``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "NDSI (Sentinel-2)". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the image instead.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_normalized_difference_snow_index",
        default_title="NDSI (Sentinel-2)", label="NDSI",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


# ----------------------------------------------------------------------------
def plot_land_surface_temperature(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "inferno",
    vmin: float | None = None,
    vmax: float | None = None,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the temperature of ``download_land_surface_temperature``.

    The values are in **Kelvin** (0 degrees Celsius = 273.15 K), as downloaded;
    nothing is converted. The colour map goes from dark (cold) to bright
    (warm). The range follows the values of this image, so the same colour can
    mean different temperatures in two images. To compare images, give both
    the same ``vmin`` and ``vmax``.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_lst``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "Land surface temperature". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map, in Kelvin. ``None`` takes the
        smallest and largest value of the image.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_land_surface_temperature",
        default_title="Land surface temperature", label="Temperature (K)",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


def plot_digital_elevation_model(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "terrain",
    vmin: float | None = None,
    vmax: float | None = None,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the heights of ``download_digital_elevation_model``.

    The values are metres above sea level. The "terrain" colour map goes from
    blue and green (low) over yellow and brown to white (high). The range
    follows the values of this image; in flat country such as Bremen a few
    metres of difference already use the whole colour map.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_dem``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "Elevation". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map, in metres. ``None`` takes the
        smallest and largest value of the image.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_digital_elevation_model",
        default_title="Elevation", label="Elevation (m)",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


def plot_soil_water_index(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    cmap: str = "Blues",
    vmin: float | None = 0.0,
    vmax: float | None = 100.0,
    colorbar: bool = True,
    show: bool | None = None,
) -> Axes:
    """Draw the soil moisture of ``download_soil_water_index``.

    The soil water index is given in percent: 0 is dry, 100 is saturated. The
    colour map goes from white (dry) to dark blue (wet). The range is fixed to
    0 ... 100, so images of different days can be compared.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_swi``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "Soil water index". Use ``""`` for no title.
    cmap:
        Name of a matplotlib colour map.
    vmin, vmax:
        Values at the two ends of the colour map. ``None`` takes the smallest
        and largest value of the image instead.
    colorbar:
        Draw a colour bar.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_one_band_file(
        file_path, "plot_soil_water_index",
        default_title="Soil water index", label="Soil water index (%)",
        title=title, cmap=cmap, vmin=vmin, vmax=vmax, colorbar=colorbar, ax=ax, show=show,
    )


# ----------------------------------------------------------------------------
# Colour pictures: the file holds colours, not a measurement
# ----------------------------------------------------------------------------
def plot_true_color_image(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    show: bool | None = None,
) -> Axes:
    """Draw the picture of ``download_true_color_image``.

    A file downloaded with the default ``enhance_color=True`` already holds
    8-bit colours and is drawn as it is. A file downloaded with
    ``enhance_color=False`` holds reflectance; it is given the same colour
    enhancement as the download would have applied, **for the picture only**.
    The file keeps its reflectance values. Pixels without data are transparent.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_tci``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "True colour (Sentinel-2)". Use ``""`` for no title.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly three bands, or if they are neither
        8-bit nor floating-point.
    """
    return _plot_picture_file(
        file_path, "plot_true_color_image", enhance_color,
        default_title="True colour (Sentinel-2)", title=title, ax=ax, show=show,
    )


def plot_false_color_urban(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    show: bool | None = None,
) -> Axes:
    """Draw the picture of ``download_false_color_urban``.

    Bands B12, B11 and B04 are shown as red, green and blue. In this false
    colour image built-up areas look in shades of grey and brown-red,
    vegetation green and water dark. A file downloaded with the default
    ``enhance_contrast=True`` already holds 8-bit colours and is drawn as it
    is. A file downloaded with ``enhance_contrast=False`` holds reflectance; it
    gets the same contrast stretch (0 ... 0.4) as the download would have
    applied, **for the picture only**. Pixels without data are transparent.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_urban``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "False colour urban (Sentinel-2)". Use ``""`` for no title.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly three bands, or if they are neither
        8-bit nor floating-point.
    """
    return _plot_picture_file(
        file_path, "plot_false_color_urban", _enhance_contrast_8bit,
        default_title="False colour urban (Sentinel-2)", title=title, ax=ax, show=show,
    )


# ----------------------------------------------------------------------------
# Classes: every value is a category


def plot_false_color_infrared(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    show: bool | None = None,
) -> Axes:
    """Draw the picture of ``download_false_color_infrared``.

    Bands B08, B04 and B03 are shown as red, green and blue. In this false colour image vegetation looks red, water dark and built-up areas grey or blue-grey. A file downloaded with the default
    ``enhance_contrast=True`` already holds 8-bit colours and is drawn as it
    is. A file downloaded with ``enhance_contrast=False`` holds reflectance; it
    gets the same contrast stretch (0 ... 0.4) as the download would have
    applied, **for the picture only**. Pixels without data are transparent.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_infrared``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "False colour infrared (Sentinel-2)". Use ``""`` for no title.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly three bands, or if they are neither
        8-bit nor floating-point.
    """
    return _plot_picture_file(
        file_path, "plot_false_color_infrared", _enhance_contrast_8bit,
        default_title="False colour infrared (Sentinel-2)", title=title, ax=ax, show=show,
    )


def plot_false_color_swir(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    show: bool | None = None,
) -> Axes:
    """Draw the picture of ``download_false_color_swir``.

    Bands B12, B8A and B04 are shown as red, green and blue. In this false colour image vegetation looks green, bare ground and built-up areas brown to orange, water black, and snow cyan while clouds stay white. A file downloaded with the default
    ``enhance_contrast=True`` already holds 8-bit colours and is drawn as it
    is. A file downloaded with ``enhance_contrast=False`` holds reflectance; it
    gets the same contrast stretch (0 ... 0.4) as the download would have
    applied, **for the picture only**. Pixels without data are transparent.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_swir``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "False colour SWIR (Sentinel-2)". Use ``""`` for no title.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes.

    Raises
    ------
    ValueError
        If the file does not have exactly three bands, or if they are neither
        8-bit nor floating-point.
    """
    return _plot_picture_file(
        file_path, "plot_false_color_swir", _enhance_contrast_8bit,
        default_title="False colour SWIR (Sentinel-2)", title=title, ax=ax, show=show,
    )


# ----------------------------------------------------------------------------
def plot_land_cover(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    show: bool | None = None,
) -> Axes:
    """Draw the classes of ``download_land_cover``.

    Every pixel is one of the WorldCover classes (``cdec.WORLDCOVER_CLASSES``)
    and is drawn in the official colour of its class (``cdec.WORLDCOVER_COLORS``).
    The legend lists only the classes that occur in the image. Pixels with
    another value are transparent.

    The colours are not read from the colour table inside the file but from
    ``cdec.WORLDCOVER_COLORS``, so the picture looks the same for every file.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_land_cover``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "Land cover (ESA WorldCover)". Use ``""`` for no title.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes. The legend is placed to the
        right of the plot; to save it in a picture file use
        ``plt.savefig("land_cover.png", bbox_inches="tight")``.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_class_file(
        file_path, "plot_land_cover", WORLDCOVER_COLORS, WORLDCOVER_CLASSES,
        legend_title="Land cover", default_title="Land cover (ESA WorldCover)",
        title=title, ax=ax, show=show,
    )


# Class 0 means "no data": it stays transparent, like the pixels outside the image.
_SCL_CLASSES_TO_DRAW = {class_id: color for class_id, color in SCL_COLORS.items() if class_id != 0}


def plot_scene_classification_map(
    file_path: str | Path,
    *,
    ax: Axes | None = None,
    title: str | None = None,
    show: bool | None = None,
) -> Axes:
    """Draw the classes of ``download_scene_classification_map``.

    Every pixel is one of the SCL classes (``cdec.SCL_CLASSES``) and is drawn
    in the colour of its class (``cdec.SCL_COLORS``). The legend lists only
    the classes that occur in the image. Pixels of class 0 (no data) are
    transparent and are not in the legend.

    The colours are not read from the colour table inside the file but from
    ``cdec.SCL_COLORS``, so the picture looks the same for every file.

    Parameters
    ----------
    file_path:
        The GeoTIFF written by ``download_scl``.
    ax:
        A matplotlib ``Axes`` to draw into. ``None`` creates a new figure.
    title:
        Title of the plot. Default: "Scene classification (Sentinel-2)". Use ``""`` for no title.
    show:
        Call ``plt.show()`` at the end. The default (``None``) shows the figure
        only if this function created it.

    Returns
    -------
    matplotlib.axes.Axes
        The axes with the plot, for further changes. The legend is placed to the
        right of the plot; to save it in a picture file use
        ``plt.savefig("scene_classification.png", bbox_inches="tight")``.

    Raises
    ------
    ValueError
        If the file does not have exactly one band.
    """
    return _plot_class_file(
        file_path, "plot_scene_classification_map", _SCL_CLASSES_TO_DRAW, SCL_CLASSES,
        legend_title="Scene classification", default_title="Scene classification (Sentinel-2)",
        title=title, ax=ax, show=show,
    )


# Short aliases, as in the download_* modules: the same function under a short name.
plot_ndvi = plot_normalized_difference_vegetation_index
plot_evi = plot_enhanced_vegetation_index
plot_tci = plot_true_color_image
plot_urban = plot_false_color_urban
plot_landsat = plot_landsat_ndvi
plot_lst = plot_land_surface_temperature
plot_swi = plot_soil_water_index
plot_dem = plot_digital_elevation_model
plot_ndwi = plot_normalized_difference_water_index
plot_ndmi = plot_normalized_difference_moisture_index
plot_ndsi = plot_normalized_difference_snow_index
plot_infrared = plot_false_color_infrared
plot_swir = plot_false_color_swir
plot_scl = plot_scene_classification_map
