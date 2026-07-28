# Time × Space Context Engine

## Objective

Identify useful contextual signals without confusing correlation with cause.

## Supported public fields

| Domain | Variables |
|---|---|
| Time | date, recency, day of week, season phase, local time, day/night, rest, appearance number |
| Game state | count, inning, times through order when available |
| Space | home/away, venue, pitch coordinates, elevation |
| Environment | temperature, wind, wind direction, roof |
| Competition | opponent, batter side, pitcher hand, pitch family, zone |
| Outcomes | defensive run-value proxy, whiff, hard contact |

## Statistical policy

1. Compute the raw group result.
2. Shrink the group toward the pitcher's overall prior.
3. report `n`, games and sample share.
4. label evidence as strong, moderate, weak or insufficient.
5. warn about multiple comparisons and confounding.
6. require out-of-sample persistence before a pattern enters an approved playbook.

## Example: Monday versus Wednesday

A weekday signal may actually reflect:

- rotation schedule and rest;
- quality of opponents;
- home/away mix;
- day/night schedule;
- travel;
- weather;
- pitcher role or injury context.

PennantIQ therefore treats weekday as an exploration dimension, not an explanation.

## Future production controls

- hierarchical models by pitcher/team/league;
- park and opponent strength adjustments;
- false-discovery control;
- rolling temporal validation;
- rule/era segmentation;
- weather and travel connectors;
- analyst-approved feature registry.
