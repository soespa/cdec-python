"""Sentinel-2 Scene Classification Layer (SCL): what the classes mean.

Every Sentinel-2 L2A scene comes with an extra band, the *Scene Classification
Layer*. For each 20 m pixel it contains one number from 0 to 11 that says what
the pixel probably shows (vegetation, water, cloud, ...). The Sentinel-2
download functions use it to throw away unusable pixels *before* they average
the scenes of your period:

    cdec.download_ndvi(path, area, period, scl_classes=(4, 5))

``scl_classes`` is the list of classes you want to **keep**. Everything else is
treated as no data. If you want to see which classes exist and what they
mean, run::

    import cdec
    cdec.show_scl_classes()          # the whole table
    cdec.show_scl_classes((4, 5))    # the table, with your choice marked

The classification is calculated automatically (by ESA's Sen2Cor processor)
and is not perfect. Thin clouds, haze and cloud edges are sometimes labelled as
land, and snow is sometimes labelled as cloud. Look at your result before you
trust it.

``max_cloud_cover`` and ``scl_classes`` are two different filters:

* ``max_cloud_cover`` drops whole *scenes* that are too cloudy overall.
* ``scl_classes`` drops single *pixels* that are cloudy, shadowed, ...
"""

from __future__ import annotations

from numbers import Integral
from typing import Sequence


# The official class names from the ESA Sentinel-2 L2A product description.
SCL_CLASSES: dict[int, str] = {
    0: "No data",
    1: "Saturated or defective",
    2: "Topographic casted shadows",
    3: "Cloud shadows",
    4: "Vegetation",
    5: "Not vegetated",
    6: "Water",
    7: "Unclassified",
    8: "Cloud, medium probability",
    9: "Cloud, high probability",
    10: "Thin cirrus",
    11: "Snow or ice",
}

# A short explanation for every class and whether you usually want to keep it.
SCL_HINTS: dict[int, str] = {
    0: "No measurement for this pixel (for example outside the satellite's "
       "track). Always exclude.",
    1: "The sensor was overexposed or the pixel is defective, so the values "
       "cannot be trusted. Always exclude.",
    2: "Dark pixels in the shadow of terrain such as hills. Scenes before "
       "2022-01-25 call this class 'dark features/shadows'. Usually exclude.",
    3: "The dark ground under a cloud. The reflectance is too low, which "
       "distorts averages and indices. Exclude.",
    4: "Green plants: forests, fields, grass, parks. Keep for vegetation "
       "indices and most maps.",
    5: "Bare soil, sand, roads, roofs and other built-up surfaces, and "
       "sometimes dry or sparse vegetation. Keep it for city maps.",
    6: "Lakes, rivers and sea. Keep for the water index, true-colour and "
       "false-colour images, exclude for NDVI/EVI (water has no vegetation signal).",
    7: "Pixels the classifier could not assign, often haze, cloud edges or "
       "mixed pixels. Exclude unless you have too few observations.",
    8: "Probably a cloud. Exclude.",
    9: "Almost certainly a cloud. Exclude.",
    10: "High, thin cloud. The ground is partly visible but looks washed out. "
        "Exclude.",
    11: "Snow or ice. Keep only for snow studies; the classifier sometimes "
        "confuses snow with cloud.",
}

# Ready-made selections, so that nobody has to remember the numbers.
SCL_LAND = (4, 5)  # vegetation + not vegetated: the default of NDVI, EVI and NDMI
SCL_LAND_AND_WATER = (4, 5, 6)  # + water: the default of NDWI, true colour and the false-colour images
SCL_LAND_WATER_AND_SNOW = (4, 5, 6, 11)  # + snow or ice: the default of NDSI

# The colours of the scene classification map (the colours of the Copernicus Browser layer).
SCL_COLORS: dict[int, str] = {
    0: "#000000",
    1: "#ff0000",
    2: "#2f2f2f",
    3: "#643200",
    4: "#00a000",
    5: "#ffe65a",
    6: "#0000ff",
    7: "#808080",
    8: "#c0c0c0",
    9: "#ffffff",
    10: "#64c8ff",
    11: "#ff96ff",
}


def show_scl_classes(selected: Sequence[int] | None = None) -> None:
    """Print the SCL classes with a short hint, one line per class.

    Pass the classes you intend to use as ``selected`` to see them marked with
    ``X`` (the classes that would be kept)::

        show_scl_classes((4, 5, 6))
    """
    selected = check_scl_classes(selected) or []

    print("keep  ID  class                       hint")
    for class_id, name in SCL_CLASSES.items():
        mark = "X" if class_id in selected else " "
        print(f"  {mark}   {class_id:>2}  {name:<26}  {SCL_HINTS[class_id]}")


def check_scl_classes(scl_classes: Sequence[int] | None) -> list[int] | None:
    """Validate the ``scl_classes`` argument of the Sentinel-2 download functions.

    Returns ``None`` if masking is switched off (``scl_classes=None``),
    otherwise the class IDs as a list of plain ``int``. Raises ``ValueError``
    for an empty selection or for anything that is not an ID from
    :data:`SCL_CLASSES`.

    The download functions call this *before* connecting to the backend, so
    that a typo fails immediately instead of after the login.
    """
    if scl_classes is None:
        return None

    error_message = (
        "scl_classes must be a non-empty sequence of integer class IDs "
        "from 0 to 11, or None to disable SCL masking. "
        "Run cdec.show_scl_classes() to see what the classes mean."
    )

    try:
        scl_classes = list(scl_classes)
    except TypeError:  # for example scl_classes=4 instead of scl_classes=(4,)
        raise ValueError(error_message) from None

    # ``True``/``False`` count as integers in Python, but are never a class ID.
    all_valid = all(
        isinstance(value, Integral) and not isinstance(value, bool) and value in SCL_CLASSES
        for value in scl_classes
    )
    if not scl_classes or not all_valid:
        raise ValueError(error_message)

    return [int(value) for value in scl_classes]


def describe_scl_classes(scl_classes: Sequence[int] | None) -> str:
    """Write a selection of SCL classes as text, e.g. ``4 Vegetation, 5 Not vegetated``.

    Expects a selection that ``check_scl_classes`` has already accepted.
    """
    if scl_classes is None:
        return "none, SCL masking is switched off"
    return ", ".join(f"{class_id} {SCL_CLASSES[class_id]}" for class_id in scl_classes)
