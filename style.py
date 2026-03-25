"""
style.py — Design tokens and HTML builders

Light theme matching the AP Hub Google Sheets mockup:
- White page background
- Navy (#001E62) section banner bars
- Sky blue (#56C0E9) sidebar accents and expand links
- #DAEeF6 alternating row tint
- Light gray sidebar (#F4F6FB)
"""

import streamlit as st

# ---------------------------------------------------------------------------
# Color tokens
# ---------------------------------------------------------------------------
COLORS = {
    "navy":    "#001E62",  # primary brand / section banners
    "navy_2":  "#002d8a",  # heatmap rank 1
    "sky":     "#56C0E9",  # sidebar pills, expand links, hover
    "orange":  "#F9A21A",  # accent / mock data badge
    "white":   "#FFFFFF",
    "g0":      "#F4F6FB",  # sidebar background
    "g1":      "#F8F9FB",  # subtle off-white
    "g2":      "#EDEEF2",  # card borders / dividers
    "g4":      "#8A8FA2",  # secondary text / sub-labels
    "g5":      "#3D4259",  # primary body text
    "row_alt": "#DAEeF6",  # alternating row tint (from mockup)
    "green":   "#1A9E5B",
    "red":     "#D63B3B",
}


# ---------------------------------------------------------------------------
# Heatmap coloring (rank-based, light-theme aware)
# ---------------------------------------------------------------------------

def heatmap_color(rank: int, n: int) -> str:
    """
    Linear interpolation from #B3C4ED (rank 1, best) → #EAEAEA (rank N, worst).
    All fills are light enough that dark text is always readable.
    """
    t = (rank - 1) / max(n - 1, 1)
    r = int(0xB3 + t * (0xEA - 0xB3))
    g = int(0xC4 + t * (0xEA - 0xC4))
    b = int(0xED + t * (0xEA - 0xED))
    return f"#{r:02X}{g:02X}{b:02X}"


def text_color(rank: int) -> str:
    # All fills are light — always use dark text
    return "#3D4259"


# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------

def inject_global_css() -> None:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700&family=DM+Sans:wght@400;500;600&family=JetBrains+Mono:wght@500&display=swap');

    /* ── Force light theme — override system dark mode ────────── */
    :root {
        color-scheme: light only !important;
    }
    @media (prefers-color-scheme: dark) {
        html, body, [data-testid="stAppViewContainer"],
        [data-testid="stHeader"], [data-testid="stSidebar"],
        .main, [class*="css"] {
            background-color: #FFFFFF !important;
            color: #3D4259 !important;
        }
    }

    /* ── Base ─────────────────────────────────────────────────── */
    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
        color: #3D4259;
        background-color: #FFFFFF;
    }

    .main .block-container {
        background: #FFFFFF;
        padding-top: 1.25rem;
        padding-bottom: 3rem;
    }

    h1, h2, h3 {
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 700;
        color: #001E62;
        letter-spacing: 0.01em;
    }

    /* ── Sidebar — light ──────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: #F4F6FB;
        border-right: 1.5px solid #EDEEF2;
    }
    section[data-testid="stSidebar"] .stSelectbox label {
        color: #001E62 !important;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.07em;
        text-transform: uppercase;
    }

    /* ── Domain section banners ───────────────────────────────── */
    .domain-banner {
        background: #001E62;
        color: #ffffff;
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 17px;
        font-weight: 700;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        padding: 9px 14px;
        margin-bottom: 10px;
        border-radius: 4px;
    }

    /* ── Subheader labels ─────────────────────────────────────── */
    .sub-label {
        font-family: 'Barlow Condensed', sans-serif;
        font-size: 13px;
        font-weight: 700;
        color: #8A8FA2;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        margin-bottom: 6px;
        margin-top: 14px;
    }

    /* ── Heatmap table ────────────────────────────────────────── */
    table.heatmap {
        width: 100%;
        border-collapse: collapse;
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
    }
    table.heatmap th {
        background: #001E62;
        color: #ffffff;
        font-family: 'Barlow Condensed', sans-serif;
        font-weight: 600;
        font-size: 12px;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        padding: 7px 10px;
        text-align: left;
    }
    table.heatmap td {
        padding: 6px 10px;
        border-bottom: 1px solid #EDEEF2;
        background: #FFFFFF;
    }
    table.heatmap tr:nth-child(even) td {
        background: #F4F6FB;
    }
    table.heatmap tr:last-child td {
        border-bottom: none;
    }
    table.heatmap tr:hover td {
        font-weight: 700 !important;
    }

    /* ── Hotlist (student) table ──────────────────────────────── */
    table.hotlist {
        width: 100%;
        border-collapse: collapse;
        font-size: 12px;
    }
    table.hotlist th {
        background: #F4F6FB;
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
        border-bottom: 1px solid #EDEEF2;
        font-family: 'DM Sans', sans-serif;
        background: #FFFFFF;
    }
    table.hotlist tr:nth-child(even) td {
        background: #DAEeF6;
    }
    table.hotlist td.mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
    }

    /* ── Expander — styled as blue expand links ───────────────── */
    [data-testid="stExpander"] {
        border: none !important;
        border-top: 1px solid #EDEEF2 !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    [data-testid="stExpander"] summary {
        color: #56C0E9 !important;
        font-style: italic;
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
        padding: 6px 2px;
    }
    [data-testid="stExpander"] summary:hover {
        color: #002d8a !important;
    }
    [data-testid="stExpander"] summary svg {
        fill: #56C0E9 !important;
    }

    /* ── Metric value display ─────────────────────────────────── */
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

    /* ── Alert badges ─────────────────────────────────────────── */
    .badge-alert {
        display: inline-block;
        background: #FFF0F0;
        color: #D63B3B;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        border-radius: 4px;
        padding: 3px 8px;
    }
    .badge-ok {
        display: inline-block;
        background: #F0FFF6;
        color: #1A9E5B;
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        border-radius: 4px;
        padding: 3px 8px;
    }

    /* ── Sidebar jump-to link pills ───────────────────────────── */
    .jump-link {
        display: block;
        color: #001E62;
        font-family: 'DM Sans', sans-serif;
        font-size: 13px;
        font-weight: 500;
        padding: 5px 10px;
        border-radius: 4px;
        text-decoration: none;
        margin-bottom: 2px;
        transition: background 0.15s;
    }
    .jump-link:hover {
        background: #DAEeF6;
        color: #001E62;
        text-decoration: none;
    }

    /* ── Hide Streamlit chrome ────────────────────────────────── */
    #MainMenu { visibility: hidden; }
    footer     { visibility: hidden; }
    header     { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# HTML builders
# ---------------------------------------------------------------------------

def domain_banner(title: str, anchor_id: str) -> str:
    """Full-width navy section header with anchor target."""
    return (
        f'<div id="{anchor_id}"></div>'
        f'<div class="domain-banner">{title}</div>'
    )


def sub_label(text: str) -> str:
    return f'<div class="sub-label">{text}</div>'


def jump_to_sidebar(sections: list[tuple[str, str]]) -> str:
    """
    Render a Jump To nav block for the sidebar.
    sections: list of (label, anchor_id)
    """
    links = "".join(
        f'<a class="jump-link" href="#{anchor}">{label}</a>'
        for label, anchor in sections
    )
    return (
        '<div style="margin-bottom:6px;font-family:Barlow Condensed,sans-serif;'
        'font-size:11px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;'
        'color:#56C0E9;background:#001E62;padding:4px 10px;border-radius:4px;">'
        'Jump To</div>'
        + links
    )


def heatmap_table(rows: list[dict], cols: list[dict], rank_col: str = None, n: int = None) -> str:
    """
    Generic heatmap HTML table.
    cols: list of {"key": str, "label": str, "align": "left"|"right", "mono": bool}
    rank_col: key whose int value drives background color
    n: total row count for rank color scale
    """
    header_cells = "".join(
        f'<th style="text-align:{c.get("align","left")}">{c["label"]}</th>'
        for c in cols
    )
    body_rows = []
    for i, row in enumerate(rows):
        rank = int(row.get(rank_col, 999)) if rank_col else None
        row_bg = COLORS["row_alt"] if i % 2 == 1 else COLORS["white"]
        cells = []
        for c in cols:
            val = row.get(c["key"], "")
            align = c.get("align", "left")
            mono_cls = ' class="mono"' if c.get("mono") else ""
            if rank_col and c["key"] != cols[0]["key"] and rank is not None and n is not None:
                bg = heatmap_color(rank, n)
                fg = text_color(rank)
                cells.append(
                    f'<td{mono_cls} style="text-align:{align};background:{bg};'
                    f'color:{fg};font-weight:600">{val}</td>'
                )
            else:
                cells.append(
                    f'<td{mono_cls} style="text-align:{align};background:{row_bg}">{val}</td>'
                )
        body_rows.append(f'<tr>{"".join(cells)}</tr>')

    return (
        '<table class="heatmap">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        '</table>'
    )


def hotlist_table(rows: list[dict], cols: list[dict]) -> str:
    """Generic student-level hotlist table."""
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

    return (
        '<table class="hotlist">'
        f'<thead><tr>{header_cells}</tr></thead>'
        f'<tbody>{"".join(body_rows)}</tbody>'
        '</table>'
    )
