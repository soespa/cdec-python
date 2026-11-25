"""Tests of the Scene Classification Layer (SCL) helpers in ``cdec.eo.scl`` (offline)."""

import numpy as np
import pytest

import cdec
from cdec.eo.scl import (
    SCL_CLASSES,
    SCL_COLORS,
    SCL_HINTS,
    SCL_LAND,
    SCL_LAND_AND_WATER,
    SCL_LAND_WATER_AND_SNOW,
    check_scl_classes,
    show_scl_classes,
)


# ----------------------------------------------------------------------------
# The class table
# ----------------------------------------------------------------------------
def test_scl_has_the_twelve_official_classes_zero_to_eleven():
    assert list(SCL_CLASSES) == list(range(12))


def test_every_class_has_a_name_and_a_hint():
    assert set(SCL_HINTS) == set(SCL_CLASSES)
    for class_id in SCL_CLASSES:
        assert SCL_CLASSES[class_id].strip(), class_id
        assert SCL_HINTS[class_id].strip(), class_id


def test_the_names_of_the_classes_students_use_most_are_right():
    """Guards against a typo in the table: these are the classes of the default selections."""
    assert SCL_CLASSES[4] == "Vegetation"
    assert SCL_CLASSES[5] == "Not vegetated"
    assert SCL_CLASSES[6] == "Water"
    assert SCL_CLASSES[9] == "Cloud, high probability"
    assert SCL_CLASSES[10] == "Thin cirrus"


def test_the_ready_made_selections_are_valid():
    assert SCL_LAND == (4, 5)
    assert SCL_LAND_AND_WATER == (4, 5, 6)
    assert SCL_LAND_WATER_AND_SNOW == (4, 5, 6, 11)
    assert check_scl_classes(SCL_LAND) == [4, 5]
    assert check_scl_classes(SCL_LAND_AND_WATER) == [4, 5, 6]
    assert check_scl_classes(SCL_LAND_WATER_AND_SNOW) == [4, 5, 6, 11]


def test_every_class_has_a_colour_in_the_form_of_a_hex_code():
    assert set(SCL_COLORS) == set(SCL_CLASSES)
    for class_id, color in SCL_COLORS.items():
        assert len(color) == 7 and color.startswith("#"), class_id
        int(color[1:], 16)  # raises ValueError if it is not hexadecimal
    assert len(set(SCL_COLORS.values())) == len(SCL_COLORS), "two classes share a colour"


def test_the_scl_names_are_available_from_the_package():
    assert cdec.SCL_CLASSES is SCL_CLASSES
    assert cdec.SCL_HINTS is SCL_HINTS
    assert cdec.SCL_LAND == SCL_LAND
    assert cdec.SCL_LAND_AND_WATER == SCL_LAND_AND_WATER
    assert cdec.SCL_LAND_WATER_AND_SNOW == SCL_LAND_WATER_AND_SNOW
    assert cdec.SCL_COLORS is SCL_COLORS
    assert cdec.show_scl_classes is show_scl_classes


# ----------------------------------------------------------------------------
# show_scl_classes
# ----------------------------------------------------------------------------
def test_show_scl_classes_prints_one_line_per_class(capsys):
    show_scl_classes()

    lines = capsys.readouterr().out.strip().splitlines()
    assert len(lines) == 1 + 12  # header + classes
    assert "Vegetation" in lines[1 + 4]
    assert all("X" not in line for line in lines[1:])  # nothing selected


def test_show_scl_classes_marks_the_selected_classes(capsys):
    show_scl_classes((4, 6))

    lines = capsys.readouterr().out.strip().splitlines()[1:]
    marked = [index for index, line in enumerate(lines) if line.lstrip().startswith("X")]
    assert marked == [4, 6]


def test_show_scl_classes_rejects_an_invalid_selection():
    with pytest.raises(ValueError, match="scl_classes"):
        show_scl_classes((4, 12))


# ----------------------------------------------------------------------------
# check_scl_classes
# ----------------------------------------------------------------------------
@pytest.mark.parametrize(
    "given, expected",
    [
        (None, None),  # None switches masking off
        ((4, 5), [4, 5]),
        ([0, 11], [0, 11]),
        (np.array([4, 5, 6]), [4, 5, 6]),
        ([np.int64(6)], [6]),
    ],
)
def test_check_scl_classes_accepts_valid_input(given, expected):
    result = check_scl_classes(given)

    assert result == expected
    if expected is not None:
        assert all(type(value) is int for value in result)  # plain ints, ready for openEO


@pytest.mark.parametrize(
    "bad", [(), [], (12,), (-1,), (4.0,), ("4",), (True,), [4, None], 4, "45"]
)
def test_check_scl_classes_rejects_invalid_input(bad):
    with pytest.raises(ValueError, match="scl_classes"):
        check_scl_classes(bad)


def test_the_error_message_points_to_the_table():
    with pytest.raises(ValueError, match="show_scl_classes"):
        check_scl_classes((99,))
