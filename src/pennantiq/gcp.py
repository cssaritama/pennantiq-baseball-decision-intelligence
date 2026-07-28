from __future__ import annotations

from pathlib import Path

import pandas as pd


def export_dataframe_to_bigquery(
    frame: pd.DataFrame,
    table_id: str,
    project: str | None = None,
    location: str = "US",
    write_disposition: str = "WRITE_APPEND",
) -> str:
    """Optional GCP adapter. Requires requirements-gcp.txt and ADC credentials."""
    try:
        from google.cloud import bigquery
    except ImportError as exc:
        raise RuntimeError("Install requirements-gcp.txt before using BigQuery.") from exc
    client = bigquery.Client(project=project, location=location)
    config = bigquery.LoadJobConfig(write_disposition=write_disposition)
    job = client.load_table_from_dataframe(frame, table_id, job_config=config)
    result = job.result()
    return f"Loaded {result.output_rows} rows into {table_id}."


def load_bigquery_table(query: str, project: str | None = None, location: str = "US") -> pd.DataFrame:
    try:
        from google.cloud import bigquery
    except ImportError as exc:
        raise RuntimeError("Install requirements-gcp.txt before using BigQuery.") from exc
    client = bigquery.Client(project=project, location=location)
    return client.query(query).to_dataframe()


def upload_to_gcs(local_path: str | Path, bucket_name: str, object_name: str | None = None) -> str:
    try:
        from google.cloud import storage
    except ImportError as exc:
        raise RuntimeError("Install requirements-gcp.txt before using Cloud Storage.") from exc
    source = Path(local_path)
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    target = object_name or source.name
    bucket.blob(target).upload_from_filename(str(source))
    return f"gs://{bucket_name}/{target}"
