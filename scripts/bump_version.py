#!/usr/bin/env python3
"""Semantic version bump for version.txt, the README badge and the index.html header.

Usage:
    python3 bump_version.py [major|minor|patch] [--dry-run]     (default: patch)

All three targets are validated first; nothing is written unless every pattern
matches exactly once. Each file is then replaced atomically.
"""
import argparse
import os
import re
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
VERSION_FILE = ROOT / "version.txt"
README = ROOT / "README.md"
INDEX = ROOT / "index.html"

SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
README_RE = re.compile(r"(badge/version-)\d+\.\d+\.\d+")
INDEX_RE = re.compile(r'(id="app-version"[^>]*>v)\d+\.\d+\.\d+')


def replace_once(pattern, text, new_version, name):
    found = len(pattern.findall(text))
    if found != 1:
        raise SystemExit(f"{name}: expected exactly 1 version marker, found {found}. Nothing was changed.")
    return pattern.sub(lambda m: m.group(1) + new_version, text)


def atomic_write(path: Path, content: str):
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=path.name + ".", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf8") as f:
            f.write(content)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("kind", nargs="?", default="patch", choices=["major", "minor", "patch"])
    ap.add_argument("--dry-run", action="store_true", help="show the change without writing files")
    args = ap.parse_args()

    if not VERSION_FILE.exists():
        raise SystemExit("version.txt not found. Create it (e.g. with 2.1.0) instead of guessing a version.")
    current = VERSION_FILE.read_text(encoding="utf8").strip()
    if not SEMVER.match(current):
        raise SystemExit(f"version.txt contains {current!r}, expected MAJOR.MINOR.PATCH")

    major, minor, patch = map(int, current.split("."))
    if args.kind == "major":
        major, minor, patch = major + 1, 0, 0
    elif args.kind == "minor":
        minor, patch = minor + 1, 0
    else:
        patch += 1
    new = f"{major}.{minor}.{patch}"

    new_readme = replace_once(README_RE, README.read_text(encoding="utf8"), new, "README.md badge")
    new_index = replace_once(INDEX_RE, INDEX.read_text(encoding="utf8"), new, "index.html header")

    if args.dry_run:
        print(f"[dry-run] would bump {current} -> {new}")
        return
    atomic_write(README, new_readme)
    atomic_write(INDEX, new_index)
    atomic_write(VERSION_FILE, new + "\n")   # written last: version.txt only changes if the others succeeded
    print(f"Successfully bumped version: {current} -> {new}")


if __name__ == "__main__":
    main()
