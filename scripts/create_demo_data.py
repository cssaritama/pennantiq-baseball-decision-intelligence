#!/usr/bin/env python3
"""Create PennantIQ's deterministic synthetic demo fixture.

All names and outcomes are fictitious. The generator exists for reproducibility,
UI testing and evaluation mechanics—not for baseball claims.
"""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


VENUES = {
    "Demo Bronx Park": {"elevation_ft": 55, "roof": "open", "park_factor": 1.04},
    "Demo Queens Park": {"elevation_ft": 20, "roof": "open", "park_factor": 0.98},
    "Demo Dome": {"elevation_ft": 640, "roof": "closed", "park_factor": 1.01},
    "Demo West Park": {"elevation_ft": 350, "roof": "open", "park_factor": 0.95},
}


def generate(rows: int = 18000, seed: int = 33) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    records = []
    pitchers = ["Demo Ace", "Demo Lefty", "Demo Power Arm", "Demo Rookie"]
    pitcher_team = {
        "Demo Ace": "DNY", "Demo Lefty": "DNY", "Demo Power Arm": "DQM", "Demo Rookie": "DQM"
    }
    batters = ["Demo Hitter Alpha", "Demo Hitter Beta", "Demo Hitter Gamma", "Demo Hitter Delta"]
    pitch_types = {
        "FF": ("Fastball", 95.2), "SI": ("Sinker", 94.1), "SL": ("Slider", 86.8),
        "CH": ("Changeup", 87.0), "CU": ("Curveball", 80.5),
    }
    dates = pd.date_range("2025-04-01", periods=120, freq="D")
    opponents = ["DBS", "DLA", "DAT", "DCH", "DTB"]

    for row_number in range(rows):
        pitcher = rng.choice(pitchers, p=[0.35, 0.26, 0.31, 0.08])
        batter = rng.choice(batters)
        stand = rng.choice(["L", "R"], p=[0.38, 0.62])
        throws = "L" if pitcher == "Demo Lefty" else "R"
        pitch_type = rng.choice(list(pitch_types), p=[0.38, 0.14, 0.23, 0.16, 0.09])
        pitch_name, base_velocity = pitch_types[pitch_type]
        balls = int(rng.integers(0, 4)); strikes = int(rng.integers(0, 3))
        zone = rng.choice(["heart", "shadow", "chase", "waste"], p=[0.26, 0.35, 0.25, 0.14])
        date = pd.Timestamp(rng.choice(dates))
        is_home = bool(rng.random() < 0.52)
        own_team = pitcher_team[pitcher]; opponent = str(rng.choice(opponents))
        home_team, away_team = (own_team, opponent) if is_home else (opponent, own_team)
        venue = str(rng.choice(list(VENUES)))
        venue_info = VENUES[venue]
        game_hour = int(rng.choice([13, 16, 19], p=[0.24, 0.15, 0.61]))
        day_night = "day" if game_hour < 17 else "night"
        temperature = float(np.clip(rng.normal(73 if venue_info["roof"] == "open" else 72, 11), 42, 99))
        wind_speed = 0.0 if venue_info["roof"] == "closed" else float(np.clip(rng.normal(8, 4), 0, 25))
        wind_direction = str(rng.choice(["in", "out", "cross", "calm"], p=[0.25, 0.25, 0.35, 0.15]))

        quality = {"heart": -0.45, "shadow": 0.35, "chase": 0.55, "waste": -0.05}[zone]
        quality += {"FF": 0.05, "SI": 0.02, "SL": 0.20, "CH": 0.12, "CU": 0.08}[pitch_type]
        if batter == "Demo Hitter Alpha" and pitch_type in ["SL", "CH"]: quality += 0.25
        if batter == "Demo Hitter Beta" and pitch_type == "FF": quality -= 0.20
        if stand == throws and pitch_type in ["SL", "CU"]: quality += 0.10
        if pitcher == "Demo Rookie": quality += rng.normal(-0.03, 0.12)
        if is_home: quality += 0.025
        quality -= (venue_info["park_factor"] - 1.0) * 0.5

        score = quality + float(rng.normal(0, 0.65))
        if score > 0.75:
            description = rng.choice(["swinging_strike", "called_strike", "foul"]); event = "strike"; run_value = -0.08
        elif score > 0.10:
            description = rng.choice(["called_strike", "foul", "hit_into_play"]); event = rng.choice(["field_out", "strike", "field_out"]); run_value = -0.03
        elif score > -0.55:
            description = rng.choice(["ball", "hit_into_play", "foul"]); event = rng.choice(["ball", "field_out", "single"]); run_value = 0.04
        else:
            description = rng.choice(["hit_into_play", "ball"]); event = rng.choice(["double", "home_run", "walk", "single"])
            run_value = {"double": 0.55, "home_run": 1.4, "walk": 0.32, "single": 0.42}[event]

        launch_speed = np.nan if event in ["strike", "ball", "walk"] else float(np.clip(rng.normal(88 + max(-score, 0) * 10, 8), 55, 116))
        plate_x = {"heart": 0.0, "shadow": rng.choice([-0.75, 0.75]), "chase": rng.choice([-1.25, 1.25]), "waste": rng.choice([-1.8, 1.8])}[zone] + rng.normal(0, 0.12)
        plate_z = {"heart": 2.55, "shadow": rng.choice([1.65, 3.35]), "chase": rng.choice([1.15, 3.85]), "waste": rng.choice([0.65, 4.4])}[zone] + rng.normal(0, 0.12)
        game_pk = 100000 + int((date - dates[0]).days) * 10 + (0 if own_team == "DNY" else 1)
        at_bat_number = int(row_number % 75 + 1)

        records.append({
            "game_date": date.date().isoformat(), "game_pk": game_pk,
            "pitcher_name": pitcher, "batter_name": batter,
            "pitcher": 100 + pitchers.index(pitcher), "batter": 200 + batters.index(batter),
            "pitch_type": pitch_type, "pitch_name": pitch_name,
            "pitch_family": "fastball" if pitch_type in ["FF", "SI"] else "breaking" if pitch_type in ["SL", "CU"] else "offspeed",
            "zone_group": zone, "balls": balls, "strikes": strikes, "stand": stand, "p_throws": throws,
            "release_speed": round(float(rng.normal(base_velocity - (0.8 if pitcher == "Demo Rookie" else 0), 1.4)), 1),
            "plate_x": round(float(plate_x), 3), "plate_z": round(float(plate_z), 3),
            "description": description, "events": event,
            "launch_speed": None if np.isnan(launch_speed) else round(launch_speed, 1),
            "delta_pitcher_run_exp": round(float(-run_value), 4),
            "home_team": home_team, "away_team": away_team, "pitcher_team": own_team,
            "opponent_team": opponent, "is_home": is_home, "home_away": "home" if is_home else "away",
            "venue": venue, "game_time_local": f"{game_hour:02d}:05", "day_night": day_night,
            "temperature": round(temperature, 1), "wind_speed": round(wind_speed, 1),
            "wind_direction": wind_direction, "roof": venue_info["roof"],
            "elevation_ft": venue_info["elevation_ft"], "starter_flag": pitcher != "Demo Rookie" or rng.random() > 0.35,
            "inning": int(rng.integers(1, 10)), "at_bat_number": at_bat_number,
            "pitch_number": int(rng.integers(1, 10)), "n_thruorder_pitcher": int(min(4, at_bat_number // 9 + 1)),
            "data_provenance": "synthetic_demo",
        })

    return pd.DataFrame(records).sort_values(["game_date", "game_pk", "at_bat_number", "pitch_number"])


if __name__ == "__main__":
    output = Path("data/sample/demo_pitches.csv")
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = generate()
    frame.to_csv(output, index=False)
    print(f"Generated {len(frame):,} synthetic pitches at {output}")
