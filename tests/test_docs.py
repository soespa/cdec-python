"""Tests of the documentation: the Sphinx pages in ``docs/`` and the README.

The documentation follows the Diataxis scheme:

* ``docs/tutorial/``     - learning (get started)
* ``docs/howto/``        - recipes for a goal
* ``docs/explanation/``  - background
* ``docs/reference/``    - look-up
* ``docs/data/``         - one page for each data type

* The first tests only read the ``.rst`` files. They always run.
* The other tests build the HTML pages in English and in German (in a
  temporary folder, nothing is written into the repository) and look at the
  result. They are skipped if Sphinx or the theme is not installed (``hatch run test``
  installs both).
* The German texts are in ``docs/locale/de/LC_MESSAGES/*.po``. A test fails
  while an English text has no German translation.
"""

import ast
import html
import importlib
import os
import re
import shutil
import subprocess
import sys
import textwrap
from pathlib import Path
from types import SimpleNamespace

import pytest

import cdec

from .test_package import ALIASES
from .test_plot import PLOT_ALIASES

ROOT = Path(__file__).parent.parent
DOCS_DIR = ROOT / "docs"

#: One page for each downloaded data type: long name of the download function -> page in docs/data/.
#: A new ``download_*`` function must be added here, and needs its page.
DATA_PAGES = {
    "download_normalized_difference_vegetation_index": "ndvi",
    "download_enhanced_vegetation_index": "evi",
    "download_normalized_difference_water_index": "ndwi",
    "download_normalized_difference_moisture_index": "ndmi",
    "download_normalized_difference_snow_index": "ndsi",
    "download_landsat_ndvi": "landsat-ndvi",
    "download_true_color_image": "true-color",
    "download_false_color_urban": "false-color-urban",
    "download_false_color_infrared": "false-color-infrared",
    "download_false_color_swir": "false-color-swir",
    "download_scene_classification_map": "scene-classification",
    "download_land_surface_temperature": "land-surface-temperature",
    "download_soil_water_index": "soil-water-index",
    "download_digital_elevation_model": "elevation",
    "download_land_cover": "land-cover",
}

#: Pages whose picture is not made yet. The picture comes from a real download: run ``pytest --live``, then
#: ``python docs/_scripts/make_figures.py``, then add the picture (``.. figure::`` with alt text and caption)
#: to the page and take it out of this set. While a picture is missing, these pages are not checked for it.
PAGES_WITHOUT_PICTURE_YET: set[str] = set()  # every page has its picture


def has_picture(page):
    return (DOCS_DIR / "_static" / "figures" / f"{page}.png").exists()


#: Short aliases of the download and plot functions (land cover has none).
SHORT_NAMES = {**ALIASES, **PLOT_ALIASES}


def plot_name(download_name):
    return download_name.replace("download_", "plot_", 1)


def page_source(page):
    return (DOCS_DIR / "data" / f"{page}.rst").read_text(encoding="utf-8")


# ----------------------------------------------------------------------------
# The .rst files: is everything that ``import cdec`` offers documented?
# ----------------------------------------------------------------------------
def documented_names():
    """Dotted names (such as ``cdec.download_tci``) used in directives in ``docs/**/*.rst``."""
    pattern = re.compile(r"^\s*\.\. (?:autofunction|autodata|py:data)::\s+(\S+)", re.MULTILINE)
    names = []
    for rst_file in sorted(DOCS_DIR.rglob("*.rst")):
        names += pattern.findall(rst_file.read_text(encoding="utf-8"))
    return names


def import_dotted_name(dotted_name):
    module_name, _, attribute = dotted_name.rpartition(".")
    return getattr(importlib.import_module(module_name), attribute)


def test_there_are_documentation_files():
    assert (DOCS_DIR / "conf.py").exists()
    assert (DOCS_DIR / "index.rst").exists()
    assert len(documented_names()) >= 20


def test_every_documented_name_exists():
    """A typo in an ``autofunction`` line would only show up as a warning when building."""
    for dotted_name in documented_names():
        import_dotted_name(dotted_name)  # raises if the name does not exist


def test_no_name_is_documented_twice():
    """Sphinx complains about a second description of the same object."""
    names = documented_names()
    duplicates = sorted({name for name in names if names.count(name) > 1})
    assert duplicates == []


@pytest.mark.parametrize("name", [name for name in cdec.__all__ if name != "__version__"])
def test_every_public_name_is_documented(name):
    """A new function or constant in ``cdec.__all__`` needs a directive on its page."""
    documented = documented_names()
    if f"cdec.{name}" in documented:
        return

    # A short alias such as download_tci is the same function as download_true_color_image.
    # It is not listed on its own; the documentation of the long name carries a note.
    obj = getattr(cdec, name)
    assert callable(obj), f"cdec.{name} is not documented in docs/**/*.rst"
    documented_functions = [import_dotted_name(dotted_name) for dotted_name in documented]
    assert any(obj is function for function in documented_functions), (
        f"cdec.{name} is not documented in docs/**/*.rst"
    )


# ----------------------------------------------------------------------------
# The structure: tutorial, how-to guides, explanation, reference, data types
# ----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "page",
    [
        "tutorial/get-started",
        "howto/index",
        "explanation/index",
        "reference/index",
        "data/index",
        "contributing",
    ],
)
def test_the_four_parts_and_the_data_pages_exist(page):
    assert (DOCS_DIR / f"{page}.rst").exists()


def test_the_old_pages_that_grouped_data_by_cloud_filter_are_gone():
    """There is no 'Sentinel-2 versus other data' page any more; every data type has its own page."""
    for old_page in ["api.rst", "data.rst", "sentinel2.rst", "quickstart.rst"]:
        assert not (DOCS_DIR / old_page).exists(), old_page


def test_there_is_a_data_page_for_every_download_function():
    download_functions = {
        name for name in cdec.__all__
        if name.startswith("download_") and name not in ALIASES.values()
    }
    assert download_functions == set(DATA_PAGES)


def test_there_are_no_data_pages_without_a_download_function():
    page_names = {path.stem for path in (DOCS_DIR / "data").glob("*.rst")} - {"index"}
    assert page_names == set(DATA_PAGES.values())


@pytest.mark.parametrize("download_name, page", DATA_PAGES.items())
def test_the_data_page_documents_the_download_and_the_plot_function(download_name, page):
    text = page_source(page)
    assert f".. autofunction:: cdec.{download_name}\n" in text
    assert f".. autofunction:: cdec.{plot_name(download_name)}\n" in text


@pytest.mark.parametrize("download_name, page", DATA_PAGES.items())
def test_every_data_page_has_the_same_parts(download_name, page):
    """The same layout everywhere: at a glance, example, things to know, download, plot."""
    text = page_source(page)
    for heading in ["Example", "Things to know", "Download", "Plot"]:
        assert re.search(rf"^{heading}\n-+$", text, re.MULTILINE), f"{page}: heading '{heading}' is missing"
    assert ".. list-table:: At a glance" in text


@pytest.mark.parametrize("download_name, page", DATA_PAGES.items())
def test_every_data_page_has_its_picture(download_name, page):
    if page in PAGES_WITHOUT_PICTURE_YET and not has_picture(page):
        pytest.skip(f"{page}: no picture yet (docs/_static/figures/{page}.png), see PAGES_WITHOUT_PICTURE_YET")
    assert f"/_static/figures/{page}.png" in page_source(page)
    assert (DOCS_DIR / "_static" / "figures" / f"{page}.png").stat().st_size > 5_000


def test_pages_with_a_picture_are_not_listed_as_waiting_for_it():
    """Reminder: when the picture exists and the page shows it, take the page out of PAGES_WITHOUT_PICTURE_YET."""
    assert PAGES_WITHOUT_PICTURE_YET <= set(DATA_PAGES.values())
    for page in PAGES_WITHOUT_PICTURE_YET:
        assert not has_picture(page), (
            f"{page} has its picture: add the figure to docs/data/{page}.rst (alt text, caption) "
            "and remove the page from PAGES_WITHOUT_PICTURE_YET"
        )


# ----------------------------------------------------------------------------
# The code examples: can a student copy one into an empty file and run it?
# ----------------------------------------------------------------------------
def python_examples(source):
    """The Python code blocks of an ``.rst`` or ``.md`` file, as text without the indentation of the page."""
    text = source.read_text(encoding="utf-8")
    if source.suffix == ".md":
        return re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    blocks, lines, i = [], text.splitlines(), 0
    while i < len(lines):
        if not re.match(r"\s*\.\. code-block:: python\s*$", lines[i]):
            i += 1
            continue
        indent = len(lines[i]) - len(lines[i].lstrip())
        block, i = [], i + 1
        while i < len(lines) and (not lines[i].strip() or len(lines[i]) - len(lines[i].lstrip()) > indent):
            block.append(lines[i])
            i += 1
        blocks.append(textwrap.dedent("\n".join(block)).strip("\n") + "\n")
    return blocks


#: Pages with examples that must be complete. The tutorial is left out: it is one session in several steps, and says so.
EXAMPLE_FILES = [
    *sorted((DOCS_DIR / "data").glob("*.rst")),
    *sorted((DOCS_DIR / "howto").glob("*.rst")),
    DOCS_DIR / "index.rst",
    ROOT / "README.md",
]


@pytest.mark.parametrize("source", EXAMPLE_FILES, ids=lambda path: path.name)
def test_examples_define_the_extents_they_use(source):
    """``spatial_extent`` and ``temporal_extent`` are set in the example itself, not on another page."""
    for block in python_examples(source):
        for name in ("spatial_extent", "temporal_extent"):
            if re.search(rf"\b{name}\b", block):
                assert re.search(rf"^\s*{name}\s*=", block, re.MULTILINE), (
                    f"{source.name}: an example uses {name} without defining it:\n{block}"
                )


#: What the made-up backend delivers for the example of a page (the default is one float band).
EXAMPLE_RESULTS = {
    "true-color": {"result_bands": 3, "result_dtype": "uint8"},
    "false-color-urban": {"result_bands": 3, "result_dtype": "uint8"},
    "false-color-infrared": {"result_bands": 3, "result_dtype": "uint8"},
    "false-color-swir": {"result_bands": 3, "result_dtype": "uint8"},
}


@pytest.mark.parametrize("page", sorted(set(DATA_PAGES.values())))
def test_the_example_of_a_data_page_runs_as_it_is(page, fake_openeo, tmp_path, monkeypatch):
    """Copy the example from the page, run it in an empty folder: it downloads a file and draws it."""
    import matplotlib.pyplot as plt

    for attribute, value in EXAMPLE_RESULTS.get(page, {}).items():
        setattr(fake_openeo, attribute, value)
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(plt, "show", lambda *args, **kwargs: None)

    block = python_examples(DOCS_DIR / "data" / f"{page}.rst")[0]  # the first block is the example
    exec(compile(block, f"docs/data/{page}.rst", "exec"), {"__name__": "example"})
    plt.close("all")

    assert len(fake_openeo.downloads) == 1
    assert len(list((tmp_path / "data").glob("*.tif"))) == 1


@pytest.mark.parametrize("download_name, page", DATA_PAGES.items())
def test_the_data_index_lists_every_page_with_its_functions(download_name, page):
    text = (DOCS_DIR / "data" / "index.rst").read_text(encoding="utf-8")
    assert re.search(rf"^   {re.escape(page)}$", text, re.MULTILINE), f"{page} is not in the toctree"
    short = SHORT_NAMES.get(download_name, download_name)
    assert f"``{short}``" in text
    assert f"``{SHORT_NAMES.get(plot_name(download_name), plot_name(download_name))}``" in text


def test_the_data_pages_are_not_grouped_by_cloud_filter():
    """The index groups by what the data is about, not by whether it has a cloud filter."""
    text = (DOCS_DIR / "data" / "index.rst").read_text(encoding="utf-8")
    for heading in [
        "Vegetation", "Water, moisture and snow", "Pictures", "Temperature and soil moisture", "Terrain and land cover",
    ]:
        assert re.search(rf"^{heading}\n-+$", text, re.MULTILINE), heading
    assert "cloud-masked" not in text.lower()


@pytest.mark.parametrize("name", [*ALIASES, *ALIASES.values(), *PLOT_ALIASES, *PLOT_ALIASES.values(), "plot_land_cover", "download_land_cover"])
def test_the_function_list_names_every_function(name):
    """docs/reference/functions.rst: all functions, with long name and alias, in one place."""
    text = (DOCS_DIR / "reference" / "functions.rst").read_text(encoding="utf-8")
    assert name in text


@pytest.mark.parametrize("page", ["ndvi", "evi", "true-color", "false-color-urban"])
def test_the_sentinel2_pages_say_where_the_cloud_filters_are_explained(page):
    text = page_source(page)
    assert "/howto/filter-clouds" in text


def test_the_tutorial_shows_download_help_and_plot():
    text = (DOCS_DIR / "tutorial" / "get-started.rst").read_text(encoding="utf-8")
    for expected in ["pip install cdec", "download_ndvi", "plot_ndvi", "help(download_ndvi)", "rasterio.open"]:
        assert expected in text


# ----------------------------------------------------------------------------
# The README: introduction, installation, quick start, the list of functions, license - and nothing else
# ----------------------------------------------------------------------------
def readme_text():
    return (ROOT / "README.md").read_text(encoding="utf-8")


def test_the_readme_is_short():
    assert len(readme_text().splitlines()) <= 100


def test_the_readme_has_installation_quick_start_data_types_build_and_license():
    headings = re.findall(r"^## (.+)$", readme_text(), re.MULTILINE)
    assert headings == ["Installation", "Quick start", "Data types", "Build and test", "License"]


def test_the_installation_in_the_readme_is_only_pip_install_cdec():
    """Students install the package; the development install is not their business."""
    text = readme_text()
    installation = text[text.index("## Installation"):text.index("## Quick start")]
    assert "pip install cdec" in installation
    assert "pip install -e" not in text
    assert "editable" not in text.lower()
    assert "development" not in installation.lower()


def test_the_readme_describes_hatch_for_the_build_at_the_bottom():
    text = readme_text()
    assert text.index("## Build and test") > text.index("## Data types")
    section = text[text.index("## Build and test"):text.index("## License")]
    for command in ("hatch run test", "hatch run docs:build", "hatch run types:check", "hatch build"):
        assert command in section, command


@pytest.mark.parametrize("download_name", DATA_PAGES)
def test_the_readme_lists_every_download_function(download_name):
    short_name = SHORT_NAMES.get(download_name, download_name)
    assert f"`{short_name}`" in readme_text(), f"{short_name} is missing in the list of data types"


def readme_table_rows():
    """The rows of the table of data types as ``{download function: [cell, ...]}`` (without the header)."""
    rows = {}
    for line in readme_text().splitlines():
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        match = re.fullmatch(r"`(download_\w+)`", cells[1]) if line.startswith("|") and len(cells) > 1 else None
        if match:
            rows[match.group(1)] = cells
    return rows


def test_the_readme_table_has_a_temporal_extent_for_every_data_type():
    header = next(line for line in readme_text().splitlines() if line.startswith("| Data |"))
    assert [cell.strip() for cell in header.strip("|").split("|")][-1] == "Temporal extent"
    rows = readme_table_rows()
    assert len(rows) == len(DATA_PAGES)
    for name, cells in rows.items():
        assert len(cells) == 5, f"{name} needs five cells: data, function, source, pixel size, temporal extent"
        assert cells[4], f"{name} has an empty temporal extent"


def test_the_readme_marks_elevation_and_land_cover_as_static():
    rows = readme_table_rows()
    for name, cells in rows.items():
        assert ("static" in cells[4]) == (name in ("download_dem", "download_land_cover")), name


@pytest.mark.parametrize(
    ("function", "page", "fact"),
    [
        ("download_landsat", "landsat-ndvi", "1997 to 2025"),
        ("download_swi", "soil-water-index", "2025-07-12"),
        ("download_dem", "elevation", "2010 to 2015"),
        ("download_land_cover", "land-cover", "2021"),
    ],
)
def test_the_temporal_extent_of_the_readme_agrees_with_the_data_page(function, page, fact):
    assert fact.split()[-1] in readme_table_rows()[function][4]
    assert fact in " ".join((ROOT / "docs" / "data" / f"{page}.rst").read_text(encoding="utf-8").split())


def test_the_readme_shows_the_ndvi_picture_of_the_documentation():
    """PyPI shows the README on its own, so the picture is linked by its web address. The file must exist."""
    match = re.search(
        r"!\[([^\]]+)\]\(https://raw\.githubusercontent\.com/[^/]+/[^/]+/main/(docs/_static/figures/ndvi\.png)\)",
        readme_text(),
    )
    assert match, "the README needs the NDVI picture (with alt text) from docs/_static/figures/"
    assert (ROOT / match.group(2)).stat().st_size > 5_000


def test_the_readme_points_to_help_for_the_result_of_a_function():
    assert "help(download_ndvi)" in readme_text()


def test_the_readme_does_not_mention_a_printed_summary():
    assert "summary" not in readme_text().lower()
    assert "verbose" not in readme_text().lower()


def test_the_readme_does_not_point_to_the_code_review():
    assert "code-review" not in readme_text().lower()
    assert "code review" not in readme_text().lower()


def test_the_readme_has_no_links_to_files_of_the_repository():
    """PyPI shows the README on its own: a relative link would be broken there."""
    relative_links = re.findall(r"\]\((?!https?://|#)([^)]+)\)", readme_text())
    assert relative_links == []


def test_the_readme_example_uses_functions_that_exist():
    example = re.search(r"```python\n(.*?)```", readme_text(), re.DOTALL).group(1)
    for name in re.findall(r"\b((?:download|plot)_\w+)", example):
        assert hasattr(cdec, name), name


# ----------------------------------------------------------------------------
# The built pages
# ----------------------------------------------------------------------------
@pytest.fixture(scope="module")
def site_folder(tmp_path_factory):
    """A temporary folder for everything the tests build: one sub-folder for each language, like the real site."""
    folder = tmp_path_factory.mktemp("docs")
    # Sphinx compiles the .po files into .mo files next to them. Compile in a copy, not in the repository
    # (and not from an old .mo file that a build left there).
    shutil.copytree(DOCS_DIR / "locale", folder / "locale", ignore=shutil.ignore_patterns("*.mo"))
    return folder


def run_sphinx(site_folder, builder, language, output):
    """Run ``sphinx-build`` with ``-W`` (a warning is an error). Returns the exit status and the warnings.

    Each build runs in a process of its own: Sphinx keeps the translations of the
    first language in memory, so a build in English after a build in German would
    show German texts.
    """
    pytest.importorskip("sphinx")
    pytest.importorskip("furo")

    warnings_file = site_folder / f"warnings-{builder}-{language}.txt"
    command = [
        sys.executable, "-m", "sphinx",
        "-W",  # a warning is an error
        "--keep-going",  # ... but report all of them
        "-q",
        "-b", builder,
        "-D", f"language={language}",
        "-D", f"locale_dirs={site_folder / 'locale'}",
        "-d", str(site_folder / "doctrees" / f"{builder}-{language}"),
        "-w", str(warnings_file),
        str(DOCS_DIR),
        str(output),
    ]
    # No docs/_ext/__pycache__ when conf.py imports the extension.
    completed = subprocess.run(
        command, capture_output=True, text=True, env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    )

    warnings = warnings_file.read_text(encoding="utf-8") if warnings_file.exists() else ""
    if completed.returncode and not warnings.strip():
        warnings = completed.stderr  # Sphinx stopped before it could write the warnings
    return SimpleNamespace(status=completed.returncode, warnings=warnings, html=output)


@pytest.fixture(scope="module")
def built_docs(site_folder):
    """Build the English HTML documentation once for all tests of this file."""
    return run_sphinx(site_folder, "html", "en", site_folder / "html" / "en")


@pytest.fixture(scope="module")
def built_docs_de(site_folder):
    """Build the German HTML documentation once for all tests of this file."""
    return run_sphinx(site_folder, "html", "de", site_folder / "html" / "de")


def page_text(built_docs, page):
    """The text of a page: tags removed, entities decoded, white space collapsed."""
    source = (built_docs.html / f"{page}.html").read_text(encoding="utf-8")
    source = re.sub(r"<(script|style).*?</\1>", "", source, flags=re.DOTALL)
    return squeeze(html.unescape(re.sub(r"<[^>]+>", "", source)))


def squeeze(text):
    """Collapse white space and turn the curly quotes that Sphinx writes into plain ones."""
    text = text.translate(str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'}))
    return re.sub(r"\s+", " ", text)


def test_the_documentation_builds_without_warnings(built_docs):
    assert built_docs.status == 0, f"Sphinx reported problems:\n{built_docs.warnings}"
    assert built_docs.warnings.strip() == ""


def test_every_source_page_becomes_a_html_page(built_docs):
    for rst_file in DOCS_DIR.rglob("*.rst"):
        if "_build" in rst_file.parts:
            continue
        page = rst_file.relative_to(DOCS_DIR).with_suffix(".html")
        assert (built_docs.html / page).exists(), page


def test_the_pictures_are_part_of_the_built_pages(built_docs):
    for page in DATA_PAGES.values():
        if page in PAGES_WITHOUT_PICTURE_YET and not has_picture(page):
            continue
        assert (built_docs.html / "_images" / f"{page}.png").exists(), page


@pytest.mark.parametrize("download_name, page", DATA_PAGES.items())
def test_the_data_page_shows_the_signature_of_both_functions(built_docs, download_name, page):
    text = page_text(built_docs, f"data/{page}")
    assert f"cdec.{download_name}(" in text
    assert f"cdec.{plot_name(download_name)}(file_path, *, ax=None" in text


@pytest.mark.parametrize("download_name, page", DATA_PAGES.items())
def test_the_data_page_shows_the_short_aliases(built_docs, download_name, page):
    text = page_text(built_docs, f"data/{page}")
    for name in (download_name, plot_name(download_name)):
        if name in SHORT_NAMES:
            assert f"Short alias: {SHORT_NAMES[name]}" in text
        else:
            assert "Short alias" not in text.split(f"cdec.{name}(")[1][:300]


def test_the_signature_shows_that_technical_options_are_keyword_only(built_docs):
    text = page_text(built_docs, "data/true-color")
    # "*," in a signature ends the positional arguments; create_cog comes after it.
    assert re.search(r"cdec\.download_true_color_image\(.*?, \*, create_cog=True", text)


def test_the_scl_table_is_generated_from_the_code(built_docs):
    text = page_text(built_docs, "reference/scl")
    for class_id, name in cdec.SCL_CLASSES.items():
        assert squeeze(name) in text, f"SCL class {class_id} ({name}) is missing"
        assert squeeze(cdec.SCL_HINTS[class_id]) in text, f"hint of SCL class {class_id} is missing"


def test_the_worldcover_table_shows_the_colors(built_docs):
    source = (built_docs.html / "data" / "land-cover.html").read_text(encoding="utf-8")
    for class_id, name in cdec.WORLDCOVER_CLASSES.items():
        assert name in html.unescape(source)
        assert cdec.WORLDCOVER_COLORS[class_id].lower() in source.lower()


def test_plot_raster_is_documented_in_the_reference(built_docs):
    assert "cdec.plot_raster(file_path" in page_text(built_docs, "reference/plotting")


# ----------------------------------------------------------------------------
# The languages: English pages, German translation, the switch between them
# ----------------------------------------------------------------------------
LOCALE_DIR = DOCS_DIR / "locale"


def languages():
    """``LANGUAGES`` of ``docs/conf.py`` (language code -> name), read without running the file."""
    match = re.search(r"^LANGUAGES = (\{.*?\})", (DOCS_DIR / "conf.py").read_text(encoding="utf-8"), re.MULTILINE)
    return ast.literal_eval(match.group(1))


def translated_languages():
    return [code for code in languages() if code != "en"]


def source_pages():
    """The pages of the documentation, such as ``data/ndvi`` (without ``.rst``)."""
    return sorted(
        rst_file.relative_to(DOCS_DIR).with_suffix("").as_posix()
        for rst_file in DOCS_DIR.rglob("*.rst")
        if "_build" not in rst_file.parts
    )


def test_english_is_the_first_language_and_german_is_offered():
    assert list(languages())[0] == "en"
    assert "de" in languages()


@pytest.mark.parametrize("code", translated_languages())
def test_every_language_has_a_translation_for_each_part_of_the_documentation(code):
    """Sphinx (``gettext_compact``) uses one ``.po`` file for each folder of ``docs/`` and for each page next to ``index``."""
    parts = {path.name for path in DOCS_DIR.iterdir() if path.is_dir() and any(path.glob("**/*.rst"))}
    parts |= {path.stem for path in DOCS_DIR.glob("*.rst")}
    catalogs = {path.stem for path in (LOCALE_DIR / code / "LC_MESSAGES").glob("*.po")}
    assert catalogs == parts


@pytest.fixture(scope="module")
def english_texts(site_folder):
    """The texts of the English pages that need a translation: Sphinx writes them into ``.pot`` files."""
    result = run_sphinx(site_folder, "gettext", "en", site_folder / "gettext")
    assert result.status == 0, f"Sphinx reported problems:\n{result.warnings}"
    return result.html


@pytest.mark.parametrize("code", translated_languages())
def test_every_english_text_has_a_translation(english_texts, code):
    """Fails after an English text changed: update the ``.po`` files (see docs/contributing.rst) and translate."""
    from babel.messages.pofile import read_po

    problems = []
    for pot_file in sorted(english_texts.glob("*.pot")):
        po_file = LOCALE_DIR / code / "LC_MESSAGES" / pot_file.name.replace(".pot", ".po")
        with open(pot_file, "rb") as file:
            wanted = [message.id for message in read_po(file) if message.id]
        with open(po_file, "rb") as file:
            translations = {message.id: message for message in read_po(file) if message.id}
        for text in wanted:
            translation = translations.get(text)
            if translation is None:
                problems.append(f"{po_file.name}: missing: {text[:70]!r}")
            elif not translation.string or translation.fuzzy:
                problems.append(f"{po_file.name}: untranslated or fuzzy: {text[:70]!r}")
    assert problems == [], "\n".join(problems[:20]) + f"\n... {len(problems)} texts in all"


@pytest.mark.parametrize("code", translated_languages())
def test_the_translations_keep_the_code_and_the_roles(code):
    """Names in ``double back-ticks`` and roles such as ``:func:`` are not translated.

    Sphinx warns about broken markup, but not about a ``literal`` that was typed without
    its back-ticks. If a literal must be translated (a text that is shown to the reader),
    change it here as well.
    """
    babel_pofile = pytest.importorskip("babel.messages.pofile")
    literal = re.compile(r"``.+?``", re.DOTALL)
    role = re.compile(r":(\w+(?::\w+)?):`")

    problems = []
    for po_file in sorted((LOCALE_DIR / code / "LC_MESSAGES").glob("*.po")):
        with open(po_file, "rb") as file:
            for message in babel_pofile.read_po(file):
                if not message.id:
                    continue
                for name, pattern in (("code", literal), ("role", role)):
                    english, translated = sorted(pattern.findall(message.id)), sorted(pattern.findall(message.string))
                    if english != translated:
                        problems.append(f"{po_file.name}: {name} differs in {message.id[:60]!r}")
    assert problems == [], "\n".join(problems[:20]) + f"\n... {len(problems)} texts in all"


def test_the_german_documentation_builds_without_warnings(built_docs_de):
    """A translation that breaks the markup (a role or a ``literal`` that is missing) is a warning."""
    assert built_docs_de.status == 0, f"Sphinx reported problems:\n{built_docs_de.warnings}"
    assert built_docs_de.warnings.strip() == ""


def test_the_german_documentation_has_the_same_pages_as_the_english_one(built_docs, built_docs_de):
    for page in source_pages():
        assert (built_docs.html / f"{page}.html").exists(), page
        assert (built_docs_de.html / f"{page}.html").exists(), page


def test_the_german_pages_are_german(built_docs, built_docs_de):
    english = page_text(built_docs, "data/ndvi")
    german = page_text(built_docs_de, "data/ndvi")
    assert "At a glance" in english and "Auf einen Blick" not in english
    assert "Auf einen Blick" in german and "At a glance" not in german
    # The documentation of the functions (the docstrings) is translated too ...
    assert "Zielpfad der GeoTIFF-Datei" in german
    assert "Target path of the GeoTIFF" not in german
    # ... and the lang attribute tells browsers and screen readers which language it is.
    assert re.search(r'<html[^>]*\blang="de"', (built_docs_de.html / "index.html").read_text(encoding="utf-8"))
    assert re.search(r'<html[^>]*\blang="en"', (built_docs.html / "index.html").read_text(encoding="utf-8"))


@pytest.mark.parametrize("download_name, page", DATA_PAGES.items())
def test_the_german_data_page_shows_the_same_signatures(built_docs_de, download_name, page):
    """Names, arguments and code are not translated."""
    text = page_text(built_docs_de, f"data/{page}")
    assert f"cdec.{download_name}(" in text
    assert f"cdec.{plot_name(download_name)}(file_path, *, ax=None" in text


@pytest.mark.parametrize("language, other", [("en", "de"), ("de", "en")])
def test_every_page_links_to_the_same_page_in_the_other_language(
    site_folder, built_docs, built_docs_de, language, other
):
    names = languages()
    for page in source_pages():
        page_file = site_folder / "html" / language / f"{page}.html"
        source = page_file.read_text(encoding="utf-8")

        # The own language is shown, not linked ...
        assert f"<strong>{names[language]}</strong>" in source, page
        # ... the other one is a link to the same page, which exists.
        links = re.findall(r'<a href="([^"]+)" lang="(\w+)" hreflang="\w+">', source)
        assert [code for _, code in links] == [other], page
        target = (page_file.parent / links[0][0]).resolve()
        assert target == (site_folder / "html" / other / f"{page}.html").resolve(), page
        assert target.exists(), page
