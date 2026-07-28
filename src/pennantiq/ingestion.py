from pathlib import Path
import dlt


def baseball_source():
    """
    Synthetic baseball decision dataset.

    This represents the ingestion layer that would
    later connect to MLB APIs, Statcast, Baseball Savant,
    internal scouting databases, and organizational data.
    """

    rows = [
        {
            "player": "Example Pitcher",
            "team": "New York",
            "velocity": 96,
            "strikeouts": 10,
            "walks": 2,
            "era": 2.85,
            "context": "home_game"
        },
        {
            "player": "Example Batter",
            "team": "Opponent",
            "average": 0.285,
            "ops": 0.910,
            "context": "night_game"
        },
    ]

    yield rows


def run_pipeline():

    pipeline = dlt.pipeline(
        pipeline_name="pennantiq",
        destination="duckdb",
        dataset_name="baseball_intelligence",
    )

    load_info = pipeline.run(
        baseball_source(),
        table_name="game_context"
    )

    return load_info


if __name__ == "__main__":
    print(run_pipeline())