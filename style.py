"""
style.py — Design tokens and helpers

All color, typography, and component styling lives here.
Source: style_example/bigboard.html
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------
COLORS = {
    "indigo":   "#001E62",  # primary brand / text
    "indigo_2": "#002d8a",  # heatmap rank 1
    "orange":   "#F9A21A",  # active tab / accent
    "blue":     "#57C0E9",  # hover / highlight
    "g1":       "#F8F9FB",  # page background
    "g2":       "#EDEEF2",  # card borders
    "g3":       "#D0D3DC",  # subtle dividers
    "g4":       "#8A8FA2",  # secondary text / labels
    "g5":       "#3D4259",  # primary body text
    "green":    "#1A9E5B",  # positive delta
    "red":      "#D63B3B",  # negative delta / alert
}

# ---------------------------------------------------------------------------
# Heatmap coloring
# ---------------------------------------------------------------------------

def heatmap_color(rank: int, n: int) -> str:
    """
    rank=1 (best)  → indigo full (#002d8a)
    rank=2         → lighter indigo (#3358b8)
    rank 3..N      → greyscale, rank=N (worst) → #8A8FA2
    """
    if rank == 1:
        return "#002d8a"
    if rank == 2:
        return "#3358b8"
    t = (rank - 3) / max(n - 3, 1)
    r = int(0xD0 + t * (0x8A - 0xD0))
    g = int(0xD3 + t * (0x8F - 0xD3))
    b = int(0xDC + t * (0xA2 - 0xDC))
    return f"#{r:02X}{g:02X}{b:02X}"


def text_color(rank: int) -> str:
    return "#FFFFFF" if rank <= 2 else "#3D4259"


# ---------------------------------------------------------------------------
# Global CSS injection
# ---------------------------------------------------------------------------

def inject_global_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #3D4259;
        background-color: #F8F9FB;
    }

    /* Page header */
    h1, h2, h3 {
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 700;
        color: #001E62;
        letter-spacing: 0.01em;
    }

    /* Metric labels and mono values */
    .mono {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
    }

    /* Cards */
    .card {
        background: #fff;
        border: 1.5px solid #EDEEF2;
        border-radius: 10px;
        box-shadow: 0 1px 3px rgba(0,30,98,.06);
        padding: 16px 20px;
        margin-bottom: 12px;
    }

    /* Heatmap table */
    table.heatmap {
        width: 100%;
        border-collapse: collapse;
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
    }
    table.heatmap th {
        background: #001E62;
        color: #fff;
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 600;
        font-size: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 8px 10px;
        text-align: left;
    }
    table.heatmap td {
        padding: 7px 10px;
        border-bottom: 1px solid #EDEEF2;
    }
    table.heatmap tr:last-child td {
        border-bottom: none;
    }
    table.heatmap tr:hover td {
        background: #F0F6FF;
    }

    /* Hotlist student table */
    table.hotlist {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }
    table.hotlist th {
        background: #F8F9FB;
        color: #8A8FA2;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        padding: 6px 8px;
        border-bottom: 1.5px solid #EDEEF2;
        text-align: left;
    }
    table.hotlist td {
        padding: 6px 8px;
        border-bottom: 1px solid #F0F0F5;
        font-family: 'DM Sans', sans-serif;
    }
    table.hotlist td.mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }

    /* Section label pill */
    .section-pill {
        display: inline-block;
        background: #EEF2FF;
        color: #001E62;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        border-radius: 4px;
        padding: 2px 7px;
        margin-right: 4px;
    }

    /* Metric value — large display */
    .metric-value {
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 700;
        font-size: 28px;
        color: #001E62;
        line-height: 1.1;
    }
    .metric-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 11px;
        font-weight: 500;
        color: #8A8FA2;
        text-transform: uppercase;
        letter-spacing: 0.07em;
    }

    /* Alert badge */
    .badge-alert {
        display: inline-block;
        background: #FFF0F0;
        color: #D63B3B;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        border-radius: 4px;
        padding: 2px 7px;
    }
    .badge-ok {
        display: inline-block;
        background: #F0FFF6;
        color: #1A9E5B;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        border-radius: 4px;
        padding: 2px 7px;
    }

    /* Streamlit sidebar */
    section[data-testid="stSidebar"] {
        background: #001E62;
    }
    section[data-testid="stSidebar"] * {
        color: #fff !important;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #8A9FCC !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 12px;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }

    /* Hide Streamlit chrome */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Reusable HTML builders
# ---------------------------------------------------------------------------

def stat_card(label: str, value: str, sublabel: str = "") -> str:
    """Returns an HTML card for a single KPI."""
    sub = f'<div class="metric-label" style="margin-top:4px;color:#8A8FA2">{sublabel}</div>' if sublabel else ""
    return f"""
    <div class="card" style="text-align:center;">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
        {sub}
    </div>
    """


def section_header(title: str, subtitle: str = "") -> str:
    sub = f'<span style="font-family:DM Sans;font-size:13px;font-weight:400;color:#8A8FA2;margin-left:10px;">{subtitle}</span>' if subtitle else ""
    return f'<h3 style="margin-bottom:4px;">{title}{sub}</h3>'


def heatmap_table(rows: list[dict], cols: list[dict], rank_col: str = None, n: int = None) -> str:
    """
    Generic heatmap HTML table.

    cols: list of {"key": str, "label": str, "align": "left"|"right", "mono": bool}
    rank_col: if set, the column key whose integer value drives background color
    n: total number of rows (for rank color scale)
    """
    header_cells = "".join(
        f'<th style="text-align:{c.get("align","left")}">{c["label"]}</th>'
        for c in cols
    )
    body_rows = []
    for row in rows:
        rank = int(row.get(rank_col, 999)) if rank_col else None
        cells = []
        for c in cols:
            val = row.get(c["key"], "")
            align = c.get("align", "left")
            mono_cls = ' class="mono"' if c.get("mono") else ""
            if rank_col and c["key"] != cols[0]["key"] and rank is not None and n is not None:
                bg = heatmap_color(rank, n)
                fg = text_color(rank)
                cells.append(
                    f'<td{mono_cls} style="text-align:{align};background:{bg};color:{fg};font-weight:600">{val}</td>'
                )
            else:
                cells.append(f'<td{mono_cls} style="text-align:{align}">{val}</td>')
        body_rows.append(f'<tr>{"".join(cells)}</tr>')

    return f"""
    <table class="heatmap">
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{"".join(body_rows)}</tbody>
    </table>
    """


def hotlist_table(rows: list[dict], cols: list[dict]) -> str:
    """Generic hotlist (student-level) HTML table."""
    header_cells = "".join(
        f'<th style="text-align:{c.get("align","left")}">{c["label"]}</th>'
        for c in cols
    )
    body_rows = []
    for row in rows:
        cells = []
        for c in cols:
            val = row.get(c["key"], "")
            align = c.get("align", "left")
            mono_cls = ' class="mono"' if c.get("mono") else ""
            cells.append(f'<td{mono_cls} style="text-align:{align}">{val}</td>')
        body_rows.append(f'<tr>{"".join(cells)}</tr>')

    return f"""
    <table class="hotlist">
        <thead><tr>{header_cells}</tr></thead>
        <tbody>{"".join(body_rows)}</tbody>
    </table>
    """
