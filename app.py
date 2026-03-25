"""
app.py — AP Hub Dashboard

Single-page layout matching the AP Hub Google Sheets mockup.
Light theme · Navy section banners · Expandable homeroom/student sub-tables.

UI only. Zero business logic. All data flows through data_client.py.
"""

import streamlit as st
import data_client as dc
import style

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AP Hub",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)
style.inject_global_css()


# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
SECTIONS = [
    ("Attendance",    "attendance"),
    ("Behavior",      "behavior"),
    ("Gradebook/GPA", "gradebook"),
    ("Assessments",   "assessments"),
    ("DIBELS",        "dibels"),
    ("iReady",        "iready"),
    ("Observations",  "observations"),
]

with st.sidebar:
    # Title block
    st.markdown(
        '<div style="font-family:Barlow Condensed,sans-serif;font-size:52px;'
        'font-weight:700;color:#001E62;letter-spacing:0.03em;padding:12px 0 2px 0;line-height:1;">'
        'AP Hub</div>'
        '<div style="font-size:11px;color:#8A8FA2;padding-bottom:4px;line-height:1.4;">'
        'Mock up · O3 With Myself data prep protocol</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:10px;color:#F9A21A;font-weight:600;padding-bottom:12px;">'
        'All data displayed is dummy mock up data for demo purposes</div>',
        unsafe_allow_html=True,
    )
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 12px 0"/>', unsafe_allow_html=True)

    # AP selector
    st.markdown(
        '<div style="background:#56C0E9;color:#fff;font-family:Barlow Condensed,sans-serif;'
        'font-size:12px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;'
        'padding:4px 10px;border-radius:4px;margin-bottom:8px;">Filter</div>',
        unsafe_allow_html=True,
    )
    ap_list = dc.get_ap_list()
    ap_options = {row["ap_manager_name"]: row["ap_manager_id"] for row in ap_list}
    selected_ap_name = st.selectbox("Viewing as", list(ap_options.keys()), label_visibility="collapsed")
    ap_id = ap_options[selected_ap_name]
    st.markdown(
        f'<div style="font-size:12px;color:#3D4259;padding:4px 2px 12px 2px;">'
        f'Viewing as <strong>{selected_ap_name}</strong></div>',
        unsafe_allow_html=True,
    )

    st.markdown('<hr style="border-color:#EDEEF2;margin:0 0 10px 0"/>', unsafe_allow_html=True)

    # Jump To nav
    st.markdown(style.jump_to_sidebar(SECTIONS), unsafe_allow_html=True)

    st.markdown('<hr style="border-color:#EDEEF2;margin:12px 0 8px 0"/>', unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:10px;color:#8A8FA2;line-height:1.5;">'
        'DuckDB · mock_data/*.csv<br/>'
        'Prod: swap data_client.py → Cube API<br/>'
        'Draft v0325</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    '<div style="font-family:Barlow Condensed,sans-serif;font-size:52px;'
    'font-weight:700;color:#F9A21A;letter-spacing:0.02em;line-height:1;'
    'margin-bottom:4px;">Demo Mock Up</div>',
    unsafe_allow_html=True,
)
st.markdown(
    f'<div style="font-size:13px;color:#8A8FA2;margin-bottom:20px;">'
    f'Viewing as <strong style="color:#001E62">{selected_ap_name}</strong></div>',
    unsafe_allow_html=True,
)


# ===========================================================================
# SECTION: ATTENDANCE
# ===========================================================================
st.markdown(style.domain_banner("Attendance", "attendance"), unsafe_allow_html=True)

# --- Grade rollup ---
st.markdown(style.sub_label("Grade Rollup"), unsafe_allow_html=True)

grade_ada     = dc.get_metrics("grade", ap_id, domain="Attendance", metric_name="ADA%")
grade_chronic = dc.get_metrics("grade", ap_id, domain="Attendance", metric_name="% Chronic Absenteeism")
grade_change  = dc.get_metrics("grade", ap_id, domain="Attendance", metric_name="ADA% Change from Last Week")
grade_2plus   = dc.get_metrics("grade", ap_id, domain="Attendance", metric_name="Students w/ 2+ Absences Last 5 Days")

grade_map: dict = {}
for row in grade_ada:
    g = str(row["grade"])
    grade_map.setdefault(g, {"grade": f"Grade {g}", "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
    grade_map[g]["ada"] = f'{row["value"]:.1f}%'
for row in grade_chronic:
    g = str(row["grade"])
    grade_map.setdefault(g, {"grade": f"Grade {g}", "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
    grade_map[g]["chronic"] = f'{row["value"]:.1f}%'
for row in grade_change:
    g = str(row["grade"])
    grade_map.setdefault(g, {"grade": f"Grade {g}", "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
    v = row["value"]
    grade_map[g]["change"] = f'+{v:.1f}%' if v > 0 else f'{v:.1f}%'
for row in grade_2plus:
    g = str(row["grade"])
    grade_map.setdefault(g, {"grade": f"Grade {g}", "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
    grade_map[g]["two_plus"] = str(int(row["value"]))

grade_rows = sorted(grade_map.values(), key=lambda r: r["grade"])
if grade_rows:
    ada_vals = [float(r["ada"].replace("%", "")) if r["ada"] != "—" else 0 for r in grade_rows]
    s_idx = sorted(range(len(ada_vals)), key=lambda i: -ada_vals[i])
    for i, row in enumerate(grade_rows):
        row["rank"] = s_idx.index(i) + 1

    st.markdown(style.heatmap_table(grade_rows, [
        {"key": "grade",    "label": "",                                     "align": "left"},
        {"key": "ada",      "label": "ADA%",                                "align": "right", "mono": True},
        {"key": "change",   "label": "ADA% Change from Last Week",          "align": "right", "mono": True},
        {"key": "chronic",  "label": "% Chronic Absenteeism",               "align": "right", "mono": True},
        {"key": "two_plus", "label": "Students w/ 2+ Absences Last 5 Days", "align": "right", "mono": True},
    ], rank_col="rank", n=len(grade_rows)), unsafe_allow_html=True)
else:
    st.info("No grade-level attendance data for this AP.")

# --- Homeroom expand ---
with st.expander("Homeroom view — Expand / Close detail view"):
    hr_ada     = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="ADA%")
    hr_chronic = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="% Chronic Absenteeism")
    hr_change  = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="ADA% Change from Last Week")
    hr_2plus   = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="Students w/ 2+ Absences Last 5 Days")

    hr_map: dict = {}
    for row in hr_ada:
        k = row["grain_key"]
        hr_map.setdefault(k, {"section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
                               "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
        hr_map[k]["ada"] = f'{row["value"]:.1f}%'
    for row in hr_chronic:
        k = row["grain_key"]
        hr_map.setdefault(k, {"section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
                               "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
        hr_map[k]["chronic"] = f'{row["value"]:.1f}%'
    for row in hr_change:
        k = row["grain_key"]
        hr_map.setdefault(k, {"section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
                               "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
        v = row["value"]
        hr_map[k]["change"] = f'+{v:.1f}%' if v > 0 else f'{v:.1f}%'
    for row in hr_2plus:
        k = row["grain_key"]
        hr_map.setdefault(k, {"section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
                               "ada": "—", "change": "—", "chronic": "—", "two_plus": "—"})
        hr_map[k]["two_plus"] = str(int(row["value"]))

    hr_rows = sorted(hr_map.values(), key=lambda r: (r["grade"], r["section"]))
    if hr_rows:
        ada_vals2 = [float(r["ada"].replace("%", "")) if r["ada"] != "—" else 0 for r in hr_rows]
        s_idx2 = sorted(range(len(ada_vals2)), key=lambda i: -ada_vals2[i])
        for i, row in enumerate(hr_rows):
            row["rank"] = s_idx2.index(i) + 1

        st.markdown(style.heatmap_table(hr_rows, [
            {"key": "section",  "label": "Homeroom",                              "align": "left",  "mono": True},
            {"key": "teacher",  "label": "Teacher",                               "align": "left"},
            {"key": "grade",    "label": "Gr",                                    "align": "center"},
            {"key": "ada",      "label": "ADA%",                                  "align": "right", "mono": True},
            {"key": "change",   "label": "ADA% Δ Week",                           "align": "right", "mono": True},
            {"key": "chronic",  "label": "% Chronic Abs",                         "align": "right", "mono": True},
            {"key": "two_plus", "label": "2+ Abs / 5 Days",                       "align": "right", "mono": True},
        ], rank_col="rank", n=len(hr_rows)), unsafe_allow_html=True)
    else:
        st.info("No homeroom attendance data for this AP.")

# --- Student expand ---
with st.expander("Student view — Expand / Close detail view"):
    ada_students = dc.get_student_ada_hotlist(ap_id)
    if ada_students:
        for r in ada_students:
            r["value"] = f'{float(r["value"]):.1f}%'
        st.markdown(style.hotlist_table(ada_students, [
            {"key": "Student_Number", "label": "Student ID", "align": "left",  "mono": True},
            {"key": "Grade_Level",    "label": "Gr",         "align": "center"},
            {"key": "Section",        "label": "Homeroom",   "align": "left",  "mono": True},
            {"key": "Teadcher_Name",  "label": "Teacher",    "align": "left"},
            {"key": "value",          "label": "ADA%",       "align": "right", "mono": True},
        ]), unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:11px;color:#8A8FA2;margin-top:6px;">'
            f'{len(ada_students)} students below ADA threshold</div>',
            unsafe_allow_html=True,
        )
    else:
        st.success("No low-ADA students flagged for this AP.")


# ===========================================================================
# SECTION: BEHAVIOR
# ===========================================================================
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(style.domain_banner("Behavior", "behavior"), unsafe_allow_html=True)

BEHAVIOR_CATS = ["Conflict", "Defiance", "Disruption", "Phone"]

# --- Grade rollup ---
st.markdown(style.sub_label("Grade Rollup — # Incidents"), unsafe_allow_html=True)

grade_beh = dc.get_metrics("grade", ap_id, domain="Behavior", metric_name="# Incidents")
gbeh_map: dict = {}
for row in grade_beh:
    g = str(row["grade"])
    cat = row["metric_category"] if row["metric_category"] else "Total"
    gbeh_map.setdefault(g, {"grade": f"Grade {g}", "total": 0})
    gbeh_map[g][cat] = int(row["value"])
    if cat != "Total":
        gbeh_map[g]["total"] = gbeh_map[g].get("total", 0) + int(row["value"])

gbeh_rows = sorted(gbeh_map.values(), key=lambda r: r["grade"])
if gbeh_rows:
    s_idx = sorted(range(len(gbeh_rows)), key=lambda i: gbeh_rows[i].get("total", 0))
    for i, r in enumerate(gbeh_rows):
        r["rank"] = s_idx.index(i) + 1
        for cat in BEHAVIOR_CATS:
            r[cat] = r.get(cat, 0)

    st.markdown(style.heatmap_table(gbeh_rows, [
        {"key": "grade", "label": "",      "align": "left"},
        {"key": "total", "label": "Total", "align": "right", "mono": True},
    ] + [{"key": c, "label": c, "align": "right", "mono": True} for c in BEHAVIOR_CATS],
    rank_col="rank", n=len(gbeh_rows)), unsafe_allow_html=True)
else:
    st.info("No grade-level behavior data for this AP.")

# --- Homeroom expand ---
with st.expander("Homeroom view — Expand / Close detail view"):
    hr_beh = dc.get_metrics("homeroom", ap_id, domain="Behavior", metric_name="# Incidents")
    hrbeh_map: dict = {}
    for row in hr_beh:
        k = row["grain_key"]
        cat = row["metric_category"] if row["metric_category"] else "Total"
        hrbeh_map.setdefault(k, {
            "section": k, "teacher": row["teacher_name"],
            "grade": str(row["grade"]), "total": 0,
        })
        hrbeh_map[k][cat] = int(row["value"])
        if cat != "Total":
            hrbeh_map[k]["total"] = hrbeh_map[k].get("total", 0) + int(row["value"])

    hrbeh_rows = sorted(hrbeh_map.values(), key=lambda r: (r["grade"], r["section"]))
    if hrbeh_rows:
        s_idx = sorted(range(len(hrbeh_rows)), key=lambda i: hrbeh_rows[i].get("total", 0))
        for i, r in enumerate(hrbeh_rows):
            r["rank"] = s_idx.index(i) + 1
            for cat in BEHAVIOR_CATS:
                r[cat] = r.get(cat, 0)

        st.markdown(style.heatmap_table(hrbeh_rows, [
            {"key": "section", "label": "Homeroom", "align": "left",  "mono": True},
            {"key": "teacher", "label": "Teacher",  "align": "left"},
            {"key": "grade",   "label": "Gr",       "align": "center"},
            {"key": "total",   "label": "Total",    "align": "right", "mono": True},
        ] + [{"key": c, "label": c, "align": "right", "mono": True} for c in BEHAVIOR_CATS],
        rank_col="rank", n=len(hrbeh_rows)), unsafe_allow_html=True)
    else:
        st.info("No homeroom behavior data for this AP.")

# --- Student (repeat referrals) expand ---
with st.expander("Student view — Expand / Close detail view"):
    referrals = dc.get_student_referrals_hotlist(ap_id)
    if referrals:
        for r in referrals:
            r["value"] = str(int(float(r["value"])))
            r["grade"] = str(r["grade"])
        st.markdown(style.hotlist_table(referrals, [
            {"key": "grain_key",       "label": "Student ID",  "align": "left",  "mono": True},
            {"key": "grade",           "label": "Gr",          "align": "center"},
            {"key": "section",         "label": "Homeroom",    "align": "left",  "mono": True},
            {"key": "teacher_name",    "label": "Teacher",     "align": "left"},
            {"key": "metric_category", "label": "Type",        "align": "left"},
            {"key": "value",           "label": "# Incidents", "align": "right", "mono": True},
        ]), unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:11px;color:#8A8FA2;margin-top:6px;">'
            f'{len(referrals)} students with repeat referrals</div>',
            unsafe_allow_html=True,
        )
    else:
        st.success("No repeat referrals flagged for this AP.")


# ===========================================================================
# SECTION: GRADEBOOK / GPA
# ===========================================================================
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(style.domain_banner("Gradebook / GPA", "gradebook"), unsafe_allow_html=True)

# --- Grade rollup ---
st.markdown(style.sub_label("Grade Rollup"), unsafe_allow_html=True)

grade_fail = dc.get_metrics("grade", ap_id, domain="Gradebook/GPA", metric_name="% Failure Rate")
grade_gpa  = dc.get_metrics("grade", ap_id, domain="Gradebook/GPA", metric_name="GPA Average")

ggpa_map: dict = {}
for row in grade_fail:
    g = str(row["grade"])
    ggpa_map.setdefault(g, {"grade": f"Grade {g}", "fail_rate": "—", "gpa": "—", "_fail_val": 0})
    ggpa_map[g]["fail_rate"] = f'{row["value"]:.1f}%'
    ggpa_map[g]["_fail_val"] = row["value"]
for row in grade_gpa:
    g = str(row["grade"])
    ggpa_map.setdefault(g, {"grade": f"Grade {g}", "fail_rate": "—", "gpa": "—", "_fail_val": 0})
    ggpa_map[g]["gpa"] = f'{row["value"]:.2f}'

ggpa_rows = sorted(ggpa_map.values(), key=lambda r: r["grade"])
if ggpa_rows:
    s_idx = sorted(range(len(ggpa_rows)), key=lambda i: ggpa_rows[i].get("_fail_val", 0))
    for i, r in enumerate(ggpa_rows):
        r["rank"] = s_idx.index(i) + 1

    st.markdown(style.heatmap_table(ggpa_rows, [
        {"key": "grade",     "label": "",          "align": "left"},
        {"key": "fail_rate", "label": "% Failure", "align": "right", "mono": True},
        {"key": "gpa",       "label": "Avg GPA",   "align": "right", "mono": True},
    ], rank_col="rank", n=len(ggpa_rows)), unsafe_allow_html=True)
else:
    st.info("No grade-level gradebook data for this AP.")

# --- Homeroom expand ---
with st.expander("Homeroom view — Expand / Close detail view"):
    cls_fail   = dc.get_metrics("classroom", ap_id, domain="Gradebook/GPA", metric_name="% Failure Rate")
    cls_gpa_hr = dc.get_metrics("homeroom",  ap_id, domain="Gradebook/GPA", metric_name="GPA Average")

    combined: dict = {}
    for row in cls_fail:
        k = row["section"]
        combined[k] = {
            "section": k, "teacher": row["teacher_name"],
            "grade": str(row["grade"]),
            "fail_rate": f'{row["value"]:.1f}%',
            "gpa": "—", "_fail_val": row["value"],
        }
    for row in cls_gpa_hr:
        k = row["grain_key"]
        combined.setdefault(k, {"section": k, "teacher": row["teacher_name"],
                                 "grade": str(row["grade"]), "fail_rate": "—",
                                 "gpa": "—", "_fail_val": 999})
        combined[k]["gpa"] = f'{row["value"]:.2f}'

    combined_rows = sorted(combined.values(), key=lambda r: (r["grade"], r["section"]))
    if combined_rows:
        s_idx = sorted(range(len(combined_rows)), key=lambda i: combined_rows[i].get("_fail_val", 0))
        for i, r in enumerate(combined_rows):
            r["rank"] = s_idx.index(i) + 1

        st.markdown(style.heatmap_table(combined_rows, [
            {"key": "section",   "label": "Homeroom", "align": "left",  "mono": True},
            {"key": "teacher",   "label": "Teacher",  "align": "left"},
            {"key": "grade",     "label": "Gr",       "align": "center"},
            {"key": "fail_rate", "label": "% Failure","align": "right", "mono": True},
            {"key": "gpa",       "label": "Avg GPA",  "align": "right", "mono": True},
        ], rank_col="rank", n=len(combined_rows)), unsafe_allow_html=True)
    else:
        st.info("No classroom gradebook data for this AP.")


# ===========================================================================
# SECTION: ASSESSMENTS
# ===========================================================================
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(style.domain_banner("Assessments", "assessments"), unsafe_allow_html=True)

ASSESS_CATS = ["MQQ 4", "CRQ 6", "QA2"]

def _pct(r, cat):
    v = r.get(cat, "—")
    try:
        return float(str(v).replace("%", ""))
    except Exception:
        return 0.0

# --- Grade rollup ---
st.markdown(style.sub_label("Grade Rollup — % Proficient by Assessment Type"), unsafe_allow_html=True)

grade_assess = dc.get_metrics("grade", ap_id, domain="Assessment", metric_name="% Proficient")
gassess_map: dict = {}
for row in grade_assess:
    g = str(row["grade"])
    cat = row["metric_category"] if row["metric_category"] else "Overall"
    gassess_map.setdefault(g, {"grade": f"Grade {g}"})
    gassess_map[g][cat] = f'{row["value"]:.1f}%'

gassess_rows = sorted(gassess_map.values(), key=lambda r: r["grade"])
if gassess_rows:
    s_idx = sorted(range(len(gassess_rows)), key=lambda i: -_pct(gassess_rows[i], ASSESS_CATS[0]))
    for i, r in enumerate(gassess_rows):
        r["rank"] = s_idx.index(i) + 1
        for cat in ASSESS_CATS:
            r.setdefault(cat, "—")

    st.markdown(style.heatmap_table(gassess_rows, [
        {"key": "grade", "label": "", "align": "left"},
    ] + [{"key": c, "label": f"% Prof — {c}", "align": "right", "mono": True} for c in ASSESS_CATS],
    rank_col="rank", n=len(gassess_rows)), unsafe_allow_html=True)
else:
    st.info("No grade-level assessment data for this AP.")

# --- Homeroom expand ---
with st.expander("Homeroom view — Expand / Close detail view"):
    cls_assess = dc.get_metrics("classroom", ap_id, domain="Assessment", metric_name="% Proficient")
    cassess_map: dict = {}
    for row in cls_assess:
        k = row["grain_key"]
        cat = row["metric_category"] if row["metric_category"] else "Overall"
        cassess_map.setdefault(k, {
            "section": row["section"], "teacher": row["teacher_name"],
            "grade": str(row["grade"]),
        })
        cassess_map[k][cat] = f'{row["value"]:.1f}%'

    cassess_rows = sorted(cassess_map.values(), key=lambda r: (r["grade"], r["teacher"]))
    if cassess_rows:
        s_idx = sorted(range(len(cassess_rows)), key=lambda i: -_pct(cassess_rows[i], ASSESS_CATS[0]))
        for i, r in enumerate(cassess_rows):
            r["rank"] = s_idx.index(i) + 1
            for cat in ASSESS_CATS:
                r.setdefault(cat, "—")

        st.markdown(style.heatmap_table(cassess_rows, [
            {"key": "section", "label": "Classroom", "align": "left",  "mono": True},
            {"key": "teacher", "label": "Teacher",   "align": "left"},
            {"key": "grade",   "label": "Gr",        "align": "center"},
        ] + [{"key": c, "label": c, "align": "right", "mono": True} for c in ASSESS_CATS],
        rank_col="rank", n=len(cassess_rows)), unsafe_allow_html=True)
    else:
        st.info("No classroom assessment data for this AP.")


# ===========================================================================
# SECTION: DIBELS
# ===========================================================================
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(style.domain_banner("DIBELS", "dibels"), unsafe_allow_html=True)

# --- Grade rollup ---
st.markdown(style.sub_label("Grade Rollup — % Met PM Benchmark"), unsafe_allow_html=True)

grade_dib = dc.get_metrics("grade", ap_id, domain="DIBELS", metric_name="% Met PM Benchmark")
gdib_rows = []
for row in grade_dib:
    gdib_rows.append({"grade": f'Grade {row["grade"]}', "pct_met": f'{row["value"]:.1f}%', "_val": row["value"]})
gdib_rows.sort(key=lambda r: r["grade"])

if gdib_rows:
    s_idx = sorted(range(len(gdib_rows)), key=lambda i: -gdib_rows[i]["_val"])
    for i, r in enumerate(gdib_rows):
        r["rank"] = s_idx.index(i) + 1

    st.markdown(style.heatmap_table(gdib_rows, [
        {"key": "grade",   "label": "",     "align": "left"},
        {"key": "pct_met", "label": "% Met","align": "right", "mono": True},
    ], rank_col="rank", n=len(gdib_rows)), unsafe_allow_html=True)
else:
    st.info("No grade-level DIBELS data for this AP.")

# --- Homeroom expand ---
with st.expander("Homeroom view — Expand / Close detail view"):
    hr_dib = dc.get_metrics("homeroom", ap_id, domain="DIBELS", metric_name="% Met PM Benchmark")
    hrdib_rows = []
    for row in hr_dib:
        hrdib_rows.append({
            "section": row["grain_key"], "teacher": row["teacher_name"],
            "grade": str(row["grade"]), "pct_met": f'{row["value"]:.1f}%', "_val": row["value"],
        })
    hrdib_rows.sort(key=lambda r: (r["grade"], r["section"]))

    if hrdib_rows:
        s_idx = sorted(range(len(hrdib_rows)), key=lambda i: -hrdib_rows[i]["_val"])
        for i, r in enumerate(hrdib_rows):
            r["rank"] = s_idx.index(i) + 1

        st.markdown(style.heatmap_table(hrdib_rows, [
            {"key": "section", "label": "Classroom", "align": "left",  "mono": True},
            {"key": "teacher", "label": "Teacher",   "align": "left"},
            {"key": "grade",   "label": "Gr",        "align": "center"},
            {"key": "pct_met", "label": "% Met",     "align": "right", "mono": True},
        ], rank_col="rank", n=len(hrdib_rows)), unsafe_allow_html=True)
    else:
        st.info("No homeroom DIBELS data for this AP.")


# ===========================================================================
# SECTION: iREADY
# ===========================================================================
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(style.domain_banner("iReady", "iready"), unsafe_allow_html=True)

st.markdown(style.sub_label("Homeroom — # Lessons Passed"), unsafe_allow_html=True)

ir_rows_raw = dc.get_metrics("homeroom", ap_id, domain="iReady", metric_name="# Lessons Passed")
ir_rows = []
for row in ir_rows_raw:
    ir_rows.append({
        "section": row["grain_key"], "teacher": row["teacher_name"],
        "grade": str(row["grade"]), "lessons": str(int(row["value"])), "_val": row["value"],
    })
ir_rows.sort(key=lambda r: (r["grade"], r["section"]))

if ir_rows:
    s_idx = sorted(range(len(ir_rows)), key=lambda i: -ir_rows[i]["_val"])
    for i, r in enumerate(ir_rows):
        r["rank"] = s_idx.index(i) + 1

    st.markdown(style.heatmap_table(ir_rows, [
        {"key": "section", "label": "Homeroom",        "align": "left",  "mono": True},
        {"key": "teacher", "label": "Teacher",          "align": "left"},
        {"key": "grade",   "label": "Gr",               "align": "center"},
        {"key": "lessons", "label": "# Lessons Passed", "align": "right", "mono": True},
    ], rank_col="rank", n=len(ir_rows)), unsafe_allow_html=True)
else:
    st.info("No iReady data for this AP.")


# ===========================================================================
# SECTION: OBSERVATIONS
# ===========================================================================
st.markdown("<br/>", unsafe_allow_html=True)
st.markdown(style.domain_banner("Observations", "observations"), unsafe_allow_html=True)

st.markdown(style.sub_label("Days Since Last Observed — Teacher Grain"), unsafe_allow_html=True)

obs_rows_raw = dc.get_metrics("teacher", ap_id, domain="Observations", metric_name="Days Since Last Observed")
obs_rows = []
for row in obs_rows_raw:
    days = int(row["value"])
    obs_rows.append({
        "teacher":     row["teacher_name"],
        "teacher_num": row["teacher_number"],
        "days":        str(days),
        "_val":        days,
    })
obs_rows.sort(key=lambda r: -r["_val"])

if obs_rows:
    s_idx = sorted(range(len(obs_rows)), key=lambda i: obs_rows[i]["_val"])
    for i, r in enumerate(obs_rows):
        r["rank"] = s_idx.index(i) + 1

    st.markdown(style.heatmap_table(obs_rows, [
        {"key": "teacher",     "label": "Teacher",            "align": "left"},
        {"key": "teacher_num", "label": "ID",                 "align": "left",  "mono": True},
        {"key": "days",        "label": "Days Since Observed", "align": "right", "mono": True},
    ], rank_col="rank", n=len(obs_rows)), unsafe_allow_html=True)

    overdue = [r for r in obs_rows if r["_val"] > 14]
    if overdue:
        st.markdown(
            f'<div class="badge-alert" style="margin-top:10px;">'
            f'⚠ {len(overdue)} teacher{"s" if len(overdue) > 1 else ""} not observed in 14+ days</div>',
            unsafe_allow_html=True,
        )
else:
    st.info("No observation data for this AP.")

st.markdown("<br/><br/>", unsafe_allow_html=True)
