"""Offline tests of all ``download_*`` functions (no internet, no login).

``fake_openeo`` (see conftest.py) replaces the openEO backend. These tests check

* WHAT is requested from openEO: collection, bands, extents, processing steps
* WHAT the package does with the downloaded file: Cloud Optimized GeoTIFF,
  colours, no-data mask, output path

Whether the real backend delivers sensible data is tested in
``test_download_live.py``.
"""

import numpy as np
import pytest
import rasterio

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
)
from cdec.eo.scl import SCL_CLASSES, SCL_COLORS
from cdec.eo.util import DEFAULT_DEM_TEMPORAL_EXTENT
from cdec.eo.worldcover import WORLDCOVER_COLORS, WORLDCOVER_TEMPORAL_EXTENT

from .helpers import assert_valid_cog, find_numbers, find_processes


# One row per data type:
#   function, openEO collection, bands that are loaded, reducer over time, bands in the result
ALL_DOWNLOADS = [
    pytest.param(download_ndvi, "SENTINEL2_L2A", ["B04", "B08", "SCL"], "mean", 1, id="ndvi"),
    pytest.param(download_evi, "SENTINEL2_L2A", ["B02", "B04", "B08", "SCL"], "mean", 1, id="evi"),
    pytest.param(download_ndwi, "SENTINEL2_L2A", ["B03", "B08", "SCL"], "mean", 1, id="ndwi"),
    pytest.param(download_ndmi, "SENTINEL2_L2A", ["B8A", "B11", "SCL"], "mean", 1, id="ndmi"),
    pytest.param(download_ndsi, "SENTINEL2_L2A", ["B03", "B11", "SCL"], "mean", 1, id="ndsi"),
    pytest.param(download_landsat, "LANDSAT_BIMONTHLY_MOSAIC", ["B03", "B04"], "mean", 1, id="landsat"),
    pytest.param(download_tci, "SENTINEL2_L2A", ["B04", "B03", "B02", "SCL"], "mean", 3, id="tci"),
    pytest.param(download_urban, "SENTINEL2_L2A", ["B12", "B11", "B04", "SCL"], "mean", 3, id="urban"),
    pytest.param(download_infrared, "SENTINEL2_L2A", ["B08", "B04", "B03", "SCL"], "mean", 3, id="infrared"),
    pytest.param(download_swir, "SENTINEL2_L2A", ["B12", "B8A", "B04", "SCL"], "mean", 3, id="swir"),
    pytest.param(download_scl, "SENTINEL2_L2A", ["SCL"], "last", 1, id="scl"),
    pytest.param(download_dem, "COPERNICUS_30", ["DEM"], "mean", 1, id="dem"),
    pytest.param(download_lst, "SENTINEL3_SLSTR_L2_LST", ["LST"], "mean", 1, id="lst"),
    pytest.param(download_land_cover, "ESA_WORLDCOVER_10M_2021_V2", ["MAP"], "max", 1, id="land_cover"),
    pytest.param(download_swi, "CLMS_SWI_EUROPE_1KM_DAILY_V2", ["swi002"], "mean", 1, id="swi"),
]

# The Sentinel-2 functions with SCL masking: function, default classes that are kept
SENTINEL2_DOWNLOADS = [
    pytest.param(download_ndvi, [4, 5], id="ndvi"),
    pytest.param(download_evi, [4, 5], id="evi"),
    pytest.param(download_ndwi, [4, 5, 6], id="ndwi"),
    pytest.param(download_ndmi, [4, 5], id="ndmi"),
    pytest.param(download_ndsi, [4, 5, 6, 11], id="ndsi"),
    pytest.param(download_tci, [4, 5, 6], id="tci"),
    pytest.param(download_urban, [4, 5, 6], id="urban"),
    pytest.param(download_infrared, [4, 5, 6], id="infrared"),
    pytest.param(download_swir, [4, 5, 6], id="swir"),
]


# ----------------------------------------------------------------------------
# What is requested from openEO
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("download, collection, bands, reducer, result_bands", ALL_DOWNLOADS)
def test_requests_the_right_data(
    download, collection, bands, reducer, result_bands,
    fake_openeo, tmp_path, spatial_extent, temporal_extent,
):
    fake_openeo.result_bands = result_bands

    download(tmp_path / "result.tif", spatial_extent, temporal_extent)

    (request,) = fake_openeo.load_collection_calls
    assert request["collection_id"] == collection
    assert request["bands"] == bands
    assert request["spatial_extent"] == spatial_extent
    assert request["temporal_extent"] == temporal_extent

    # The time dimension is reduced to one image with mean (or max for land cover).
    graph = fake_openeo.downloads[0]["process_graph"]
    assert fake_openeo.downloads[0]["format"] == "GTiff"
    assert find_processes(graph, reducer), f"expected a '{reducer}' reducer in the process graph"


def test_static_data_sets_have_a_default_temporal_extent(fake_openeo, tmp_path, spatial_extent):
    """The DEM and the land-cover map do not change, so no period is needed."""
    download_dem(tmp_path / "dem.tif", spatial_extent)
    download_land_cover(tmp_path / "land_cover.tif", spatial_extent)

    dem_request, land_cover_request = fake_openeo.load_collection_calls
    assert dem_request["temporal_extent"] == DEFAULT_DEM_TEMPORAL_EXTENT
    assert land_cover_request["temporal_extent"] == WORLDCOVER_TEMPORAL_EXTENT


# ----------------------------------------------------------------------------
# Sentinel-2: cloud / SCL masking
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("download, default_classes", SENTINEL2_DOWNLOADS)
def test_scl_masking_is_on_by_default(
    download, default_classes, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    fake_openeo.result_bands = 3
    download(tmp_path / "result.tif", spatial_extent, temporal_extent)

    graph = fake_openeo.downloads[0]["process_graph"]
    assert "SCL" in fake_openeo.load_collection_calls[0]["bands"]
    assert find_processes(graph, "mask")
    assert find_processes(graph, "array_contains")[0]["data"] == default_classes


@pytest.mark.parametrize("download, default_classes", SENTINEL2_DOWNLOADS)
def test_scl_classes_can_be_chosen(
    download, default_classes, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    fake_openeo.result_bands = 3
    download(tmp_path / "result.tif", spatial_extent, temporal_extent, scl_classes=(4, 5, 6, 11))

    graph = fake_openeo.downloads[0]["process_graph"]
    assert find_processes(graph, "array_contains")[0]["data"] == [4, 5, 6, 11]


@pytest.mark.parametrize("download, default_classes", SENTINEL2_DOWNLOADS)
def test_scl_masking_can_be_switched_off(
    download, default_classes, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    fake_openeo.result_bands = 3
    download(tmp_path / "result.tif", spatial_extent, temporal_extent, scl_classes=None)

    graph = fake_openeo.downloads[0]["process_graph"]
    assert "SCL" not in fake_openeo.load_collection_calls[0]["bands"]
    assert not find_processes(graph, "mask")


@pytest.mark.parametrize("download, default_classes", SENTINEL2_DOWNLOADS)
@pytest.mark.parametrize("bad_classes", [(), (12,), (-1,), (4.0,), ("4",), (True,), 4])
def test_invalid_scl_classes_fail_before_login(
    download, default_classes, bad_classes,
    fake_openeo, tmp_path, spatial_extent, temporal_extent,
):
    with pytest.raises(ValueError, match="scl_classes"):
        download(tmp_path / "result.tif", spatial_extent, temporal_extent, scl_classes=bad_classes)

    assert fake_openeo.logins == 0
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize("download, default_classes", SENTINEL2_DOWNLOADS)
def test_max_cloud_cover_is_passed_on(
    download, default_classes, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    fake_openeo.result_bands = 3
    download(tmp_path / "result.tif", spatial_extent, temporal_extent, max_cloud_cover=35)

    assert fake_openeo.load_collection_calls[0]["max_cloud_cover"] == 35


@pytest.mark.parametrize("download, default_classes", SENTINEL2_DOWNLOADS)
def test_max_cloud_cover_and_scl_classes_can_be_given_without_their_names(
    download, default_classes, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    """The two options students change most come right after the three standard arguments."""
    fake_openeo.result_bands = 3
    download(tmp_path / "result.tif", spatial_extent, temporal_extent, 35, (4, 5, 6, 11))

    graph = fake_openeo.downloads[0]["process_graph"]
    assert fake_openeo.load_collection_calls[0]["max_cloud_cover"] == 35
    assert find_processes(graph, "array_contains")[0]["data"] == [4, 5, 6, 11]


def test_vegetation_index_formulas_contain_their_constants(
    fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    download_evi(tmp_path / "evi.tif", spatial_extent, temporal_extent)
    evi_graph = fake_openeo.downloads[0]["process_graph"]

    # EVI = 2.5 * (NIR - red) / (NIR + 6 * red - 7.5 * blue + 1) on reflectance
    assert {2.5, 6.0, 7.5, 1.0, 0.0001} <= find_numbers(evi_graph)

    download_ndvi(tmp_path / "ndvi.tif", spatial_extent, temporal_extent)
    ndvi_graph = fake_openeo.downloads[1]["process_graph"]
    for process in ("subtract", "add", "divide"):
        assert find_processes(ndvi_graph, process), f"NDVI needs '{process}'"


def operands_of(graph, process_id):
    """The band labels that a process (``subtract`` or ``add``) uses as x and y, e.g. ``("B03", "B08")``."""
    (arguments,) = [a for a in find_processes(graph, process_id) if "x" in a and "y" in a]
    reducer_nodes = {
        node_id: node
        for process in find_processes(graph, "reduce_dimension")
        for node_id, node in process["reducer"]["process_graph"].items()
    }

    def label(reference):
        return reducer_nodes[reference["from_node"]]["arguments"]["label"]

    return label(arguments["x"]), label(arguments["y"])


@pytest.mark.parametrize(
    "download, first, second",
    [
        pytest.param(download_ndwi, "B03", "B08", id="ndwi"),  # (green - NIR) / (green + NIR)
        pytest.param(download_ndmi, "B8A", "B11", id="ndmi"),  # (NIR - SWIR) / (NIR + SWIR)
        pytest.param(download_ndsi, "B03", "B11", id="ndsi"),  # (green - SWIR) / (green + SWIR)
    ],
)
def test_normalized_difference_indices_subtract_in_the_right_order(
    download, first, second, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    """The index is (first - second) / (first + second). Swapped bands would turn the sign around."""
    download(tmp_path / "index.tif", spatial_extent, temporal_extent)
    graph = fake_openeo.downloads[0]["process_graph"]

    assert operands_of(graph, "subtract") == (first, second)
    assert sorted(operands_of(graph, "add")) == sorted((first, second))
    assert find_processes(graph, "divide")


# ----------------------------------------------------------------------------
# Scene classification map: the most recent class of every pixel
# ----------------------------------------------------------------------------
def test_the_scene_classification_map_is_not_averaged_and_not_masked(
    fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    download_scl(tmp_path / "scl.tif", spatial_extent, temporal_extent)

    graph = fake_openeo.downloads[0]["process_graph"]
    assert find_processes(graph, "last")
    assert not find_processes(graph, "mean")  # class numbers have no average
    assert not find_processes(graph, "mask")
    assert fake_openeo.load_collection_calls[0]["max_cloud_cover"] == 100  # clouds are what the map shows


def test_the_scene_classification_map_can_ignore_cloudy_scenes(
    fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    download_scl(tmp_path / "scl.tif", spatial_extent, temporal_extent, max_cloud_cover=40)

    assert fake_openeo.load_collection_calls[0]["max_cloud_cover"] == 40


@pytest.mark.parametrize("backend_dtype", ["uint8", "float32", "int16"])
def test_the_scene_classification_map_gets_the_scl_colour_table(
    backend_dtype, fake_openeo, tmp_path, spatial_extent, temporal_extent
):
    """The colour table must survive for every data type the backend may deliver."""
    fake_openeo.result_dtype = backend_dtype
    fake_openeo.result_class_ids = True

    path = download_scl(tmp_path / "scl.tif", spatial_extent, temporal_extent)

    with rasterio.open(path) as raster:
        assert raster.dtypes == ("uint8",)
        colormap = raster.colormap(1)
        for class_id, color in SCL_COLORS.items():
            assert colormap[class_id][:3] == tuple(bytes.fromhex(color.removeprefix("#")))
        assert colormap[0][3] == 0  # class 0 = no data is transparent
        assert colormap[6][3] == 255
        assert set(raster.read(1).flatten()) <= {0, 10, 30, 50, 80}  # class IDs are untouched


def test_every_scl_class_has_a_colour():
    assert set(SCL_COLORS) == set(SCL_CLASSES)


# ----------------------------------------------------------------------------
# What happens with the downloaded file
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("download, collection, bands, reducer, result_bands", ALL_DOWNLOADS)
def test_result_is_a_cloud_optimized_geotiff_at_the_given_path(
    download, collection, bands, reducer, result_bands,
    fake_openeo, tmp_path, spatial_extent, temporal_extent,
):
    fake_openeo.result_bands = result_bands
    target = tmp_path / "new" / "folder" / "result.tif"  # folders do not exist yet

    returned = download(target, spatial_extent, temporal_extent)

    assert returned == target.resolve()
    assert returned.is_absolute()
    assert_valid_cog(returned)
    with rasterio.open(returned) as raster:
        assert raster.count == result_bands
    # Only the result remains: no hidden temporary folders or partial files.
    assert list(target.parent.iterdir()) == [target]


def test_cog_can_be_switched_off(fake_openeo, tmp_path, spatial_extent):
    cog = download_dem(tmp_path / "cog.tif", spatial_extent, create_cog=True)
    plain = download_dem(tmp_path / "plain.tif", spatial_extent, create_cog=False)

    with rasterio.open(cog) as raster:
        assert raster.profile["tiled"] is True
    with rasterio.open(plain) as raster:
        assert raster.profile["tiled"] is False
    assert set(tmp_path.iterdir()) == {cog, plain}


def test_tci_is_enhanced_to_8_bit_rgb(fake_openeo, tmp_path, spatial_extent, temporal_extent):
    fake_openeo.result_bands = 3  # the "backend" delivers float reflectance with an empty strip

    path = download_tci(tmp_path / "tci.tif", spatial_extent, temporal_extent)

    with rasterio.open(path) as raster:
        assert raster.dtypes == ("uint8", "uint8", "uint8")
        # the 10 empty columns of the made-up download are still marked as "no data"
        assert (raster.read_masks(1)[:, :10] == 0).all()
        assert (raster.read_masks(1)[:, 10:] == 255).all()
        assert (raster.read(1)[:, :10] == 0).all()


def test_tci_enhancement_can_be_switched_off(fake_openeo, tmp_path, spatial_extent, temporal_extent):
    fake_openeo.result_bands = 3

    path = download_tci(tmp_path / "tci.tif", spatial_extent, temporal_extent, enhance_color=False)

    with rasterio.open(path) as raster:
        assert raster.dtypes == ("float32", "float32", "float32")
        assert 0.0 < np.nanmax(raster.read(1)) < 1.0  # untouched reflectance


def test_urban_is_enhanced_to_8_bit_rgb(fake_openeo, tmp_path, spatial_extent, temporal_extent):
    fake_openeo.result_bands = 3

    path = download_urban(tmp_path / "urban.tif", spatial_extent, temporal_extent)

    with rasterio.open(path) as raster:
        assert raster.dtypes == ("uint8", "uint8", "uint8")
        assert (raster.read_masks(1)[:, :10] == 0).all()
        assert (raster.read_masks(1)[:, 10:] == 255).all()


def test_urban_enhancement_can_be_switched_off(fake_openeo, tmp_path, spatial_extent, temporal_extent):
    fake_openeo.result_bands = 3

    path = download_urban(
        tmp_path / "urban.tif", spatial_extent, temporal_extent, enhance_contrast=False
    )

    with rasterio.open(path) as raster:
        assert raster.dtypes == ("float32", "float32", "float32")


@pytest.mark.parametrize("backend_dtype", ["uint8", "float32", "int16"])
def test_land_cover_gets_the_worldcover_colour_table(
    backend_dtype, fake_openeo, tmp_path, spatial_extent
):
    """The colour table must survive for every data type the backend may deliver."""
    fake_openeo.result_dtype = backend_dtype
    fake_openeo.result_class_ids = True

    path = download_land_cover(tmp_path / "land_cover.tif", spatial_extent)

    with rasterio.open(path) as raster:
        assert raster.dtypes == ("uint8",)
        colormap = raster.colormap(1)
        built_up = bytes.fromhex(WORLDCOVER_COLORS[50].removeprefix("#"))
        assert colormap[50][:3] == tuple(built_up)
        assert set(raster.read(1).flatten()) <= {0, 10, 30, 50, 80}  # class IDs are untouched


# ----------------------------------------------------------------------------
# Soil Water Index: the depth chooses the band
# ----------------------------------------------------------------------------
@pytest.mark.parametrize("depth, band", [(2, "swi002"), (20, "swi020"), (100, "swi100")])
def test_swi_depth_selects_the_band(depth, band, fake_openeo, tmp_path, spatial_extent, temporal_extent):
    download_swi(tmp_path / "swi.tif", spatial_extent, temporal_extent, depth=depth)

    assert fake_openeo.load_collection_calls[0]["bands"] == [band]


@pytest.mark.parametrize("bad_depth", [0, 3, 1000, "2", None])
def test_swi_rejects_unknown_depth_before_login(bad_depth, fake_openeo, tmp_path, spatial_extent, temporal_extent):
    with pytest.raises(ValueError, match="depth"):
        download_swi(tmp_path / "swi.tif", spatial_extent, temporal_extent, depth=bad_depth)

    assert fake_openeo.logins == 0
