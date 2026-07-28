#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.pennantiq.gcp import export_dataframe_to_bigquery


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--table", required=True, help="project.dataset.table")
    parser.add_argument("--project")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args()
    frame = pd.read_csv(args.input, low_memory=False)
    disposition = "WRITE_TRUNCATE" if args.replace else "WRITE_APPEND"
    print(export_dataframe_to_bigquery(frame, args.table, args.project, write_disposition=disposition))


if __name__ == "__main__":
    main()
