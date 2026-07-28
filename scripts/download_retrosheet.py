#!/usr/bin/env python3
"""Download selected Retrosheet CSV products for a completed season.

Retrosheet permits commercial use with a mandatory attribution statement. This
script writes that statement beside every downloaded dataset. Verify the current
Retrosheet notice before redistribution.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import shutil
import urllib.request
import zipfile

ATTRIBUTION = """The information used here was obtained free of
charge from and is copyrighted by Retrosheet. Interested
parties may contact Retrosheet at 20 Sunset Rd.,
Newark, DE 19711.
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=2025)
    parser.add_argument("--output-dir", default="data/retrosheet")
    parser.add_argument(
        "--files", nargs="+", default=["gameinfo.csv", "teamstats.csv", "pitching.csv"],
        help="Files to extract from the annual CSV package.",
    )
    args = parser.parse_args()
    if args.year > 2025:
        raise SystemExit("The bundled connector targets completed Retrosheet releases through 2025.")

    output = Path(args.output_dir) / str(args.year)
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f"{args.year}csvs.zip"
    url = f"https://www.retrosheet.org/downloads/{args.year}/{args.year}csvs.zip"
    print(f"Downloading {url}")
    with urllib.request.urlopen(url, timeout=120) as response, archive.open("wb") as target:
        shutil.copyfileobj(response, target)

    extracted = []
    with zipfile.ZipFile(archive) as bundle:
        members = {Path(name).name: name for name in bundle.namelist()}
        for filename in args.files:
            if filename not in members:
                print(f"Warning: {filename} not found in package")
                continue
            destination = output / filename
            with bundle.open(members[filename]) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target)
            extracted.append(destination)

    (output / "RETROSHEET_ATTRIBUTION.txt").write_text(ATTRIBUTION, encoding="utf-8")
    print("Extracted:")
    for path in extracted:
        print(f"- {path}")
    print("Mandatory attribution written to RETROSHEET_ATTRIBUTION.txt")


if __name__ == "__main__":
    main()
