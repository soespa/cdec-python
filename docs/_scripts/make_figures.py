"""Draw the example pictures of the data type pages.

The pictures show real data (Bremen, see the captions). They are made from the
files that ``pytest --live`` downloaded to ``tests/output/``, and they are saved
in ``docs/_static/figures/``. Run this script again when a plot function
changes, and commit the new pictures::

    python docs/_scripts/make_figures.py
"""

from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "src"))

import cdec  # noqa: E402

DOWNLOADS = ROOT / "tests" / "output"
FIGURES = ROOT / "docs" / "_static" / "figures"

# picture name -> (file downloaded by the live tests, plot function)
FIGURE_SOURCES = {
    "ndvi": ("test_ndvi.tif", cdec.plot_ndvi),
    "evi": ("test_evi.tif", cdec.plot_evi),
    "ndwi": ("test_ndwi.tif", cdec.plot_ndwi),
    "ndmi": ("test_ndmi.tif", cdec.plot_ndmi),
    "ndsi": ("test_ndsi_zugspitze.tif", cdec.plot_ndsi),  # Bremen has no snow in June: the Alps in winter
    "true-color": ("test_tci.tif", cdec.plot_tci),
    "false-color-urban": ("test_urban.tif", cdec.plot_urban),
    "false-color-infrared": ("test_infrared.tif", cdec.plot_infrared),
    "false-color-swir": ("test_swir.tif", cdec.plot_swir),
    "scene-classification": ("test_scl.tif", cdec.plot_scl),
    "landsat-ndvi": ("test_landsat.tif", cdec.plot_landsat),
    "land-surface-temperature": ("test_lst.tif", cdec.plot_lst),
    "soil-water-index": ("test_swi_for_a_period_covered_by_version_2.tif", cdec.plot_swi),
    "elevation": ("test_dem.tif", cdec.plot_dem),
    "land-cover": ("test_land_cover.tif", cdec.plot_land_cover),
}


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    for name, (file_name, plot) in FIGURE_SOURCES.items():
        source = DOWNLOADS / file_name
        if not source.exists():  # not downloaded yet: draw the others
            print(f"skipped {name}: {source.name} is missing, run  pytest --live")
            continue
        ax = plot(source, show=False, title="")
        ax.figure.set_size_inches(7, 5)
        ax.figure.savefig(FIGURES / f"{name}.png", dpi=80, bbox_inches="tight")
        print("wrote", FIGURES / f"{name}.png")


if __name__ == "__main__":
    main()
