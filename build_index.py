#!/usr/bin/env python3
"""Regenerate the PEP 503 'simple' index from the wheels/ directory."""

import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent
WHEELS_DIR = ROOT / "wheels"
SIMPLE_DIR = ROOT / "simple"

DIST_FILE_RE = re.compile(r"\.(whl|tar\.gz|tar\.bz2|zip)$")


def normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def dist_name(filename: str) -> str:
    if filename.endswith(".whl"):
        # PEP 427: {name}-{version}-{build}?-{tag}-{abi}-{platform}.whl
        return filename.split("-")[0]
    # sdist: {name}-{version}.tar.gz / .tar.bz2 / .zip
    stem = DIST_FILE_RE.sub("", filename)
    return stem.rsplit("-", 1)[0]


def main() -> None:
    WHEELS_DIR.mkdir(exist_ok=True)
    if SIMPLE_DIR.exists():
        shutil.rmtree(SIMPLE_DIR)
    SIMPLE_DIR.mkdir()

    packages: dict[str, list[str]] = {}
    for path in sorted(WHEELS_DIR.iterdir()):
        if not path.is_file() or not DIST_FILE_RE.search(path.name):
            continue
        name = normalize(dist_name(path.name))
        packages.setdefault(name, []).append(path.name)

    for name, files in packages.items():
        pkg_dir = SIMPLE_DIR / name
        pkg_dir.mkdir()
        links = "\n".join(
            f'    <a href="../../wheels/{f}">{f}</a><br>' for f in files
        )
        (pkg_dir / "index.html").write_text(
            f"<!DOCTYPE html>\n<html>\n  <body>\n{links}\n  </body>\n</html>\n"
        )

    top_links = "\n".join(
        f'    <a href="{name}/">{name}</a><br>' for name in sorted(packages)
    )
    (SIMPLE_DIR / "index.html").write_text(
        f"<!DOCTYPE html>\n<html>\n  <body>\n{top_links}\n  </body>\n</html>\n"
    )

    print(f"Indexed {len(packages)} package(s) from {WHEELS_DIR}")


if __name__ == "__main__":
    main()
