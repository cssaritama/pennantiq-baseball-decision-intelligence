#!/usr/bin/env python3
"""User-initiated Statcast download through pybaseball.

The script does not redistribute MLB data. Review the current source terms before use.
Requests are intentionally bounded to reduce load and improve reproducibility.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.pennantiq.data import normalize_statcast_dataframe


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", required=True, help="YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="YYYY-MM-DD")
    parser.add_argument("--team", help="MLB abbreviation such as NYY or NYM")
    parser.add_argument("--output", default="data/real/statcast.csv")
    parser.add_argument("--max-days", type=int, default=31)
    args = parser.parse_args()

    from pandas import Timestamp
    start = Timestamp(args.start); end = Timestamp(args.end)
    if end < start:
        raise SystemExit("--end must be on or after --start")
    if (end - start).days + 1 > args.max_days:
        raise SystemExit(f"Request exceeds the configured {args.max_days}-day safety limit.")

    try:
        from pybaseball import cache, statcast
    except ImportError as exc:
        raise SystemExit("Install requirements-real.txt first.") from exc

    cache.enable()
    raw = statcast(args.start, args.end, team=args.team, verbose=True, parallel=True)
    normalized = normalize_statcast_dataframe(raw)
    normalized["data_provenance"] = "statcast_user_download_pybaseball"
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    normalized.to_csv(output, index=False)
    print(f"Saved {len(normalized):,} normalized pitch records to {output}")
    print("Do not commit this file unless you have verified redistribution rights.")


if __name__ == "__main__":
    main()
