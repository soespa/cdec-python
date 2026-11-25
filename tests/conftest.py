"""Shared pytest setup.

* the test area and test period (fixtures ``spatial_extent`` / ``temporal_extent``)
* the ``--live`` switch for tests that really download data
* ``fake_openeo``: a stand-in for the openEO backend so most tests run offline
* the matplotlib backend that draws without a window (for ``test_plot.py``)
"""

from contextlib import nullcontext
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # the tests draw plots into memory; no window may open

import openeo
import pytest
from openeo.rest.datacube import DataCube

from cdec.eo.util import get_connection
from .helpers import write_test_raster


# ----------------------------------------------------------------------------
# The area (around Bremen) and the period used by all tests
# ----------------------------------------------------------------------------
SPATIAL_EXTENT = {"west": 8.721771, "south": 53.025027, "east": 8.904419, "north": 53.114965}
TEMPORAL_EXTENT = ["2024-06-01", "2024-06-30"]

# Downloads of the live tests are kept here, so you can open them in QGIS.
OUTPUT_DIR = Path(__file__).parent / "output"


@pytest.fixture
def spatial_extent():
    return dict(SPATIAL_EXTENT)  # a copy, so that no test can change the original


@pytest.fixture
def temporal_extent():
    return list(TEMPORAL_EXTENT)


# ----------------------------------------------------------------------------
# --live: tests that really download data are skipped unless you ask for them
# ----------------------------------------------------------------------------
def pytest_addoption(parser):
    parser.addoption(
        "--live",
        action="store_true",
        default=False,
        help="also run the tests that download real data (needs a Copernicus Data Space login)",
    )


def pytest_collection_modifyitems(config, items):
    if config.getoption("--live"):
        return
    skip_live = pytest.mark.skip(reason="downloads real data: run with --live")
    for item in items:
        if "live" in item.keywords:
            item.add_marker(skip_live)


@pytest.fixture(scope="session")
def openeo_login(request):
    """Log in to the Copernicus Data Space once, before the first live test.

    pytest normally hides everything that is printed. The first login prints a
    web address and a code you have to open in your browser, so the output
    capturing is switched off while logging in. Later runs reuse the token that
    the openEO client stored on your computer and do not ask again.
    """
    capture = request.config.pluginmanager.getplugin("capturemanager")
    with capture.global_and_fixture_disabled() if capture else nullcontext():
        get_connection()


@pytest.fixture
def output_tif(request):
    """Path ``tests/output/<name of the test>.tif`` for a live test.

    A file from an earlier run is removed first, so a failing download can
    never be hidden by an old result.
    """
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"{request.node.name}.tif"
    path.unlink(missing_ok=True)
    return path


# ----------------------------------------------------------------------------
# fake_openeo: the backend for offline tests
# ----------------------------------------------------------------------------
class FakeBackend:
    """Stands in for the openEO backend, so tests need no internet and no login.

    * ``load_collection`` records the request and builds a *real* openEO data
      cube (only the process graph, nothing is sent anywhere).
    * ``cube.download`` records the finished process graph and writes a small
      made-up GeoTIFF instead of downloading.

    Tests can set what the "backend" delivers before they call a download
    function: ``result_bands``, ``result_dtype`` and ``result_class_ids``.
    """

    def __init__(self):
        self.result_bands = 1
        self.result_dtype = "float32"
        self.result_class_ids = False

        self.logins = 0  # how often authenticate_oidc() was called
        self.load_collection_calls = []  # one dict per load_collection(...)
        self.downloads = []  # one dict per download: {"format", "process_graph"}

    # What util.get_connection() calls: openeo.connect(url).authenticate_oidc()
    def connect(self, url, **kwargs):
        return self

    def authenticate_oidc(self):
        self.logins += 1
        return self

    # What the download functions call: connection.load_collection(...)
    def load_collection(self, collection_id, **kwargs):
        self.load_collection_calls.append({"collection_id": collection_id, **kwargs})
        return DataCube.load_collection(collection_id, connection=None, **kwargs)

    # What replaces cube.download(...)
    def download_cube(self, cube, outputfile=None, format=None, **kwargs):
        self.downloads.append({"format": format, "process_graph": cube.flat_graph()})
        write_test_raster(
            outputfile,
            count=self.result_bands,
            dtype=self.result_dtype,
            class_ids=self.result_class_ids,
        )


@pytest.fixture
def fake_openeo(monkeypatch):
    backend = FakeBackend()

    # A plain function (not backend.download_cube) so that Python hands the
    # data cube over as the first argument, like for a real method.
    def download(cube, outputfile=None, format=None, **kwargs):
        backend.download_cube(cube, outputfile, format)

    monkeypatch.setattr(openeo, "connect", backend.connect)
    monkeypatch.setattr(DataCube, "download", download)
    return backend
