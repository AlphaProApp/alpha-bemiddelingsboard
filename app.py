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
APP_TZ = ZoneInfo("Europe/Amsterdam")
VERBORGEN_RECRUITER_NAMEN = {"Recruiter 3"}


st.set_page_config(page_title="Kandidaten Beheer", layout="wide")

st.markdown(
    """
    <style>
    .block-container { padding-top: 1.4rem; padding-bottom: 2rem; }
    h1, h2, h3 { letter-spacing: 0; }
    div[data-testid="stVerticalBlock"] { gap: 0.45rem; }
    div[data-testid="stHorizontalBlock"] { gap: 0.65rem; }
    div[data-testid="stExpander"] details { border-radius: 6px; }
    div[data-testid="stExpander"] summary { font-size: 0.9rem; }
    .crm-section {
        border-top: 1px solid #e5e7eb;
        padding-top: 0.85rem;
        margin-top: 1rem;
    }
    .crm-row {
        border-bottom: 1px solid #edf0f2;
        padding: 0.35rem 0;
        font-size: 0.9rem;
    }
    .crm-muted { color: #667085; font-size: 0.82rem; }
    .crm-chip {
        display: inline-block;
        border: 1px solid #d0d5dd;
        border-radius: 999px;
        padding: 0.08rem 0.45rem;
        font-size: 0.78rem;
        font-weight: 600;
        background: #f8fafc;
        white-space: nowrap;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def require_authentication():
    if st.session_state.get("authenticated"):
        return

    st.title("Alpha Bemiddelingsboard")
    password = st.text_input("Wachtwoord", type="password")

    if st.button("Inloggen"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state["authenticated"] = True
            st.rerun()
        else:
            st.error("Onjuist wachtwoord")

    st.stop()


@st.cache_resource
def get_supabase():
    return create_client(st.secrets["SUPABASE_URL"], st.secrets["SUPABASE_KEY"])


def supabase():
    return get_supabase()


def fetch_recruiters():
    recruiters = supabase().table("recruiters").select("*").order("naam").execute().data
    return [recruiter for recruiter in recruiters if is_visible_recruiter(recruiter)]


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


def run_intro_status_updates():
    aanbiedingen = (
        supabase()
        .table("aanbiedingen")
        .select("id, status, datum_intro")
        .in_("status", ["intro", "latent"])
        .execute()
        .data
    )
    today = today_amsterdam()

    for aanbieding in aanbiedingen:
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


def update_aanbieding_status(aanbieding_id, status, datum_intro=None):
    if status == "intro" and not datum_intro:
        return False

    updates = {"status": status}
    if status in INTRO_STATUSSEN and datum_intro:
        if isinstance(datum_intro, date):
            updates["datum_intro"] = datum_intro.isoformat()
        else:
            updates["datum_intro"] = datum_intro
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
):
    supabase().table("aanbiedingen").update(
        {
            "contactpersoon": contactpersoon,
            "tarief": tarief,
            "opmerking": opmerking,
            "status": status,
            "datum_verstuurd": datum_verstuurd,
            "datum_intro": datum_intro,
            "laatste_klantreactie": laatste_klantreactie,
            "opvolgdatum": opvolgdatum,
        }
    ).eq("id", aanbieding_id).execute()


def verwijder_aanbieding(aanbieding_id):
    supabase().table("aanbiedingen").delete().eq("id", aanbieding_id).execute()


def display_value(value):
    return value if value else "-"


def status_badge(status):
    label = aanbieding_status_label(status)
    return f'<span class="crm-chip">{label}</span>'


def selecteer_aanbieding(aanbieding_id):
    st.session_state["selected_offer_id"] = aanbieding_id


def plan_intro(aanbieding_id):
    st.session_state["intro_planning_offer_id"] = aanbieding_id


def show_intro_planning_form(aanbieding, key_prefix):
    st.markdown("**Intro plannen**")
    with st.form(f"{key_prefix}-intro-plannen-{aanbieding['id']}"):
        datum_intro = st.date_input(
            "Datum Intro",
            value=parse_optional_date(aanbieding.get("datum_intro")) or today_amsterdam(),
        )
        form_cols = st.columns([1, 1, 3])
        opslaan = form_cols[0].form_submit_button("Intro opslaan")
        annuleren = form_cols[1].form_submit_button("Annuleren")

    if opslaan:
        update_aanbieding_status(aanbieding["id"], "intro", datum_intro=datum_intro)
        st.session_state.pop("intro_planning_offer_id", None)
        st.success("Intro opgeslagen.")
        st.rerun()

    if annuleren:
        st.session_state.pop("intro_planning_offer_id", None)
        st.rerun()


def show_aanbieding_actiepanel(aanbieding, current_recruiter, key_prefix, include_open_candidate=False):
    st.markdown('<div class="crm-section"></div>', unsafe_allow_html=True)
    titel = f"Acties voor: {display_value(aanbieding.get('bedrijf'))} — {display_value(aanbieding.get('contactpersoon'))}"
    st.subheader(titel)

    primary_cols = st.columns([1.2, 1])
    if primary_cols[0].button("Markeer als verstuurd", key=f"{key_prefix}-sent-{aanbieding['id']}"):
        markeer_aanbieding_verstuurd(aanbieding["id"], current_recruiter)
        st.success("Aanbieding gemarkeerd als verstuurd.")
        st.rerun()

    if include_open_candidate:
        if primary_cols[1].button("Open kandidaat", key=f"{key_prefix}-open-candidate-{aanbieding['id']}"):
            st.session_state["selected_candidate_id"] = aanbieding["kandidaat_id"]
            st.session_state.view = "detail"
            st.rerun()

    status_cols = st.columns(3)
    status_actions = [
        "intro",
        "latent",
        "automatisch_afgewezen_langlopende_intro",
        "afgewezen",
        "teruggetrokken",
        "mismatch",
        "nvt",
    ]
    for index, status in enumerate(status_actions):
        col = status_cols[index % len(status_cols)]
        if col.button(aanbieding_status_label(status), key=f"{key_prefix}-status-{status}-{aanbieding['id']}"):
            if status == "intro":
                plan_intro(aanbieding["id"])
                st.rerun()
            update_aanbieding_status(aanbieding["id"], status)
            st.success("Status bijgewerkt.")
            st.rerun()

    if aanbieding["id"] == st.session_state.get("intro_planning_offer_id"):
        show_intro_planning_form(aanbieding, key_prefix)

    with st.form(f"{key_prefix}-edit-{aanbieding['id']}"):
        edit_cols = st.columns(5)
        status = edit_cols[0].selectbox(
            "Status",
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
        datum_intro = edit_cols[4].date_input(
            "Datum Intro",
            value=(
                parse_optional_date(aanbieding.get("datum_intro"))
                or (today_amsterdam() if aanbieding.get("status") in INTRO_STATUSSEN else None)
            ),
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
        if status in INTRO_STATUSSEN and not datum_intro:
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
        )
        st.success("Aanbieding bijgewerkt.")
        st.rerun()

    st.markdown("**Gevaarlijke actie**")
    danger_cols = st.columns([1.5, 2])
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

    header = st.columns([1.5, 1.2, 0.8, 1, 1.2, 1.1, 1.1, 0.9, 1, 1.6, 1.5])
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
        col.markdown(f"**{label}**")

    for aanbieding in aanbiedingen:
        assigned_to = aanbieding.get("assigned_to") or {}
        created_by = aanbieding.get("created_by") or {}
        sent_by = aanbieding.get("sent_by") or {}

        st.markdown('<div class="crm-row"></div>', unsafe_allow_html=True)
        row = st.columns([1.5, 1.2, 0.8, 1, 1.2, 1.1, 1.1, 0.9, 1, 1.6, 1.5])
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
            action_cols = st.columns(2)
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

    header = st.columns([1.4, 1.4, 1, 1, 1.2, 1.2, 1, 1.5, 1.5])
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
        col.markdown(f"**{label}**")

    for aanbieding in aanbiedingen:
        candidate = aanbieding.get("candidate") or {}
        sent_by = aanbieding.get("sent_by") or {}

        st.markdown('<div class="crm-row"></div>', unsafe_allow_html=True)
        row = st.columns([1.4, 1.4, 1, 1, 1.2, 1.2, 1, 1.5, 1.5])
        row[0].write(display_value(aanbieding.get("bedrijf")))
        row[1].write(display_value(candidate.get("naam")))
        row[2].markdown(status_badge(aanbieding.get("status")), unsafe_allow_html=True)
        row[3].write(display_value(aanbieding.get("contactpersoon")))
        row[4].write(display_value(aanbieding.get("tarief")))
        row[5].write(display_value(aanbieding.get("datum_verstuurd")))
        row[6].write(display_value(display_recruiter_name(sent_by.get("naam"))))
        row[7].write(display_value(aanbieding.get("opmerking")))
        with row[8]:
            action_cols = st.columns(2)
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
    st.table([{"Recruiter": name, "Aantal": count} for name, count in open_counts.items()])

    st.subheader("Aanbiedingen deze week")
    week_counts = count_by_recruiter_in_window(
        recruiters,
        aanbiedingen,
        "sent_by_recruiter_id",
        "datum_verstuurd",
        week_start,
        week_end,
    )
    st.metric("Totaal deze week", sum(week_counts.values()))
    st.caption(
        f"Weekperiode: {week_start.strftime('%d-%m-%Y %H:%M')} t/m {week_end.strftime('%d-%m-%Y %H:%M')}"
    )
    st.table([{"Recruiter": name, "Aantal": count} for name, count in week_counts.items()])

    st.subheader("Intro's")
    actuele_intros = [aanbieding for aanbieding in aanbiedingen if aanbieding.get("status") in INTRO_STATUSSEN]
    st.metric("Totaal actuele intro's", len(actuele_intros))
    st.table(
        [
            {
                "Naam kandidaat": (aanbieding.get("candidate") or {}).get("naam") or "-",
                "Naam klant": aanbieding.get("bedrijf") or "-",
                "Datum Intro": aanbieding.get("datum_intro") or "-",
                "Status": aanbieding_status_label(aanbieding.get("status")),
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
    st.metric("Totaal aanbiedingen deze maand", sum(month_offer_counts.values()))
    st.metric("Totaal intro's deze maand", sum(month_intro_counts.values()))
    st.table(
        [
            {
                "Recruiter": recruiter["naam"],
                "Totale aanbiedingen deze maand": month_offer_counts.get(recruiter["naam"], 0),
                "Intro's deze maand": month_intro_counts.get(recruiter["naam"], 0),
            }
            for recruiter in recruiters
        ]
    )


def main():
    require_authentication()

    st.title("Kandidaten Beheer")

    recruiters = fetch_recruiters()
    if not recruiters:
        st.error("Geen recruiters gevonden. Draai eerst het database-schema in Supabase.")
        return

    recruiter_names = [r["naam"] for r in recruiters]
    selected_name = st.sidebar.selectbox("Recruiter", recruiter_names)
    current_recruiter = next(r for r in recruiters if r["naam"] == selected_name)

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

    st.sidebar.divider()
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
        show_candidates_list(fetch_candidates(status="Actief"))
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
