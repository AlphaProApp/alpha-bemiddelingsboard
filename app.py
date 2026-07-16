from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo

import streamlit as st
from supabase import create_client


KANDIDAAT_STATUSSEN = [
    "Actief",
    "Kandidaten opslag",
    "Inactief",
    "Geplaatst",
    "Teruggetrokken",
    "Opgelost",
]
ERVARING_BINNEN_OPTIES = [
    "Engineer",
    "Industrieel Monteur",
    "Werkvoorbereider / Planner",
    "Inkoper",
    "Staffing / Overig",
    "Logistiek",
    "Productie",
    "Manager",
    "QESH / SHE",
    "Monteur Utiliteit",
    "HVAC / Koeltechniek",
    "Overig",
]
REISAFSTAND_OPTIES = [
    "1-15 minuten",
    "15-30 minuten",
    "30-45 minuten",
    "45-60 minuten",
    "60+ minuten",
]
WERKTIJDEN_OPTIES = [
    "Dagdienst",
    "2 Ploegen",
    "3 Ploegen",
    "4 Ploegen",
    "5 Ploegen",
]
DISCIPLINE_OPTIES = [
    "Electrical",
    "Werktuigbouwkunde",
    "Chemie",
    "Industriële Automatisering",
]
SOFTWAREKENNIS_OPTIES = [
    "EPLAN",
    "AutoCAD",
    "AutoCAD Electrical",
    "Inventor",
    "SolidWorks",
    "Revit",
    "Plant3D",
    "MicroStation",
    "Tekla",
    "Creo",
    "CATIA",
    "PCS7",
    "ABB 800xA",
    "DeltaV",
    "Honeywell Experion",
    "Yokogawa Centum",
    "Foxboro",
    "TIA Portal",
    "Siemens S7",
    "Siemens S5",
    "Omron",
    "Allen Bradley",
    "Schneider / Modicon",
    "Beckhoff",
    "Mitsubishi",
    "Priva",
    "Johnson Controls",
    "Siemens Desigo",
    "Trend",
    "Ultimo",
    "SAP",
    "Maximo",
]
AANBIEDING_STATUS_LABELS = {
    "open": "Open",
    "verstuurd": "Verstuurd",
    "intro": "Intro",
    "latent": "Latent",
    "automatisch_afgewezen_langlopende_intro": "Automatisch afgewezen of Langlopende Intro",
    "afgewezen": "Afgewezen",
    "teruggetrokken": "Teruggetrokken",
    "mismatch": "Mismatch",
    "nvt": "Geen reactie of geen vacature",
}
AANBIEDING_STATUSSEN = list(AANBIEDING_STATUS_LABELS.keys())
INTRO_STATUSSEN = ["intro", "latent", "automatisch_afgewezen_langlopende_intro"]
INTRO_STATUS_LABELS = {
    "eerste_gesprek": "1e Gesprek",
    "tweede_gesprek_meeloopdag": "2e Gesprek / Meeloopdag",
    "intro_afgewezen": "Afgewezen",
    "kandidaat_teruggetrokken": "Kandidaat teruggetrokken",
    "geplaatst": "Geplaatst",
}
INTRO_STATUSSEN_OPTIES = list(INTRO_STATUS_LABELS.keys())
ACTIEVE_INTRO_STATUSSEN = ["eerste_gesprek", "tweede_gesprek_meeloopdag", None]
APP_TZ = ZoneInfo("Europe/Amsterdam")
VERBORGEN_RECRUITER_NAMEN = {"Recruiter 3"}


st.set_page_config(page_title="Kandidaten Beheer", layout="wide")

def inject_custom_css():
    st.markdown(
        """
        <style>
        :root {
            --crm-bg: #f3f6f8;
            --crm-sidebar: #e3eaf0;
            --crm-surface: #ffffff;
            --crm-surface-soft: #f7f9fb;
            --crm-border: #d4dde5;
            --crm-border-soft: #e1e7ed;
            --crm-text: #18384a;
            --crm-heading: #163247;
            --crm-muted: #627282;
            --crm-steel: #a9b4be;
            --crm-accent: #5faf8f;
            --crm-accent-strong: #33846b;
            --crm-accent-soft: #edf8f3;
            --crm-danger: #a33a3a;
            --crm-danger-soft: #fff5f5;
        }
        header[data-testid="stHeader"] {
            background: transparent;
            height: 0;
        }
        header[data-testid="stHeader"] > div {
            height: 0;
        }
        .stApp {
            background: var(--crm-bg);
            color: var(--crm-text);
        }
        .block-container {
            padding-top: 0.65rem;
            padding-bottom: 2rem;
            max-width: 1500px;
        }
        h1, h2, h3 {
            letter-spacing: 0;
            color: var(--crm-heading);
            font-weight: 750;
        }
        h1 {
            font-size: 1.72rem;
            margin: 0 0 0.25rem 0;
        }
        h2 {
            font-size: 1.22rem;
            margin: 0.95rem 0 0.25rem 0;
        }
        h3 {
            font-size: 1rem;
            margin: 0.65rem 0 0.15rem 0;
        }
        .stCaption, caption, small {
            color: var(--crm-muted);
        }
        div[data-testid="stVerticalBlock"] {
            gap: 0.48rem;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0.68rem;
            align-items: center;
        }
        section[data-testid="stSidebar"] {
            background: var(--crm-sidebar);
            border-right: 1px solid #c3ced8;
        }
        section[data-testid="stSidebar"] > div {
            padding-top: 1.15rem;
        }
        .alpha-sidebar-brand {
            border-bottom: 1px solid #c3ced8;
            margin: 0 0 0.85rem 0;
            padding: 0 0 0.75rem 0;
        }
        .alpha-sidebar-kicker {
            color: var(--crm-heading);
            font-size: 0.86rem;
            font-weight: 850;
            letter-spacing: 0.08em;
        }
        .alpha-sidebar-subtitle {
            color: #667786;
            font-size: 0.78rem;
            font-weight: 650;
            margin-top: 0.08rem;
        }
        .alpha-sidebar-accent {
            width: 2.2rem;
            height: 3px;
            background: var(--crm-accent);
            border-radius: 999px;
            margin-top: 0.42rem;
        }
        section[data-testid="stSidebar"] label,
        section[data-testid="stSidebar"] p {
            color: var(--crm-heading);
            font-weight: 600;
        }
        section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
            background: #ffffff;
            border-color: #c3ced8;
            border-radius: 6px;
            min-height: 2.1rem;
        }
        .sidebar-menu-label {
            color: #667786;
            font-size: 0.72rem;
            font-weight: 800;
            letter-spacing: 0.05em;
            text-transform: uppercase;
            margin: 0.7rem 0 0.18rem 0;
        }
        .consultant-card-label {
            color: #667786;
            font-size: 0.72rem;
            font-weight: 800;
            text-transform: uppercase;
            letter-spacing: 0.04em;
            margin: 0 0 0.05rem 0;
            padding-top: 0.05rem;
        }
        .consultant-card-name {
            color: var(--crm-heading);
            font-size: 0.98rem;
            font-weight: 800;
            line-height: 1.8rem;
            margin-bottom: 0;
        }
        .consultant-sidebar-separator {
            border-bottom: 1px solid #c3ced8;
            margin-bottom: 0.64rem;
            padding-bottom: 0.66rem;
        }
        section[data-testid="stSidebar"] div.stButton > button {
            min-height: 1.65rem;
            min-width: 0;
            padding: 0.12rem 0.48rem;
            border-radius: 5px;
            background: rgba(255, 255, 255, 0.58);
            border-color: #b8c3cd;
            color: var(--crm-heading);
            box-shadow: none;
            font-size: 0.78rem;
        }
        section[data-testid="stSidebar"] div.stButton > button:hover {
            background: #ffffff;
            border-color: var(--crm-accent);
            color: var(--crm-heading);
        }
        div[data-testid="stForm"],
        div[data-testid="stExpander"] details,
        div[data-testid="stTable"],
        div[data-testid="stDataFrame"] {
            background: var(--crm-surface);
            border: 1px solid var(--crm-border-soft);
            border-radius: 7px;
            box-shadow: 0 1px 2px rgba(22, 50, 71, 0.04);
        }
        div[data-testid="stForm"] {
            padding: 0.9rem;
        }
        div[data-testid="stExpander"] summary {
            font-size: 0.9rem;
            font-weight: 700;
        }
        div[data-testid="stTable"] {
            overflow: hidden;
        }
        div[data-testid="stTable"] table {
            border-collapse: collapse;
            font-size: 0.88rem;
        }
        div[data-testid="stTable"] thead tr th {
            background: #edf2f5;
            color: var(--crm-heading);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.02em;
            font-weight: 750;
            border-bottom: 1px solid var(--crm-border);
            padding: 0.42rem 0.55rem;
        }
        div[data-testid="stTable"] tbody tr td,
        div[data-testid="stTable"] tbody tr th {
            border-bottom: 1px solid var(--crm-border-soft);
            padding: 0.42rem 0.55rem;
            color: var(--crm-text);
        }
        div[data-testid="stTable"] tbody tr:hover {
            background: #f9fbfc;
        }
        div.stButton > button,
        div[data-testid="stFormSubmitButton"] > button {
            min-height: 1.95rem;
            min-width: 4.85rem;
            padding: 0.25rem 0.72rem;
            border-radius: 5px;
            border-color: #b8c3cd;
            background: #ffffff;
            color: var(--crm-heading);
            white-space: nowrap;
            font-size: 0.85rem;
            font-weight: 700;
            box-shadow: 0 1px 1px rgba(22, 50, 71, 0.03);
            transition: background 120ms ease, border-color 120ms ease, color 120ms ease;
        }
        div[data-testid="stFormSubmitButton"] > button {
            background: var(--crm-heading);
            border-color: var(--crm-heading);
            color: #ffffff;
        }
        div.stButton > button:hover,
        div[data-testid="stFormSubmitButton"] > button:hover {
            border-color: var(--crm-accent);
            color: var(--crm-heading);
            background: var(--crm-accent-soft);
        }
        div[data-testid="stFormSubmitButton"] > button:hover {
            border-color: var(--crm-accent-strong);
            background: var(--crm-accent-strong);
            color: #ffffff;
        }
        div.stButton > button p,
        div[data-testid="stFormSubmitButton"] > button p {
            white-space: nowrap;
            overflow-wrap: normal;
            word-break: keep-all;
        }
        div.stButton {
            margin: 0.08rem 0;
        }
        input, textarea, div[data-baseweb="select"] > div {
            border-radius: 6px !important;
            border-color: #cbd5df !important;
        }
        input:focus, textarea:focus {
            border-color: var(--crm-accent) !important;
            box-shadow: 0 0 0 1px rgba(95, 175, 143, 0.12) !important;
        }
        div[data-testid="stMarkdownContainer"] p {
            margin-bottom: 0.15rem;
            line-height: 1.35;
        }
        .crm-section {
            border-top: 1px solid var(--crm-border);
            padding-top: 0.95rem;
            margin-top: 1.05rem;
        }
        .crm-row {
            border-top: 1px solid var(--crm-border-soft);
            height: 1px;
            margin: 0.38rem 0 0.32rem 0;
        }
        .crm-muted {
            color: var(--crm-muted);
            font-size: 0.82rem;
        }
        .crm-action-card div[data-testid="stVerticalBlock"] {
            gap: 0.42rem;
        }
        .crm-action-card h3 {
            margin-top: 0;
            margin-bottom: 0.15rem;
            font-size: 1.02rem;
        }
        .crm-panel-title {
            color: var(--crm-heading);
            font-size: 1.02rem;
            font-weight: 800;
            margin-bottom: 0.35rem;
        }
        .crm-subsection-title {
            color: var(--crm-heading);
            font-size: 0.78rem;
            font-weight: 800;
            letter-spacing: 0.02em;
            margin-top: 0.45rem;
            margin-bottom: 0.2rem;
            text-transform: uppercase;
        }
        .crm-subcard {
            background: var(--crm-surface-soft);
            border: 1px solid var(--crm-border-soft);
            border-radius: 7px;
            padding: 0.72rem 0.8rem;
            margin: 0.35rem 0 0.55rem 0;
        }
        .crm-kpi-card {
            background: var(--crm-surface);
            border: 1px solid var(--crm-border-soft);
            border-radius: 7px;
            padding: 0.72rem 0.85rem;
            box-shadow: 0 1px 2px rgba(22, 50, 71, 0.04);
            border-left: 3px solid var(--crm-accent);
        }
        .crm-kpi-label {
            color: var(--crm-muted);
            font-size: 0.76rem;
            font-weight: 750;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 0.2rem;
        }
        .crm-kpi-value {
            color: var(--crm-heading);
            font-size: 1.72rem;
            line-height: 1.1;
            font-weight: 800;
        }
        .crm-kpi-help {
            color: var(--crm-muted);
            font-size: 0.78rem;
            margin-top: 0.25rem;
        }
        .crm-chip {
            display: inline-flex;
            align-items: center;
            justify-content: center;
            max-width: 100%;
            border: 1px solid #d0d5dd;
            border-radius: 999px;
            padding: 0.12rem 0.55rem;
            font-size: 0.74rem;
            line-height: 1.2;
            font-weight: 750;
            background: #f7f9fb;
            color: var(--crm-heading);
            white-space: nowrap;
        }
        .crm-chip-open { background: #f7f9fb; border-color: #cfd8e1; color: #3d4d5c; }
        .crm-chip-verstuurd { background: #eef5f8; border-color: #c7d7e1; color: #1d5369; }
        .crm-chip-intro { background: var(--crm-accent-soft); border-color: #b8dece; color: #25765f; }
        .crm-chip-latent { background: #fbf8ef; border-color: #e8dcb5; color: #765d21; }
        .crm-chip-automatisch_afgewezen_langlopende_intro { background: #fbf0f0; border-color: #e4c3c3; color: #8b3131; }
        .crm-chip-afgewezen,
        .crm-chip-teruggetrokken { background: #fbf0f0; border-color: #e4c3c3; color: #8b3131; }
        .crm-chip-mismatch { background: #fbf5ed; border-color: #e5d0b9; color: #7f5630; }
        .crm-chip-nvt { background: #f1f3f5; border-color: #ccd3da; color: #52606d; }
        .crm-table-header p,
        .crm-table-header strong {
            color: var(--crm-heading);
            font-size: 0.76rem;
            text-transform: uppercase;
            letter-spacing: 0.02em;
        }
        .crm-cell {
            font-size: 0.88rem;
            color: var(--crm-text);
        }
        .crm-cell p {
            overflow-wrap: anywhere;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


inject_custom_css()


@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def supabase():
    return get_supabase()


def fetch_recruiters():
    recruiters = supabase().table("recruiters").select("*").order("naam").execute().data
    return [recruiter for recruiter in recruiters if is_visible_recruiter(recruiter)]


def require_recruiter_login(recruiters):
    logged_in_recruiter_id = st.session_state.get("logged_in_recruiter_id")
    current_recruiter = next(
        (recruiter for recruiter in recruiters if recruiter["id"] == logged_in_recruiter_id),
        None,
    )
    if current_recruiter:
        return current_recruiter

    st.title("Alpha Bemiddelingsboard")
    st.subheader("Inloggen")

    recruiter_options_list = [recruiter["naam"] for recruiter in recruiters]
    selected_name = st.selectbox("Consultant", recruiter_options_list)
    login_code = st.text_input("Wachtwoord of pincode", type="password")

    if st.button("Inloggen"):
        selected_recruiter = next(
            recruiter for recruiter in recruiters if recruiter["naam"] == selected_name
        )
        expected_code = selected_recruiter.get("login_code")
        if expected_code and login_code == expected_code:
            st.session_state["logged_in_recruiter_id"] = selected_recruiter["id"]
            st.session_state["logged_in_recruiter_name"] = selected_recruiter["naam"]
            st.session_state["logged_in_is_manager"] = bool(selected_recruiter.get("is_manager"))
            st.rerun()
        else:
            st.error("Onjuiste code")

    st.stop()


def logout_recruiter():
    for key in [
        "logged_in_recruiter_id",
        "logged_in_recruiter_name",
        "logged_in_is_manager",
        "selected_candidate_id",
        "candidate_id",
        "selected_offer_id",
        "intro_planning_offer_id",
    ]:
        st.session_state.pop(key, None)
    st.rerun()


def is_visible_recruiter(recruiter):
    return bool(recruiter.get("naam")) and recruiter.get("naam") not in VERBORGEN_RECRUITER_NAMEN


def display_recruiter_name(name):
    if not name or name in VERBORGEN_RECRUITER_NAMEN:
        return "-"
    return name


def recruiter_options(recruiters):
    return {recruiter["naam"]: recruiter["id"] for recruiter in recruiters}


def recruiter_name(recruiters, recruiter_id):
    recruiter = next((r for r in recruiters if r["id"] == recruiter_id), None)
    return display_recruiter_name(recruiter["naam"]) if recruiter else "-"


def related_recruiter_name(related_recruiter, recruiters, recruiter_id):
    name = (related_recruiter or {}).get("naam")
    if name:
        return display_recruiter_name(name)
    return recruiter_name(recruiters, recruiter_id)


def parse_optional_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def today_amsterdam():
    return datetime.now(APP_TZ).date()


def current_week_window_amsterdam():
    now = datetime.now(APP_TZ)
    week_start_date = (now - timedelta(days=now.weekday())).date()
    week_start = datetime.combine(week_start_date, time(7, 30), APP_TZ)
    if now < week_start:
        week_start -= timedelta(days=7)
    return week_start, week_start + timedelta(days=7)


def current_month_window_amsterdam():
    now = datetime.now(APP_TZ)
    month_start = datetime(now.year, now.month, 1, tzinfo=APP_TZ)
    if now.month == 12:
        next_month = datetime(now.year + 1, 1, 1, tzinfo=APP_TZ)
    else:
        next_month = datetime(now.year, now.month + 1, 1, tzinfo=APP_TZ)
    return month_start, next_month


def split_csv(value):
    if not value:
        return []
    return [item.strip() for item in value.split(",") if item.strip()]


def join_csv(values):
    return ", ".join(values)


def aanbieding_status_label(status):
    return AANBIEDING_STATUS_LABELS.get(status, status or "-")


def aanbieding_status_index(status):
    if status in AANBIEDING_STATUSSEN:
        return AANBIEDING_STATUSSEN.index(status)
    return AANBIEDING_STATUSSEN.index("open")


def intro_status_label(status):
    return INTRO_STATUS_LABELS.get(status, status or "-")


def intro_status_index(status):
    if status in INTRO_STATUSSEN_OPTIES:
        return INTRO_STATUSSEN_OPTIES.index(status)
    return INTRO_STATUSSEN_OPTIES.index("eerste_gesprek")


def is_intro_related_status(status):
    return status in INTRO_STATUSSEN


def is_active_intro_for_aging(intro_status):
    return intro_status in ACTIEVE_INTRO_STATUSSEN


def run_intro_status_updates():
    aanbiedingen = (
        supabase()
        .table("aanbiedingen")
        .select("id, status, datum_intro, intro_status")
        .in_("status", ["intro", "latent"])
        .execute()
        .data
    )
    today = today_amsterdam()

    for aanbieding in aanbiedingen:
        if not is_active_intro_for_aging(aanbieding.get("intro_status")):
            continue

        datum_intro = parse_optional_date(aanbieding.get("datum_intro"))
        if not datum_intro:
            continue

        age_days = (today - datum_intro).days
        nieuwe_status = None
        if age_days >= 32:
            nieuwe_status = "automatisch_afgewezen_langlopende_intro"
        elif age_days >= 14 and aanbieding.get("status") != "latent":
            nieuwe_status = "latent"

        if nieuwe_status:
            update_aanbieding_status(aanbieding["id"], nieuwe_status, datum_intro=datum_intro)


def fetch_candidates(status=None, owner_id=None):
    query = (
        supabase()
        .table("kandidaten")
        .select("*, eigenaar:recruiters(naam)")
        .order("created_at", desc=True)
    )
    if status:
        query = query.eq("status", status)
    if owner_id:
        query = query.eq("eigenaar_id", owner_id)
    return query.execute().data


def fetch_candidate(candidate_id):
    return (
        supabase()
        .table("kandidaten")
        .select("*, eigenaar:recruiters(naam)")
        .eq("id", candidate_id)
        .single()
        .execute()
        .data
    )


def update_candidate_status(candidate_id, status):
    supabase().table("kandidaten").update({"status": status}).eq("id", candidate_id).execute()


def delete_candidate_with_aanbiedingen(candidate_id):
    supabase().table("aanbiedingen").delete().eq("kandidaat_id", candidate_id).execute()
    supabase().table("kandidaten").delete().eq("id", candidate_id).execute()


def fetch_aanbiedingen(candidate_id):
    return (
        supabase()
        .table("aanbiedingen")
        .select(
            "*, "
            "assigned_to:recruiters!aanbiedingen_assigned_to_recruiter_id_fkey(naam), "
            "created_by:recruiters!aanbiedingen_aangeboden_door_id_fkey(naam), "
            "sent_by:recruiters!aanbiedingen_sent_by_recruiter_id_fkey(naam)"
        )
        .eq("kandidaat_id", candidate_id)
        .order("created_at", desc=True)
        .execute()
        .data
    )


def fetch_mijn_aanbiedingen(recruiter_id, alleen_open=True):
    query = (
        supabase()
        .table("aanbiedingen")
        .select(
            "*, candidate:kandidaten(naam), "
            "created_by:recruiters!aanbiedingen_aangeboden_door_id_fkey(naam), "
            "sent_by:recruiters!aanbiedingen_sent_by_recruiter_id_fkey(naam)"
        )
        .eq("assigned_to_recruiter_id", recruiter_id)
        .order("created_at", desc=True)
    )
    if alleen_open:
        query = query.eq("status", "open")
    return query.execute().data


def fetch_alle_aanbiedingen():
    return (
        supabase()
        .table("aanbiedingen")
        .select(
            "*, "
            "candidate:kandidaten(naam), "
            "assigned_to:recruiters!aanbiedingen_assigned_to_recruiter_id_fkey(naam), "
            "sent_by:recruiters!aanbiedingen_sent_by_recruiter_id_fkey(naam)"
        )
        .execute()
        .data
    )


def show_candidates_list(candidates):
    if not candidates:
        st.info("Geen kandidaten gevonden.")
        return

    for candidate in candidates:
        owner = candidate.get("eigenaar") or {}
        with st.container(border=True):
            cols = st.columns([3, 2, 2, 2, 2, 1])
            cols[0].subheader(candidate["naam"])
            cols[1].write(candidate.get("woonplaats") or "-")
            cols[2].write(candidate.get("ervaring_binnen") or "-")
            cols[3].write(candidate.get("reisafstand") or "-")
            cols[4].write(display_recruiter_name(owner.get("naam")))
            st.caption(
                f"Huidige Functie(s): {candidate.get('ervaring_binnen') or '-'} | "
                f"Discipline(s): {candidate.get('disciplines') or '-'} | "
                f"Softwarekennis: {candidate.get('softwarekennis') or '-'} | "
                f"Werktijden: {candidate.get('werktijden') or '-'}"
            )
            if cols[5].button("Open", key=f"open-candidate-{candidate['id']}"):
                st.session_state["selected_candidate_id"] = candidate["id"]
                st.session_state.view = "detail"
                st.rerun()


def candidate_function_groups(candidate):
    functies = split_csv(candidate.get("ervaring_binnen"))
    return [functies[0]] if functies else ["Niet ingevuld"]


def ordered_candidate_groups(candidates):
    groups = {}
    for candidate in candidates:
        for functie in candidate_function_groups(candidate):
            groups.setdefault(functie, [])
            if candidate not in groups[functie]:
                groups[functie].append(candidate)

    fixed_order = ERVARING_BINNEN_OPTIES + ["Niet ingevuld"]
    ordered_names = [name for name in fixed_order if name in groups]
    extra_names = sorted(name for name in groups if name not in fixed_order)
    return [(name, groups[name]) for name in ordered_names + extra_names]


def show_compact_candidate_rows(candidates, key_prefix):
    header = st.columns([1.5, 1.05, 1.45, 1.2, 1, 1.05, 0.75], gap="small")
    labels = [
        "Naam",
        "Woonplaats",
        "Huidige Functie(s)",
        "Discipline(s)",
        "Reisafstand",
        "Werktijden",
        "Actie",
    ]
    for col, label in zip(header, labels):
        col.markdown(f'<div class="crm-table-header"><strong>{label}</strong></div>', unsafe_allow_html=True)

    for candidate in candidates:
        st.markdown('<div class="crm-row"></div>', unsafe_allow_html=True)
        row = st.columns([1.5, 1.05, 1.45, 1.2, 1, 1.05, 0.75], gap="small")
        row[0].write(candidate.get("naam") or "-")
        row[1].write(candidate.get("woonplaats") or "-")
        row[2].write(candidate.get("ervaring_binnen") or "-")
        row[3].write(candidate.get("disciplines") or "-")
        row[4].write(candidate.get("reisafstand") or "-")
        row[5].write(candidate.get("werktijden") or "-")
        if row[6].button("Open", key=f"open-active-{key_prefix}-{candidate['id']}"):
            st.session_state["selected_candidate_id"] = candidate["id"]
            st.session_state.view = "detail"
            st.rerun()


def show_active_candidates_grouped(candidates):
    if not candidates:
        st.info("Geen actieve kandidaten gevonden.")
        return

    for group_name, group_candidates in ordered_candidate_groups(candidates):
        st.subheader(f"{group_name} ({len(group_candidates)})")
        show_compact_candidate_rows(group_candidates, group_name.lower().replace(" ", "-").replace("/", "-"))


def show_add_candidate(current_recruiter):
    st.header("Kandidaat toevoegen")

    with st.form("add_candidate"):
        naam = st.text_input("Naam")
        woonplaats = st.text_input("Woonplaats")
        leeftijd = st.number_input("Leeftijd", min_value=0, max_value=100, value=0)
        opleiding = st.text_input("Opleiding")
        ervaring_binnen = st.multiselect("Huidige Functie(s)", ERVARING_BINNEN_OPTIES)
        disciplines = st.multiselect("Discipline(s)", DISCIPLINE_OPTIES)
        softwarekennis = st.multiselect("Softwarekennis", SOFTWAREKENNIS_OPTIES)
        reisafstand = st.selectbox("Reisafstand", [""] + REISAFSTAND_OPTIES)
        werktijden = st.multiselect("Werktijden", WERKTIJDEN_OPTIES)
        gezochte_functies = st.text_input("Gezochte functie(s)")
        salarisindicatie = st.text_input("Salarisindicatie")
        tarief = st.text_input("Tarief")
        korte_omschrijving = st.text_area("Korte omschrijving")
        cv_link = st.text_input("CV-link")
        submitted = st.form_submit_button("Opslaan")

    if not submitted:
        return
    if not naam:
        st.error("Naam is verplicht.")
        return

    result = (
        supabase()
        .table("kandidaten")
        .insert(
            {
                "naam": naam,
                "woonplaats": woonplaats,
                "leeftijd": leeftijd or None,
                "opleiding": opleiding,
                "ervaring_binnen": join_csv(ervaring_binnen),
                "disciplines": join_csv(disciplines),
                "softwarekennis": join_csv(softwarekennis),
                "reisafstand": reisafstand or None,
                "werktijden": join_csv(werktijden),
                "gezochte_functies": gezochte_functies,
                "salarisindicatie": salarisindicatie,
                "tarief": tarief,
                "korte_omschrijving": korte_omschrijving,
                "eigenaar_id": current_recruiter["id"],
                "status": "Actief",
                "cv_link": cv_link,
            }
        )
        .execute()
    )
    st.success("Kandidaat toegevoegd.")
    st.session_state["selected_candidate_id"] = result.data[0]["id"]
    st.session_state.view = "detail"
    st.rerun()


def show_candidate_details(candidate, current_recruiter):
    owner = candidate.get("eigenaar") or {}
    is_owner = candidate["eigenaar_id"] == current_recruiter["id"]

    st.header(candidate["naam"])
    st.caption(f"Eigenaar: {display_recruiter_name(owner.get('naam'))}")

    st.subheader("Kandidaatprofiel")

    if is_owner:
        with st.form("edit_candidate"):
            naam = st.text_input("Naam", value=candidate.get("naam") or "")
            woonplaats = st.text_input("Woonplaats", value=candidate.get("woonplaats") or "")
            leeftijd = st.number_input(
                "Leeftijd",
                min_value=0,
                max_value=100,
                value=candidate.get("leeftijd") or 0,
            )
            opleiding = st.text_input("Opleiding", value=candidate.get("opleiding") or "")
            ervaring_binnen = st.multiselect(
                "Huidige Functie(s)",
                ERVARING_BINNEN_OPTIES,
                default=[value for value in split_csv(candidate.get("ervaring_binnen")) if value in ERVARING_BINNEN_OPTIES],
            )
            disciplines = st.multiselect(
                "Discipline(s)",
                DISCIPLINE_OPTIES,
                default=[value for value in split_csv(candidate.get("disciplines")) if value in DISCIPLINE_OPTIES],
            )
            softwarekennis = st.multiselect(
                "Softwarekennis",
                SOFTWAREKENNIS_OPTIES,
                default=[value for value in split_csv(candidate.get("softwarekennis")) if value in SOFTWAREKENNIS_OPTIES],
            )
            reisafstand_value = candidate.get("reisafstand") or ""
            reisafstand = st.selectbox(
                "Reisafstand",
                [""] + REISAFSTAND_OPTIES,
                index=([""] + REISAFSTAND_OPTIES).index(reisafstand_value)
                if reisafstand_value in [""] + REISAFSTAND_OPTIES
                else 0,
            )
            werktijden = st.multiselect(
                "Werktijden",
                WERKTIJDEN_OPTIES,
                default=[value for value in split_csv(candidate.get("werktijden")) if value in WERKTIJDEN_OPTIES],
            )
            gezochte_functies = st.text_input(
                "Gezochte functie(s)",
                value=candidate.get("gezochte_functies") or "",
            )
            salarisindicatie = st.text_input(
                "Salarisindicatie",
                value=candidate.get("salarisindicatie") or "",
            )
            tarief = st.text_input("Tarief", value=candidate.get("tarief") or "")
            korte_omschrijving = st.text_area(
                "Korte omschrijving",
                value=candidate.get("korte_omschrijving") or "",
            )
            status = st.selectbox(
                "Status",
                KANDIDAAT_STATUSSEN,
                index=(
                    KANDIDAAT_STATUSSEN.index(candidate["status"])
                    if candidate["status"] in KANDIDAAT_STATUSSEN
                    else 0
                ),
            )
            cv_link = st.text_input("CV-link", value=candidate.get("cv_link") or "")
            submitted = st.form_submit_button("Kandidaat opslaan")

        if submitted:
            supabase().table("kandidaten").update(
                {
                    "naam": naam,
                    "woonplaats": woonplaats,
                    "leeftijd": leeftijd or None,
                    "opleiding": opleiding,
                    "ervaring_binnen": join_csv(ervaring_binnen),
                    "disciplines": join_csv(disciplines),
                    "softwarekennis": join_csv(softwarekennis),
                    "reisafstand": reisafstand or None,
                    "werktijden": join_csv(werktijden),
                    "gezochte_functies": gezochte_functies,
                    "salarisindicatie": salarisindicatie,
                    "tarief": tarief,
                    "korte_omschrijving": korte_omschrijving,
                    "status": status,
                    "cv_link": cv_link,
                }
            ).eq("id", candidate["id"]).execute()
            st.success("Kandidaat bijgewerkt.")
            st.rerun()
    else:
        st.write("**Woonplaats:**", candidate.get("woonplaats") or "-")
        st.write("**Leeftijd:**", candidate.get("leeftijd") or "-")
        st.write("**Opleiding:**", candidate.get("opleiding") or "-")
        st.write("**Huidige Functie(s):**", candidate.get("ervaring_binnen") or "-")
        st.write("**Discipline(s):**", candidate.get("disciplines") or "-")
        st.write("**Softwarekennis:**", candidate.get("softwarekennis") or "-")
        st.write("**Reisafstand:**", candidate.get("reisafstand") or "-")
        st.write("**Werktijden:**", candidate.get("werktijden") or "-")
        st.write("**Gezochte functie(s):**", candidate.get("gezochte_functies") or "-")
        st.write("**Salarisindicatie:**", candidate.get("salarisindicatie") or "-")
        st.write("**Tarief:**", candidate.get("tarief") or "-")
        st.write("**Status:**", candidate.get("status") or "-")
        st.write("**Korte omschrijving:**")
        st.write(candidate.get("korte_omschrijving") or "-")

    if candidate.get("cv_link"):
        st.link_button("CV openen", candidate["cv_link"])

    st.subheader("Status / opslag")
    if candidate.get("status") == "Actief":
        if st.button("Verplaats naar kandidaten opslag"):
            update_candidate_status(candidate["id"], "Kandidaten opslag")
            st.success("Kandidaat verplaatst naar Kandidaten opslag.")
            st.session_state.view = "Kandidaten opslag"
            st.rerun()
    elif candidate.get("status") == "Kandidaten opslag":
        if st.button("Terugzetten naar actieve kandidaten"):
            update_candidate_status(candidate["id"], "Actief")
            st.success("Kandidaat teruggezet naar Actieve kandidaten.")
            st.session_state.view = "Actieve kandidaten"
            st.rerun()

    st.subheader("Gevaarlijke acties")
    st.warning("Definitief verwijderen verwijdert ook alle gekoppelde aanbiedingen.")
    confirmed = st.checkbox(
        "Ik weet zeker dat ik deze kandidaat wil verwijderen",
        key=f"delete-candidate-confirm-{candidate['id']}",
    )
    if confirmed and st.button("Definitief verwijderen", key=f"delete-candidate-{candidate['id']}"):
        target_view = (
            "Kandidaten opslag"
            if candidate.get("status") == "Kandidaten opslag"
            else "Actieve kandidaten"
        )
        delete_candidate_with_aanbiedingen(candidate["id"])
        st.session_state.pop("selected_candidate_id", None)
        st.session_state.pop("candidate_id", None)
        st.session_state.view = target_view
        st.success("Kandidaat definitief verwijderd.")
        st.rerun()


def show_aanbieding_toevoegen(candidate_id, recruiters, current_recruiter):
    st.subheader("Bedrijf toevoegen aan aanbiedingslijst")
    options = recruiter_options(recruiters)

    with st.form("aanbieding_toevoegen"):
        bedrijf = st.text_input("Bedrijf")
        contactpersoon = st.text_input("Contactpersoon")
        tarief = st.text_input("Tarief")
        assigned_name = st.selectbox("Moet gedaan worden door", list(options.keys()))
        opmerking = st.text_area("Opmerking")
        submitted = st.form_submit_button("Toevoegen")

    if not submitted:
        return
    if not bedrijf:
        st.error("Bedrijf is verplicht.")
        return

    supabase().table("aanbiedingen").insert(
        {
            "kandidaat_id": candidate_id,
            "bedrijf": bedrijf,
            "contactpersoon": contactpersoon,
            "tarief": tarief,
            "status": "open",
            "assigned_to_recruiter_id": options[assigned_name],
            "aangeboden_door_id": current_recruiter["id"],
            "opmerking": opmerking,
        }
    ).execute()
    st.success("Bedrijf toegevoegd aan aanbiedingslijst.")
    st.rerun()


def markeer_aanbieding_verstuurd(aanbieding_id, current_recruiter):
    supabase().table("aanbiedingen").update(
        {
            "status": "verstuurd",
            "datum_verstuurd": today_amsterdam().isoformat(),
            "sent_by_recruiter_id": current_recruiter["id"],
        }
    ).eq("id", aanbieding_id).execute()


def update_aanbieding_status(aanbieding_id, status, datum_intro=None, intro_status=None):
    if status == "intro" and not datum_intro:
        return False

    updates = {"status": status}
    if status in INTRO_STATUSSEN and datum_intro:
        if isinstance(datum_intro, date):
            updates["datum_intro"] = datum_intro.isoformat()
        else:
            updates["datum_intro"] = datum_intro
    if status == "intro" and intro_status:
        updates["intro_status"] = intro_status
    supabase().table("aanbiedingen").update(updates).eq("id", aanbieding_id).execute()
    return True


def update_aanbieding_basis(aanbieding_id, contactpersoon, tarief, opmerking, status):
    supabase().table("aanbiedingen").update(
        {
            "contactpersoon": contactpersoon,
            "tarief": tarief,
            "opmerking": opmerking,
            "status": status,
        }
    ).eq("id", aanbieding_id).execute()


def update_aanbieding_details(
    aanbieding_id,
    contactpersoon,
    tarief,
    opmerking,
    status,
    datum_verstuurd=None,
    datum_intro=None,
    laatste_klantreactie=None,
    opvolgdatum=None,
    intro_status=None,
):
    updates = {
        "contactpersoon": contactpersoon,
        "tarief": tarief,
        "opmerking": opmerking,
        "status": status,
        "datum_verstuurd": datum_verstuurd,
        "datum_intro": datum_intro,
        "laatste_klantreactie": laatste_klantreactie,
        "opvolgdatum": opvolgdatum,
    }
    if is_intro_related_status(status):
        updates["intro_status"] = intro_status or "eerste_gesprek"
    else:
        updates["intro_status"] = None

    supabase().table("aanbiedingen").update(updates).eq("id", aanbieding_id).execute()


def verwijder_aanbieding(aanbieding_id):
    supabase().table("aanbiedingen").delete().eq("id", aanbieding_id).execute()


def display_value(value):
    return value if value else "-"


def status_badge(status):
    label = aanbieding_status_label(status)
    css_status = (status or "open").replace(" ", "_")
    return f'<span class="crm-chip crm-chip-{css_status}">{label}</span>'


def kpi_card(label, value, help_text=None):
    help_html = f'<div class="crm-kpi-help">{help_text}</div>' if help_text else ""
    st.markdown(
        f"""
        <div class="crm-kpi-card">
            <div class="crm-kpi-label">{label}</div>
            <div class="crm-kpi-value">{value}</div>
            {help_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def selecteer_aanbieding(aanbieding_id):
    st.session_state["selected_offer_id"] = aanbieding_id


def plan_intro(aanbieding_id):
    st.session_state["intro_planning_offer_id"] = aanbieding_id


def show_intro_planning_form(aanbieding, key_prefix):
    st.markdown('<div class="crm-subcard">', unsafe_allow_html=True)
    st.markdown('<div class="crm-subsection-title">Intro plannen</div>', unsafe_allow_html=True)
    with st.form(f"{key_prefix}-intro-plannen-{aanbieding['id']}"):
        intro_cols = st.columns([1, 1.35, 2.2], gap="small")
        datum_intro = intro_cols[0].date_input(
            "Datum Intro",
            value=parse_optional_date(aanbieding.get("datum_intro")) or today_amsterdam(),
        )
        intro_status = intro_cols[1].selectbox(
            "Introstatus",
            INTRO_STATUSSEN_OPTIES,
            format_func=intro_status_label,
            index=intro_status_index(aanbieding.get("intro_status")),
        )
        form_cols = st.columns([0.95, 0.8, 3], gap="small")
        opslaan = form_cols[0].form_submit_button("Intro opslaan")
        annuleren = form_cols[1].form_submit_button("Annuleren")
    st.markdown("</div>", unsafe_allow_html=True)

    if opslaan:
        update_aanbieding_status(aanbieding["id"], "intro", datum_intro=datum_intro, intro_status=intro_status)
        st.session_state.pop("intro_planning_offer_id", None)
        st.success("Intro opgeslagen.")
        st.rerun()

    if annuleren:
        st.session_state.pop("intro_planning_offer_id", None)
        st.rerun()


def show_aanbieding_actiepanel(aanbieding, current_recruiter, key_prefix, include_open_candidate=False):
    st.markdown('<div class="crm-section"></div>', unsafe_allow_html=True)
    bedrijf = display_value(aanbieding.get("bedrijf"))
    contactpersoon = aanbieding.get("contactpersoon")
    titel = f"Acties voor: {bedrijf}"
    if contactpersoon:
        titel = f"{titel} - {contactpersoon}"

    st.markdown('<div class="crm-action-card">', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f'<div class="crm-panel-title">{titel}</div>', unsafe_allow_html=True)

        st.markdown('<div class="crm-subsection-title">Snelle acties</div>', unsafe_allow_html=True)
        primary_cols = st.columns([0.95, 0.8, 4], gap="small")
        if primary_cols[0].button("Markeer als verstuurd", key=f"{key_prefix}-sent-{aanbieding['id']}"):
            markeer_aanbieding_verstuurd(aanbieding["id"], current_recruiter)
            st.success("Aanbieding gemarkeerd als verstuurd.")
            st.rerun()

        if include_open_candidate:
            if primary_cols[1].button("Open kandidaat", key=f"{key_prefix}-open-candidate-{aanbieding['id']}"):
                st.session_state["selected_candidate_id"] = aanbieding["kandidaat_id"]
                st.session_state.view = "detail"
                st.rerun()

        st.markdown('<div class="crm-subsection-title">Status wijzigen</div>', unsafe_allow_html=True)
        status_options = [
            "intro",
            "latent",
            "afgewezen",
            "teruggetrokken",
            "mismatch",
            "nvt",
            "automatisch_afgewezen_langlopende_intro",
        ]
        status_index = (
            status_options.index(aanbieding.get("status"))
            if aanbieding.get("status") in status_options
            else 0
        )
        status_cols = st.columns([1.55, 0.95, 3.4], gap="small")
        nieuwe_status = status_cols[0].selectbox(
            "Nieuwe status",
            status_options,
            format_func=aanbieding_status_label,
            index=status_index,
            key=f"{key_prefix}-status-select-{aanbieding['id']}",
        )
        if status_cols[1].button("Status opslaan", key=f"{key_prefix}-status-save-{aanbieding['id']}"):
            if nieuwe_status == "intro":
                plan_intro(aanbieding["id"])
                st.rerun()
            update_aanbieding_status(aanbieding["id"], nieuwe_status)
            st.success("Status bijgewerkt.")
            st.rerun()

        if aanbieding["id"] == st.session_state.get("intro_planning_offer_id"):
            show_intro_planning_form(aanbieding, key_prefix)

        st.markdown('<div class="crm-subsection-title">Bewerken</div>', unsafe_allow_html=True)
        with st.form(f"{key_prefix}-edit-{aanbieding['id']}"):
            edit_cols = st.columns(4)
            status = edit_cols[0].selectbox(
                "Aanbiedingstatus",
                AANBIEDING_STATUSSEN,
                format_func=aanbieding_status_label,
                index=aanbieding_status_index(aanbieding.get("status")),
            )
            contactpersoon = edit_cols[1].text_input(
                "Contactpersoon",
                value=aanbieding.get("contactpersoon") or "",
            )
            tarief = edit_cols[2].text_input("Tarief", value=aanbieding.get("tarief") or "")
            datum_verstuurd = edit_cols[3].date_input(
                "Datum verstuurd",
                value=parse_optional_date(aanbieding.get("datum_verstuurd")),
            )
            datum_intro = None
            intro_status = None
            if is_intro_related_status(status) or aanbieding.get("datum_intro"):
                intro_cols = st.columns(2)
                datum_intro = intro_cols[0].date_input(
                    "Datum Intro",
                    value=(
                        parse_optional_date(aanbieding.get("datum_intro"))
                        or (today_amsterdam() if is_intro_related_status(status) else None)
                    ),
                )
                if is_intro_related_status(status):
                    intro_status = intro_cols[1].selectbox(
                        "Introstatus",
                        INTRO_STATUSSEN_OPTIES,
                        format_func=intro_status_label,
                        index=intro_status_index(aanbieding.get("intro_status")),
                    )
            datum_cols = st.columns(2)
            laatste_klantreactie = datum_cols[0].date_input(
                "Laatste klantreactie",
                value=parse_optional_date(aanbieding.get("laatste_klantreactie")),
            )
            opvolgdatum = datum_cols[1].date_input(
                "Opvolgdatum",
                value=parse_optional_date(aanbieding.get("opvolgdatum")),
            )
            opmerking = st.text_area("Opmerking", value=aanbieding.get("opmerking") or "", height=110)
            submitted = st.form_submit_button("Opslaan")

        if submitted:
            if is_intro_related_status(status) and not datum_intro:
                st.error("Kies eerst een Datum Intro.")
                return

            update_aanbieding_details(
                aanbieding["id"],
                contactpersoon,
                tarief,
                opmerking,
                status,
                datum_verstuurd.isoformat() if datum_verstuurd else None,
                datum_intro.isoformat() if datum_intro else None,
                laatste_klantreactie.isoformat() if laatste_klantreactie else None,
                opvolgdatum.isoformat() if opvolgdatum else None,
                intro_status,
            )
            st.success("Aanbieding bijgewerkt.")
            st.rerun()

        st.markdown('<div class="crm-subsection-title">Gevaarlijke actie</div>', unsafe_allow_html=True)
        danger_cols = st.columns([1.7, 1.15, 2.8], gap="small")
        confirm = danger_cols[0].checkbox(
            "Ik weet zeker dat ik deze aanbieding wil verwijderen",
            key=f"{key_prefix}-confirm-delete-{aanbieding['id']}",
        )
        if danger_cols[1].button(
            "Verwijder uit aanbiedingslijst",
            key=f"{key_prefix}-delete-{aanbieding['id']}",
            disabled=not confirm,
        ):
            verwijder_aanbieding(aanbieding["id"])
            st.session_state.pop("selected_offer_id", None)
            st.success("Aanbiedingregel verwijderd.")
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)


def show_aanbieding_opmerking_editor(aanbieding):
    with st.expander("Details bewerken"):
        with st.form(f"opmerking-form-{aanbieding['id']}"):
            contactpersoon = st.text_input(
                "Contactpersoon",
                value=aanbieding.get("contactpersoon") or "",
            )
            tarief = st.text_input("Tarief", value=aanbieding.get("tarief") or "")
            opmerking = st.text_area("Opmerking", value=aanbieding.get("opmerking") or "")
            laatste_klantreactie = st.date_input(
                "Laatste klantreactie",
                value=parse_optional_date(aanbieding.get("laatste_klantreactie")),
            )
            opvolgdatum = st.date_input(
                "Opvolgdatum",
                value=parse_optional_date(aanbieding.get("opvolgdatum")),
            )
            submitted = st.form_submit_button("Opslaan")

        if submitted:
            update_aanbieding_details(
                aanbieding["id"],
                contactpersoon,
                tarief,
                opmerking,
                aanbieding.get("status") or "open",
                aanbieding.get("datum_verstuurd"),
                aanbieding.get("datum_intro"),
                laatste_klantreactie.isoformat() if laatste_klantreactie else None,
                opvolgdatum.isoformat() if opvolgdatum else None,
                aanbieding.get("intro_status"),
            )
            st.success("Aanbieding bijgewerkt.")
            st.rerun()


def show_aanbiedingslijst(candidate_id, recruiters, current_recruiter):
    st.markdown('<div class="crm-section"></div>', unsafe_allow_html=True)
    st.subheader("Aanbiedingslijst")
    aanbiedingen = fetch_aanbiedingen(candidate_id)

    if not aanbiedingen:
        st.info("Nog geen bedrijven op de aanbiedingslijst.")
        return

    header = st.columns([1.45, 1.15, 0.75, 1, 1.1, 1.05, 1.05, 0.85, 0.95, 1.35, 2.15], gap="small")
    labels = [
        "Bedrijf",
        "Contactpersoon",
        "Tarief",
        "Status",
        "Moet doen",
        "Aangemaakt door",
        "Verstuurd door",
        "Verstuurd",
        "Klantreactie",
        "Opmerking",
        "Actie",
    ]
    for col, label in zip(header, labels):
        col.markdown(f'<div class="crm-table-header"><strong>{label}</strong></div>', unsafe_allow_html=True)

    for aanbieding in aanbiedingen:
        assigned_to = aanbieding.get("assigned_to") or {}
        created_by = aanbieding.get("created_by") or {}
        sent_by = aanbieding.get("sent_by") or {}

        st.markdown('<div class="crm-row"></div>', unsafe_allow_html=True)
        row = st.columns([1.45, 1.15, 0.75, 1, 1.1, 1.05, 1.05, 0.85, 0.95, 1.35, 2.15], gap="small")
        row[0].write(display_value(aanbieding.get("bedrijf")))
        row[1].write(display_value(aanbieding.get("contactpersoon")))
        row[2].write(display_value(aanbieding.get("tarief")))
        row[3].markdown(status_badge(aanbieding.get("status")), unsafe_allow_html=True)
        row[4].write(display_value(related_recruiter_name(assigned_to, recruiters, aanbieding.get("assigned_to_recruiter_id"))))
        row[5].write(display_value(related_recruiter_name(created_by, recruiters, aanbieding.get("aangeboden_door_id"))))
        row[6].write(display_value(related_recruiter_name(sent_by, recruiters, aanbieding.get("sent_by_recruiter_id"))))
        row[7].write(display_value(aanbieding.get("datum_verstuurd")))
        row[8].write(display_value(aanbieding.get("laatste_klantreactie")))
        row[9].write(display_value(aanbieding.get("opmerking")))
        with row[10]:
            action_cols = st.columns([1.25, 0.9], gap="small")
            if action_cols[0].button("Verstuurd", key=f"sent-row-detail-{aanbieding['id']}"):
                markeer_aanbieding_verstuurd(aanbieding["id"], current_recruiter)
                st.success("Aanbieding gemarkeerd als verstuurd.")
                st.rerun()
            if action_cols[1].button("Meer", key=f"select-detail-{aanbieding['id']}"):
                selecteer_aanbieding(aanbieding["id"])
                st.rerun()
        if aanbieding["id"] == st.session_state.get("selected_offer_id"):
            show_aanbieding_actiepanel(aanbieding, current_recruiter, "detail")


def show_candidate_page(current_recruiter, recruiters):
    candidate_id = st.session_state.get("selected_candidate_id") or st.session_state.get("candidate_id")
    if not candidate_id:
        st.info("Kies eerst een kandidaat uit de lijst.")
        return

    candidate = fetch_candidate(candidate_id)
    if not candidate:
        st.error("Kandidaat niet gevonden.")
        return

    show_candidate_details(candidate, current_recruiter)
    st.divider()
    show_aanbieding_toevoegen(candidate_id, recruiters, current_recruiter)
    show_aanbiedingslijst(candidate_id, recruiters, current_recruiter)


def show_mijn_aanbieding_acties(aanbieding, current_recruiter):
    show_aanbieding_actiepanel(
        aanbieding,
        current_recruiter,
        "mijn",
        include_open_candidate=True,
    )


def show_mijn_open_aanbiedingen(current_recruiter):
    st.header("Mijn te versturen aanbiedingen")
    toon_alle_statussen = st.checkbox("Toon ook mijn niet-open aanbiedingen")
    aanbiedingen = fetch_mijn_aanbiedingen(
        current_recruiter["id"],
        alleen_open=not toon_alle_statussen,
    )

    if not aanbiedingen:
        st.info("Geen aanbiedingen gevonden.")
        return

    header = st.columns([1.35, 1.35, 0.95, 1, 1.05, 1.05, 1, 1.35, 2.05], gap="small")
    labels = [
        "Bedrijf",
        "Kandidaat",
        "Status",
        "Contactpersoon",
        "Tarief",
        "Verstuurd",
        "Verstuurd door",
        "Opmerking",
        "Actie",
    ]
    for col, label in zip(header, labels):
        col.markdown(f'<div class="crm-table-header"><strong>{label}</strong></div>', unsafe_allow_html=True)

    for aanbieding in aanbiedingen:
        candidate = aanbieding.get("candidate") or {}
        sent_by = aanbieding.get("sent_by") or {}

        st.markdown('<div class="crm-row"></div>', unsafe_allow_html=True)
        row = st.columns([1.35, 1.35, 0.95, 1, 1.05, 1.05, 1, 1.35, 2.05], gap="small")
        row[0].write(display_value(aanbieding.get("bedrijf")))
        row[1].write(display_value(candidate.get("naam")))
        row[2].markdown(status_badge(aanbieding.get("status")), unsafe_allow_html=True)
        row[3].write(display_value(aanbieding.get("contactpersoon")))
        row[4].write(display_value(aanbieding.get("tarief")))
        row[5].write(display_value(aanbieding.get("datum_verstuurd")))
        row[6].write(display_value(display_recruiter_name(sent_by.get("naam"))))
        row[7].write(display_value(aanbieding.get("opmerking")))
        with row[8]:
            action_cols = st.columns([1.25, 0.9], gap="small")
            if action_cols[0].button("Verstuurd", key=f"sent-row-mijn-{aanbieding['id']}"):
                markeer_aanbieding_verstuurd(aanbieding["id"], current_recruiter)
                st.success("Aanbieding gemarkeerd als verstuurd.")
                st.rerun()
            if action_cols[1].button("Meer", key=f"select-mijn-{aanbieding['id']}"):
                selecteer_aanbieding(aanbieding["id"])
                st.rerun()
        if aanbieding["id"] == st.session_state.get("selected_offer_id"):
            show_mijn_aanbieding_acties(aanbieding, current_recruiter)


def count_by_recruiter(recruiters, aanbiedingen, field_name, status=None):
    counts = {recruiter["naam"]: 0 for recruiter in recruiters}
    for aanbieding in aanbiedingen:
        if status and aanbieding.get("status") != status:
            continue
        name = recruiter_name(recruiters, aanbieding.get(field_name))
        if name != "-":
            counts[name] += 1
    return counts


def date_in_window(value, start_dt, end_dt):
    parsed = parse_optional_date(value)
    if not parsed:
        return False
    return start_dt.date() <= parsed < end_dt.date()


def count_by_recruiter_in_window(recruiters, aanbiedingen, field_name, date_field, start_dt, end_dt, statuses=None):
    counts = {recruiter["naam"]: 0 for recruiter in recruiters}
    for aanbieding in aanbiedingen:
        if statuses and aanbieding.get("status") not in statuses:
            continue
        if not date_in_window(aanbieding.get(date_field), start_dt, end_dt):
            continue
        recruiter_id = aanbieding.get(field_name)
        name = recruiter_name(recruiters, recruiter_id)
        if name != "-":
            counts[name] += 1
    return counts


def show_dashboard(recruiters):
    st.header("Dashboard")
    aanbiedingen = fetch_alle_aanbiedingen()
    week_start, week_end = current_week_window_amsterdam()
    month_start, month_end = current_month_window_amsterdam()

    st.subheader("Openstaande Aanbiedingen")
    open_counts = count_by_recruiter(recruiters, aanbiedingen, "assigned_to_recruiter_id", "open")
    st.table([{"Consultant": name, "Aantal": count} for name, count in open_counts.items()])

    st.subheader("Aanbiedingen deze week")
    week_counts = count_by_recruiter_in_window(
        recruiters,
        aanbiedingen,
        "sent_by_recruiter_id",
        "datum_verstuurd",
        week_start,
        week_end,
    )
    kpi_card(
        "Totaal deze week",
        sum(week_counts.values()),
        f"{week_start.strftime('%d-%m-%Y %H:%M')} t/m {week_end.strftime('%d-%m-%Y %H:%M')}",
    )
    st.table([{"Consultant": name, "Aantal": count} for name, count in week_counts.items()])

    st.subheader("Intro's")
    actuele_intros = [
        aanbieding
        for aanbieding in aanbiedingen
        if aanbieding.get("status") in INTRO_STATUSSEN
        and aanbieding.get("datum_intro")
        and is_active_intro_for_aging(aanbieding.get("intro_status"))
    ]
    kpi_card("Totaal actuele intro's", len(actuele_intros))
    st.table(
        [
            {
                "Naam kandidaat": (aanbieding.get("candidate") or {}).get("naam") or "-",
                "Naam klant": aanbieding.get("bedrijf") or "-",
                "Datum Intro": aanbieding.get("datum_intro") or "-",
                "Introstatus": intro_status_label(aanbieding.get("intro_status")),
                "Aanbiedingstatus": aanbieding_status_label(aanbieding.get("status")),
            }
            for aanbieding in actuele_intros
        ]
    )

    st.subheader("Deze maand")
    month_offer_counts = count_by_recruiter_in_window(
        recruiters,
        aanbiedingen,
        "sent_by_recruiter_id",
        "datum_verstuurd",
        month_start,
        month_end,
    )
    month_intro_counts = count_by_recruiter_in_window(
        recruiters,
        aanbiedingen,
        "sent_by_recruiter_id",
        "datum_intro",
        month_start,
        month_end,
        statuses=INTRO_STATUSSEN,
    )
    month_kpis = st.columns(2)
    with month_kpis[0]:
        kpi_card("Totaal aanbiedingen deze maand", sum(month_offer_counts.values()))
    with month_kpis[1]:
        kpi_card("Totaal intro's deze maand", sum(month_intro_counts.values()))
    st.table(
        [
            {
                "Consultant": recruiter["naam"],
                "Totale aanbiedingen deze maand": month_offer_counts.get(recruiter["naam"], 0),
                "Intro's deze maand": month_intro_counts.get(recruiter["naam"], 0),
            }
            for recruiter in recruiters
        ]
    )


def main():
    recruiters = fetch_recruiters()
    if not recruiters:
        st.error("Geen consultants gevonden. Draai eerst het database-schema in Supabase.")
        return

    current_recruiter = require_recruiter_login(recruiters)

    st.title("Kandidaten Beheer")
    st.sidebar.markdown(
        """
        <div class="alpha-sidebar-brand">
            <div class="alpha-sidebar-kicker">ALPHA PRO</div>
            <div class="alpha-sidebar-subtitle">Bemiddelingsboard</div>
            <div class="alpha-sidebar-accent"></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.sidebar.markdown('<div class="consultant-card-label">Consultant</div>', unsafe_allow_html=True)
    consultant_cols = st.sidebar.columns([1.2, 0.85], gap="small")
    consultant_cols[0].markdown(
        f'<div class="consultant-card-name">{current_recruiter["naam"]}</div>',
        unsafe_allow_html=True,
    )
    if consultant_cols[1].button("Uitloggen"):
        logout_recruiter()
    st.sidebar.markdown('<div class="consultant-sidebar-separator"></div>', unsafe_allow_html=True)

    run_intro_status_updates()

    menu_items = [
        "Dashboard",
        "Mijn kandidaten",
        "Actieve kandidaten",
        "Kandidaten opslag",
        "Mijn te versturen aanbiedingen",
        "Kandidaat toevoegen",
    ]
    valid_views = menu_items + ["detail"]

    if "view" not in st.session_state:
        st.session_state.view = "Mijn kandidaten"
    if st.session_state.view == "Alle Kandidaten":
        st.session_state.view = "Actieve kandidaten"
    if st.session_state.view == "Mijn Kandidaten":
        st.session_state.view = "Mijn kandidaten"
    if st.session_state.view == "Kandidaatdetail":
        st.session_state.view = "detail"
    if st.session_state.view not in valid_views:
        st.session_state.view = "Mijn kandidaten"
    if "last_synced_view" not in st.session_state:
        st.session_state.last_synced_view = st.session_state.view
    if "menu_view" not in st.session_state:
        st.session_state.menu_view = (
            st.session_state.view
            if st.session_state.view in menu_items
            else "Mijn kandidaten"
        )
    if st.session_state.menu_view not in menu_items:
        st.session_state.menu_view = "Mijn kandidaten"
    if st.session_state.view != st.session_state.last_synced_view and st.session_state.view in menu_items:
        st.session_state.menu_view = st.session_state.view
    if "last_menu_view" not in st.session_state:
        st.session_state.last_menu_view = st.session_state.menu_view

    st.sidebar.markdown('<div class="sidebar-menu-label">Menu</div>', unsafe_allow_html=True)
    st.sidebar.radio(
        "Menu",
        menu_items,
        key="menu_view",
    )

    if st.session_state.menu_view != st.session_state.last_menu_view:
        st.session_state.view = st.session_state.menu_view
    elif st.session_state.view in menu_items and st.session_state.menu_view != st.session_state.view:
        st.session_state.view = st.session_state.menu_view
    st.session_state.last_menu_view = st.session_state.menu_view
    st.session_state.last_synced_view = st.session_state.view

    if st.session_state.view == "Dashboard":
        show_dashboard(recruiters)
    elif st.session_state.view == "Mijn kandidaten":
        st.header("Mijn kandidaten")
        show_candidates_list(fetch_candidates(status="Actief", owner_id=current_recruiter["id"]))
    elif st.session_state.view == "Actieve kandidaten":
        st.header("Actieve kandidaten")
        show_active_candidates_grouped(fetch_candidates(status="Actief"))
    elif st.session_state.view == "Kandidaten opslag":
        st.header("Kandidaten opslag")
        show_candidates_list(fetch_candidates(status="Kandidaten opslag"))
    elif st.session_state.view == "Mijn te versturen aanbiedingen":
        show_mijn_open_aanbiedingen(current_recruiter)
    elif st.session_state.view == "Kandidaat toevoegen":
        show_add_candidate(current_recruiter)
    elif st.session_state.view == "detail":
        show_candidate_page(current_recruiter, recruiters)


if __name__ == "__main__":
    main()
