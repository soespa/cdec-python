"""Look at the plot functions: draw all of them into one picture.

Not a test (pytest does not run it): run it yourself.

    python tests/plot_gallery.py              # made-up landscape, works offline
    python tests/plot_gallery.py --real       # the files in tests/output (from `pytest --live`)
    python tests/plot_gallery.py --no-show    # only write the picture, open no window

The picture is also saved: tests/output/plot_gallery_made_up.png or
tests/output/plot_gallery_real.png. Open it, or call a plot function yourself:

    from cdec import plot_ndvi
    plot_ndvi("tests/output/test_ndvi.tif")
"""

import argparse
import sys
import tempfile
from pathlib import Path

import matplotlib
import numpy as np
import rasterio
from rasterio.transform import from_origin

HERE = Path(__file__).parent
OUTPUT_DIR = HERE / "output"

parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument("--real", action="store_true", help="draw the files in tests/output instead of made-up data")
parser.add_argument("--no-show", action="store_true", help="do not open a window, only save the picture")
arguments = parser.parse_args()

if arguments.no_show:
    matplotlib.use("Agg")  # draw into memory, no window (also works on a computer without a screen)

import matplotlib.pyplot as plt  # noqa: E402  (after the backend was chosen)

sys.path.insert(0, str(HERE.parent / "src"))  # so that it also works without "pip install -e ."
from cdec import (  # noqa: E402
    plot_dem, plot_evi, plot_infrared, plot_land_cover, plot_landsat, plot_lst, plot_ndmi, plot_ndsi,
    plot_ndvi, plot_ndwi, plot_scl, plot_swi, plot_swir, plot_tci, plot_urban,
)
from cdec.eo.postprocessing import enhance_color_raster, enhance_contrast_raster  # noqa: E402
from cdec.eo.scene_classification import _apply_scl_colormap  # noqa: E402
from cdec.eo.worldcover import _apply_worldcover_colormap  # noqa: E402


# ----------------------------------------------------------------------------
# The files to draw: a list of (file, plot function)
# ----------------------------------------------------------------------------
def real_files() -> list[tuple[Path, callable]]:
    """The downloads of the live tests. The name of the file tells which plot function fits."""
    # first match wins: "landsat" must be checked before "ndvi"
    plot_function_for = [
        ("swi", plot_swi), ("land_cover", plot_land_cover), ("landsat", plot_landsat),
        ("ndvi", plot_ndvi), ("evi", plot_evi), ("ndwi", plot_ndwi), ("ndmi", plot_ndmi), ("ndsi", plot_ndsi),
        ("tci", plot_tci), ("urban", plot_urban), ("infrared", plot_infrared), ("swir", plot_swir),
        ("scl", plot_scl), ("lst", plot_lst), ("dem", plot_dem),
    ]
    found = []
    for path in sorted(OUTPUT_DIR.glob("*.tif")):
        for keyword, plot_function in plot_function_for:
            if keyword in path.name:
                found.append((path, plot_function))
                break
        else:
            print(f"skipped {path.name}: no plot function known for this name")
    return found


def made_up_files(folder: Path) -> list[tuple[Path, callable]]:
    """A small landscape with a river, a town and fields, written like the backend would write it.

    The Sentinel-2 files are in UTM (metres), the other files in longitude/latitude (degrees),
    as in the real downloads.
    """
    rng = np.random.default_rng(1)
    height, width = 120, 150
    y, x = np.mgrid[0:height, 0:width]
    river = np.abs(y - (40 + 25 * np.sin(x / 18))) < 5
    town = (x - 100) ** 2 + (y - 85) ** 2 < 22**2
    fields = (np.sin(x / 9) * np.cos(y / 7) > 0.2) & ~town & ~river

    def noise(size):
        return rng.normal(0, size, (height, width))

    def empty_edge(band):
        band = band.astype("float32")
        band[:, :12] = np.nan  # a strip without data on the left
        return band

    utm = ("EPSG:32632", from_origin(480000, 5880000, 80, 80))
    degrees = ("EPSG:4326", from_origin(8.72, 53.115, 0.0012, 0.0008))

    def write(name, bands, place, dtype="float32", nodata=None):
        path = folder / name
        crs, transform = place
        with rasterio.open(path, "w", driver="GTiff", count=len(bands), dtype=dtype, width=width, height=height,
                           crs=crs, transform=transform, nodata=nodata) as dst:
            for number, band in enumerate(bands, start=1):
                dst.write(band, number)
        return path

    ndvi = np.where(river, -0.2, np.where(town, 0.12, np.where(fields, 0.75, 0.5))) + noise(0.03)
    red = np.where(town, 0.22, np.where(river, 0.03, 0.05)) + noise(0.005)
    green = np.where(town, 0.21, np.where(river, 0.04, 0.09)) + noise(0.005)
    blue = np.where(town, 0.20, np.where(river, 0.05, 0.04)) + noise(0.005)
    swir2 = np.where(town, 0.28, 0.07) + noise(0.005)
    swir1 = np.where(town, 0.25, np.where(river, 0.01, 0.20)) + noise(0.005)
    temperature = 290 + 12 * town + 3 * fields - 6 * river + noise(0.4)
    height_above_sea = 3 + 0.04 * x + 2 * np.sin(y / 11) - 2.5 * river
    soil_water = np.clip(45 + 35 * river + 15 * fields - 25 * town + noise(3), 0, 100)
    classes = np.where(river, 80, np.where(town, 50, np.where(fields, 40, 10))).astype("uint8")
    classes[:, :12] = 0
    scene = np.where(river, 6, np.where(town, 5, np.where(fields, 4, 4))).astype("uint8")
    scene[(x - 30) ** 2 + (y - 95) ** 2 < 14**2] = 9  # a cloud
    scene[(x - 40) ** 2 + (y - 100) ** 2 < 8**2] = 3  # and its shadow
    scene[:, :12] = 0
    water_index = np.where(river, 0.45, np.where(town, -0.35, -0.6)) + noise(0.04)
    moisture_index = np.where(river, 0.3, np.where(town, -0.1, np.where(fields, 0.4, 0.25))) + noise(0.03)
    snow_index = np.where(river, -0.5, np.where(town, -0.55, -0.7)) + noise(0.04)

    tci = write("true_colour.tif", [empty_edge(red), empty_edge(green), empty_edge(blue)], utm)
    enhance_color_raster(tci)  # like download_tci: an 8-bit picture
    reflectance = write("true_colour_reflectance.tif", [empty_edge(red), empty_edge(green), empty_edge(blue)], utm)
    urban = write("urban.tif", [empty_edge(swir2), empty_edge(swir1), empty_edge(red)], utm)
    enhance_contrast_raster(urban)
    infrared = write("infrared.tif", [empty_edge(0.4 * ndvi + 0.1), empty_edge(red), empty_edge(green)], utm)
    enhance_contrast_raster(infrared)
    swir = write("swir.tif", [empty_edge(swir2), empty_edge(0.4 * ndvi + 0.1), empty_edge(red)], utm)
    enhance_contrast_raster(swir)
    land_cover = write("land_cover.tif", [classes], degrees, dtype="uint8", nodata=0)
    _apply_worldcover_colormap(land_cover)
    scene_classification = write("scl.tif", [scene], utm, dtype="uint8", nodata=0)
    _apply_scl_colormap(scene_classification)

    return [
        (write("ndvi.tif", [empty_edge(ndvi)], utm), plot_ndvi),
        (write("evi.tif", [empty_edge(ndvi * 0.8)], utm), plot_evi),
        (write("ndwi.tif", [empty_edge(water_index)], utm), plot_ndwi),
        (write("ndmi.tif", [empty_edge(moisture_index)], utm), plot_ndmi),
        (write("ndsi.tif", [empty_edge(snow_index)], utm), plot_ndsi),
        (tci, plot_tci),
        (reflectance, plot_tci),
        (urban, plot_urban),
        (infrared, plot_infrared),
        (swir, plot_swir),
        (scene_classification, plot_scl),
        (write("landsat.tif", [empty_edge(ndvi)], degrees), plot_landsat),
        (write("lst.tif", [empty_edge(temperature)], degrees), plot_lst),
        (write("dem.tif", [empty_edge(height_above_sea)], degrees), plot_dem),
        (write("soil_water_index.tif", [empty_edge(soil_water)], degrees), plot_swi),
        (land_cover, plot_land_cover),
    ]


# ----------------------------------------------------------------------------
# Draw them
# ----------------------------------------------------------------------------
def draw(files: list[tuple[Path, callable]], picture: Path) -> None:
    columns = 3
    rows = -(-len(files) // columns)  # round up
    # One sub-figure per plot: the wide legend of the land cover then does not change the others.
    fig = plt.figure(figsize=(6 * columns, 5 * rows), layout="constrained")
    subfigures = np.atleast_1d(fig.subfigures(rows, columns)).ravel()

    for subfigure, (path, plot_function) in zip(subfigures, files):
        ax = subfigure.subplots()
        plot_function(path, ax=ax)  # with ax=: nothing is shown yet
        ax.set_title(f"{ax.get_title()}\n{path.name}", fontsize=9)
        print(f"{plot_function.__name__:<50} {path.name}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    fig.savefig(picture, dpi=80)
    print(f"\nsaved: {picture}")
    if not arguments.no_show:
        plt.show()


if arguments.real:
    files = real_files()
    if not files:
        sys.exit(f"No .tif files in {OUTPUT_DIR}. Run:  pytest --live")
    draw(files, OUTPUT_DIR / "plot_gallery_real.png")
else:
    with tempfile.TemporaryDirectory() as folder:
        draw(made_up_files(Path(folder)), OUTPUT_DIR / "plot_gallery_made_up.png")
