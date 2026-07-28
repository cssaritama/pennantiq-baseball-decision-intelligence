from __future__ import annotations

from pathlib import Path
import pandas as pd


def run_pipeline(csv_path: str = "data/sample/demo_pitches.csv", destination: str = "duckdb"):
    """Automated dlt ingestion used by the reproducible local workflow."""
    import dlt

    path = Path(csv_path)
    if not path.exists():
        raise FileNotFoundError(path)

    @dlt.resource(name="pitches", write_disposition="replace")
    def rows():
        for chunk in pd.read_csv(path, chunksize=1000):
            yield from chunk.to_dict(orient="records")

    pipeline = dlt.pipeline(
        pipeline_name="pennantiq",
        destination=destination,
        dataset_name="pennantiq",
    )
    return pipeline.run(rows())


if __name__ == "__main__":
    print(run_pipeline())
