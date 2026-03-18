import streamlit as st
import json
import base64
import requests
import time
from collections import Counter
from datetime import date, timedelta
import calendar

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kensite Breakdown Tracker",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand constants (identical to Prep Schedule) ───────────────────────────────
K_GREEN      = "#0d823b"
K_GREEN_DARK = "#0a6630"
K_GREEN_PALE = "#e8f5ee"
K_GREY       = "#40424a"
K_LGREY      = "#dadada"
K_WHITE      = "#ffffff"

# SVG logo — same as Prep Schedule
_SVG_RAW = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40">'
    '<rect width="120" height="40" rx="4" fill="#0d823b"/>'
    '<text x="10" y="27" font-family="Figtree,Calibri,sans-serif" '
    'font-weight="800" font-size="18" fill="white" letter-spacing="1">KENSITE</text>'
    '</svg>'
)
_SVG_B64 = base64.b64encode(_SVG_RAW.encode()).decode()
KENSITE_LOGO_HTML = f'<img src="data:image/svg+xml;base64,{_SVG_B64}" height="32" alt="Kensite"/>'

# ── Brand CSS ──────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Figtree', Calibri, sans-serif !important;
    color: {K_GREY};
}}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{
    background: {K_GREEN} !important;
}}
[data-testid="stSidebar"] * {{
    color: {K_WHITE} !important;
    font-family: 'Figtree', Calibri, sans-serif !important;
}}
[data-testid="stSidebar"] .stSelectbox > div > div {{
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    color: {K_WHITE} !important;
}}
[data-testid="stSidebar"] hr {{
    border-color: rgba(255,255,255,0.25) !important;
}}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    color: {K_WHITE} !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.25) !important;
}}

/* ── Top header bar ── */
.ks-header {{
    display: flex;
    align-items: center;
    gap: 16px;
    background: {K_WHITE};
    border-bottom: 3px solid {K_GREEN};
    padding: 14px 20px 12px 20px;
    margin: -1rem -1rem 1.5rem -1rem;
}}
.ks-header-titles h1 {{
    margin: 0;
    font-size: 1.35rem;
    font-weight: 800;
    color: {K_GREY};
    letter-spacing: -0.3px;
    line-height: 1.1;
}}
.ks-header-titles p {{
    margin: 2px 0 0 0;
    font-size: 0.78rem;
    color: {K_GREEN};
    font-weight: 600;
    letter-spacing: 0.3px;
    text-transform: uppercase;
}}

/* ── Month label ── */
.ks-month-label {{
    font-size: 1.3rem;
    font-weight: 800;
    color: {K_GREY};
    letter-spacing: -0.3px;
    padding-top: 6px;
}}

/* ── Calendar day headers ── */
.ks-day-header {{
    background: {K_GREEN};
    color: {K_WHITE};
    text-align: center;
    padding: 7px 4px;
    font-weight: 700;
    font-size: 0.72rem;
    border-radius: 4px;
    letter-spacing: 0.8px;
    text-transform: uppercase;
}}

/* ── Calendar day cells ── */
.ks-day {{
    background: {K_WHITE};
    border: 1.5px solid {K_LGREY};
    border-radius: 6px;
    padding: 8px 8px 6px 8px;
    min-height: 72px;
    position: relative;
}}
.ks-day.ks-has-wo {{
    border-color: {K_GREEN};
    background: {K_GREEN_PALE};
}}
.ks-day.ks-today {{
    border-color: {K_GREEN};
    border-width: 2px;
    background: {K_GREEN_PALE};
}}
.ks-day.ks-empty {{
    background: #fafafa;
    border-color: #eeeeee;
    min-height: 72px;
}}
.ks-day-num {{
    font-weight: 700;
    font-size: 0.88rem;
    color: {K_GREY};
    line-height: 1;
}}
.ks-day-num.ks-today-num {{
    color: {K_GREEN};
}}
.ks-wo-badge {{
    display: inline-block;
    background: {K_GREEN};
    color: {K_WHITE};
    border-radius: 10px;
    padding: 2px 7px;
    font-size: 0.67rem;
    font-weight: 700;
    margin-top: 5px;
    letter-spacing: 0.2px;
}}

/* ── Add / View button ── */
.ks-add-btn > div > button {{
    background: {K_WHITE} !important;
    color: {K_GREEN} !important;
    border: 1.5px solid {K_GREEN} !important;
    border-radius: 5px !important;
    font-size: 0.72rem !important;
    font-weight: 700 !important;
    padding: 3px 0 !important;
    font-family: 'Figtree', Calibri, sans-serif !important;
}}
.ks-add-btn > div > button:hover {{
    background: {K_GREEN_PALE} !important;
}}

/* ── Week summary strip ── */
.ks-week-strip {{
    background: {K_WHITE};
    border: 1px solid {K_LGREY};
    border-left: 4px solid {K_GREEN};
    border-radius: 5px;
    padding: 8px 14px;
    margin-bottom: 8px;
    font-size: 0.8rem;
    color: {K_GREY};
}}
.ks-week-strip .ks-wk-label {{
    font-weight: 700;
    color: {K_GREEN};
    font-size: 0.82rem;
}}
.ks-week-strip .ks-cat-pill {{
    display: inline-block;
    background: {K_GREEN_PALE};
    border: 1px solid {K_GREEN};
    color: {K_GREEN_DARK};
    border-radius: 10px;
    padding: 1px 8px;
    font-size: 0.67rem;
    font-weight: 700;
    margin: 2px 2px 2px 0;
}}
.ks-week-strip .ks-charge-total {{
    font-weight: 700;
    color: {K_GREEN_DARK};
}}

/* ── WO chip (day view) ── */
.ks-wo-chip {{
    background: {K_GREEN_PALE};
    border: 1px solid #c3dfc9;
    border-left: 4px solid {K_GREEN};
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 8px;
    font-size: 0.82rem;
    color: {K_GREY};
}}
.ks-wo-chip .ks-wo-title {{
    font-weight: 800;
    font-size: 0.92rem;
    color: {K_GREEN_DARK};
    margin-bottom: 3px;
}}
.ks-wo-chip .ks-wo-meta {{
    font-size: 0.78rem;
    color: {K_GREY};
    opacity: 0.85;
    margin-bottom: 7px;
}}

/* ── Status pills ── */
.ks-pill-done {{
    display: inline-block;
    background: {K_GREEN};
    color: {K_WHITE};
    border-radius: 10px;
    padding: 2px 9px;
    font-size: 0.67rem;
    font-weight: 700;
    margin: 2px 2px 2px 0;
}}
.ks-pill-pend {{
    display: inline-block;
    background: {K_LGREY};
    color: {K_GREY};
    border-radius: 10px;
    padding: 2px 9px;
    font-size: 0.67rem;
    font-weight: 600;
    margin: 2px 2px 2px 0;
    opacity: 0.65;
}}
.ks-pill-charge {{
    display: inline-block;
    background: #fff8e1;
    color: #7a5c00;
    border: 1px solid #f0c940;
    border-radius: 10px;
    padding: 2px 9px;
    font-size: 0.67rem;
    font-weight: 700;
    margin: 2px 2px 2px 0;
}}

/* ── Metric strip ── */
.ks-metric-row {{
    display: flex;
    gap: 10px;
    margin-bottom: 1.2rem;
}}
.ks-metric-card {{
    background: {K_WHITE};
    border: 1.5px solid {K_LGREY};
    border-top: 3px solid {K_GREEN};
    border-radius: 6px;
    padding: 12px 16px;
    flex: 1;
    text-align: center;
}}
.ks-metric-card .ks-mv {{
    font-size: 1.9rem;
    font-weight: 800;
    color: {K_GREEN};
    line-height: 1;
}}
.ks-metric-card .ks-ml {{
    font-size: 0.72rem;
    color: {K_GREY};
    font-weight: 600;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}}

/* ── Form sections ── */
.ks-form-section {{
    background: #f9fafb;
    border: 1px solid {K_LGREY};
    border-top: 3px solid {K_GREEN};
    border-radius: 6px;
    padding: 16px 18px 12px 18px;
    margin-bottom: 14px;
}}
.ks-form-section h4 {{
    margin: 0 0 12px 0;
    color: {K_GREEN};
    font-weight: 800;
    font-size: 0.82rem;
    text-transform: uppercase;
    letter-spacing: 0.6px;
}}

/* ── Section headings ── */
.ks-section-heading {{
    font-size: 1.1rem;
    font-weight: 800;
    color: {K_GREY};
    letter-spacing: -0.2px;
    margin: 0 0 2px 0;
}}
.ks-section-sub {{
    font-size: 0.75rem;
    color: {K_GREEN};
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.4px;
    margin: 0 0 14px 0;
}}

/* ── Divider ── */
.ks-divider {{
    border: none;
    border-top: 1px solid {K_LGREY};
    margin: 1rem 0;
}}

/* ── Primary buttons ── */
.stButton > button {{
    background: {K_GREEN} !important;
    color: {K_WHITE} !important;
    border: none !important;
    border-radius: 5px !important;
    font-family: 'Figtree', Calibri, sans-serif !important;
    font-weight: 700 !important;
}}
.stButton > button:hover {{
    background: {K_GREEN_DARK} !important;
}}
</style>
""", unsafe_allow_html=True)

# ── GitHub config ──────────────────────────────────────────────────────────────
GITHUB_TOKEN  = st.secrets["GITHUB_TOKEN"]
GITHUB_REPO   = st.secrets["GITHUB_REPO"]
GITHUB_BRANCH = st.secrets.get("GITHUB_BRANCH", "main")
DATA_FILE     = "data/breakdowns.json"
GH_HEADERS    = {
    "Authorization": f"token {GITHUB_TOKEN}",
    "Accept": "application/vnd.github.v3+json",
}

def gh_get():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
    r = requests.get(url, headers=GH_HEADERS, params={"ref": GITHUB_BRANCH})
    if r.status_code == 404:
        return {}, None
    r.raise_for_status()
    d = r.json()
    return json.loads(base64.b64decode(d["content"]).decode()), d["sha"]

def gh_put(data, sha=None):
    url = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{DATA_FILE}"
    payload = {
        "message": "Update breakdown data",
        "content": base64.b64encode(json.dumps(data, indent=2).encode()).decode(),
        "branch":  GITHUB_BRANCH,
    }
    if sha:
        payload["sha"] = sha
    requests.put(url, headers=GH_HEADERS, json=payload).raise_for_status()

@st.cache_data(ttl=30)
def load_data():
    data, sha = gh_get()
    return data, sha

def save_data(data):
    _, fresh_sha = gh_get()
    gh_put(data, sha=fresh_sha)
    st.cache_data.clear()

# ── Session state ──────────────────────────────────────────────────────────────
if "data" not in st.session_state or "sha" not in st.session_state:
    _data, _sha = load_data()
    st.session_state.data = _data
    st.session_state.sha  = _sha
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "calendar"
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None
if "edit_wo_id" not in st.session_state:
    st.session_state.edit_wo_id = None
if "cal_year" not in st.session_state:
    st.session_state.cal_year = date.today().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = date.today().month

CATEGORIES = ["Plumbing", "Electrical", "General", "Welfare", "Generator", "Install", "Demob"]
CHECKLIST_LABELS = {
    "logged_responded":  "Logged / Responded",
    "eta_advised":       "ETA Advised",
    "wo_allocated":      "WO Allocated",
    "attended":          "Attended",
    "chargeable":        "Chargeable",
    "charges_processed": "Charges Processed and Advised",
    "invoiced":          "Invoiced",
    "complete":          "Complete",
}

# ── Helpers ────────────────────────────────────────────────────────────────────
def get_day_wos(day_str):
    return st.session_state.data.get(day_str, [])

def save_wo(day_str, wo):
    if day_str not in st.session_state.data:
        st.session_state.data[day_str] = []
    existing = st.session_state.data[day_str]
    for i, w in enumerate(existing):
        if w["id"] == wo["id"]:
            existing[i] = wo
            save_data(st.session_state.data)
            return
    existing.append(wo)
    save_data(st.session_state.data)

def delete_wo(day_str, wo_id):
    st.session_state.data[day_str] = [
        w for w in st.session_state.data.get(day_str, []) if w["id"] != wo_id
    ]
    save_data(st.session_state.data)

def wo_checklist_done(wo):
    done = []
    for key in ["logged_responded", "eta_advised", "wo_allocated", "attended"]:
        if wo.get(key):
            done.append(CHECKLIST_LABELS[key])
    if wo.get("chargeable"):
        done.append(CHECKLIST_LABELS["chargeable"])
        if wo.get("charges_processed"):
            done.append(CHECKLIST_LABELS["charges_processed"])
        if wo.get("invoiced"):
            done.append(CHECKLIST_LABELS["invoiced"])
    if wo.get("complete"):
        done.append(CHECKLIST_LABELS["complete"])
    return done

def get_month_all_wos(year, month):
    result = []
    for d in range(1, calendar.monthrange(year, month)[1] + 1):
        ds = f"{year}-{month:02d}-{d:02d}"
        result.extend(st.session_state.data.get(ds, []))
    return result

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<div style='margin-bottom:14px'>{KENSITE_LOGO_HTML}</div>",
                unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:1rem;font-weight:800;color:{K_WHITE};"
        f"letter-spacing:-0.2px;margin-bottom:1px;'>Breakdown Tracker</div>"
        f"<div style='font-size:0.68rem;color:rgba(255,255,255,0.65);"
        f"text-transform:uppercase;letter-spacing:0.6px;margin-bottom:14px;'>"
        f"Complete Site Solutions</div>",
        unsafe_allow_html=True
    )

    if st.button("📅  Calendar View", use_container_width=True):
        st.session_state.view_mode = "calendar"
        st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.7rem;font-weight:700;"
        f"color:rgba(255,255,255,0.7);text-transform:uppercase;"
        f"letter-spacing:0.5px;margin-bottom:8px;'>Month</div>",
        unsafe_allow_html=True
    )
    months   = ["January","February","March","April","May","June",
                "July","August","September","October","November","December"]
    sel_month = st.selectbox("Month", months,
                             index=st.session_state.cal_month - 1,
                             label_visibility="collapsed")
    sel_year  = st.selectbox("Year", list(range(2024, 2031)),
                             index=list(range(2024, 2031)).index(st.session_state.cal_year),
                             label_visibility="collapsed")
    if st.button("Go", use_container_width=True):
        st.session_state.cal_month = months.index(sel_month) + 1
        st.session_state.cal_year  = sel_year
        st.session_state.view_mode = "calendar"
        st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)

    # Month summary
    all_wos        = get_month_all_wos(st.session_state.cal_year, st.session_state.cal_month)
    n_chargeable   = sum(1 for w in all_wos if w.get("chargeable"))
    total_invoiced = sum(
        float(w.get("amount_invoiced", 0) or 0)
        for w in all_wos if w.get("chargeable") and w.get("invoiced")
    )
    st.markdown(
        f"<div style='font-size:0.7rem;font-weight:700;"
        f"color:rgba(255,255,255,0.7);text-transform:uppercase;"
        f"letter-spacing:0.5px;margin-bottom:10px;'>"
        f"{calendar.month_name[st.session_state.cal_month]} Summary</div>",
        unsafe_allow_html=True
    )
    for label, val in [
        ("Work Orders", str(len(all_wos))),
        ("Chargeable",  str(n_chargeable)),
        ("Invoiced",    f"£{total_invoiced:,.2f}"),
    ]:
        st.markdown(
            f"<div style='display:flex;justify-content:space-between;"
            f"font-size:0.82rem;margin-bottom:6px;'>"
            f"<span style='opacity:0.75;'>{label}</span>"
            f"<span style='font-weight:800;'>{val}</span></div>",
            unsafe_allow_html=True
        )

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.67rem;color:rgba(255,255,255,0.45);line-height:1.6;'>"
        f"kensite.co.uk<br>01942 878 747<br>enquiries@kensite.co.uk</div>",
        unsafe_allow_html=True
    )

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown(
    f"<div class='ks-header'>"
    f"{KENSITE_LOGO_HTML}"
    f"<div class='ks-header-titles'>"
    f"<h1>Breakdown Tracker</h1>"
    f"<p>Callout and Works Order Management</p>"
    f"</div></div>",
    unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════════════════════
# CALENDAR VIEW
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.view_mode == "calendar":
    year  = st.session_state.cal_year
    month = st.session_state.cal_month
    today = date.today()

    # Month nav
    col_prev, col_title, col_next = st.columns([1, 5, 1])
    with col_prev:
        if st.button("◀ Prev", use_container_width=True):
            if month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year  = year - 1
            else:
                st.session_state.cal_month -= 1
            st.rerun()
    with col_title:
        st.markdown(
            f"<div class='ks-month-label'>{calendar.month_name[month]} {year}</div>",
            unsafe_allow_html=True
        )
    with col_next:
        if st.button("Next ▶", use_container_width=True):
            if month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year  = year + 1
            else:
                st.session_state.cal_month += 1
            st.rerun()

    # Day-of-week headers
    hcols = st.columns(7)
    for i, dn in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
        with hcols[i]:
            st.markdown(f'<div class="ks-day-header">{dn}</div>', unsafe_allow_html=True)

    # Build cell list
    first_weekday, num_days = calendar.monthrange(year, month)
    cal_cells = [None] * first_weekday + list(range(1, num_days + 1))
    while len(cal_cells) % 7 != 0:
        cal_cells.append(None)

    # Render each week row
    for row_start in range(0, len(cal_cells), 7):
        week_cells = cal_cells[row_start:row_start + 7]
        cols = st.columns(7)

        for i, day_num in enumerate(week_cells):
            with cols[i]:
                if day_num is None:
                    st.markdown('<div class="ks-day ks-empty"></div>', unsafe_allow_html=True)
                else:
                    ds   = f"{year}-{month:02d}-{day_num:02d}"
                    wos  = get_day_wos(ds)
                    n    = len(wos)
                    is_t = date(year, month, day_num) == today

                    cls     = "ks-day" + (" ks-today" if is_t else "") + (" ks-has-wo" if n > 0 else "")
                    num_cls = " ks-today-num" if is_t else ""
                    badge   = (f'<span class="ks-wo-badge">{n} WO{"s" if n!=1 else ""}</span>'
                               if n > 0 else "")

                    st.markdown(
                        f'<div class="{cls}">'
                        f'<div class="ks-day-num{num_cls}">{day_num}</div>'
                        f'{badge}</div>',
                        unsafe_allow_html=True
                    )
                    st.markdown("<div class='ks-add-btn'>", unsafe_allow_html=True)
                    btn_txt = "＋ Add / View" if n == 0 else f"📋 View ({n})"
                    if st.button(btn_txt, key=f"day_{ds}", use_container_width=True):
                        st.session_state.selected_date = ds
                        st.session_state.view_mode     = "day"
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

        # Week summary strip
        week_days = [d for d in week_cells if d is not None]
        if week_days:
            week_wos = []
            for d in week_days:
                week_wos.extend(
                    st.session_state.data.get(f"{year}-{month:02d}-{d:02d}", [])
                )
            if week_wos:
                cat_counts  = Counter(w.get("category", "General") for w in week_wos)
                cat_pills   = " ".join(
                    f'<span class="ks-cat-pill">{cat}: {cnt}</span>'
                    for cat, cnt in sorted(cat_counts.items())
                )
                wk_invoiced = sum(
                    float(w.get("amount_invoiced", 0) or 0)
                    for w in week_wos if w.get("chargeable") and w.get("invoiced")
                )
                charge_str = (
                    f' &nbsp;·&nbsp; <span class="ks-charge-total">Charges: £{wk_invoiced:,.2f}</span>'
                    if wk_invoiced > 0 else ""
                )
                d_range = f"{week_days[0]}–{week_days[-1]} {calendar.month_abbr[month]}"
                n_wos   = len(week_wos)
                st.markdown(
                    f'<div class="ks-week-strip">'
                    f'<span class="ks-wk-label">{d_range}</span>'
                    f' &nbsp;·&nbsp; {n_wos} WO{"s" if n_wos!=1 else ""}'
                    f' &nbsp; {cat_pills}{charge_str}'
                    f'</div>',
                    unsafe_allow_html=True
                )

# ══════════════════════════════════════════════════════════════════════════════
# DAY VIEW
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.view_mode == "day":
    ds       = st.session_state.selected_date
    day_date = date.fromisoformat(ds)
    wos      = get_day_wos(ds)

    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("◀ Calendar"):
            st.session_state.view_mode = "calendar"
            st.rerun()
    with col_title:
        st.markdown(
            f"<div class='ks-section-heading'>{day_date.strftime('%A %d %B %Y')}</div>"
            f"<div class='ks-section-sub'>Work Orders</div>",
            unsafe_allow_html=True
        )

    # Metric strip
    n_total  = len(wos)
    n_done   = sum(1 for w in wos if w.get("complete"))
    n_charge = sum(1 for w in wos if w.get("chargeable"))
    invoiced = sum(
        float(w.get("amount_invoiced", 0) or 0)
        for w in wos if w.get("chargeable") and w.get("invoiced")
    )
    st.markdown(
        f'<div class="ks-metric-row">'
        f'<div class="ks-metric-card"><div class="ks-mv">{n_total}</div>'
        f'<div class="ks-ml">Work Orders</div></div>'
        f'<div class="ks-metric-card"><div class="ks-mv">{n_done}</div>'
        f'<div class="ks-ml">Complete</div></div>'
        f'<div class="ks-metric-card"><div class="ks-mv">{n_charge}</div>'
        f'<div class="ks-ml">Chargeable</div></div>'
        f'<div class="ks-metric-card"><div class="ks-mv">£{invoiced:,.0f}</div>'
        f'<div class="ks-ml">Invoiced Ex VAT</div></div>'
        f'</div>',
        unsafe_allow_html=True
    )

    if st.button("＋  Add New Work Order"):
        st.session_state.view_mode = "add_wo"
        st.rerun()

    st.markdown("<hr class='ks-divider'/>", unsafe_allow_html=True)

    if not wos:
        st.info("No work orders recorded for this day.")
    else:
        for wo in wos:
            done = wo_checklist_done(wo)

            pill_keys = ["logged_responded","eta_advised","wo_allocated","attended","chargeable"]
            if wo.get("chargeable"):
                pill_keys += ["charges_processed","invoiced"]
            pill_keys.append("complete")

            pills_html = ""
            for key in pill_keys:
                label = CHECKLIST_LABELS[key]
                cls   = "ks-pill-done" if label in done else "ks-pill-pend"
                pills_html += f'<span class="{cls}">{label}</span>'

            charge_badge = ""
            if wo.get("chargeable") and wo.get("amount_invoiced"):
                charge_badge = (
                    f'<span class="ks-pill-charge">'
                    f'£{float(wo.get("amount_invoiced",0)):,.2f} Ex VAT</span>'
                )

            st.markdown(
                f'<div class="ks-wo-chip">'
                f'<div class="ks-wo-title">'
                f'WO {wo.get("wo_number","—")} &nbsp;·&nbsp; {wo.get("unit_number","—")}'
                f'</div>'
                f'<div class="ks-wo-meta">'
                f'{wo.get("customer","—")} &nbsp;·&nbsp; '
                f'{wo.get("postcode","—")} &nbsp;·&nbsp; '
                f'{wo.get("category","—")}'
                f'</div>'
                f'{pills_html}{charge_badge}'
                f'</div>',
                unsafe_allow_html=True
            )

            col_edit, col_del, _ = st.columns([1, 1, 6])
            with col_edit:
                if st.button("✏️ Edit", key=f"edit_{wo['id']}"):
                    st.session_state.edit_wo_id = wo["id"]
                    st.session_state.view_mode  = "edit_wo"
                    st.rerun()
            with col_del:
                if st.button("🗑️ Delete", key=f"del_{wo['id']}"):
                    delete_wo(ds, wo["id"])
                    st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# ADD / EDIT FORM
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.view_mode in ("add_wo", "edit_wo"):
    ds       = st.session_state.selected_date
    day_date = date.fromisoformat(ds)
    is_edit  = st.session_state.view_mode == "edit_wo"

    existing_wo = {}
    if is_edit:
        for wo in get_day_wos(ds):
            if wo["id"] == st.session_state.edit_wo_id:
                existing_wo = wo
                break

    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("◀ Back"):
            st.session_state.view_mode = "day"
            st.rerun()
    with col_title:
        action = "Edit" if is_edit else "New"
        st.markdown(
            f"<div class='ks-section-heading'>{action} Work Order</div>"
            f"<div class='ks-section-sub'>{day_date.strftime('%A %d %B %Y')}</div>",
            unsafe_allow_html=True
        )

    # Details
    st.markdown('<div class="ks-form-section"><h4>Work Order Details</h4>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        wo_number   = st.text_input("WO Number *",  value=existing_wo.get("wo_number", ""))
        customer    = st.text_input("Customer *",    value=existing_wo.get("customer", ""))
    with col2:
        unit_number = st.text_input("Unit Number *", value=existing_wo.get("unit_number", ""))
        postcode    = st.text_input("Postcode",       value=existing_wo.get("postcode", ""))
    cat_idx  = CATEGORIES.index(existing_wo["category"]) if existing_wo.get("category") in CATEGORIES else 2
    category = st.selectbox("Issue Category *", CATEGORIES, index=cat_idx)
    st.markdown('</div>', unsafe_allow_html=True)

    # Checklist
    st.markdown('<div class="ks-form-section"><h4>Progress Checklist</h4>', unsafe_allow_html=True)
    logged_responded = st.checkbox("Logged / Responded", value=existing_wo.get("logged_responded", False))
    eta_advised      = st.checkbox("ETA Advised",         value=existing_wo.get("eta_advised", False))
    wo_allocated     = st.checkbox("WO Allocated",        value=existing_wo.get("wo_allocated", False))
    attended         = st.checkbox("Attended",            value=existing_wo.get("attended", False))
    st.markdown("<hr class='ks-divider'/>", unsafe_allow_html=True)
    chargeable = st.checkbox("Chargeable?", value=existing_wo.get("chargeable", False))

    charges_processed = False
    invoiced_cb       = False
    amount_invoiced   = ""
    if chargeable:
        charges_processed = st.checkbox(
            "Charges Processed and Advised",
            value=existing_wo.get("charges_processed", False)
        )
        invoiced_cb     = st.checkbox("Invoiced", value=existing_wo.get("invoiced", False))
        amount_invoiced = st.text_input(
            "Amount Invoiced Ex VAT (£)",
            value=str(existing_wo.get("amount_invoiced", "")),
            placeholder="e.g. 450.00"
        )
    complete = st.checkbox("Complete", value=existing_wo.get("complete", False))
    st.markdown('</div>', unsafe_allow_html=True)

    # Save / Cancel
    col_save, col_cancel, _ = st.columns([1, 1, 4])
    with col_save:
        if st.button("💾 Update WO" if is_edit else "💾 Save WO", use_container_width=True):
            if not wo_number or not unit_number or not customer:
                st.error("Please fill in WO Number, Unit Number, and Customer.")
            else:
                new_wo = {
                    "id":                existing_wo.get("id", str(int(time.time() * 1000))),
                    "wo_number":         wo_number,
                    "unit_number":       unit_number,
                    "customer":          customer,
                    "postcode":          postcode,
                    "category":          category,
                    "logged_responded":  logged_responded,
                    "eta_advised":       eta_advised,
                    "wo_allocated":      wo_allocated,
                    "attended":          attended,
                    "chargeable":        chargeable,
                    "charges_processed": charges_processed,
                    "invoiced":          invoiced_cb,
                    "amount_invoiced":   amount_invoiced,
                    "complete":          complete,
                }
                save_wo(ds, new_wo)
                st.session_state.edit_wo_id = None
                st.session_state.view_mode  = "day"
                st.rerun()
    with col_cancel:
        if st.button("Cancel", use_container_width=True):
            st.session_state.view_mode = "day"
            st.rerun()
