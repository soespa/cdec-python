"""Sphinx configuration of the CDEC documentation.

Build the HTML pages (English and German) from the repository folder::

    pip install -e ".[docs]"
    python docs/_scripts/build_docs.py

and open ``docs/_build/html/index.html`` in a browser. One language only::

    sphinx-build -b html docs docs/_build/html/en
    sphinx-build -b html -D language=de docs docs/_build/html/de
"""

import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DOCS_DIR.parent / "src"))  # import cdec even if it is not installed
sys.path.insert(0, str(DOCS_DIR / "_ext"))  # our own table directive

import cdec  # noqa: E402  (needs the paths above)

# -- Project information ------------------------------------------------------
project = "CDEC"
author = "Soeren Sparmann"
copyright = "2026, Soeren Sparmann"
release = cdec.__version__
version = release

# -- General configuration ----------------------------------------------------
extensions = [
    "sphinx.ext.autodoc",  # autofunction, automodule: documentation from the docstrings
    "sphinx.ext.napoleon",  # understands the "Parameters" / "Returns" sections of our docstrings
    "sphinx.ext.viewcode",  # a [source] link next to every function
    "cdec_tables",  # tables of the SCL and WorldCover classes (docs/_ext/cdec_tables.py)
]
exclude_patterns = ["_build"]

# -- Languages ----------------------------------------------------------------
# The pages are written in English. The other languages are translations of the
# same pages (docs/locale/<language>/LC_MESSAGES/*.po), built one after the
# other into docs/_build/html/<language>. See "Translate the documentation" in
# docs/contributing.rst.
LANGUAGES = {"en": "English", "de": "Deutsch"}  # code -> name shown in the language switch
language = "en"  # build another language with: -D language=de
locale_dirs = ["locale/"]

# -- Documentation from the docstrings ----------------------------------------
autodoc_member_order = "bysource"  # keep the order of the source file
autodoc_typehints = "description"  # show the types of the arguments in the parameter list
autodoc_typehints_description_target = "documented"
# Show "SpatialExtent" instead of the long union behind it.
autodoc_type_aliases = {
    "SpatialExtent": "SpatialExtent",
    "TemporalExtent": "TemporalExtent",
    "OverviewResampling": "OverviewResampling",
}
napoleon_google_docstring = False  # our docstrings use the NumPy style
toc_object_entries_show_parents = "hide"  # "download_ndvi" instead of "cdec.download_ndvi" in the sidebar

# -- HTML output --------------------------------------------------------------
html_theme = "furo"
html_title = f"CDEC {release}"


def add_alias_note(app, what, name, obj, options, lines):
    """Start the documentation of a download function with its short alias.

    ``download_true_color_image`` and ``download_tci`` are the same function,
    so the alias is found by comparing the objects. Nothing has to be typed.
    """
    if what != "function":
        return
    aliases = [
        alias for alias in cdec.__all__
        if alias != obj.__name__ and getattr(cdec, alias, None) is obj
    ]
    if aliases:
        names = ", ".join(f"``{alias}``" for alias in aliases)
        lines[:0] = [f"*Short alias:* {names}", ""]


def add_language_switch(app, pagename, templatename, context, doctree):
    """Put "English | Deutsch" above every page: links to the same page in the other languages.

    The languages are built into sibling folders (``en/``, ``de/``), so the
    link to the other language is ``../de/<same page>.html``. Search and index
    pages have no document and no switch.
    """
    if doctree is None or "body" not in context:
        return
    links = []
    for code, name in LANGUAGES.items():
        if code == app.config.language:
            links.append(f"<strong>{name}</strong>")
        else:
            target = context["pathto"](f"../{code}/{pagename}.html", 1)
            links.append(f'<a href="{target}" lang="{code}" hreflang="{code}">{name}</a>')
    switch = f'<p class="language-switch" style="text-align:right;margin:0 0 0.5rem">{" | ".join(links)}</p>'
    context["body"] = switch + context["body"]


def setup(app):
    app.connect("autodoc-process-docstring", add_alias_note)
    app.connect("html-page-context", add_language_switch)
