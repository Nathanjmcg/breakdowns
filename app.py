import streamlit as st
import json
import base64
import requests
from datetime import date, timedelta
import calendar

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Kensite Breakdown Tracker",
    page_icon="🔧",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Brand CSS ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Figtree', sans-serif !important;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d823b !important;
}
[data-testid="stSidebar"] * {
    color: #ffffff !important;
}
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stDateInput label {
    color: #ffffff !important;
    font-weight: 600;
}
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: rgba(255,255,255,0.15) !important;
    color: #ffffff !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}

/* Main header */
.main-header {
    background: #0d823b;
    color: white;
    padding: 1.2rem 2rem;
    border-radius: 8px;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    gap: 1rem;
}
.main-header h1 {
    margin: 0;
    font-size: 1.8rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: white;
}
.main-header .tagline {
    font-size: 0.85rem;
    opacity: 0.85;
    font-weight: 400;
    margin: 0;
}

/* Calendar grid */
.cal-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 6px;
    margin-bottom: 1rem;
}
.cal-day-header {
    background: #0d823b;
    color: white;
    text-align: center;
    padding: 8px 4px;
    font-weight: 700;
    font-size: 0.75rem;
    border-radius: 4px;
    letter-spacing: 0.5px;
}
.cal-day {
    background: #f8f9fa;
    border: 1.5px solid #dadada;
    border-radius: 6px;
    padding: 8px;
    min-height: 80px;
    cursor: pointer;
    transition: all 0.15s ease;
    position: relative;
}
.cal-day:hover {
    border-color: #0d823b;
    background: #f0faf4;
}
.cal-day.has-wo {
    border-color: #0d823b;
    background: #f0faf4;
}
.cal-day.today {
    border-color: #0d823b;
    border-width: 2px;
    background: #e6f4ec;
}
.cal-day.empty {
    background: #fafafa;
    border-color: #eeeeee;
    cursor: default;
}
.cal-day-num {
    font-weight: 700;
    font-size: 0.9rem;
    color: #40424a;
}
.cal-day-num.today-num {
    color: #0d823b;
}
.wo-badge {
    background: #0d823b;
    color: white;
    border-radius: 12px;
    padding: 2px 8px;
    font-size: 0.7rem;
    font-weight: 700;
    display: inline-block;
    margin-top: 4px;
}

/* Week summary bar */
.week-summary {
    background: white;
    border: 1.5px solid #dadada;
    border-left: 4px solid #0d823b;
    border-radius: 6px;
    padding: 10px 14px;
    margin-bottom: 6px;
    font-size: 0.82rem;
}
.week-summary .week-label {
    font-weight: 700;
    color: #0d823b;
    font-size: 0.85rem;
}
.week-summary .cat-pill {
    display: inline-block;
    background: #f0faf4;
    border: 1px solid #0d823b;
    color: #0d823b;
    border-radius: 12px;
    padding: 1px 8px;
    font-size: 0.7rem;
    font-weight: 600;
    margin: 2px 2px 2px 0;
}
.week-summary .charge-total {
    font-weight: 700;
    color: #0d823b;
}

/* WO cards */
.wo-card {
    background: white;
    border: 1.5px solid #dadada;
    border-left: 4px solid #0d823b;
    border-radius: 6px;
    padding: 12px 16px;
    margin-bottom: 10px;
}
.wo-card h4 {
    margin: 0 0 6px 0;
    color: #0d823b;
    font-size: 1rem;
    font-weight: 700;
}
.wo-card .meta {
    font-size: 0.8rem;
    color: #40424a;
    margin-bottom: 8px;
}

/* Status pills */
.pill-done {
    display: inline-block;
    background: #0d823b;
    color: white;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 0.68rem;
    font-weight: 600;
    margin: 1px;
}
.pill-pend {
    display: inline-block;
    background: #dadada;
    color: #40424a;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 0.68rem;
    font-weight: 600;
    margin: 1px;
}
.pill-charge {
    display: inline-block;
    background: #fff3cd;
    color: #856404;
    border-radius: 10px;
    padding: 2px 8px;
    font-size: 0.68rem;
    font-weight: 600;
    margin: 1px;
    border: 1px solid #ffc107;
}

/* Metric cards */
.metric-row {
    display: flex;
    gap: 12px;
    margin-bottom: 1rem;
}
.metric-card {
    background: white;
    border: 1.5px solid #dadada;
    border-radius: 8px;
    padding: 14px 18px;
    flex: 1;
    text-align: center;
}
.metric-card .value {
    font-size: 2rem;
    font-weight: 800;
    color: #0d823b;
    line-height: 1;
}
.metric-card .label {
    font-size: 0.75rem;
    color: #40424a;
    font-weight: 500;
    margin-top: 4px;
}

/* Buttons */
.stButton > button {
    background: #0d823b !important;
    color: white !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Figtree', sans-serif !important;
    font-weight: 600 !important;
}
.stButton > button:hover {
    background: #0a6b30 !important;
}

/* Form sections */
.form-section {
    background: #f8f9fa;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    border: 1px solid #dadada;
}
.form-section h4 {
    color: #0d823b;
    font-weight: 700;
    margin: 0 0 10px 0;
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

hr { border-color: #dadada; }

/* Navigation month label */
.month-label {
    font-size: 1.4rem;
    font-weight: 800;
    color: #40424a;
    letter-spacing: -0.3px;
}
</style>
""", unsafe_allow_html=True)

# ── GitHub config ─────────────────────────────────────────────────────────────
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
    """Load WO data from GitHub. Cached for 30 seconds."""
    data, sha = gh_get()
    return data, sha

def save_data(data):
    """Write full data dict back to GitHub, always fetching fresh SHA first."""
    _, fresh_sha = gh_get()
    gh_put(data, sha=fresh_sha)
    st.cache_data.clear()

# ── Session state ──────────────────────────────────────────────────────────────
if "data" not in st.session_state or "sha" not in st.session_state:
    _data, _sha = load_data()
    st.session_state.data = _data
    st.session_state.sha  = _sha
if "view_mode" not in st.session_state:
    st.session_state.view_mode = "calendar"  # calendar | day | add_wo | edit_wo
if "selected_date" not in st.session_state:
    st.session_state.selected_date = None
if "edit_wo_id" not in st.session_state:
    st.session_state.edit_wo_id = None
if "cal_year" not in st.session_state:
    st.session_state.cal_year = date.today().year
if "cal_month" not in st.session_state:
    st.session_state.cal_month = date.today().month

CATEGORIES = ["Plumbing", "Electrical", "General", "Welfare", "Generator", "Install", "Demob"]
CHECKLIST_STEPS = [
    "logged_responded",
    "eta_advised",
    "wo_allocated",
    "attended",
]
CHECKLIST_LABELS = {
    "logged_responded": "Logged / Responded",
    "eta_advised": "ETA Advised",
    "wo_allocated": "WO Allocated",
    "attended": "Attended",
    "chargeable": "Chargeable?",
    "charges_processed": "Charges Processed and Advised",
    "invoiced": "Invoiced",
    "complete": "Complete",
}

# ── Helper ─────────────────────────────────────────────────────────────────────
def get_day_wos(day_str):
    return st.session_state.data.get(day_str, [])

def save_wo(day_str, wo):
    """Upsert a WO into the in-memory dict then persist to GitHub."""
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
    """Remove a WO from the in-memory dict then persist to GitHub."""
    st.session_state.data[day_str] = [
        w for w in st.session_state.data.get(day_str, []) if w["id"] != wo_id
    ]
    save_data(st.session_state.data)

def wo_status_summary(wo):
    """Returns list of completed checklist item labels."""
    done = []
    for step in CHECKLIST_STEPS:
        if wo.get(step):
            done.append(CHECKLIST_LABELS[step])
    if wo.get("chargeable"):
        done.append("Chargeable")
        if wo.get("charges_processed"):
            done.append("Charges Processed")
        if wo.get("invoiced"):
            done.append("Invoiced")
    if wo.get("complete"):
        done.append("Complete")
    return done

def get_week_ranges(year, month):
    """Return list of (week_start, week_end) for each week containing days of the month."""
    first_day = date(year, month, 1)
    last_day = date(year, month, calendar.monthrange(year, month)[1])
    weeks = []
    current = first_day - timedelta(days=first_day.weekday())  # back to Monday
    while current <= last_day:
        week_end = current + timedelta(days=6)
        weeks.append((current, week_end))
        current += timedelta(days=7)
    return weeks

def get_month_all_wos(year, month):
    """All WOs in the month."""
    result = []
    num_days = calendar.monthrange(year, month)[1]
    for d in range(1, num_days + 1):
        day_str = f"{year}-{month:02d}-{d:02d}"
        for wo in st.session_state.data.get(day_str, []):
            result.append((day_str, wo))
    return result

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <div>
        <h1>🔧 Kensite Breakdown Tracker</h1>
        <p class="tagline">Complete Site Solutions — Breakdown and Callout Management</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Navigation")
    if st.button("📅  Calendar View", use_container_width=True):
        st.session_state.view_mode = "calendar"
        st.rerun()
    
    st.markdown("---")
    st.markdown("## Month")
    months = ["January","February","March","April","May","June",
              "July","August","September","October","November","December"]
    sel_month = st.selectbox("Month", months, index=st.session_state.cal_month - 1)
    sel_year = st.selectbox("Year", list(range(2024, 2030)), index=list(range(2024,2030)).index(st.session_state.cal_year))

    if st.button("Go", use_container_width=True):
        st.session_state.cal_month = months.index(sel_month) + 1
        st.session_state.cal_year = sel_year
        st.session_state.view_mode = "calendar"
        st.rerun()

    st.markdown("---")
    # Month summary stats
    all_wos = get_month_all_wos(st.session_state.cal_year, st.session_state.cal_month)
    total_wo = len(all_wos)
    chargeable = [w for _, w in all_wos if w.get("chargeable")]
    total_invoiced = sum(float(w.get("amount_invoiced", 0) or 0) for w in chargeable if w.get("invoiced"))
    st.markdown(f"**Month Summary**")
    st.markdown(f"Total WOs: **{total_wo}**")
    st.markdown(f"Chargeable: **{len(chargeable)}**")
    st.markdown(f"Invoiced: **£{total_invoiced:,.2f}**")
    
    st.markdown("---")
    st.markdown('<small style="color:rgba(255,255,255,0.6)">Kensite Services Ltd<br>Complete Site Solutions</small>', unsafe_allow_html=True)

# ── CALENDAR VIEW ──────────────────────────────────────────────────────────────
if st.session_state.view_mode == "calendar":
    year = st.session_state.cal_year
    month = st.session_state.cal_month

    # Month nav
    col_prev, col_title, col_next = st.columns([1, 4, 1])
    with col_prev:
        if st.button("◀ Prev"):
            if month == 1:
                st.session_state.cal_month = 12
                st.session_state.cal_year = year - 1
            else:
                st.session_state.cal_month = month - 1
            st.rerun()
    with col_title:
        st.markdown(f'<div class="month-label">{calendar.month_name[month]} {year}</div>', unsafe_allow_html=True)
    with col_next:
        if st.button("Next ▶"):
            if month == 12:
                st.session_state.cal_month = 1
                st.session_state.cal_year = year + 1
            else:
                st.session_state.cal_month = month + 1
            st.rerun()

    st.markdown("")

    # Day headers
    days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    header_cols = st.columns(7)
    for i, d in enumerate(days_of_week):
        with header_cols[i]:
            st.markdown(f'<div class="cal-day-header">{d}</div>', unsafe_allow_html=True)

    # Build calendar
    first_weekday, num_days = calendar.monthrange(year, month)
    today = date.today()

    # Pad start
    cal_cells = [None] * first_weekday
    for d in range(1, num_days + 1):
        cal_cells.append(d)
    # Pad end to complete grid
    while len(cal_cells) % 7 != 0:
        cal_cells.append(None)

    # Render weeks
    week_idx = 0
    for row_start in range(0, len(cal_cells), 7):
        week_cells = cal_cells[row_start:row_start + 7]
        cols = st.columns(7)
        for i, day_num in enumerate(week_cells):
            with cols[i]:
                if day_num is None:
                    st.markdown('<div class="cal-day empty"></div>', unsafe_allow_html=True)
                else:
                    day_str = f"{year}-{month:02d}-{day_num:02d}"
                    wos = get_day_wos(day_str)
                    n = len(wos)
                    is_today = (date(year, month, day_num) == today)

                    badge = f'<span class="wo-badge">{n} WO{"s" if n != 1 else ""}</span>' if n > 0 else ""
                    today_cls = " today" if is_today else ""
                    has_cls = " has-wo" if n > 0 else ""
                    num_cls = " today-num" if is_today else ""

                    st.markdown(f"""
                    <div class="cal-day{today_cls}{has_cls}">
                        <div class="cal-day-num{num_cls}">{day_num}</div>
                        {badge}
                    </div>
                    """, unsafe_allow_html=True)

                    btn_label = f"{'📋' if n > 0 else '➕'} {day_num}"
                    if st.button(btn_label, key=f"day_{day_str}", use_container_width=True):
                        st.session_state.selected_date = day_str
                        st.session_state.view_mode = "day"
                        st.rerun()

        week_idx += 1
        # Week summary
        week_days = [d for d in week_cells if d is not None]
        if week_days:
            week_wos = []
            for d in week_days:
                ds = f"{year}-{month:02d}-{d:02d}"
                week_wos.extend(st.session_state.data.get(ds, []))
            
            if week_wos:
                from collections import Counter
                cat_counts = Counter(w.get("category", "General") for w in week_wos)
                cat_pills = " ".join(f'<span class="cat-pill">{cat}: {cnt}</span>' for cat, cnt in sorted(cat_counts.items()))
                wk_invoiced = sum(float(w.get("amount_invoiced", 0) or 0) for w in week_wos if w.get("chargeable") and w.get("invoiced"))
                charge_str = f' &nbsp;|&nbsp; <span class="charge-total">Charges: £{wk_invoiced:,.2f}</span>' if wk_invoiced > 0 else ""
                d_range = f"{week_days[0]}–{week_days[-1]} {calendar.month_abbr[month]}"
                st.markdown(f"""
                <div class="week-summary">
                    <span class="week-label">Week: {d_range}</span> — {len(week_wos)} WO{"s" if len(week_wos)!=1 else ""} &nbsp; {cat_pills}{charge_str}
                </div>
                """, unsafe_allow_html=True)

# ── DAY VIEW ───────────────────────────────────────────────────────────────────
elif st.session_state.view_mode == "day":
    day_str = st.session_state.selected_date
    day_date = date.fromisoformat(day_str)
    formatted = day_date.strftime("%A %d %B %Y")

    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("◀ Back to Calendar"):
            st.session_state.view_mode = "calendar"
            st.rerun()
    with col_title:
        st.markdown(f"### {formatted}")

    wos = get_day_wos(day_str)

    # Day metrics
    n_total = len(wos)
    n_complete = sum(1 for w in wos if w.get("complete"))
    n_chargeable = sum(1 for w in wos if w.get("chargeable"))
    day_invoiced = sum(float(w.get("amount_invoiced", 0) or 0) for w in wos if w.get("chargeable") and w.get("invoiced"))

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card"><div class="value">{n_total}</div><div class="label">Work Orders</div></div>
        <div class="metric-card"><div class="value">{n_complete}</div><div class="label">Complete</div></div>
        <div class="metric-card"><div class="value">{n_chargeable}</div><div class="label">Chargeable</div></div>
        <div class="metric-card"><div class="value">£{day_invoiced:,.0f}</div><div class="label">Invoiced Ex VAT</div></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("➕  Add New Work Order", use_container_width=False):
        st.session_state.view_mode = "add_wo"
        st.rerun()

    st.markdown("---")

    if not wos:
        st.info("No work orders recorded for this day. Use the button above to add one.")
    else:
        for wo in wos:
            done_steps = wo_status_summary(wo)
            all_steps_labels = list(CHECKLIST_LABELS.values())
            pills_html = "".join(
                f'<span class="pill-done">{s}</span>' if s in done_steps else f'<span class="pill-pend">{s}</span>'
                for s in all_steps_labels
                if not (s == "Charges Processed and Advised" and not wo.get("chargeable"))
                if not (s == "Invoiced" and not wo.get("chargeable"))
                if not (s == "Chargeable?" and True)  # always show
            )
            charge_info = ""
            if wo.get("chargeable") and wo.get("amount_invoiced"):
                charge_info = f'<span class="pill-charge">£{float(wo.get("amount_invoiced",0)):,.2f} Ex VAT</span>'

            st.markdown(f"""
            <div class="wo-card">
                <h4>WO {wo.get("wo_number","—")} — {wo.get("unit_number","—")}</h4>
                <div class="meta">
                    <strong>{wo.get("customer","—")}</strong> &nbsp;|&nbsp; {wo.get("postcode","—")} &nbsp;|&nbsp; {wo.get("category","—")}
                </div>
                {pills_html} {charge_info}
            </div>
            """, unsafe_allow_html=True)

            col_edit, col_del, _ = st.columns([1, 1, 6])
            with col_edit:
                if st.button("✏️ Edit", key=f"edit_{wo['id']}"):
                    st.session_state.edit_wo_id = wo["id"]
                    st.session_state.view_mode = "edit_wo"
                    st.rerun()
            with col_del:
                if st.button("🗑️ Delete", key=f"del_{wo['id']}"):
                    delete_wo(day_str, wo["id"])
                    st.rerun()

# ── ADD / EDIT WO FORM ─────────────────────────────────────────────────────────
elif st.session_state.view_mode in ("add_wo", "edit_wo"):
    day_str = st.session_state.selected_date
    day_date = date.fromisoformat(day_str)
    is_edit = st.session_state.view_mode == "edit_wo"

    # Load existing WO if editing
    existing_wo = {}
    if is_edit:
        for wo in get_day_wos(day_str):
            if wo["id"] == st.session_state.edit_wo_id:
                existing_wo = wo
                break

    col_back, col_title = st.columns([1, 5])
    with col_back:
        if st.button("◀ Back"):
            st.session_state.view_mode = "day"
            st.rerun()
    with col_title:
        action = "Edit" if is_edit else "Add"
        st.markdown(f"### {action} Work Order — {day_date.strftime('%d %B %Y')}")

    st.markdown('<div class="form-section"><h4>Work Order Details</h4>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        wo_number = st.text_input("WO Number *", value=existing_wo.get("wo_number", ""))
        customer = st.text_input("Customer *", value=existing_wo.get("customer", ""))
    with col2:
        unit_number = st.text_input("Unit Number *", value=existing_wo.get("unit_number", ""))
        postcode = st.text_input("Postcode", value=existing_wo.get("postcode", ""))

    cat_idx = CATEGORIES.index(existing_wo.get("category", "General")) if existing_wo.get("category") in CATEGORIES else 2
    category = st.selectbox("Issue Category *", CATEGORIES, index=cat_idx)

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="form-section"><h4>Progress Checklist</h4>', unsafe_allow_html=True)

    logged_responded = st.checkbox("Logged / Responded", value=existing_wo.get("logged_responded", False))
    eta_advised = st.checkbox("ETA Advised", value=existing_wo.get("eta_advised", False))
    wo_allocated = st.checkbox("WO Allocated", value=existing_wo.get("wo_allocated", False))
    attended = st.checkbox("Attended", value=existing_wo.get("attended", False))

    st.markdown("---")
    chargeable = st.checkbox("Chargeable?", value=existing_wo.get("chargeable", False))

    charges_processed = False
    invoiced = False
    amount_invoiced = ""

    if chargeable:
        charges_processed = st.checkbox("Charges Processed and Advised", value=existing_wo.get("charges_processed", False))
        invoiced = st.checkbox("Invoiced", value=existing_wo.get("invoiced", False))
        amount_invoiced = st.text_input("Amount Invoiced Ex VAT (£)", value=str(existing_wo.get("amount_invoiced", "")), placeholder="e.g. 450.00")

    complete = st.checkbox("Complete", value=existing_wo.get("complete", False))

    st.markdown('</div>', unsafe_allow_html=True)

    col_save, col_cancel = st.columns([1, 5])
    with col_save:
        save_label = "💾 Update WO" if is_edit else "💾 Save WO"
        if st.button(save_label, use_container_width=True):
            if not wo_number or not unit_number or not customer:
                st.error("Please fill in WO Number, Unit Number, and Customer.")
            else:
                import time
                new_wo = {
                    "id": existing_wo.get("id", str(int(time.time() * 1000))),
                    "wo_number": wo_number,
                    "unit_number": unit_number,
                    "customer": customer,
                    "postcode": postcode,
                    "category": category,
                    "logged_responded": logged_responded,
                    "eta_advised": eta_advised,
                    "wo_allocated": wo_allocated,
                    "attended": attended,
                    "chargeable": chargeable,
                    "charges_processed": charges_processed,
                    "invoiced": invoiced,
                    "amount_invoiced": amount_invoiced,
                    "complete": complete,
                }
                save_wo(day_str, new_wo)
                st.session_state.edit_wo_id = None
                st.session_state.view_mode = "day"
                st.success("Work order saved.")
                st.rerun()
    with col_cancel:
        if st.button("Cancel"):
            st.session_state.view_mode = "day"
            st.rerun()
