"""
app.py — AP Unified Dashboard

UI only. Zero business logic. Zero Pandas aggregation.
All data flows through data_client.py.
"""

import streamlit as st
import data_client as dc
import style

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AP Dashboard — Justice",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded",
)
style.inject_global_css()


# ---------------------------------------------------------------------------
# Sidebar — AP selector
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        '<div style="font-family:Barlow Condensed,sans-serif;font-size:22px;'
        'font-weight:700;letter-spacing:0.03em;padding:12px 0 4px 0;">'
        'AP Dashboard</div>'
        '<div style="font-size:11px;color:#8A9FCC;letter-spacing:0.07em;'
        'text-transform:uppercase;padding-bottom:16px;">Justice School · 2024–25</div>',
        unsafe_allow_html=True,
    )

    ap_list = dc.get_ap_list()
    ap_options = {row["ap_manager_name"]: row["ap_manager_id"] for row in ap_list}
    selected_ap_name = st.selectbox("Viewing as", list(ap_options.keys()))
    ap_id = ap_options[selected_ap_name]

    st.markdown(
        '<hr style="border-color:#1a3270;margin:16px 0"/>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="background:#F9A21A;color:#001E62;font-family:JetBrains Mono,monospace;'
        'font-size:10px;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;'
        'border-radius:5px;padding:5px 10px;text-align:center;">⚡ Mock Data — Prototype</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div style="font-size:10px;color:#8A9FCC;letter-spacing:0.05em;margin-top:8px;">'
        'DuckDB · mock_data/*.csv<br/>Prod: swap data_client.py → Cube API</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Page header
# ---------------------------------------------------------------------------
st.markdown(
    f'<h1 style="margin-bottom:2px">Justice School</h1>'
    f'<div style="font-family:DM Sans;font-size:14px;color:#8A8FA2;margin-bottom:20px;">'
    f'Viewing: <strong style="color:#001E62">{selected_ap_name}</strong>'
    f'</div>',
    unsafe_allow_html=True,
)


# ---------------------------------------------------------------------------
# Domain tabs
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "Attendance",
    "Behavior",
    "Assessments",
    "Gradebook / GPA",
    "iReady",
    "DIBELS",
    "Observations",
])


# ============================================================
# TAB 1 — ATTENDANCE
# ============================================================
with tabs[0]:
    st.markdown(style.section_header("Attendance", "ADA · Chronic Absenteeism · Weekly Flags"), unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 16px 0"/>', unsafe_allow_html=True)

    # --- Grade macro ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Grade Rollup</div>', unsafe_allow_html=True)

    grade_ada = dc.get_metrics("grade", ap_id, domain="Attendance", metric_name="ADA%")
    grade_chronic = dc.get_metrics("grade", ap_id, domain="Attendance", metric_name="% Chronic Absenteeism")

    # Merge grade rows into one display dict per grade
    grade_map: dict = {}
    for row in grade_ada:
        g = str(row["grade"])
        grade_map.setdefault(g, {"grade": g, "ada": "—", "chronic": "—", "n": row["student_count"]})
        grade_map[g]["ada"] = f'{row["value"]:.1f}%'
    for row in grade_chronic:
        g = str(row["grade"])
        grade_map.setdefault(g, {"grade": g, "ada": "—", "chronic": "—", "n": row["student_count"]})
        grade_map[g]["chronic"] = f'{row["value"]:.1f}%'

    grade_rows = sorted(grade_map.values(), key=lambda r: r["grade"])

    if grade_rows:
        # Rank by ADA descending (higher ADA = better = rank 1)
        ada_vals = [float(r["ada"].replace("%", "")) if r["ada"] != "—" else 0 for r in grade_rows]
        sorted_idx = sorted(range(len(ada_vals)), key=lambda i: -ada_vals[i])
        rank_map = {sorted_idx[i]: i + 1 for i in range(len(sorted_idx))}
        for i, row in enumerate(grade_rows):
            row["rank"] = rank_map[i]

        cols_def = [
            {"key": "grade", "label": "Grade", "align": "left"},
            {"key": "n", "label": "Students", "align": "right", "mono": True},
            {"key": "ada", "label": "ADA%", "align": "right", "mono": True},
            {"key": "chronic", "label": "% Chronic Abs", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(grade_rows, cols_def, rank_col="rank", n=len(grade_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No grade-level attendance data for this AP.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- Homeroom operational table ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Homeroom Detail</div>', unsafe_allow_html=True)

    hr_ada = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="ADA%")
    hr_chronic = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="% Chronic Absenteeism")
    hr_change = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="ADA% Change from Last Week")
    hr_2plus = dc.get_metrics("homeroom", ap_id, domain="Attendance", metric_name="Students w/ 2+ Absences Last 5 Days")

    # Build homeroom lookup
    hr_map: dict = {}
    for row in hr_ada:
        k = row["grain_key"]
        hr_map.setdefault(k, {
            "section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
            "n": row["student_count"], "ada": "—", "chronic": "—", "change": "—", "two_plus": "—"
        })
        hr_map[k]["ada"] = f'{row["value"]:.1f}%'
    for row in hr_chronic:
        k = row["grain_key"]
        hr_map.setdefault(k, {"section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
                               "n": row["student_count"], "ada": "—", "chronic": "—", "change": "—", "two_plus": "—"})
        hr_map[k]["chronic"] = f'{row["value"]:.1f}%'
    for row in hr_change:
        k = row["grain_key"]
        hr_map.setdefault(k, {"section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
                               "n": row["student_count"], "ada": "—", "chronic": "—", "change": "—", "two_plus": "—"})
        v = row["value"]
        hr_map[k]["change"] = f'+{v:.1f}%' if v > 0 else f'{v:.1f}%'
    for row in hr_2plus:
        k = row["grain_key"]
        hr_map.setdefault(k, {"section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
                               "n": row["student_count"], "ada": "—", "chronic": "—", "change": "—", "two_plus": "—"})
        hr_map[k]["two_plus"] = str(int(row["value"]))

    hr_rows = sorted(hr_map.values(), key=lambda r: (r["grade"], r["section"]))

    if hr_rows:
        ada_vals2 = [float(r["ada"].replace("%", "")) if r["ada"] != "—" else 0 for r in hr_rows]
        s_idx = sorted(range(len(ada_vals2)), key=lambda i: -ada_vals2[i])
        r_map2 = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, row in enumerate(hr_rows):
            row["rank"] = r_map2[i]

        cols_hr = [
            {"key": "section", "label": "Section", "align": "left", "mono": True},
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "grade", "label": "Gr", "align": "center"},
            {"key": "n", "label": "Stu", "align": "right", "mono": True},
            {"key": "ada", "label": "ADA%", "align": "right", "mono": True},
            {"key": "change", "label": "Δ Week", "align": "right", "mono": True},
            {"key": "chronic", "label": "% Chronic", "align": "right", "mono": True},
            {"key": "two_plus", "label": "2+ Abs/5d", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(hr_rows, cols_hr, rank_col="rank", n=len(hr_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No homeroom attendance data for this AP.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- ADA hotlist (lazy) ---
    with st.expander(f"Low-ADA Student Hotlist  ·  click to load"):
        ada_students = dc.get_student_ada_hotlist(ap_id)
        if ada_students:
            cols_stu = [
                {"key": "Student_Number", "label": "Student ID", "align": "left", "mono": True},
                {"key": "Grade_Level", "label": "Gr", "align": "center"},
                {"key": "Section", "label": "Section", "align": "left", "mono": True},
                {"key": "Teadcher_Name", "label": "Teacher", "align": "left"},
                {"key": "value", "label": "ADA%", "align": "right", "mono": True},
            ]
            # Format value as percent
            for r in ada_students:
                r["value"] = f'{float(r["value"]):.1f}%'
            st.markdown(
                style.hotlist_table(ada_students, cols_stu),
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-size:11px;color:#8A8FA2;margin-top:8px;">'
                f'{len(ada_students)} students below ADA threshold</div>',
                unsafe_allow_html=True,
            )
        else:
            st.success("No low-ADA students flagged for this AP.")


# ============================================================
# TAB 2 — BEHAVIOR
# ============================================================
with tabs[1]:
    st.markdown(style.section_header("Behavior", "Incidents by category · Repeat referrals"), unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 16px 0"/>', unsafe_allow_html=True)

    BEHAVIOR_CATS = ["Conflict", "Defiance", "Disruption", "Phone"]

    # --- Grade macro ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Grade Rollup — # Incidents</div>', unsafe_allow_html=True)

    grade_beh = dc.get_metrics("grade", ap_id, domain="Behavior", metric_name="# Incidents")

    # Build grade × category table
    gbeh_map: dict = {}
    for row in grade_beh:
        g = str(row["grade"])
        cat = row["metric_category"] if row["metric_category"] else "Total"
        gbeh_map.setdefault(g, {"grade": g, "total": 0})
        gbeh_map[g][cat] = int(row["value"])
        if cat != "Total":
            gbeh_map[g]["total"] = gbeh_map[g].get("total", 0) + int(row["value"])

    gbeh_rows = sorted(gbeh_map.values(), key=lambda r: r["grade"])

    if gbeh_rows:
        s_idx = sorted(range(len(gbeh_rows)), key=lambda i: gbeh_rows[i].get("total", 0))
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(gbeh_rows):
            r["rank"] = r_map[i]
            for cat in BEHAVIOR_CATS:
                r[cat] = r.get(cat, 0)

        cols_gbeh = [
            {"key": "grade", "label": "Grade", "align": "left"},
            {"key": "total", "label": "Total", "align": "right", "mono": True},
        ] + [{"key": c, "label": c, "align": "right", "mono": True} for c in BEHAVIOR_CATS]

        st.markdown(
            style.heatmap_table(gbeh_rows, cols_gbeh, rank_col="rank", n=len(gbeh_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No grade-level behavior data for this AP.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- Homeroom behavior ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Homeroom Detail</div>', unsafe_allow_html=True)

    hr_beh = dc.get_metrics("homeroom", ap_id, domain="Behavior", metric_name="# Incidents")

    hrbeh_map: dict = {}
    for row in hr_beh:
        k = row["grain_key"]
        cat = row["metric_category"] if row["metric_category"] else "Total"
        hrbeh_map.setdefault(k, {
            "section": k, "teacher": row["teacher_name"], "grade": str(row["grade"]),
            "n": row["student_count"], "total": 0,
        })
        hrbeh_map[k][cat] = int(row["value"])
        if cat != "Total":
            hrbeh_map[k]["total"] = hrbeh_map[k].get("total", 0) + int(row["value"])

    hrbeh_rows = sorted(hrbeh_map.values(), key=lambda r: (r["grade"], r["section"]))

    if hrbeh_rows:
        s_idx = sorted(range(len(hrbeh_rows)), key=lambda i: hrbeh_rows[i].get("total", 0))
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(hrbeh_rows):
            r["rank"] = r_map[i]
            for cat in BEHAVIOR_CATS:
                r[cat] = r.get(cat, 0)

        cols_hrbeh = [
            {"key": "section", "label": "Section", "align": "left", "mono": True},
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "grade", "label": "Gr", "align": "center"},
            {"key": "n", "label": "Stu", "align": "right", "mono": True},
            {"key": "total", "label": "Total", "align": "right", "mono": True},
        ] + [{"key": c, "label": c, "align": "right", "mono": True} for c in BEHAVIOR_CATS]

        st.markdown(
            style.heatmap_table(hrbeh_rows, cols_hrbeh, rank_col="rank", n=len(hrbeh_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No homeroom behavior data for this AP.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- Repeat referral hotlist (lazy) ---
    with st.expander("Repeat Referral Hotlist  ·  click to load"):
        referrals = dc.get_student_referrals_hotlist(ap_id)
        if referrals:
            cols_ref = [
                {"key": "grain_key", "label": "Student ID", "align": "left", "mono": True},
                {"key": "grade", "label": "Gr", "align": "center"},
                {"key": "section", "label": "Section", "align": "left", "mono": True},
                {"key": "teacher_name", "label": "Teacher", "align": "left"},
                {"key": "metric_category", "label": "Type", "align": "left"},
                {"key": "value", "label": "# Incidents", "align": "right", "mono": True},
            ]
            for r in referrals:
                r["value"] = str(int(float(r["value"])))
                r["grade"] = str(r["grade"])
            st.markdown(
                style.hotlist_table(referrals, cols_ref),
                unsafe_allow_html=True,
            )
            st.markdown(
                f'<div style="font-size:11px;color:#8A8FA2;margin-top:8px;">'
                f'{len(referrals)} students with repeat referrals</div>',
                unsafe_allow_html=True,
            )
        else:
            st.success("No repeat referrals flagged for this AP.")


# ============================================================
# TAB 3 — ASSESSMENTS
# ============================================================
with tabs[2]:
    st.markdown(style.section_header("Assessments", "% Proficient by assessment type"), unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 16px 0"/>', unsafe_allow_html=True)

    ASSESS_CATS = ["MQQ 4", "CRQ 6", "QA2"]

    # --- Grade macro ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Grade Rollup</div>', unsafe_allow_html=True)

    grade_assess = dc.get_metrics("grade", ap_id, domain="Assessment", metric_name="% Proficient")

    gassess_map: dict = {}
    for row in grade_assess:
        g = str(row["grade"])
        cat = row["metric_category"] if row["metric_category"] else "Overall"
        gassess_map.setdefault(g, {"grade": g})
        gassess_map[g][cat] = f'{row["value"]:.1f}%'

    gassess_rows = sorted(gassess_map.values(), key=lambda r: r["grade"])

    if gassess_rows:
        # Rank by first available category value
        def _pct(r, cat):
            v = r.get(cat, "—")
            try:
                return float(v.replace("%", ""))
            except Exception:
                return 0.0

        s_idx = sorted(range(len(gassess_rows)), key=lambda i: -_pct(gassess_rows[i], ASSESS_CATS[0]))
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(gassess_rows):
            r["rank"] = r_map[i]
            for cat in ASSESS_CATS:
                r.setdefault(cat, "—")

        cols_gassess = [
            {"key": "grade", "label": "Grade", "align": "left"},
        ] + [{"key": c, "label": f"% Prof {c}", "align": "right", "mono": True} for c in ASSESS_CATS]

        st.markdown(
            style.heatmap_table(gassess_rows, cols_gassess, rank_col="rank", n=len(gassess_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No grade-level assessment data for this AP.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- Classroom detail ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Classroom Detail</div>', unsafe_allow_html=True)

    cls_assess = dc.get_metrics("classroom", ap_id, domain="Assessment", metric_name="% Proficient")

    cassess_map: dict = {}
    for row in cls_assess:
        k = row["grain_key"]
        cat = row["metric_category"] if row["metric_category"] else "Overall"
        cassess_map.setdefault(k, {
            "section": row["section"], "teacher": row["teacher_name"],
            "course": row["course_name"], "grade": str(row["grade"]),
            "n": row["student_count"],
        })
        cassess_map[k][cat] = f'{row["value"]:.1f}%'

    cassess_rows = sorted(cassess_map.values(), key=lambda r: (r["grade"], r["teacher"], r["course"]))

    if cassess_rows:
        s_idx = sorted(range(len(cassess_rows)), key=lambda i: -_pct(cassess_rows[i], ASSESS_CATS[0]))
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(cassess_rows):
            r["rank"] = r_map[i]
            for cat in ASSESS_CATS:
                r.setdefault(cat, "—")

        cols_cassess = [
            {"key": "section", "label": "Section", "align": "left", "mono": True},
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "course", "label": "Course", "align": "left"},
            {"key": "grade", "label": "Gr", "align": "center"},
            {"key": "n", "label": "Stu", "align": "right", "mono": True},
        ] + [{"key": c, "label": f"% Prof {c}", "align": "right", "mono": True} for c in ASSESS_CATS]

        st.markdown(
            style.heatmap_table(cassess_rows, cols_cassess, rank_col="rank", n=len(cassess_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No classroom assessment data for this AP.")


# ============================================================
# TAB 4 — GRADEBOOK / GPA
# ============================================================
with tabs[3]:
    st.markdown(style.section_header("Gradebook / GPA", "% Failure rate · GPA average"), unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 16px 0"/>', unsafe_allow_html=True)

    # --- Grade macro ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Grade Rollup</div>', unsafe_allow_html=True)

    grade_fail = dc.get_metrics("grade", ap_id, domain="Gradebook/GPA", metric_name="% Failure Rate")
    grade_gpa = dc.get_metrics("grade", ap_id, domain="Gradebook/GPA", metric_name="GPA Average")

    ggpa_map: dict = {}
    for row in grade_fail:
        g = str(row["grade"])
        ggpa_map.setdefault(g, {"grade": g, "fail_rate": "—", "gpa": "—"})
        ggpa_map[g]["fail_rate"] = f'{row["value"]:.1f}%'
    for row in grade_gpa:
        g = str(row["grade"])
        ggpa_map.setdefault(g, {"grade": g, "fail_rate": "—", "gpa": "—"})
        ggpa_map[g]["gpa"] = f'{row["value"]:.2f}'

    ggpa_rows = sorted(ggpa_map.values(), key=lambda r: r["grade"])

    if ggpa_rows:
        def _num(r, k):
            try:
                return float(str(r.get(k, "0")).replace("%", ""))
            except Exception:
                return 0.0

        s_idx = sorted(range(len(ggpa_rows)), key=lambda i: _num(ggpa_rows[i], "fail_rate"))
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(ggpa_rows):
            r["rank"] = r_map[i]

        cols_ggpa = [
            {"key": "grade", "label": "Grade", "align": "left"},
            {"key": "fail_rate", "label": "% Failure Rate", "align": "right", "mono": True},
            {"key": "gpa", "label": "GPA Average", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(ggpa_rows, cols_ggpa, rank_col="rank", n=len(ggpa_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No grade-level gradebook data for this AP.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- Classroom detail ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Classroom Detail</div>', unsafe_allow_html=True)

    cls_fail = dc.get_metrics("classroom", ap_id, domain="Gradebook/GPA", metric_name="% Failure Rate")
    cls_gpa_hr = dc.get_metrics("homeroom", ap_id, domain="Gradebook/GPA", metric_name="GPA Average")

    # Classroom failure rate table
    cfail_rows = []
    for row in cls_fail:
        cfail_rows.append({
            "section": row["section"],
            "teacher": row["teacher_name"],
            "course": row["course_name"],
            "grade": str(row["grade"]),
            "n": row["student_count"],
            "fail_rate": f'{row["value"]:.1f}%',
            "_fail_val": row["value"],
        })
    cfail_rows.sort(key=lambda r: (r["grade"], r["teacher"], r["course"]))

    if cfail_rows:
        s_idx = sorted(range(len(cfail_rows)), key=lambda i: cfail_rows[i]["_fail_val"])
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(cfail_rows):
            r["rank"] = r_map[i]

        cols_cfail = [
            {"key": "section", "label": "Section", "align": "left", "mono": True},
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "course", "label": "Course", "align": "left"},
            {"key": "grade", "label": "Gr", "align": "center"},
            {"key": "n", "label": "Stu", "align": "right", "mono": True},
            {"key": "fail_rate", "label": "% Failure Rate", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(cfail_rows, cols_cfail, rank_col="rank", n=len(cfail_rows)),
            unsafe_allow_html=True,
        )

    # Homeroom GPA table (separate)
    if cls_gpa_hr:
        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown('<div style="font-family:Barlow Condensed;font-size:13px;font-weight:700;'
                    'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:6px;">'
                    'Homeroom GPA Average</div>', unsafe_allow_html=True)

        gpa_rows = []
        for row in cls_gpa_hr:
            gpa_rows.append({
                "section": row["grain_key"],
                "teacher": row["teacher_name"],
                "grade": str(row["grade"]),
                "n": row["student_count"],
                "gpa": f'{row["value"]:.2f}',
                "_gpa_val": row["value"],
            })
        gpa_rows.sort(key=lambda r: (r["grade"], r["section"]))

        s_idx = sorted(range(len(gpa_rows)), key=lambda i: -gpa_rows[i]["_gpa_val"])
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(gpa_rows):
            r["rank"] = r_map[i]

        cols_gpa = [
            {"key": "section", "label": "Section", "align": "left", "mono": True},
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "grade", "label": "Gr", "align": "center"},
            {"key": "n", "label": "Stu", "align": "right", "mono": True},
            {"key": "gpa", "label": "GPA Average", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(gpa_rows, cols_gpa, rank_col="rank", n=len(gpa_rows)),
            unsafe_allow_html=True,
        )


# ============================================================
# TAB 5 — iREADY
# ============================================================
with tabs[4]:
    st.markdown(style.section_header("iReady", "# Lessons passed · homeroom grain"), unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 16px 0"/>', unsafe_allow_html=True)

    ir_rows_raw = dc.get_metrics("homeroom", ap_id, domain="iReady", metric_name="# Lessons Passed")

    ir_rows = []
    for row in ir_rows_raw:
        ir_rows.append({
            "section": row["grain_key"],
            "teacher": row["teacher_name"],
            "grade": str(row["grade"]),
            "n": row["student_count"],
            "lessons": str(int(row["value"])),
            "_val": row["value"],
        })
    ir_rows.sort(key=lambda r: (r["grade"], r["section"]))

    if ir_rows:
        s_idx = sorted(range(len(ir_rows)), key=lambda i: -ir_rows[i]["_val"])
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(ir_rows):
            r["rank"] = r_map[i]

        cols_ir = [
            {"key": "section", "label": "Section", "align": "left", "mono": True},
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "grade", "label": "Gr", "align": "center"},
            {"key": "n", "label": "Stu", "align": "right", "mono": True},
            {"key": "lessons", "label": "# Lessons Passed", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(ir_rows, cols_ir, rank_col="rank", n=len(ir_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No iReady data for this AP.")


# ============================================================
# TAB 6 — DIBELS
# ============================================================
with tabs[5]:
    st.markdown(style.section_header("DIBELS", "% Met PM Benchmark"), unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 16px 0"/>', unsafe_allow_html=True)

    # --- Grade macro ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Grade Rollup</div>', unsafe_allow_html=True)

    grade_dib = dc.get_metrics("grade", ap_id, domain="DIBELS", metric_name="% Met PM Benchmark")

    gdib_rows = []
    for row in grade_dib:
        gdib_rows.append({
            "grade": str(row["grade"]),
            "n": row["student_count"],
            "pct_met": f'{row["value"]:.1f}%',
            "_val": row["value"],
        })
    gdib_rows.sort(key=lambda r: r["grade"])

    if gdib_rows:
        s_idx = sorted(range(len(gdib_rows)), key=lambda i: -gdib_rows[i]["_val"])
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(gdib_rows):
            r["rank"] = r_map[i]

        cols_gdib = [
            {"key": "grade", "label": "Grade", "align": "left"},
            {"key": "n", "label": "Students", "align": "right", "mono": True},
            {"key": "pct_met", "label": "% Met PM Benchmark", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(gdib_rows, cols_gdib, rank_col="rank", n=len(gdib_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No grade-level DIBELS data for this AP.")

    st.markdown("<br/>", unsafe_allow_html=True)

    # --- Homeroom detail ---
    st.markdown('<div style="font-family:Barlow Condensed;font-size:15px;font-weight:700;'
                'color:#8A8FA2;letter-spacing:0.07em;text-transform:uppercase;margin-bottom:8px;">'
                'Homeroom Detail</div>', unsafe_allow_html=True)

    hr_dib = dc.get_metrics("homeroom", ap_id, domain="DIBELS", metric_name="% Met PM Benchmark")

    hrdib_rows = []
    for row in hr_dib:
        hrdib_rows.append({
            "section": row["grain_key"],
            "teacher": row["teacher_name"],
            "grade": str(row["grade"]),
            "n": row["student_count"],
            "pct_met": f'{row["value"]:.1f}%',
            "_val": row["value"],
        })
    hrdib_rows.sort(key=lambda r: (r["grade"], r["section"]))

    if hrdib_rows:
        s_idx = sorted(range(len(hrdib_rows)), key=lambda i: -hrdib_rows[i]["_val"])
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(hrdib_rows):
            r["rank"] = r_map[i]

        cols_hrdib = [
            {"key": "section", "label": "Section", "align": "left", "mono": True},
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "grade", "label": "Gr", "align": "center"},
            {"key": "n", "label": "Stu", "align": "right", "mono": True},
            {"key": "pct_met", "label": "% Met PM Benchmark", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(hrdib_rows, cols_hrdib, rank_col="rank", n=len(hrdib_rows)),
            unsafe_allow_html=True,
        )
    else:
        st.info("No homeroom DIBELS data for this AP.")


# ============================================================
# TAB 7 — OBSERVATIONS
# ============================================================
with tabs[6]:
    st.markdown(style.section_header("Observations", "Days since last observed · teacher grain"), unsafe_allow_html=True)
    st.markdown('<hr style="border-color:#EDEEF2;margin:4px 0 16px 0"/>', unsafe_allow_html=True)

    obs_rows_raw = dc.get_metrics("teacher", ap_id, domain="Observations", metric_name="Days Since Last Observed")

    obs_rows = []
    for row in obs_rows_raw:
        days = int(row["value"])
        obs_rows.append({
            "teacher": row["teacher_name"],
            "teacher_num": row["teacher_number"],
            "grade": str(row["grade"]) if row["grade"] else "—",
            "days": str(days),
            "_val": days,
        })
    # Sort by days desc — longest unobserved first
    obs_rows.sort(key=lambda r: -r["_val"])

    if obs_rows:
        # Rank by days asc (fewer days = better = rank 1)
        s_idx = sorted(range(len(obs_rows)), key=lambda i: obs_rows[i]["_val"])
        r_map = {s_idx[i]: i + 1 for i in range(len(s_idx))}
        for i, r in enumerate(obs_rows):
            r["rank"] = r_map[i]

        cols_obs = [
            {"key": "teacher", "label": "Teacher", "align": "left"},
            {"key": "teacher_num", "label": "ID", "align": "left", "mono": True},
            {"key": "days", "label": "Days Since Observed", "align": "right", "mono": True},
        ]
        st.markdown(
            style.heatmap_table(obs_rows, cols_obs, rank_col="rank", n=len(obs_rows)),
            unsafe_allow_html=True,
        )
        # Flag anyone over 14 days
        overdue = [r for r in obs_rows if r["_val"] > 14]
        if overdue:
            st.markdown(
                f'<div class="badge-alert" style="margin-top:12px;">'
                f'⚠ {len(overdue)} teacher{"s" if len(overdue) > 1 else ""} not observed in 14+ days</div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No observation data for this AP.")
