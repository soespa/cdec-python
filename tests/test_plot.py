"""Tests of the plot functions (they draw into memory; no window opens).

* the data type functions (``plot_ndvi``, ``plot_tci``, ...): colour map, value range, labels
* ``plot_raster``: decides by the format of the file
* colour pictures, no-data pixels, land-cover legend, axis labels
* the whole way: a ``download_*`` function writes a file, the matching ``plot_*`` function draws it
"""

import inspect

import matplotlib.pyplot as plt
import numpy as np
import pytest
import rasterio
from matplotlib.colors import to_rgba
from rasterio.plot import reshape_as_image

import cdec
import cdec.plot.products
from cdec import (
    download_dem,
    download_evi,
    download_infrared,
    download_land_cover,
    download_landsat,
    download_lst,
    download_ndmi,
    download_ndsi,
    download_ndvi,
    download_ndwi,
    download_scl,
    download_swi,
    download_swir,
    download_tci,
    download_urban,
    plot_dem,
    plot_evi,
    plot_infrared,
    plot_land_cover,
    plot_landsat,
    plot_lst,
    plot_ndmi,
    plot_ndsi,
    plot_ndvi,
    plot_ndwi,
    plot_raster,
    plot_scl,
    plot_swi,
    plot_swir,
    plot_tci,
    plot_urban,
)
from cdec.eo.postprocessing import enhance_color, enhance_color_raster, enhance_contrast, enhance_contrast_raster
from cdec.eo.scl import SCL_CLASSES, SCL_COLORS
from cdec.eo.worldcover import WORLDCOVER_CLASSES, WORLDCOVER_COLORS

from .helpers import write_test_raster

EMPTY_COLUMNS = 10  # write_test_raster leaves this many columns on the left without data


@pytest.fixture(autouse=True)
def close_all_figures():
    """Every test starts without open figures (and leaves none behind)."""
    plt.close("all")
    yield
    plt.close("all")


def make_file(tmp_path, name="file.tif", **options):
    path = tmp_path / name
    write_test_raster(path, **options)
    return path


def make_picture_file(tmp_path, enhance_raster):
    """A three-band 8-bit colour picture, made like the download functions do it."""
    path = make_file(tmp_path, "picture.tif", count=3)
    enhance_raster(path)  # reflectance -> 8-bit colours, in place
    return path


def read_band(path, band=1):
    with rasterio.open(path) as src:
        return src.read(band)


def picture_of(ax):
    """The (height, width, 4) array of red, green, blue and transparency that was drawn."""
    return np.asarray(ax.images[0].get_array())


# ----------------------------------------------------------------------------
# Names: long names, short aliases
# ----------------------------------------------------------------------------
PLOT_ALIASES = {
    "plot_normalized_difference_vegetation_index": "plot_ndvi",
    "plot_enhanced_vegetation_index": "plot_evi",
    "plot_normalized_difference_water_index": "plot_ndwi",
    "plot_normalized_difference_moisture_index": "plot_ndmi",
    "plot_normalized_difference_snow_index": "plot_ndsi",
    "plot_true_color_image": "plot_tci",
    "plot_false_color_urban": "plot_urban",
    "plot_false_color_infrared": "plot_infrared",
    "plot_false_color_swir": "plot_swir",
    "plot_scene_classification_map": "plot_scl",
    "plot_landsat_ndvi": "plot_landsat",
    "plot_land_surface_temperature": "plot_lst",
    "plot_soil_water_index": "plot_swi",
    "plot_digital_elevation_model": "plot_dem",
}
ALL_PLOT_NAMES = [*PLOT_ALIASES, *PLOT_ALIASES.values(), "plot_land_cover", "plot_raster"]


@pytest.mark.parametrize("long_name, short_name", PLOT_ALIASES.items())
def test_the_short_alias_is_the_same_function_as_the_long_name(long_name, short_name):
    for namespace in (cdec, cdec.plot):
        assert getattr(namespace, short_name) is getattr(namespace, long_name)
    assert long_name in cdec.__all__
    assert short_name in cdec.__all__


def test_there_is_a_plot_function_for_every_download_function():
    """plot_ndvi for download_ndvi, plot_tci for download_tci, ..."""
    from .test_package import ALIASES

    for long_name, short_name in ALIASES.items():
        assert long_name.replace("download_", "plot_") in PLOT_ALIASES
        assert short_name.replace("download_", "plot_") in PLOT_ALIASES.values()
    assert hasattr(cdec, "plot_land_cover")


def test_every_plot_function_is_in_the_alias_table():
    """Reminder: a new plot function needs a long name, a short alias and a line in PLOT_ALIASES."""
    defined_here = {
        name
        for name, function in inspect.getmembers(cdec.plot.products, inspect.isfunction)
        if name.startswith("plot_") and function.__module__ == cdec.plot.products.__name__
    }
    assert defined_here == set(PLOT_ALIASES) | set(PLOT_ALIASES.values()) | {"plot_land_cover"}


@pytest.mark.parametrize("name", ALL_PLOT_NAMES)
def test_only_the_file_is_a_positional_argument(name):
    parameters = list(inspect.signature(getattr(cdec, name)).parameters.values())
    assert parameters[0].name == "file_path"
    assert all(p.kind is inspect.Parameter.KEYWORD_ONLY for p in parameters[1:])


# ----------------------------------------------------------------------------
# The data types with one band: colour map, range, labels
# ----------------------------------------------------------------------------
# function, colour map, fixed range (None = follows the values of the image), colour bar label, title
ONE_BAND_PLOTS = [
    pytest.param(plot_ndvi, "RdYlGn", (-1, 1), "NDVI", "NDVI (Sentinel-2)", id="ndvi"),
    pytest.param(plot_evi, "RdYlGn", (-1, 1), "EVI", "EVI (Sentinel-2)", id="evi"),
    pytest.param(plot_ndwi, "RdBu", (-1, 1), "NDWI", "NDWI (Sentinel-2)", id="ndwi"),
    pytest.param(plot_ndmi, "BrBG", (-1, 1), "NDMI", "NDMI (Sentinel-2)", id="ndmi"),
    pytest.param(plot_ndsi, "PuBu", (-1, 1), "NDSI", "NDSI (Sentinel-2)", id="ndsi"),
    pytest.param(plot_landsat, "RdYlGn", (-1, 1), "NDVI", "NDVI (Landsat)", id="landsat"),
    pytest.param(plot_lst, "inferno", None, "Temperature (K)", "Land surface temperature", id="lst"),
    pytest.param(plot_dem, "terrain", None, "Elevation (m)", "Elevation", id="dem"),
    pytest.param(plot_swi, "Blues", (0, 100), "Soil water index (%)", "Soil water index", id="swi"),
]


@pytest.mark.parametrize("plot, cmap, value_range, label, title", ONE_BAND_PLOTS)
def test_one_band_plots_use_the_colours_of_their_data_type(plot, cmap, value_range, label, title, tmp_path):
    path = make_file(tmp_path, count=1)
    fig, ax = plt.subplots()

    result = plot(path, ax=ax, show=False)

    assert result is ax
    (image,) = ax.images
    assert image.get_cmap().name == cmap
    if value_range is None:
        values = read_band(path)
        assert image.get_clim() == pytest.approx((np.nanmin(values), np.nanmax(values)))
    else:
        assert image.get_clim() == value_range
    assert ax.get_title() == title
    colorbar_axes = fig.axes[1]
    assert colorbar_axes.get_ylabel() == label


@pytest.mark.parametrize("plot", [param.values[0] for param in ONE_BAND_PLOTS])
def test_every_option_can_be_changed(plot, tmp_path):
    path = make_file(tmp_path, count=1)
    fig, ax = plt.subplots()

    plot(path, ax=ax, show=False, title="My title", cmap="viridis", vmin=0.1, vmax=0.2, colorbar=False)

    (image,) = ax.images
    assert image.get_cmap().name == "viridis"
    assert image.get_clim() == (0.1, 0.2)
    assert ax.get_title() == "My title"
    assert len(fig.axes) == 1  # no colour bar


def test_an_empty_title_means_no_title(tmp_path):
    path = make_file(tmp_path, count=1)
    ax = plot_ndvi(path, title="", show=False)
    assert ax.get_title() == ""


def test_pixels_without_data_do_not_change_the_colour_range(tmp_path):
    """The empty columns are NaN. The range must come from the pixels that have values."""
    path = make_file(tmp_path, count=1, empty_columns=10)
    ax = plot_lst(path, show=False)

    values = read_band(path)
    assert np.isnan(values).any()
    assert ax.images[0].get_clim() == pytest.approx((np.nanmin(values), np.nanmax(values)))


def test_a_declared_nodata_value_is_not_drawn_either(tmp_path):
    path = make_file(tmp_path, count=1, dtype="float32", declare_nodata=True)
    ax = plot_dem(path, show=False)
    values = read_band(path)
    assert ax.images[0].get_clim() == pytest.approx((np.nanmin(values), np.nanmax(values)))


# ----------------------------------------------------------------------------
# The two colour pictures
# ----------------------------------------------------------------------------
def test_true_color_draws_a_finished_picture_as_it_is(tmp_path):
    path = make_picture_file(tmp_path, enhance_color_raster)
    ax = plot_tci(path, show=False)

    picture = picture_of(ax)
    assert picture.dtype == np.uint8
    assert picture.shape[2] == 4
    in_the_file = reshape_as_image(read_band_all(path))
    assert np.array_equal(picture[:, EMPTY_COLUMNS:, :3], in_the_file[:, EMPTY_COLUMNS:])
    assert ax.get_title() == "True colour (Sentinel-2)"


def read_band_all(path):
    with rasterio.open(path) as src:
        return src.read()


def test_pixels_without_data_are_transparent_in_a_picture(tmp_path):
    path = make_picture_file(tmp_path, enhance_color_raster)
    picture = picture_of(plot_tci(path, show=False))

    assert (picture[:, :EMPTY_COLUMNS, 3] == 0).all()
    assert (picture[:, EMPTY_COLUMNS:, 3] == 255).all()


def test_true_color_applies_the_enhancement_to_reflectance_for_the_picture_only(tmp_path):
    """A file downloaded with enhance_color=False holds reflectance: the plot enhances it in memory."""
    path = make_file(tmp_path, count=3)
    reflectance_before = read_band_all(path)

    picture = picture_of(plot_tci(path, show=False))

    expected = enhance_color(np.nan_to_num(reflectance_before))
    assert np.array_equal(picture[:, EMPTY_COLUMNS:, :3], reshape_as_image(expected)[:, EMPTY_COLUMNS:])
    assert (picture[:, :EMPTY_COLUMNS, 3] == 0).all()

    # the file keeps its reflectance
    with rasterio.open(path) as src:
        assert src.dtypes[0] == "float32"
    assert np.array_equal(read_band_all(path), reflectance_before, equal_nan=True)


def test_false_color_urban_applies_the_contrast_stretch_to_reflectance(tmp_path):
    path = make_file(tmp_path, count=3)
    reflectance = read_band_all(path)

    picture = picture_of(plot_urban(path, show=False))

    stretched = np.clip(enhance_contrast(np.nan_to_num(reflectance)) * 255, 0, 255).astype(np.uint8)
    assert np.array_equal(picture[:, EMPTY_COLUMNS:, :3], reshape_as_image(stretched)[:, EMPTY_COLUMNS:])


def test_false_color_urban_draws_a_finished_picture_as_it_is(tmp_path):
    path = make_picture_file(tmp_path, enhance_contrast_raster)
    picture = picture_of(plot_urban(path, show=False))

    in_the_file = reshape_as_image(read_band_all(path))
    assert np.array_equal(picture[:, EMPTY_COLUMNS:, :3], in_the_file[:, EMPTY_COLUMNS:])
    assert (picture[:, :EMPTY_COLUMNS, 3] == 0).all()


@pytest.mark.parametrize(
    "plot, title",
    [
        pytest.param(plot_infrared, "False colour infrared (Sentinel-2)", id="infrared"),
        pytest.param(plot_swir, "False colour SWIR (Sentinel-2)", id="swir"),
    ],
)
class TestFalseColourImages:
    def test_a_finished_picture_is_drawn_as_it_is(self, plot, title, tmp_path):
        path = make_picture_file(tmp_path, enhance_contrast_raster)
        ax = plot(path, show=False)

        picture = picture_of(ax)
        in_the_file = reshape_as_image(read_band_all(path))
        assert np.array_equal(picture[:, EMPTY_COLUMNS:, :3], in_the_file[:, EMPTY_COLUMNS:])
        assert (picture[:, :EMPTY_COLUMNS, 3] == 0).all()
        assert ax.get_title() == title

    def test_reflectance_gets_the_contrast_stretch_for_the_picture_only(self, plot, title, tmp_path):
        path = make_file(tmp_path, count=3)
        reflectance = read_band_all(path)

        picture = picture_of(plot(path, show=False))

        stretched = np.clip(enhance_contrast(np.nan_to_num(reflectance)) * 255, 0, 255).astype(np.uint8)
        assert np.array_equal(picture[:, EMPTY_COLUMNS:, :3], reshape_as_image(stretched)[:, EMPTY_COLUMNS:])
        assert np.array_equal(read_band_all(path), reflectance, equal_nan=True)  # the file is not changed

    def test_a_file_with_one_band_is_refused(self, plot, title, tmp_path):
        path = make_file(tmp_path, count=1)
        with pytest.raises(ValueError):
            plot(path, show=False)


def test_pictures_have_no_colour_bar(tmp_path):
    path = make_picture_file(tmp_path, enhance_color_raster)
    fig, ax = plt.subplots()
    plot_tci(path, ax=ax, show=False)
    assert len(fig.axes) == 1


# ----------------------------------------------------------------------------
# Land cover: colours and legend
# ----------------------------------------------------------------------------
def test_land_cover_uses_the_official_colours_and_lists_the_classes_found(tmp_path):
    path = make_file(tmp_path, count=1, dtype="uint8", class_ids=True)  # classes 10, 30, 50, 80
    ax = plot_land_cover(path, show=False)

    legend_texts = [text.get_text() for text in ax.get_legend().get_texts()]
    assert legend_texts == [
        f"{class_id}  {WORLDCOVER_CLASSES[class_id]}" for class_id in (10, 30, 50, 80)
    ]

    picture = picture_of(ax)
    class_ids = read_band(path)
    for class_id in (10, 30, 50, 80):
        row, column = np.argwhere(class_ids == class_id)[0]
        assert tuple(picture[row, column]) == pytest.approx(to_rgba(WORLDCOVER_COLORS[class_id]))
    assert (picture[:, :EMPTY_COLUMNS, 3] == 0).all()  # class 0 = no data
    assert ax.get_title() == "Land cover (ESA WorldCover)"


def test_land_cover_leaves_unknown_values_empty(tmp_path):
    path = make_file(tmp_path, count=1, dtype="uint8", class_ids=True, empty_columns=0)
    with rasterio.open(path, "r+") as src:
        data = src.read(1)
        data[0, 0] = 99  # not a WorldCover class
        src.write(data, 1)

    ax = plot_land_cover(path, show=False)

    assert picture_of(ax)[0, 0, 3] == 0
    assert all("99" not in text.get_text() for text in ax.get_legend().get_texts())


def test_land_cover_does_not_need_the_colour_table_of_the_file(tmp_path):
    path = make_file(tmp_path, count=1, dtype="float32", class_ids=True)
    with rasterio.open(path) as src:
        assert src.colorinterp[0] != rasterio.enums.ColorInterp.palette
    assert len(plot_land_cover(path, show=False).images) == 1


# ----------------------------------------------------------------------------
# Scene classification: colours and legend
# ----------------------------------------------------------------------------
def make_scl_file(tmp_path, classes=(4, 5, 6, 9)):
    """A one-band file of SCL class IDs: ``classes`` in four blocks of columns, class 0 on the left."""
    path = tmp_path / "scl.tif"
    make_file(tmp_path, "scl.tif", count=1, dtype="uint8", class_ids=True)
    with rasterio.open(path, "r+") as src:
        data = np.zeros((src.height, src.width), dtype="uint8")
        block = (src.width - EMPTY_COLUMNS) // len(classes)
        for number, class_id in enumerate(classes):
            start = EMPTY_COLUMNS + number * block
            data[:, start : start + block] = class_id
        data[:, EMPTY_COLUMNS + len(classes) * block :] = classes[-1]
        src.write(data, 1)
    return path


def test_scene_classification_uses_the_scl_colours_and_lists_the_classes_found(tmp_path):
    path = make_scl_file(tmp_path)
    ax = plot_scl(path, show=False)

    legend_texts = [text.get_text() for text in ax.get_legend().get_texts()]
    assert legend_texts == [f"{class_id}  {SCL_CLASSES[class_id]}" for class_id in (4, 5, 6, 9)]

    picture = picture_of(ax)
    class_ids = read_band(path)
    for class_id in (4, 5, 6, 9):
        row, column = np.argwhere(class_ids == class_id)[0]
        assert tuple(picture[row, column]) == pytest.approx(to_rgba(SCL_COLORS[class_id]))
    assert (picture[:, :EMPTY_COLUMNS, 3] == 0).all()  # class 0 = no data
    assert ax.get_title() == "Scene classification (Sentinel-2)"


def test_scene_classification_leaves_unknown_values_empty(tmp_path):
    path = make_scl_file(tmp_path)
    with rasterio.open(path, "r+") as src:
        data = src.read(1)
        data[0, EMPTY_COLUMNS] = 99  # not an SCL class
        src.write(data, 1)

    ax = plot_scl(path, show=False)

    assert picture_of(ax)[0, EMPTY_COLUMNS, 3] == 0
    assert all("99" not in text.get_text() for text in ax.get_legend().get_texts())


def test_scene_classification_does_not_need_the_colour_table_of_the_file(tmp_path):
    path = make_scl_file(tmp_path)
    with rasterio.open(path) as src:
        assert src.colorinterp[0] != rasterio.enums.ColorInterp.palette
    assert len(plot_scl(path, show=False).images) == 1


def test_scene_classification_refuses_a_file_with_more_than_one_band(tmp_path):
    path = make_file(tmp_path, count=3)
    with pytest.raises(ValueError):
        plot_scl(path, show=False)


# ----------------------------------------------------------------------------
# plot_raster: any file, decided by its format
# ----------------------------------------------------------------------------
def test_plot_raster_draws_a_three_band_8_bit_file_as_a_picture(tmp_path):
    path = make_picture_file(tmp_path, enhance_color_raster)
    fig, ax = plt.subplots()
    plot_raster(path, ax=ax, show=False)

    assert picture_of(ax).shape[2] == 4
    assert len(fig.axes) == 1


def test_plot_raster_draws_a_single_band_with_a_colour_bar(tmp_path):
    path = make_file(tmp_path, count=1)
    fig, ax = plt.subplots()
    plot_raster(path, ax=ax, show=False)

    (image,) = ax.images
    assert image.get_cmap().name == "viridis"
    values = read_band(path)
    assert image.get_clim() == pytest.approx((np.nanmin(values), np.nanmax(values)))
    assert len(fig.axes) == 2


def test_plot_raster_does_not_guess_colours_for_floating_point_bands(tmp_path):
    """Three float bands are reflectance, not a picture: it draws the band you ask for."""
    path = make_file(tmp_path, count=3)

    ax = plot_raster(path, band=2, show=False)

    assert ax.images[0].get_array().ndim == 2
    drawn = np.ma.filled(ax.images[0].get_array().astype(float), np.nan)
    assert np.array_equal(drawn, read_band(path, 2), equal_nan=True)


def test_a_data_type_function_is_plot_raster_with_the_right_choices(tmp_path):
    """docs/plotting.rst and README say: plot_ndvi(path) is plot_raster(path, cmap=..., vmin=..., ...)."""
    path = make_file(tmp_path, count=1)
    fig_1, ax_1 = plt.subplots()
    fig_2, ax_2 = plt.subplots()

    plot_ndvi(path, ax=ax_1, show=False)
    plot_raster(path, ax=ax_2, show=False, cmap="RdYlGn", vmin=-1, vmax=1, label="NDVI", title="NDVI (Sentinel-2)")

    image_1, image_2 = ax_1.images[0], ax_2.images[0]
    assert np.array_equal(
        np.ma.filled(image_1.get_array().astype(float), np.nan),
        np.ma.filled(image_2.get_array().astype(float), np.nan),
        equal_nan=True,
    )
    assert image_1.get_cmap().name == image_2.get_cmap().name
    assert image_1.get_clim() == image_2.get_clim()
    assert ax_1.get_title() == ax_2.get_title()
    assert fig_1.axes[1].get_ylabel() == fig_2.axes[1].get_ylabel()


def test_plot_raster_takes_the_label_from_the_file_unless_told_otherwise(tmp_path):
    path = make_file(tmp_path, count=1)
    with rasterio.open(path, "r+") as src:
        src.set_band_description(1, "Soil moisture")

    fig, ax = plt.subplots()
    plot_raster(path, ax=ax, show=False)
    assert fig.axes[1].get_ylabel() == "Soil moisture"

    fig, ax = plt.subplots()
    plot_raster(path, ax=ax, show=False, label="Own label")
    assert fig.axes[1].get_ylabel() == "Own label"


# ----------------------------------------------------------------------------
# Axes: unit and shape
# ----------------------------------------------------------------------------
def test_axes_of_a_metric_coordinate_system_are_labelled_in_metres(tmp_path):
    path = make_file(tmp_path, count=1, crs="EPSG:32632")
    ax = plot_ndvi(path, show=False)

    assert ax.get_xlabel() == "Easting (m)"
    assert ax.get_ylabel() == "Northing (m)"
    assert ax.get_aspect() == 1.0


def test_axes_of_longitude_and_latitude_are_labelled_in_degrees_and_corrected(tmp_path):
    """One degree of longitude is shorter than one degree of latitude; the picture must not look stretched."""
    path = make_file(tmp_path, count=1, crs="EPSG:4326")
    ax = plot_ndvi(path, show=False)

    assert ax.get_xlabel() == "Longitude (degrees)"
    assert ax.get_ylabel() == "Latitude (degrees)"
    with rasterio.open(path) as src:
        middle_latitude = (src.bounds.bottom + src.bounds.top) / 2
    assert ax.get_aspect() == pytest.approx(1 / np.cos(np.radians(middle_latitude)))
    assert ax.get_aspect() > 1.5  # near Bremen: about 1.66


def test_metric_axes_have_few_ticks_so_the_labels_do_not_overlap(tmp_path):
    path = make_file(tmp_path, count=1, crs="EPSG:32632")
    ax = plot_ndvi(path, show=False)

    left, right = ax.get_xlim()
    ticks_in_view = [tick for tick in ax.get_xticks() if left <= tick <= right]
    assert 2 <= len(ticks_in_view) <= 5


def test_the_picture_covers_the_area_of_the_file(tmp_path):
    path = make_file(tmp_path, count=1)
    ax = plot_ndvi(path, show=False)

    with rasterio.open(path) as src:
        left, bottom, right, top = src.bounds
    x_min, x_max = ax.get_xlim()
    y_min, y_max = ax.get_ylim()
    assert (x_min, x_max) == pytest.approx((left, right))
    assert (y_min, y_max) == pytest.approx((bottom, top))


# ----------------------------------------------------------------------------
# Figure and plt.show()
# ----------------------------------------------------------------------------
@pytest.fixture
def shown(monkeypatch):
    """A list that records every call of plt.show(), instead of trying to open a window."""
    calls = []
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: calls.append("show"))
    return calls


def test_without_ax_a_figure_is_created_and_shown(tmp_path, shown):
    path = make_file(tmp_path, count=1)
    ax = plot_ndvi(path)

    assert shown == ["show"]
    assert plt.get_fignums() == [ax.figure.number]


def test_with_ax_nothing_is_shown_because_you_decide_when(tmp_path, shown):
    path = make_file(tmp_path, count=1)
    fig, (left, right) = plt.subplots(1, 2)

    plot_ndvi(path, ax=left)
    plot_evi(path, ax=right)

    assert shown == []
    assert len(plt.get_fignums()) == 1
    assert len(left.images) == len(right.images) == 1
    assert left.get_title() != right.get_title()


def test_show_can_be_switched_on_and_off(tmp_path, shown):
    path = make_file(tmp_path, count=1)

    plot_ndvi(path, show=False)
    assert shown == []

    plot_ndvi(path, ax=plt.subplots()[1], show=True)
    assert shown == ["show"]


# ----------------------------------------------------------------------------
# Mistakes of the student
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("plot", [param.values[0] for param in ONE_BAND_PLOTS] + [plot_land_cover])
def test_a_file_with_three_bands_is_refused_by_the_one_band_functions(plot, tmp_path):
    path = make_file(tmp_path, "colour.tif", count=3)
    with pytest.raises(ValueError, match=r"needs a file with 1 band\(s\), but 'colour.tif' has 3"):
        plot(path)
    assert plt.get_fignums() == []  # no empty figure is left behind


@pytest.mark.parametrize("plot", [plot_tci, plot_urban])
def test_a_file_with_one_band_is_refused_by_the_picture_functions(plot, tmp_path):
    path = make_file(tmp_path, "ndvi.tif", count=1)
    with pytest.raises(ValueError, match=r"needs a file with 3 band\(s\), but 'ndvi.tif' has 1"):
        plot(path)
    assert plt.get_fignums() == []


@pytest.mark.parametrize("plot", [plot_tci, plot_urban])
def test_pictures_must_be_8_bit_or_floating_point(plot, tmp_path):
    path = make_file(tmp_path, count=3, dtype="uint16")
    with pytest.raises(ValueError, match="uint16"):
        plot(path)


def test_the_error_tells_which_function_to_use_instead(tmp_path):
    path = make_file(tmp_path, count=3)
    with pytest.raises(ValueError, match="plot_raster"):
        plot_ndvi(path)


# ----------------------------------------------------------------------------
# The whole way: download -> file -> plot
# ----------------------------------------------------------------------------
# download function, plot function, bands in the downloaded file
DOWNLOAD_AND_PLOT = [
    pytest.param(download_ndvi, plot_ndvi, 1, id="ndvi"),
    pytest.param(download_evi, plot_evi, 1, id="evi"),
    pytest.param(download_ndwi, plot_ndwi, 1, id="ndwi"),
    pytest.param(download_ndmi, plot_ndmi, 1, id="ndmi"),
    pytest.param(download_ndsi, plot_ndsi, 1, id="ndsi"),
    pytest.param(download_landsat, plot_landsat, 1, id="landsat"),
    pytest.param(download_tci, plot_tci, 3, id="tci"),
    pytest.param(download_urban, plot_urban, 3, id="urban"),
    pytest.param(download_infrared, plot_infrared, 3, id="infrared"),
    pytest.param(download_swir, plot_swir, 3, id="swir"),
    pytest.param(download_scl, plot_scl, 1, id="scl"),
    pytest.param(download_dem, plot_dem, 1, id="dem"),
    pytest.param(download_lst, plot_lst, 1, id="lst"),
    pytest.param(download_land_cover, plot_land_cover, 1, id="land_cover"),
    pytest.param(download_swi, plot_swi, 1, id="swi"),
]


@pytest.mark.parametrize("download, plot, bands", DOWNLOAD_AND_PLOT)
def test_the_file_of_every_download_function_can_be_plotted(
    download, plot, bands, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    fake_openeo.result_bands = bands
    fake_openeo.result_class_ids = download in (download_land_cover, download_scl)
    path = tmp_path / "result.tif"
    download(path, spatial_extent, temporal_extent, verbose=False)

    ax = plot(path, show=False)

    assert len(ax.images) == 1
    assert ax.get_title() != ""


@pytest.mark.parametrize(
    "download, plot",
    [
        (download_tci, plot_tci),
        (download_urban, plot_urban),
        (download_infrared, plot_infrared),
        (download_swir, plot_swir),
    ],
)
def test_pictures_from_the_download_keep_their_empty_pixels_transparent(
    download, plot, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    """The mask survives the conversion to a Cloud Optimized GeoTIFF."""
    fake_openeo.result_bands = 3
    path = tmp_path / "result.tif"
    download(path, spatial_extent, temporal_extent, verbose=False)

    picture = picture_of(plot(path, show=False))

    assert (picture[:, :EMPTY_COLUMNS, 3] == 0).all()
    assert (picture[:, EMPTY_COLUMNS:, 3] == 255).all()


@pytest.mark.parametrize(
    "download, plot, option",
    [
        (download_tci, plot_tci, "enhance_color"),
        (download_urban, plot_urban, "enhance_contrast"),
        (download_infrared, plot_infrared, "enhance_contrast"),
        (download_swir, plot_swir, "enhance_contrast"),
    ],
)
def test_reflectance_from_the_download_looks_like_the_finished_picture(
    download, plot, option, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    """enhance_*=False keeps the reflectance in the file; the plot shows the same colours as enhance_*=True."""
    fake_openeo.result_bands = 3
    finished = tmp_path / "finished.tif"
    reflectance = tmp_path / "reflectance.tif"
    download(finished, spatial_extent, temporal_extent, verbose=False)
    download(reflectance, spatial_extent, temporal_extent, verbose=False, **{option: False})

    with rasterio.open(reflectance) as src:
        assert src.dtypes[0] == "float32"
    picture_of_finished = picture_of(plot(finished, show=False))
    picture_of_reflectance = picture_of(plot(reflectance, show=False))

    assert np.array_equal(picture_of_finished, picture_of_reflectance)
