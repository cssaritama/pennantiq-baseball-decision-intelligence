# Real Data Guide

## Data strategy

PennantIQ must be easy to clone and honest about rights. Therefore it separates:

1. synthetic reproducible pitch data;
2. a small frozen real results snapshot;
3. user-initiated public-data downloads;
4. licensed/team-owned production data.

## Included files

### `data/sample/demo_pitches.csv`

Synthetic. Safe for tests and UI. Not baseball evidence.

### `data/frozen_real/new_york_results_2026.csv`

Factual final scores for the included July 2026 window. It supports a real Command Center preview but not pitch analysis.

## Statcast option

```bash
pip install -r requirements-real.txt
python scripts/download_statcast_pybaseball.py \
  --start 2026-07-01 --end 2026-07-07 --team NYY \
  --output data/real/nyy_week.csv
```

The connector limits the default request to 31 days and enables pybaseball caching. The user must review current MLB/Baseball Savant terms.

## Retrosheet option

```bash
python scripts/download_retrosheet.py --year 2025
```

Retrosheet allows commercial use with its exact attribution statement. The script places that statement beside the files.

## Why no large real pitch dataset is committed

- source terms may restrict redistribution;
- large files reduce clone reliability;
- current data changes;
- a reproducible benchmark should be frozen and licensed;
- production teams should use their own governed data.

## Minimum production data domains

- games and schedule;
- pitch events;
- player and roster identities;
- parks and environmental context;
- video/tracking references;
- injury/health only under appropriate medical and privacy governance;
- human scouting and decision logs.

## Quality checks

- schema and type validation;
- duplicate keys;
- missing players and locations;
- chronological consistency;
- source timestamp and extraction timestamp;
- tracking-system era;
- rule changes;
- impossible count or inning values;
- leakage labels;
- provenance and license.
