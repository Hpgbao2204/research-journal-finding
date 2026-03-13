"""Convenience entry point to run ETL from project root."""

from src.pipeline.etl_pipeline import run_etl


if __name__ == "__main__":
    run_etl()
