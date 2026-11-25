"""Sphinx extension: tables of the package's class dictionaries.

The SCL and WorldCover classes are defined once, in the source code. This
extension builds the tables of the documentation from those dictionaries, so
the documentation cannot differ from the code.

``.. class-table::`` takes the name of a dictionary (class ID -> name) and
optionally a dictionary with hints and one with colours::

    .. class-table:: cdec.SCL_CLASSES
       :hints: cdec.SCL_HINTS

    .. class-table:: cdec.WORLDCOVER_CLASSES
       :colors: cdec.WORLDCOVER_COLORS

``:swatch:`#006400``` writes a hex colour; HTML output adds a small coloured square.
"""

from __future__ import annotations

import re
from importlib import import_module

from docutils import nodes
from docutils.parsers.rst import Directive, directives
from docutils.statemachine import StringList


def load(dotted_name: str) -> dict:
    """Import ``cdec.SCL_CLASSES`` and similar names."""
    module_name, _, attribute = dotted_name.rpartition(".")
    return getattr(import_module(module_name), attribute)


def escape(text: str) -> str:
    """Make a text safe for a reStructuredText table cell."""
    for character in "\\*`_|":
        text = text.replace(character, "\\" + character)
    return text


class ClassTable(Directive):
    required_arguments = 1  # the dictionary with the class names
    option_spec = {
        "hints": directives.unchanged,  # dictionary with a hint per class
        "colors": directives.unchanged,  # dictionary with a hex colour per class
    }

    def run(self):
        names = load(self.arguments[0])
        hints = load(self.options["hints"]) if "hints" in self.options else None
        colors = load(self.options["colors"]) if "colors" in self.options else None

        header = ["ID", "Class"] + (["Hint"] if hints else []) + (["Color"] if colors else [])
        rows = [header]
        for class_id, name in names.items():
            row = [str(class_id), escape(name)]
            if hints:
                row.append(escape(hints[class_id]))
            if colors:
                row.append(f":swatch:`{colors[class_id]}`")
            rows.append(row)

        lines = [".. list-table::", "   :header-rows: 1", "   :widths: auto", ""]
        for row in rows:
            lines.append("   * - " + row[0])
            lines += [f"     - {cell}" for cell in row[1:]]

        # Give the lines the source of the directive. Without a source Sphinx does not offer the
        # table texts for translation (the headings and the hints would stay English).
        source, _ = self.state_machine.get_source_and_line(self.lineno)
        container = nodes.container()
        self.state.nested_parse(StringList(lines, source=source), self.content_offset, container)
        return container.children


def swatch_role(name, rawtext, text, lineno, inliner, options=None, content=None):
    """``:swatch:`#006400``` -> a coloured square and the colour code."""
    color = text.strip()
    if not re.fullmatch(r"#[0-9a-fA-F]{6}", color):
        message = inliner.reporter.error(f"swatch needs a colour like #006400, got {text!r}", line=lineno)
        return [inliner.problematic(rawtext, rawtext, message)], [message]
    square = (
        '<span style="display:inline-block;width:1.1em;height:1.1em;vertical-align:-0.2em;'
        f'margin-right:0.4em;border:1px solid #888;background:{color}"></span>'
    )
    # The square exists only in HTML; the colour code is text in every output format.
    return [nodes.raw("", square, format="html"), nodes.literal(color, color)], []


def setup(app):
    app.add_directive("class-table", ClassTable)
    app.add_role("swatch", swatch_role)
    return {"parallel_read_safe": True, "parallel_write_safe": True}
