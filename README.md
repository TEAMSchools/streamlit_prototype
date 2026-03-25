# AP Hub — Data Dashboard Prototype

> ⚠ **DEMO PROTOTYPE — ALL DATA IS SYNTHETIC MOCK DATA**
> This application contains no real student, staff, or school data of any kind.
> All names, IDs, metrics, and school references are entirely fabricated for
> demonstration and prototyping purposes only.

---

## Purpose

This is a working prototype of the **AP Hub**, a weekly data prep dashboard built to support the *O3 With Myself* protocol at KIPP Team and Family Schools (KTAF). The goal is to give Assistant Principals a single-page view of the outcome metrics that matter most — attendance, behavior, gradebook, assessments, DIBELS, iReady, and observations — organized to drive weekly planning.

The dashboard is designed so an AP can open it before an O3 and have the key data already surfaced, ranked, and flagged, rather than pulling it from five separate systems.

## What This Prototype Demonstrates

- Single-page scrolling layout with domain sections (Attendance → Observations)
- Grade-level rollup → homeroom detail → student-level hotlist, all within one page
- Heatmap ranking tables for quick visual triage
- Expandable student hotlists (low ADA, repeat referrals)
- AP-selector filter in the sidebar
- Architecture that mirrors a real Cube API data contract (swap `data_client.py` internals for production)

## ⚠ Mock Data Disclaimer

**This prototype uses entirely synthetic, fabricated data.**

- **No real students.** Student IDs, grade levels, and all associated metrics are randomly generated.
- **No real staff.** Teacher names, AP names, and staff IDs do not correspond to any actual employee.
- **No real schools.** The school name "School 1" is a placeholder with no relation to any actual KTAF campus or any other school.
- **No real metrics.** ADA percentages, incident counts, GPA values, and assessment scores are fabricated for UI demonstration only.

All mock data files are located in `mock_data/` and are named with the `_mock_data` suffix to make their status unambiguous.

This codebase is safe to share publicly. It contains no FERPA-protected, personally identifiable, or otherwise sensitive information.

---

## Architecture

```
app.py              — Streamlit UI (single-page layout, no business logic)
data_client.py      — Mock Cube API layer (DuckDB over CSVs; swap for Cube in prod)
style.py            — Design tokens, CSS, and HTML table builders
mock_data/          — Synthetic CSV files (⚠ mock data only)
```

### The Cube API Contract

`data_client.py` is structured to mirror the shape of a real [Cube](https://cube.dev) REST/GraphQL API call. Every public function returns `list[dict]` (JSON-serializable). In production, replace the DuckDB query bodies with Cube API calls — the UI layer (`app.py`) and the function signatures never change.

```
MOCK:  DuckDB → mock_data/*_mock_data.csv
PROD:  Cube REST/GraphQL → BigQuery (KTAF data warehouse)
```

## Mock Data Files

| File | Contents |
|------|----------|
| `metrics_v2_mock_data.csv` | Pre-aggregated metrics by grain (grade / homeroom / classroom / teacher) |
| `hotlist_student_ada_v2_mock_data.csv` | Student-level low-ADA hotlist |
| `hotlist_student_referrals_v2_mock_data.csv` | Student-level repeat-referral hotlist |
| `AP_manager_mock_data.csv` | AP manager roster (maps teachers to APs) |
| `roster_mock_data.csv` | Student–section–teacher roster |

## Running Locally

```bash
pip install streamlit duckdb pandas
streamlit run app.py
```

## Deployment

Hosted on [Streamlit Community Cloud](https://streamlit.io/cloud) connected to this repository. Redeploys automatically on push to `main`.

---

*Prototype — Draft v0325 | KIPP Team and Family Schools, Data Team*
*All data displayed is dummy mock up data for demo purposes only.*
