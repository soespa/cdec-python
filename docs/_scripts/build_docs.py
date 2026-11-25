"""Build the documentation in every language.

    python docs/_scripts/build_docs.py [output folder]

Writes one folder for each language (``<output>/en``, ``<output>/de``) and an
``<output>/index.html`` that forwards to the language of the browser. The
default output folder is ``docs/_build/html``. Every build uses ``-W``: a
warning is an error, and the exit code is not 0 if any language failed.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

DOCS_DIR = Path(__file__).resolve().parents[1]

REDIRECT = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>CDEC</title>
<script>
  var languages = {languages};
  var wanted = (navigator.language || "en").slice(0, 2).toLowerCase();
  location.replace((languages.indexOf(wanted) >= 0 ? wanted : "en") + "/index.html");
</script>
</head>
<body>
<p>{links}</p>
</body>
</html>
"""


def read_languages():
    """The ``LANGUAGES`` of ``docs/conf.py``: language code -> name."""
    spec = importlib.util.spec_from_file_location("cdec_docs_conf", DOCS_DIR / "conf.py")
    conf = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(conf)
    return conf.LANGUAGES


def main(argv):
    output = Path(argv[1]) if len(argv) > 1 else DOCS_DIR / "_build" / "html"
    languages = read_languages()

    failed = []
    for code in languages:
        print(f"--- {languages[code]} ({code}) ---", flush=True)
        # One process for each language: Sphinx keeps the translations of the first
        # language in memory, so a later language would start from German texts.
        status = subprocess.run(
            [
                sys.executable, "-m", "sphinx",
                "-W", "--keep-going",
                "-b", "html",
                "-D", f"language={code}",
                "-d", str(output.parent / "doctrees" / code),  # one cache for each language
                str(DOCS_DIR),
                str(output / code),
            ]
        ).returncode
        if status:
            failed.append(code)

    links = " | ".join(f'<a href="{code}/index.html">{name}</a>' for code, name in languages.items())
    (output / "index.html").write_text(
        REDIRECT.format(languages=list(languages), links=links), encoding="utf-8"
    )

    if failed:
        print("Failed: " + ", ".join(failed))
        return 1
    print(f"Open {output / 'index.html'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
