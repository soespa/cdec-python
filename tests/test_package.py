"""Tests of the public interface: what ``import cdec`` offers."""

import importlib
import inspect
import pkgutil
import re

import pytest

import cdec
import cdec.eo
from cdec.eo.scl import SCL_LAND, SCL_LAND_AND_WATER, SCL_LAND_WATER_AND_SNOW


def download_functions_in_the_package():
    """All public ``download_*`` functions defined in the modules of ``cdec.eo``."""
    functions = {}
    for module_info in pkgutil.iter_modules(cdec.eo.__path__):
        module = importlib.import_module(f"cdec.eo.{module_info.name}")
        for name, function in inspect.getmembers(module, inspect.isfunction):
            defined_here = function.__module__ == module.__name__
            if name.startswith("download_") and defined_here and name != "download_raster_cube":
                functions[name] = function
    return functions


def test_there_are_download_functions_to_check():
    assert len(download_functions_in_the_package()) >= 15


def test_every_download_function_can_be_imported_from_cdec_and_cdec_eo():
    for name in download_functions_in_the_package():
        assert hasattr(cdec, name), f"cdec.{name} is missing - add it to cdec/eo/__init__.py"
        assert hasattr(cdec.eo, name), f"cdec.eo.{name} is missing"
        assert name in cdec.__all__


def test_every_name_in___all___exists():
    for name in cdec.__all__:
        assert hasattr(cdec, name), name
    for name in cdec.eo.__all__:
        assert hasattr(cdec.eo, name), name


def test_every_download_function_has_a_docstring_with_its_parameters():
    for name, function in download_functions_in_the_package().items():
        assert function.__doc__, f"{name} has no docstring"
        for parameter in inspect.signature(function).parameters:
            assert parameter in function.__doc__, f"{name}: parameter '{parameter}' is not documented"


def test_all_download_functions_start_with_the_same_arguments():
    """Consistent API: download_xxx(file_path, spatial_extent, temporal_extent, ...)."""
    for name, function in download_functions_in_the_package().items():
        parameters = list(inspect.signature(function).parameters)
        assert parameters[:3] == ["file_path", "spatial_extent", "temporal_extent"], name


def test_version_is_available():
    assert isinstance(cdec.__version__, str)


# ----------------------------------------------------------------------------
# Long names and short aliases
# ----------------------------------------------------------------------------
# long name -> short alias. ``download_land_cover`` is already descriptive.
ALIASES = {
    "download_normalized_difference_vegetation_index": "download_ndvi",
    "download_enhanced_vegetation_index": "download_evi",
    "download_normalized_difference_water_index": "download_ndwi",
    "download_normalized_difference_moisture_index": "download_ndmi",
    "download_normalized_difference_snow_index": "download_ndsi",
    "download_true_color_image": "download_tci",
    "download_false_color_urban": "download_urban",
    "download_false_color_infrared": "download_infrared",
    "download_false_color_swir": "download_swir",
    "download_scene_classification_map": "download_scl",
    "download_landsat_ndvi": "download_landsat",
    "download_land_surface_temperature": "download_lst",
    "download_soil_water_index": "download_swi",
    "download_digital_elevation_model": "download_dem",
}


@pytest.mark.parametrize("long_name, short_name", ALIASES.items())
def test_the_short_alias_is_the_same_function_as_the_long_name(long_name, short_name):
    for namespace in (cdec, cdec.eo):
        assert getattr(namespace, short_name) is getattr(namespace, long_name)
    assert long_name in cdec.__all__
    assert short_name in cdec.__all__


def test_every_download_function_is_in_the_alias_table():
    """Reminder: a new download function needs a long name, a short alias and a line in ALIASES."""
    known = set(ALIASES) | set(ALIASES.values()) | {"download_land_cover"}
    assert set(download_functions_in_the_package()) == known


# ----------------------------------------------------------------------------
# The options students see
# ----------------------------------------------------------------------------
def test_technical_options_must_be_passed_by_keyword():
    """``create_cog`` and ``overview_resampling`` cannot be mixed up with the options before them."""
    for name, function in download_functions_in_the_package().items():
        parameters = inspect.signature(function).parameters
        for option in ("create_cog", "overview_resampling"):
            assert parameters[option].kind is inspect.Parameter.KEYWORD_ONLY, f"{name}: {option}"


def test_every_download_function_describes_the_file_it_writes():
    """``help(download_xxx)`` is the place to learn what is in the result: there is no printed summary."""
    for name, function in download_functions_in_the_package().items():
        returns = " ".join(inspect.getdoc(function).split("Returns\n-------")[1].split())  # one line
        assert "Absolute path of the GeoTIFF" in returns, name
        assert re.search(r"pixel size", returns), f"{name}: the Returns section does not give the pixel size"
        assert re.search(r"no[- ]data|without data", returns), f"{name}: the Returns section does not say how no data is stored"
        assert re.search(r"float32|uint8", returns), f"{name}: the Returns section does not give the data type"


SENTINEL2_FUNCTIONS = {
    "download_normalized_difference_vegetation_index": SCL_LAND,
    "download_enhanced_vegetation_index": SCL_LAND,
    "download_normalized_difference_water_index": SCL_LAND_AND_WATER,
    "download_normalized_difference_moisture_index": SCL_LAND,
    "download_normalized_difference_snow_index": SCL_LAND_WATER_AND_SNOW,
    "download_true_color_image": SCL_LAND_AND_WATER,
    "download_false_color_urban": SCL_LAND_AND_WATER,
    "download_false_color_infrared": SCL_LAND_AND_WATER,
    "download_false_color_swir": SCL_LAND_AND_WATER,
}


@pytest.mark.parametrize("name, default_classes", SENTINEL2_FUNCTIONS.items())
def test_sentinel2_functions_put_max_cloud_cover_and_scl_classes_first(name, default_classes):
    parameters = inspect.signature(getattr(cdec, name)).parameters

    assert list(parameters)[3:5] == ["max_cloud_cover", "scl_classes"]
    assert parameters["max_cloud_cover"].default == 20
    assert parameters["scl_classes"].default == default_classes
    assert parameters["max_cloud_cover"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD
    assert parameters["scl_classes"].kind is inspect.Parameter.POSITIONAL_OR_KEYWORD


def test_the_scene_classification_map_has_no_scl_classes_option():
    """It *is* the SCL: nothing can be masked with it. It uses every scene unless told otherwise."""
    parameters = inspect.signature(cdec.download_scene_classification_map).parameters

    assert list(parameters)[3:4] == ["max_cloud_cover"]
    assert "scl_classes" not in parameters
    assert parameters["max_cloud_cover"].default == 100
    assert parameters["overview_resampling"].default == "nearest"
