"""
data_client.py — Mock Cube API layer

================================================================================
⚠ DEMO / PROTOTYPE ONLY — ALL DATA IS SYNTHETIC MOCK DATA ⚠

This module simulates the Cube API contract using local CSV files.
NO real student, staff, or school data is used anywhere in this codebase.
All names, IDs, metrics, and school references are entirely fabricated
for demonstration and prototyping purposes only.

MOCK phase:  DuckDB queries over mock_data/*_mock_data.csv
PROD phase:  swap internals for Cube REST/GraphQL — UI never changes

Contract: all public functions return list[dict] (JSON-serializable).
Zero Pandas aggregations — data arrives pre-aggregated from the CSVs.
================================================================================
"""

import os
import duckdb

# ---------------------------------------------------------------------------
# ⚠ MOCK DATA FILE PATHS — synthetic demo data only, not real records
# ---------------------------------------------------------------------------
# Resolve paths relative to this file so the app works regardless of cwd
_BASE = os.path.dirname(__file__)
_METRICS           = os.path.join(_BASE, "mock_data", "metrics_v2_mock_data.csv")
_ADA_HOTLIST       = os.path.join(_BASE, "mock_data", "hotlist_student_ada_v2_mock_data.csv")
_REFERRALS_HOTLIST = os.path.join(_BASE, "mock_data", "hotlist_student_referrals_v2_mock_data.csv")
_AP_MANAGER        = os.path.join(_BASE, "mock_data", "AP_manager_mock_data.csv")


def _con() -> duckdb.DuckDBPyConnection:
    return duckdb.connect()


def get_ap_list() -> list[dict]:
    """
    Return all AP managers for the sidebar selector.
    ⚠ MOCK DATA — names and IDs are entirely synthetic, not real staff records.
    """
    con = _con()
    return con.execute("""
        SELECT DISTINCT "AP_ID" AS ap_manager_id, "AP_Name" AS ap_manager_name
        FROM read_csv_auto(?)
        ORDER BY ap_manager_name
    """, [_AP_MANAGER]).df().to_dict(orient="records")


def get_metrics(
    grain_type: str,
    ap_manager_id: str,
    grade: str = None,
    domain: str = None,
    metric_name: str = None,
) -> list[dict]:
    """
    Main workhorse. Queries metrics_v2_mock_data.csv filtered by grain + AP.

    ⚠ MOCK DATA — all metric values, teacher names, and section IDs are
    synthetic and fabricated for demo purposes only.

    grain_type: 'grade' | 'homeroom' | 'classroom' | 'teacher'
    ap_manager_id: AP_XXXXXXXX
    grade: optional — '5' | '6' | '7' | '8'
    domain: optional — e.g. 'Attendance', 'Behavior', 'iReady', etc.
    metric_name: optional — e.g. 'ADA%', '# Incidents', etc.

    PROD: replace body with Cube REST/GraphQL call — signature unchanged.
    """
    con = _con()
    return con.execute("""
        SELECT *
        FROM read_csv_auto(?)
        WHERE grain_type    = ?
          AND ap_manager_id = ?
          AND (? IS NULL OR CAST(grade AS VARCHAR) = ?)
          AND (? IS NULL OR metric_domain = ?)
          AND (? IS NULL OR metric_name = ?)
        ORDER BY grade, grain_key, metric_domain, metric_name, metric_category
    """, [
        _METRICS,
        grain_type, ap_manager_id,
        grade, grade,
        domain, domain,
        metric_name, metric_name,
    ]).df().to_dict(orient="records")


def get_student_ada_hotlist(
    ap_manager_id: str,
    section: str = None,
) -> list[dict]:
    """
    Lazy-load only. Returns low-ADA students for the given AP.
    Optionally filtered to a single homeroom section.
    ⚠ MOCK DATA — student IDs and ADA values are entirely synthetic.
    PROD: replace body with Cube REST/GraphQL call — signature unchanged.
    """
    con = _con()
    return con.execute("""
        SELECT *
        FROM read_csv_auto(?)
        WHERE ap_manager_id = ?
          AND value IS NOT NULL
          AND (? IS NULL OR Section = ?)
        ORDER BY value ASC, Grade_Level, Student_Number
    """, [_ADA_HOTLIST, ap_manager_id, section, section]).df().to_dict(orient="records")


def get_student_referrals_hotlist(
    ap_manager_id: str,
    section: str = None,
) -> list[dict]:
    """
    Lazy-load only. Returns repeat-referral students for the given AP.
    Optionally filtered to a single homeroom section.
    ⚠ MOCK DATA — student IDs and referral counts are entirely synthetic.
    PROD: replace body with Cube REST/GraphQL call — signature unchanged.
    """
    con = _con()
    return con.execute("""
        SELECT *
        FROM read_csv_auto(?)
        WHERE ap_manager_id = ?
          AND (? IS NULL OR section = ?)
        ORDER BY value DESC, grade, grain_key
    """, [_REFERRALS_HOTLIST, ap_manager_id, section, section]).df().to_dict(orient="records")
