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

# ── Brand constants ────────────────────────────────────────────────────────────
K_GREEN      = "#0d823b"
K_GREEN_DARK = "#0a6630"
K_GREEN_PALE = "#e8f5ee"
K_GREY       = "#40424a"
K_LGREY      = "#dadada"
K_WHITE      = "#ffffff"

_SVG_RAW = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40">'
    '<rect width="120" height="40" rx="4" fill="#0d823b"/>'
    '<text x="10" y="27" font-family="Figtree,Calibri,sans-serif" '
    'font-weight="800" font-size="18" fill="white" letter-spacing="1">KENSITE</text>'
    '</svg>'
)
_SVG_B64 = base64.b64encode(_SVG_RAW.encode()).decode()
KENSITE_LOGO_HTML = f'<img src="data:image/svg+xml;base64,{_SVG_B64}" height="32" alt="Kensite"/>'

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Figtree:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Figtree', Calibri, sans-serif !important;
    color: {K_GREY};
}}
.main .block-container {{ padding-top: 0.75rem; padding-bottom: 2rem; max-width: 100%; }}

/* ── Sidebar ── */
[data-testid="stSidebar"] {{ background: {K_GREEN} !important; }}
[data-testid="stSidebar"] * {{
    color: {K_WHITE} !important;
    font-family: 'Figtree', Calibri, sans-serif !important;
}}
[data-testid="stSidebar"] .stSelectbox > div > div {{
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}}
[data-testid="stSidebar"] hr {{ border-color: rgba(255,255,255,0.25) !important; }}
[data-testid="stSidebar"] .stButton > button {{
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.35) !important;
    color: {K_WHITE} !important;
    font-weight: 600 !important;
}}
[data-testid="stSidebar"] .stButton > button:hover {{
    background: rgba(255,255,255,0.28) !important;
}}

/* ── Header ── */
.ks-header {{
    display: flex; align-items: center; gap: 12px;
    padding: 10px 0 12px;
    border-bottom: 2px solid {K_GREEN};
    margin-bottom: 1rem;
}}
.ks-title {{ font-size: 20px; font-weight: 800; color: {K_GREEN}; letter-spacing: -.3px; }}
.ks-sub {{ font-size: 12px; color: {K_GREY}; opacity: .6; margin-left: auto; }}

/* ── Month nav label ── */
.ks-month-label {{
    font-size: 1.25rem; font-weight: 800; color: {K_GREY};
    letter-spacing: -0.3px; padding-top: 5px;
}}

/* ── Day name headers ── */
.ks-col-head {{
    text-align: center; font-size: 11px; font-weight: 700;
    color: {K_GREY}; opacity: .45; letter-spacing: .07em;
    text-transform: uppercase; padding-bottom: 4px;
}}

/* ── Day cards ── */
.day-card {{
    border: 1px solid {K_LGREY}; border-radius: 8px;
    overflow: hidden; min-height: 110px; background: {K_WHITE}; margin: 1px;
}}
.day-card.is-today {{ border-color: {K_GREEN}; border-width: 2px; }}
.day-card.is-empty-day {{ background: #fafafa; border-color: #ebebeb; min-height: 110px; }}
.day-head {{
    padding: 6px 9px 5px; border-bottom: 1px solid {K_LGREY};
    background: {K_WHITE};
}}
.day-name {{
    font-size: 10px; font-weight: 700; color: {K_GREY};
    opacity: .45; text-transform: uppercase; letter-spacing: .07em;
}}
.day-date {{ font-size: 16px; font-weight: 800; color: {K_GREY}; }}
.day-date.is-today {{ color: {K_GREEN}; }}
.day-body {{ padding: 5px; }}

/* WO summary pills inside day card */
.wo-sum-pill {{
    display: flex; align-items: center; gap: 5px;
    padding: 3px 6px; border-radius: 5px; margin-bottom: 2px;
    font-size: 11px; font-weight: 600;
}}
.wo-sum-dot {{ width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }}
.wo-sum-label {{ flex: 1; min-width: 0; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }}
.day-empty-msg {{ font-size: 10px; color: {K_GREY}; opacity: .3; padding: 4px 5px; font-style: italic; }}

/* ── Add / View button ── */
.ks-add-btn button {{
    background-color: {K_WHITE} !important;
    color: {K_GREEN} !important;
    border: 1.5px solid {K_GREEN} !important;
    font-weight: 700 !important;
    border-radius: 6px !important;
    font-size: 11px !important;
}}
.ks-add-btn button:hover {{ background-color: {K_GREEN_PALE} !important; }}

/* ── Week summary bar (above each week row) ── */
.wk-bar {{
    background: {K_GREEN_PALE}; border: 1px solid #c3dfc9;
    border-radius: 8px; padding: 7px 12px; margin-bottom: 6px;
    font-size: 11px; color: {K_GREEN_DARK};
}}
.wk-bar-title {{ font-weight: 700; font-size: 11px; margin-bottom: 4px; }}
.wk-unit-row {{ display: flex; flex-wrap: wrap; gap: 4px; align-items: center; }}
.wku {{
    background: {K_GREEN}; color: white; border-radius: 4px;
    padding: 2px 8px; font-size: 10.5px; font-weight: 600;
}}
.wku.cat {{ background: {K_GREEN_DARK}; }}
.wku.charge {{ background: #7a5c00; }}

/* ── Primary buttons ── */
.stButton > button {{
    background: {K_GREEN} !important;
    color: {K_WHITE} !important;
    border: none !important;
    border-radius: 5px !important;
    font-family: 'Figtree', Calibri, sans-serif !important;
    font-weight: 700 !important;
}}
.stButton > button:hover {{ background: {K_GREEN_DARK} !important; }}

/* ── Dialog / modal WO chip ── */
.dlg-wo-chip {{
    background: {K_GREEN_PALE}; border: 1px solid #c3dfc9;
    border-left: 5px solid {K_GREEN}; border-radius: 8px;
    padding: 12px 14px; margin-bottom: 6px;
}}
.dlg-wo-title {{ font-size: 16px; font-weight: 800; color: {K_GREEN_DARK}; margin-bottom: 2px; }}
.dlg-wo-meta {{ font-size: 12px; color: {K_GREY}; opacity: .7; margin-bottom: 8px; }}

/* Status pills */
.ks-pill-done {{
    display: inline-block; background: {K_GREEN}; color: {K_WHITE};
    border-radius: 10px; padding: 2px 9px; font-size: 0.67rem;
    font-weight: 700; margin: 2px 2px 2px 0;
}}
.ks-pill-pend {{
    display: inline-block; background: {K_LGREY}; color: {K_GREY};
    border-radius: 10px; padding: 2px 9px; font-size: 0.67rem;
    font-weight: 600; margin: 2px 2px 2px 0; opacity: .65;
}}
.ks-pill-charge {{
    display: inline-block; background: #fff8e1; color: #7a5c00;
    border: 1px solid #f0c940; border-radius: 10px; padding: 2px 9px;
    font-size: 0.67rem; font-weight: 700; margin: 2px 2px 2px 0;
}}

/* ── Form sections in dialog ── */
.ks-form-section {{
    background: #f9fafb; border: 1px solid {K_LGREY};
    border-top: 3px solid {K_GREEN}; border-radius: 6px;
    padding: 14px 16px 10px; margin-bottom: 12px;
}}
.ks-form-section h4 {{
    margin: 0 0 10px 0; color: {K_GREEN}; font-weight: 800;
    font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.6px;
}}

/* ── Progress bar ── */
.wo-progress-wrap {{
    margin-top: 8px;
    display: flex; align-items: center; gap: 8px;
}}
.wo-progress-track {{
    flex: 1; height: 7px; background: #e8e8e8;
    border-radius: 4px; overflow: hidden;
}}
.wo-progress-fill {{
    height: 100%; border-radius: 4px;
    transition: width 0.3s ease;
}}
.wo-progress-label {{
    font-size: 0.68rem; font-weight: 700;
    min-width: 32px; text-align: right;
}}

/* ── Repeat-visit tracker ── */
.tracker-section {{ margin-top: 1.5rem; }}
.tracker-header {{
    font-size: 0.72rem; font-weight: 700; color: {K_GREY};
    text-transform: uppercase; letter-spacing: 0.5px;
    opacity: 0.55; margin-bottom: 8px;
}}
.tracker-card {{
    background: {K_WHITE}; border: 1px solid {K_LGREY};
    border-top: 3px solid {K_GREEN}; border-radius: 6px;
    padding: 10px 14px; margin-bottom: 8px;
}}
.tracker-card h5 {{
    margin: 0 0 8px 0; font-size: 0.78rem; font-weight: 800;
    color: {K_GREEN}; text-transform: uppercase; letter-spacing: 0.4px;
}}
.tracker-row {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 5px 8px; border-radius: 5px; margin-bottom: 3px;
    font-size: 0.8rem;
}}
.tracker-row.warn-amber {{
    background: #fff8e1; color: #7a5c00;
    border-left: 3px solid #f0c940;
}}
.tracker-row.warn-red {{
    background: #fdecea; color: #7b1a1a;
    border-left: 3px solid #e53935;
}}
.tracker-row .tr-name {{ font-weight: 700; }}
.tracker-row .tr-count {{
    font-weight: 800; font-size: 0.78rem;
    background: rgba(0,0,0,0.08); border-radius: 10px;
    padding: 1px 8px;
}}
</style>
""", unsafe_allow_html=True)

# ── GitHub data layer ──────────────────────────────────────────────────────────
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
    return gh_get()

def save_data(data):
    _, fresh_sha = gh_get()
    gh_put(data, sha=fresh_sha)
    st.cache_data.clear()

# ── Session state ──────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    _data, _sha = load_data()
    st.session_state.data = _data
    st.session_state.sha  = _sha
for k, v in [
    ("modal_date", None),
    ("modal_edit_id", None),
    ("day_view_date", None),
    ("cal_year",  date.today().year),
    ("cal_month", date.today().month),
]:
    if k not in st.session_state:
        st.session_state[k] = v

CATEGORIES = ["Plumbing", "Electrical", "General", "Welfare", "Generator", "Install", "Demob"]

# category → colour
CAT_STYLE = {
    "Plumbing":   ("#e8f0fe", "#1a3a8c"),
    "Electrical": ("#fff3cd", "#7a5c00"),
    "General":    (K_GREEN_PALE, K_GREEN_DARK),
    "Welfare":    ("#f3e8ff", "#5b21b6"),
    "Generator":  ("#fdecea", "#7b1a1a"),
    "Install":    ("#e6f4ea", "#137333"),
    "Demob":      ("#fce8e6", "#a50e0e"),
}

CHECKLIST_LABELS = {
    "logged_responded":  "Logged / Responded",
    "eta_advised":       "ETA Advised",
    "wo_allocated":      "WO Allocated",
    "attended":          "Attended",
    "chargeable":        "Chargeable",
    "charges_processed": "Charges Processed",
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

def wo_done_steps(wo):
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

def wo_progress(wo):
    """Return (pct, colour_hex, label) for the WO checklist progress."""
    # Max possible steps depends on whether chargeable
    steps = ['logged_responded', 'eta_advised', 'wo_allocated', 'attended']
    if wo.get('chargeable'):
        steps += ['charges_processed', 'invoiced']
    steps.append('complete')
    total   = len(steps)
    done    = sum(1 for s in steps if wo.get(s))
    pct     = int(done / total * 100) if total > 0 else 0

    # Red → yellow → green via HSL interpolation
    # 0% = hsl(0,85%,48%)  red
    # 50% = hsl(45,95%,45%) amber/yellow
    # 100% = hsl(134,80%,32%) green
    if pct <= 50:
        h = int(pct / 50 * 45)          # 0 → 45
        s = 85 + int(pct / 50 * 10)     # 85 → 95
        l = 48 - int(pct / 50 * 3)      # 48 → 45
    else:
        ratio = (pct - 50) / 50
        h = int(45 + ratio * 89)        # 45 → 134
        s = int(95 - ratio * 15)        # 95 → 80
        l = int(45 - ratio * 13)        # 45 → 32
    colour = f"hsl({h},{s}%,{l}%)"
    return pct, colour, f"{done}/{total}"


def get_month_all_wos(year, month):
    result = []
    for d in range(1, calendar.monthrange(year, month)[1] + 1):
        result.extend(st.session_state.data.get(f"{year}-{month:02d}-{d:02d}", []))
    return result

def repeat_visit_tracker():
    """Return dicts of {name: count} for units, postcodes, customers across ALL data."""
    units, postcodes, customers = Counter(), Counter(), Counter()
    for wos in st.session_state.data.values():
        for wo in wos:
            u = (wo.get('unit_number') or '').strip().upper()
            p = (wo.get('postcode') or '').strip().upper()
            c = (wo.get('customer') or '').strip()
            if u:
                units[u] += 1
            if p:
                postcodes[p] += 1
            if c:
                customers[c] += 1
    return units, postcodes, customers


def week_summary_bar(year, month, week_days):
    """Return HTML for the green wk-bar above a week row."""
    week_wos = []
    for d in week_days:
        week_wos.extend(st.session_state.data.get(f"{year}-{month:02d}-{d:02d}", []))
    if not week_wos:
        return ""

    cat_counts  = Counter(w.get("category", "General") for w in week_wos)
    n_complete  = sum(1 for w in week_wos if w.get("complete"))
    n_charge    = sum(1 for w in week_wos if w.get("chargeable"))
    invoiced    = sum(
        float(w.get("amount_invoiced", 0) or 0)
        for w in week_wos if w.get("chargeable") and w.get("invoiced")
    )

    cat_tags = "".join(
        f'<span class="wku cat">{cat}: {cnt}</span>'
        for cat, cnt in sorted(cat_counts.items())
    )
    charge_tag = (
        f'<span class="wku charge">£{invoiced:,.2f} invoiced</span>'
        if invoiced > 0 else ""
    )
    complete_tag = (
        f'<span style="background:#fff;color:{K_GREEN_DARK};border:1px solid #c3dfc9;'
        f'border-radius:4px;padding:2px 8px;font-size:10.5px;font-weight:600;">'
        f'✓ {n_complete}/{len(week_wos)} complete</span>'
    )
    chargeable_tag = (
        f'<span style="background:#fff8e1;color:#7a5c00;border-radius:4px;'
        f'padding:2px 8px;font-size:10.5px;font-weight:600;">'
        f'⚡ {n_charge} chargeable</span>'
    ) if n_charge > 0 else ""

    d_range = f"{week_days[0]}–{week_days[-1]} {calendar.month_abbr[month]}"

    return (
        f'<div class="wk-bar">'
        f'<div class="wk-bar-title">Week summary &nbsp;·&nbsp; {d_range}'
        f' &nbsp;·&nbsp; {len(week_wos)} WO{"s" if len(week_wos)!=1 else ""}</div>'
        f'<div class="wk-unit-row">{cat_tags} {complete_tag} {chargeable_tag} {charge_tag}</div>'
        f'</div>'
    )

# ══════════════════════════════════════════════════════════════════════════════
# DIALOGS
# ══════════════════════════════════════════════════════════════════════════════

@st.dialog("Work Orders", width="large")
def day_view_dialog(day_str):
    day_date = date.fromisoformat(day_str)
    st.markdown(
        f"<div style='font-size:14px;font-weight:700;color:{K_GREEN};"
        f"margin-bottom:1rem;'>📅 {day_date.strftime('%A %-d %B %Y')}</div>",
        unsafe_allow_html=True
    )
    wos = get_day_wos(day_str)

    if not wos:
        st.info("No work orders for this day.")
    else:
        for wo in wos:
            done = wo_done_steps(wo)
            pct, prog_colour, prog_label = wo_progress(wo)
            pill_keys = ["logged_responded","eta_advised","wo_allocated","attended","chargeable"]
            if wo.get("chargeable"):
                pill_keys += ["charges_processed","invoiced"]
            pill_keys.append("complete")
            pills = "".join(
                f'<span class="ks-pill-done">{CHECKLIST_LABELS[k]}</span>'
                if CHECKLIST_LABELS[k] in done
                else f'<span class="ks-pill-pend">{CHECKLIST_LABELS[k]}</span>'
                for k in pill_keys
            )
            charge_badge = ""
            if wo.get("chargeable") and wo.get("amount_invoiced"):
                charge_badge = (
                    f'<span class="ks-pill-charge">'
                    f'£{float(wo.get("amount_invoiced",0)):,.2f} Ex VAT</span>'
                )
            progress_html = (
                f'<div class="wo-progress-wrap">'
                f'<div class="wo-progress-track">'
                f'<div class="wo-progress-fill" style="width:{pct}%;background:{prog_colour};"></div>'
                f'</div>'
                f'<span class="wo-progress-label" style="color:{prog_colour};">{pct}%</span>'
                f'</div>'
            )

            rc1, rc2, rc3 = st.columns([5, 1, 1])
            with rc1:
                st.markdown(
                    f'<div class="dlg-wo-chip">'
                    f'<div class="dlg-wo-title">'
                    f'WO {wo.get("wo_number","—")} &nbsp;·&nbsp; {wo.get("unit_number","—")}'
                    f'</div>'
                    f'<div class="dlg-wo-meta">'
                    f'{wo.get("customer","—")} &nbsp;·&nbsp; '
                    f'{wo.get("postcode","—")} &nbsp;·&nbsp; '
                    f'{wo.get("category","—")}'
                    f'</div>'
                    f'{pills}{charge_badge}'
                    f'{progress_html}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            with rc2:
                if st.button("✏️", key=f"dv_edit_{wo['id']}", help="Edit",
                             use_container_width=True):
                    st.session_state.day_view_date = None
                    st.session_state.modal_date    = day_str
                    st.session_state.modal_edit_id = wo["id"]
                    st.rerun()
            with rc3:
                if st.button("🗑️", key=f"dv_del_{wo['id']}", help="Delete",
                             use_container_width=True):
                    delete_wo(day_str, wo["id"])
                    st.rerun()

    st.markdown("<hr style='margin:1rem 0'>", unsafe_allow_html=True)
    ac1, ac2 = st.columns(2)
    with ac1:
        if st.button("＋ Add Work Order", use_container_width=True, type="primary"):
            st.session_state.day_view_date = None
            st.session_state.modal_date    = day_str
            st.session_state.modal_edit_id = None
            st.rerun()
    with ac2:
        if st.button("Close", use_container_width=True):
            st.session_state.day_view_date = None
            st.rerun()


@st.dialog("Add / Edit Work Order", width="large")
def wo_modal(day_str, edit_id=None):
    day_date = date.fromisoformat(day_str)
    existing = {}
    if edit_id:
        for w in get_day_wos(day_str):
            if w["id"] == edit_id:
                existing = w
                break

    st.markdown(
        f"<div style='font-size:13px;color:{K_GREY};opacity:.6;"
        f"margin-bottom:1rem;'>📅 {day_date.strftime('%A %-d %B %Y')}</div>",
        unsafe_allow_html=True
    )

    # ── Details ──
    st.markdown('<div class="ks-form-section"><h4>Work Order Details</h4>', unsafe_allow_html=True)
    fc1, fc2 = st.columns(2)
    with fc1:
        wo_number   = st.text_input("WO Number *",   value=existing.get("wo_number", ""))
        customer    = st.text_input("Customer *",     value=existing.get("customer", ""))
    with fc2:
        unit_number = st.text_input("Unit Number *",  value=existing.get("unit_number", ""))
        postcode    = st.text_input("Postcode",        value=existing.get("postcode", ""))
    cat_idx  = CATEGORIES.index(existing["category"]) if existing.get("category") in CATEGORIES else 2
    category = st.selectbox("Issue Category *", CATEGORIES, index=cat_idx)
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Checklist ──
    st.markdown('<div class="ks-form-section"><h4>Progress Checklist</h4>', unsafe_allow_html=True)
    logged_responded = st.checkbox("Logged / Responded", value=existing.get("logged_responded", False))
    eta_advised      = st.checkbox("ETA Advised",         value=existing.get("eta_advised", False))
    wo_allocated     = st.checkbox("WO Allocated",        value=existing.get("wo_allocated", False))
    attended         = st.checkbox("Attended",            value=existing.get("attended", False))
    st.markdown(f"<hr style='border-color:{K_LGREY};margin:.75rem 0;'>", unsafe_allow_html=True)
    chargeable = st.checkbox("Chargeable?", value=existing.get("chargeable", False))

    charges_processed = False
    invoiced_cb       = False
    amount_invoiced   = ""
    if chargeable:
        charges_processed = st.checkbox(
            "Charges Processed and Advised",
            value=existing.get("charges_processed", False)
        )
        invoiced_cb = st.checkbox("Invoiced", value=existing.get("invoiced", False))
        amount_invoiced = st.text_input(
            "Amount Invoiced Ex VAT (£)",
            value=str(existing.get("amount_invoiced", "")),
            placeholder="e.g. 450.00"
        )
    complete = st.checkbox("Complete", value=existing.get("complete", False))
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Buttons ──
    ba1, ba2, ba3 = st.columns([2, 2, 2])
    with ba1:
        label = "✅ Update WO" if edit_id else "✅ Save WO"
        if st.button(label, type="primary", use_container_width=True):
            if not wo_number or not unit_number or not customer:
                st.error("Please fill in WO Number, Unit Number, and Customer.")
            else:
                new_wo = {
                    "id":                existing.get("id", str(int(time.time() * 1000))),
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
                save_wo(day_str, new_wo)
                st.session_state.modal_date    = None
                st.session_state.modal_edit_id = None
                st.rerun()
    with ba2:
        if st.button("Cancel", use_container_width=True):
            st.session_state.modal_date    = None
            st.session_state.modal_edit_id = None
            st.rerun()
    with ba3:
        if edit_id:
            if st.button("🗑 Delete", use_container_width=True):
                delete_wo(day_str, edit_id)
                st.session_state.modal_date    = None
                st.session_state.modal_edit_id = None
                st.rerun()


# ── Trigger dialogs (must be before page render) ───────────────────────────────
if st.session_state.day_view_date:
    day_view_dialog(st.session_state.day_view_date)
elif st.session_state.modal_date:
    wo_modal(st.session_state.modal_date, st.session_state.modal_edit_id)

# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════════════════════════════
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

    st.markdown("<hr/>", unsafe_allow_html=True)
    st.markdown(
        f"<div style='font-size:0.7rem;font-weight:700;color:rgba(255,255,255,0.7);"
        f"text-transform:uppercase;letter-spacing:0.5px;margin-bottom:8px;'>Month</div>",
        unsafe_allow_html=True
    )
    months = ["January","February","March","April","May","June",
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
        st.rerun()

    st.markdown("<hr/>", unsafe_allow_html=True)

    all_wos        = get_month_all_wos(st.session_state.cal_year, st.session_state.cal_month)
    n_chargeable   = sum(1 for w in all_wos if w.get("chargeable"))
    total_invoiced = sum(
        float(w.get("amount_invoiced", 0) or 0)
        for w in all_wos if w.get("chargeable") and w.get("invoiced")
    )
    st.markdown(
        f"<div style='font-size:0.7rem;font-weight:700;color:rgba(255,255,255,0.7);"
        f"text-transform:uppercase;letter-spacing:0.5px;margin-bottom:10px;'>"
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

# ══════════════════════════════════════════════════════════════════════════════
# PAGE HEADER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"<div class='ks-header'>{KENSITE_LOGO_HTML}"
    f"<span class='ks-title'>Breakdown Tracker</span>"
    f"<span class='ks-sub'>Callout and Works Order Management</span>"
    f"</div>",
    unsafe_allow_html=True
)

# ══════════════════════════════════════════════════════════════════════════════
# CALENDAR
# ══════════════════════════════════════════════════════════════════════════════
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

# Day name headers
hcols = st.columns(7)
for i, dn in enumerate(["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]):
    with hcols[i]:
        st.markdown(f"<div class='ks-col-head'>{dn}</div>", unsafe_allow_html=True)

# Build cell grid
first_weekday, num_days = calendar.monthrange(year, month)
cal_cells = [None] * first_weekday + list(range(1, num_days + 1))
while len(cal_cells) % 7 != 0:
    cal_cells.append(None)

# Render weeks
for row_start in range(0, len(cal_cells), 7):
    week_cells = cal_cells[row_start:row_start + 7]
    week_days  = [d for d in week_cells if d is not None]

    # ── Week summary bar above the row ────────────────────────────────────────
    bar_html = week_summary_bar(year, month, week_days)
    if bar_html:
        st.markdown(bar_html, unsafe_allow_html=True)

    # ── Day cards ─────────────────────────────────────────────────────────────
    cols = st.columns(7)
    for i, day_num in enumerate(week_cells):
        with cols[i]:
            if day_num is None:
                st.markdown('<div class="day-card is-empty-day"></div>', unsafe_allow_html=True)
            else:
                ds     = f"{year}-{month:02d}-{day_num:02d}"
                wos    = get_day_wos(ds)
                n      = len(wos)
                is_t   = date(year, month, day_num) == today
                card_c = "is-today" if is_t else ""
                date_c = "is-today" if is_t else ""

                # Build summary HTML for inside the card
                if wos:
                    cat_counts = Counter(w.get("category","General") for w in wos)
                    summary_html = ""
                    for cat, cnt in cat_counts.items():
                        bg, fg = CAT_STYLE.get(cat, (K_GREEN_PALE, K_GREEN_DARK))
                        summary_html += (
                            f'<div class="wo-sum-pill" style="background:{bg};color:{fg};">'
                            f'<div class="wo-sum-dot" style="background:{fg};opacity:.5;"></div>'
                            f'<span class="wo-sum-label">{cnt} × {cat}</span>'
                            f'</div>'
                        )
                    # show complete count if any
                    n_done = sum(1 for w in wos if w.get("complete"))
                    if n_done > 0:
                        summary_html += (
                            f'<div style="font-size:9px;color:{K_GREEN_DARK};'
                            f'font-weight:700;padding:1px 5px;">✓ {n_done}/{n} complete</div>'
                        )
                else:
                    summary_html = "<div class='day-empty-msg'>No callouts</div>"

                st.markdown(
                    f"<div class='day-card {card_c}'>"
                    f"<div class='day-head'>"
                    f"<div class='day-name'>{date(year,month,day_num).strftime('%a')}</div>"
                    f"<div class='day-date {date_c}'>{day_num}</div>"
                    f"</div>"
                    f"<div class='day-body'>{summary_html}</div>"
                    f"</div>",
                    unsafe_allow_html=True
                )

    # ── Add / View buttons below each day ─────────────────────────────────────
    btn_cols = st.columns(7)
    for i, day_num in enumerate(week_cells):
        with btn_cols[i]:
            if day_num is None:
                st.write("")
            else:
                ds  = f"{year}-{month:02d}-{day_num:02d}"
                wos = get_day_wos(ds)
                n   = len(wos)
                st.markdown("<div class='ks-add-btn'>", unsafe_allow_html=True)
                btn_txt = f"📋 View ({n})" if n > 0 else "＋ Add / View"
                if st.button(btn_txt, key=f"day_{ds}", use_container_width=True):
                    if wos:
                        st.session_state.day_view_date = ds
                    else:
                        st.session_state.modal_date    = ds
                        st.session_state.modal_edit_id = None
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# REPEAT VISIT TRACKER
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div style='margin-top:2rem'></div>", unsafe_allow_html=True)
st.markdown(
    f"<div style='border-top:2px solid {K_GREEN};margin-bottom:1rem;'></div>",
    unsafe_allow_html=True
)
st.markdown(
    f"<div style='font-size:1rem;font-weight:800;color:{K_GREEN};"
    f"letter-spacing:-0.2px;margin-bottom:4px;'>🔁 Repeat Visit Tracker</div>"
    f"<div style='font-size:0.75rem;color:{K_GREY};opacity:0.6;margin-bottom:1rem;'>"
    f"Across all recorded data — flags units attended more than once, "
    f"postcodes visited more than once, and customers visited more than 3 times.</div>",
    unsafe_allow_html=True
)

units_ctr, postcodes_ctr, customers_ctr = repeat_visit_tracker()

# Filter by thresholds
repeat_units     = {k: v for k, v in units_ctr.items()     if v > 1}
repeat_postcodes = {k: v for k, v in postcodes_ctr.items() if v > 1}
repeat_customers = {k: v for k, v in customers_ctr.items() if v > 3}

def tracker_rows_html(items, amber_threshold, red_threshold):
    """Render sorted rows with amber/red banding."""
    if not items:
        return f"<div style='font-size:0.78rem;color:{K_GREY};opacity:0.4;padding:6px 2px;font-style:italic;'>None to report</div>"
    html = ""
    for name, count in sorted(items.items(), key=lambda x: -x[1]):
        cls = "warn-red" if count >= red_threshold else "warn-amber"
        html += (
            f'<div class="tracker-row {cls}">'
            f'<span class="tr-name">{name}</span>'
            f'<span class="tr-count">{count}×</span>'
            f'</div>'
        )
    return html

tc1, tc2, tc3 = st.columns(3)

with tc1:
    st.markdown(
        f'<div class="tracker-card">'
        f'<h5>⚙️ Unit Numbers — Attended &gt;1×</h5>'
        f'{tracker_rows_html(repeat_units, 2, 4)}'
        f'</div>',
        unsafe_allow_html=True
    )

with tc2:
    st.markdown(
        f'<div class="tracker-card">'
        f'<h5>📍 Postcodes — Visited &gt;1×</h5>'
        f'{tracker_rows_html(repeat_postcodes, 2, 4)}'
        f'</div>',
        unsafe_allow_html=True
    )

with tc3:
    st.markdown(
        f'<div class="tracker-card">'
        f'<h5>🏢 Customers — Visited &gt;3×</h5>'
        f'{tracker_rows_html(repeat_customers, 4, 7)}'
        f'</div>',
        unsafe_allow_html=True
    )
