#!/usr/bin/env python3
"""
Export a Pipfile.lock into a requirements.txt (and optional dev requirements).
Usage:
    python scripts/export_requirements.py --lockfile Pipfile.lock --out requirements.txt
    python scripts/export_requirements.py --lockfile Pipfile.lock --out requirements-dev.txt --dev

The script will parse the `default` and `develop` sections and write canonical
pip requirement lines, including version pins and environment markers where provided.
"""
from __future__ import annotations
import json
import argparse
from pathlib import Path


def format_req(name: str, data: dict, no_markers: bool = False) -> str:
    # Version is usually like '==1.2.3' or '*'
    version = data.get("version") or ""
    if version == "*" or version == "":
        req = name
    else:
        # version is already a string starting with '==' or similar
        req = f"{name}{version}"

    # extras
    extras = data.get("extras")
    if extras:
        # extras might be a list or dict; normalize
        if isinstance(extras, dict):
            extras = list(extras.keys())
        if isinstance(extras, (list, tuple)):
            req = f"{name}[{', '.join(extras)}]{version}"

    markers = data.get("markers")
    if markers and not no_markers:
        # pip expects ; markers with a space
        req = f"{req} ; {markers}"
    return req


def write_requirements(lockpath: Path, outpath: Path, include_dev: bool = False, no_markers: bool = False) -> None:
    data = json.loads(lockpath.read_text(encoding="utf-8"))
    lines = []
    default = data.get("default", {})
    develop = data.get("develop", {})
    # default
    for name, info in sorted(default.items()):
        lines.append(format_req(name, info, no_markers=no_markers))
    # optionally add dev
    if include_dev and develop:
        lines.append("")
        lines.append("# development packages")
        for name, info in sorted(develop.items()):
            lines.append(format_req(name, info, no_markers=no_markers))

    outpath.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lockfile", default="Pipfile.lock", help="Path to Pipfile.lock")
    parser.add_argument("--out", default="requirements.txt", help="Output requirements file")
    parser.add_argument("--dev", action="store_true", help="Include develop section as development packages")
    parser.add_argument("--no-markers", action="store_true", help="Strip environment markers like '; python_version >= \"3.8\"'")
    args = parser.parse_args()
    lock = Path(args.lockfile)
    if not lock.exists():
        raise SystemExit(f"Lock file not found: {lock}")
    out = Path(args.out)
    write_requirements(lock, out, args.dev, args.no_markers)
    print(f"Wrote requirements to {out}")
