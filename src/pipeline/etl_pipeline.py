"""ETL pipeline to build a local SQLite journal database from SJR + WoS sources."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Iterable, Optional

import pandas as pd


# --------------------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"
LOG_DIR = PROJECT_ROOT / "logs"

SJR_CSV_PATH = DATA_DIR / "scimagojr 2024.csv"
WOS_CSV_PATH = DATA_DIR / "wos_master_journal_list.csv"
DB_PATH = OUTPUT_DIR / "journals.db"
TABLE_NAME = "Journal"


def setup_logging() -> None:
    """Configure logging to file + console for easier debugging and operations."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / "etl_pipeline.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


def read_csv_with_fallback(
    file_path: Path,
    sep: str = ",",
    encoding_candidates: Optional[Iterable[str]] = None,
) -> pd.DataFrame:
    """
    Read CSV with fallback encodings and robust bad-line handling.

    Args:
        file_path: Path to CSV file.
        sep: Delimiter of CSV.
        encoding_candidates: Optional list of encodings to try.

    Returns:
        Loaded pandas DataFrame.

    Raises:
        RuntimeError: If all encodings fail.
    """
    if encoding_candidates is None:
        encoding_candidates = ["utf-8", "utf-8-sig", "latin1", "cp1252"]

    last_exception: Exception | None = None
    for enc in encoding_candidates:
        try:
            logging.info("Reading %s with encoding=%s, sep='%s'", file_path, enc, sep)
            df = pd.read_csv(file_path, sep=sep, encoding=enc, on_bad_lines="skip")
            logging.info("Loaded %s rows from %s", len(df), file_path.name)
            return df
        except Exception as exc:  # noqa: BLE001 - We log and continue fallback attempts.
            last_exception = exc
            logging.warning("Failed reading %s with encoding=%s: %s", file_path.name, enc, exc)

    raise RuntimeError(f"Unable to read {file_path} with tried encodings") from last_exception


def find_column(df: pd.DataFrame, candidates: list[str]) -> Optional[str]:
    """Find first matching column from candidate names (case-insensitive)."""
    normalized = {c.strip().lower(): c for c in df.columns}
    for cand in candidates:
        key = cand.strip().lower()
        if key in normalized:
            return normalized[key]
    return None


def normalize_issn_series(series: pd.Series) -> pd.Series:
    """
    Normalize ISSN values to comparable key format.

    Example:
      - "15424863, 00079235" -> "15424863"
      - "1234-5678" -> "12345678"
    """
    cleaned = series.fillna("").astype(str).str.strip()
    cleaned = cleaned.str.split(",").str[0].str.strip()
    cleaned = cleaned.str.replace("-", "", regex=False)
    cleaned = cleaned.replace("", pd.NA)
    return cleaned


def normalize_title_series(series: pd.Series) -> pd.Series:
    """Normalize title text for fallback title-based matching."""
    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", " ", regex=True)
    )


def build_merged_dataframe(sjr_df: pd.DataFrame, wos_df: pd.DataFrame) -> pd.DataFrame:
    """Merge SJR and WoS data by ISSN if available, otherwise fallback to title."""
    sjr_title_col = find_column(sjr_df, ["Title"])
    sjr_issn_col = find_column(sjr_df, ["Issn", "ISSN"])
    sjr_quartile_col = find_column(sjr_df, ["SJR Best Quartile", "SJR Rank", "Quartile"])
    sjr_category_col = find_column(sjr_df, ["Categories", "Areas", "Subject Area/Category"])
    sjr_publisher_col = find_column(sjr_df, ["Publisher"])

    wos_title_col = find_column(wos_df, ["Title", "Journal Title"])
    wos_issn_col = find_column(wos_df, ["ISSN", "Issn", "eISSN", "EISSN"])
    wos_publisher_col = find_column(wos_df, ["Publisher", "Publisher Name"])
    wos_category_col = find_column(
        wos_df,
        ["Core Collection", "Web of Science Categories", "Subject Category", "Category"],
    )

    if not sjr_title_col:
        raise ValueError("SJR dataset missing mandatory column: Title")

    if not wos_title_col:
        raise ValueError("WoS dataset missing mandatory column: Title")

    sjr = sjr_df.copy()
    wos = wos_df.copy()

    sjr["_title_key"] = normalize_title_series(sjr[sjr_title_col])
    wos["_title_key"] = normalize_title_series(wos[wos_title_col])

    merge_on_issn = bool(sjr_issn_col and wos_issn_col)

    if merge_on_issn:
        logging.info("ISSN columns found in both datasets. Merging by ISSN.")
        sjr["_issn_key"] = normalize_issn_series(sjr[sjr_issn_col])
        wos["_issn_key"] = normalize_issn_series(wos[wos_issn_col])

        merged = pd.merge(
            sjr,
            wos,
            how="left",
            on="_issn_key",
            suffixes=("_sjr", "_wos"),
        )
        issn_out = merged["_issn_key"]
    else:
        logging.warning(
            "WoS file does not contain ISSN column. Fallback to TITLE-based merge. "
            "Please provide ISSN in WoS data for higher matching quality."
        )
        merged = pd.merge(
            sjr,
            wos,
            how="left",
            on="_title_key",
            suffixes=("_sjr", "_wos"),
        )
        if sjr_issn_col:
            issn_out = normalize_issn_series(merged[sjr_issn_col])
        else:
            issn_out = pd.Series([pd.NA] * len(merged), index=merged.index)

    def get_merged_col(col_name: str | None, suffix: str) -> pd.Series:
        if not col_name:
            return pd.Series([pd.NA] * len(merged), index=merged.index)
        if f"{col_name}{suffix}" in merged.columns:
            return merged[f"{col_name}{suffix}"]
        if col_name in merged.columns:
            return merged[col_name]
        return pd.Series([pd.NA] * len(merged), index=merged.index)

    title_out = get_merged_col(sjr_title_col, "_sjr")
    rank_out = get_merged_col(sjr_quartile_col, "_sjr")

    subject_parts = []
    if sjr_category_col:
        sjr_cat = get_merged_col(sjr_category_col, "_sjr")
        subject_parts.append(sjr_cat.astype(str))
    if wos_category_col:
        wos_cat = get_merged_col(wos_category_col, "_wos")
        subject_parts.append(wos_cat.astype(str))

    if subject_parts:
        subject_out = subject_parts[0]
        for part in subject_parts[1:]:
            subject_out = (
                subject_out.fillna("")
                .str.cat(part.fillna(""), sep=" | ")
                .str.strip(" |")
            )
    else:
        subject_out = pd.Series([pd.NA] * len(merged), index=merged.index)

    publisher_sjr = get_merged_col(sjr_publisher_col, "_sjr")
    publisher_wos = get_merged_col(wos_publisher_col, "_wos")
    publisher_out = publisher_sjr.combine_first(publisher_wos)

    result = pd.DataFrame(
        {
            "Title": title_out,
            "ISSN": issn_out,
            "SJR_Rank": rank_out,
            "Subject_Area_Category": subject_out,
            "Publisher": publisher_out,
        }
    )

    # Handle missing data with consistent default values where appropriate.
    result["Title"] = result["Title"].fillna("Unknown Title")
    result["ISSN"] = result["ISSN"].fillna("Unknown ISSN")
    result["SJR_Rank"] = result["SJR_Rank"].fillna("Unranked")
    result["Subject_Area_Category"] = result["Subject_Area_Category"].replace("", pd.NA).fillna("Uncategorized")
    result["Publisher"] = result["Publisher"].fillna("Unknown Publisher")

    # Remove exact duplicates to keep the final journal table cleaner.
    result = result.drop_duplicates(subset=["Title", "ISSN", "SJR_Rank", "Subject_Area_Category", "Publisher"]).reset_index(drop=True)

    logging.info("Final merged dataset shape: %s", result.shape)
    return result


def load_to_sqlite(df: pd.DataFrame, db_path: Path, table_name: str) -> None:
    """Load DataFrame into SQLite table, replacing old table if exists."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        with sqlite3.connect(db_path) as conn:
            df.to_sql(table_name, conn, if_exists="replace", index=False)
            conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name.lower()}_issn ON {table_name}(ISSN)")
            conn.commit()
        logging.info("Loaded %s rows into SQLite table %s at %s", len(df), table_name, db_path)
    except Exception as exc:  # noqa: BLE001
        logging.exception("Failed to load data into SQLite: %s", exc)
        raise


def run_etl() -> None:
    """Orchestrate full ETL process from CSV files to SQLite."""
    setup_logging()
    logging.info("Starting ETL pipeline...")

    try:
        sjr_df = read_csv_with_fallback(SJR_CSV_PATH, sep=";")
        wos_df = read_csv_with_fallback(WOS_CSV_PATH, sep=",")

        merged_df = build_merged_dataframe(sjr_df, wos_df)
        load_to_sqlite(merged_df, DB_PATH, TABLE_NAME)

        logging.info("ETL pipeline completed successfully.")
    except Exception as exc:  # noqa: BLE001
        logging.exception("ETL pipeline failed: %s", exc)
        raise


if __name__ == "__main__":
    run_etl()
