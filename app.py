from datetime import date

import streamlit as st
from supabase import create_client


KANDIDAAT_STATUSSEN = ["Actief", "Inactief", "Geplaatst", "Teruggetrokken"]
AANBIEDING_STATUSSEN = ["open", "verstuurd", "intro", "afgewezen", "teruggetrokken"]


st.set_page_config(page_title="Kandidaten Beheer", layout="wide")


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
    return supabase().table("recruiters").select("*").order("naam").execute().data


def recruiter_options(recruiters):
    return {recruiter["naam"]: recruiter["id"] for recruiter in recruiters}


def recruiter_name(recruiters, recruiter_id):
    recruiter = next((r for r in recruiters if r["id"] == recruiter_id), None)
    return recruiter["naam"] if recruiter else "-"


def parse_optional_date(value):
    if not value:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(value)


def fetch_candidates(only_active=True, owner_id=None):
    query = (
        supabase()
        .table("kandidaten")
        .select("*, eigenaar:recruiters(naam)")
        .order("created_at", desc=True)
    )
    if only_active:
        query = query.eq("status", "Actief")
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


def fetch_mijn_open_aanbiedingen(recruiter_id):
    return (
        supabase()
        .table("aanbiedingen")
        .select(
            "*, candidate:kandidaten(naam), "
            "created_by:recruiters!aanbiedingen_aangeboden_door_id_fkey(naam)"
        )
        .eq("assigned_to_recruiter_id", recruiter_id)
        .eq("status", "open")
        .order("created_at", desc=True)
        .execute()
        .data
    )


def fetch_alle_aanbiedingen():
    return (
        supabase()
        .table("aanbiedingen")
        .select(
            "*, "
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
            cols = st.columns([3, 2, 2, 2, 1])
            cols[0].subheader(candidate["naam"])
            cols[1].write(candidate.get("woonplaats") or "-")
            cols[2].write(candidate.get("gezochte_functies") or "-")
            cols[3].write(owner.get("naam") or "-")
            if cols[4].button("Open", key=f"open-candidate-{candidate['id']}"):
                st.session_state.candidate_id = candidate["id"]
                st.session_state.view = "Kandidaatdetail"
                st.rerun()


def show_add_candidate(current_recruiter):
    st.header("Kandidaat toevoegen")

    with st.form("add_candidate"):
        naam = st.text_input("Naam")
        woonplaats = st.text_input("Woonplaats")
        leeftijd = st.number_input("Leeftijd", min_value=0, max_value=100, value=0)
        opleiding = st.text_input("Opleiding")
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
    st.session_state.candidate_id = result.data[0]["id"]
    st.session_state.view = "Kandidaatdetail"
    st.rerun()


def show_candidate_details(candidate, current_recruiter):
    owner = candidate.get("eigenaar") or {}
    is_owner = candidate["eigenaar_id"] == current_recruiter["id"]

    st.header(candidate["naam"])
    st.caption(f"Eigenaar: {owner.get('naam', '-')}")

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
                index=KANDIDAAT_STATUSSEN.index(candidate["status"]),
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
        st.write("**Gezochte functie(s):**", candidate.get("gezochte_functies") or "-")
        st.write("**Salarisindicatie:**", candidate.get("salarisindicatie") or "-")
        st.write("**Tarief:**", candidate.get("tarief") or "-")
        st.write("**Status:**", candidate.get("status") or "-")
        st.write("**Korte omschrijving:**")
        st.write(candidate.get("korte_omschrijving") or "-")

    if candidate.get("cv_link"):
        st.link_button("CV openen", candidate["cv_link"])


def show_aanbieding_toevoegen(candidate_id, recruiters, current_recruiter):
    st.subheader("Bedrijf toevoegen aan aanbiedingslijst")
    options = recruiter_options(recruiters)

    with st.form("aanbieding_toevoegen"):
        bedrijf = st.text_input("Bedrijf")
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
            "datum_verstuurd": date.today().isoformat(),
            "sent_by_recruiter_id": current_recruiter["id"],
        }
    ).eq("id", aanbieding_id).execute()


def update_aanbieding_status(aanbieding_id, status):
    supabase().table("aanbiedingen").update({"status": status}).eq("id", aanbieding_id).execute()


def show_aanbieding_opmerking_editor(aanbieding):
    with st.expander("Opmerking aanpassen"):
        with st.form(f"opmerking-form-{aanbieding['id']}"):
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
            supabase().table("aanbiedingen").update(
                {
                    "opmerking": opmerking,
                    "laatste_klantreactie": (
                        laatste_klantreactie.isoformat() if laatste_klantreactie else None
                    ),
                    "opvolgdatum": opvolgdatum.isoformat() if opvolgdatum else None,
                }
            ).eq("id", aanbieding["id"]).execute()
            st.success("Opmerking bijgewerkt.")
            st.rerun()


def show_aanbiedingslijst(candidate_id, recruiters, current_recruiter):
    st.subheader("Aanbiedingslijst")
    aanbiedingen = fetch_aanbiedingen(candidate_id)

    if not aanbiedingen:
        st.info("Nog geen bedrijven op de aanbiedingslijst.")
        return

    header = st.columns([2, 1, 2, 2, 2, 1, 2, 2, 3])
    labels = [
        "Bedrijf",
        "Status",
        "Moet gedaan worden door",
        "Aangemaakt door",
        "Verstuurd door",
        "Datum verstuurd",
        "Laatste klantreactie",
        "Opmerking",
        "Acties",
    ]
    for col, label in zip(header, labels):
        col.write(f"**{label}**")

    for aanbieding in aanbiedingen:
        assigned_to = aanbieding.get("assigned_to") or {}
        created_by = aanbieding.get("created_by") or {}
        sent_by = aanbieding.get("sent_by") or {}

        row = st.columns([2, 1, 2, 2, 2, 1, 2, 2, 3])
        row[0].write(aanbieding.get("bedrijf") or "-")
        row[1].write(aanbieding.get("status") or "-")
        row[2].write(
            assigned_to.get("naam")
            or recruiter_name(recruiters, aanbieding.get("assigned_to_recruiter_id"))
        )
        row[3].write(created_by.get("naam") or recruiter_name(recruiters, aanbieding.get("aangeboden_door_id")))
        row[4].write(sent_by.get("naam") or recruiter_name(recruiters, aanbieding.get("sent_by_recruiter_id")))
        row[5].write(aanbieding.get("datum_verstuurd") or "-")
        row[6].write(aanbieding.get("laatste_klantreactie") or "-")
        row[7].write(aanbieding.get("opmerking") or "-")

        with row[8]:
            if aanbieding["status"] == "open":
                if st.button("Markeer als verstuurd", key=f"verstuurd-{aanbieding['id']}"):
                    markeer_aanbieding_verstuurd(aanbieding["id"], current_recruiter)
                    st.success("Aanbieding gemarkeerd als verstuurd.")
                    st.rerun()

            action_cols = st.columns(3)
            for action_col, status in zip(action_cols, ["intro", "afgewezen", "teruggetrokken"]):
                if action_col.button(status, key=f"{status}-{aanbieding['id']}"):
                    update_aanbieding_status(aanbieding["id"], status)
                    st.success("Status bijgewerkt.")
                    st.rerun()

        show_aanbieding_opmerking_editor(aanbieding)


def show_candidate_page(current_recruiter, recruiters):
    candidate_id = st.session_state.get("candidate_id")
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


def show_mijn_open_aanbiedingen(current_recruiter):
    st.header("Mijn te versturen aanbiedingen")
    aanbiedingen = fetch_mijn_open_aanbiedingen(current_recruiter["id"])

    if not aanbiedingen:
        st.info("Je hebt geen open aanbiedingen om te versturen.")
        return

    for aanbieding in aanbiedingen:
        candidate = aanbieding.get("candidate") or {}
        created_by = aanbieding.get("created_by") or {}
        with st.container(border=True):
            cols = st.columns([2, 2, 2, 2])
            cols[0].write(f"**{aanbieding.get('bedrijf') or '-'}**")
            cols[1].write(f"Kandidaat: {candidate.get('naam') or '-'}")
            cols[2].write(f"Aangemaakt door: {created_by.get('naam') or '-'}")
            if cols[3].button("Markeer als verstuurd", key=f"mijn-verstuurd-{aanbieding['id']}"):
                markeer_aanbieding_verstuurd(aanbieding["id"], current_recruiter)
                st.success("Aanbieding gemarkeerd als verstuurd.")
                st.rerun()

            if st.button("Open kandidaat", key=f"mijn-open-kandidaat-{aanbieding['id']}"):
                st.session_state.candidate_id = aanbieding["kandidaat_id"]
                st.session_state.view = "Kandidaatdetail"
                st.rerun()


def count_by_recruiter(recruiters, aanbiedingen, field_name, status=None):
    counts = {recruiter["naam"]: 0 for recruiter in recruiters}
    for aanbieding in aanbiedingen:
        if status and aanbieding.get("status") != status:
            continue
        name = recruiter_name(recruiters, aanbieding.get(field_name))
        if name != "-":
            counts[name] += 1
    return counts


def count_sent_by_recruiter(recruiters, aanbiedingen):
    counts = {recruiter["naam"]: 0 for recruiter in recruiters}
    for aanbieding in aanbiedingen:
        if not aanbieding.get("sent_by_recruiter_id"):
            continue
        name = recruiter_name(recruiters, aanbieding["sent_by_recruiter_id"])
        if name != "-":
            counts[name] += 1
    return counts


def show_dashboard(recruiters):
    st.header("Dashboard")
    aanbiedingen = fetch_alle_aanbiedingen()

    sections = [
        (
            "Open te versturen aanbiedingen per recruiter",
            count_by_recruiter(recruiters, aanbiedingen, "assigned_to_recruiter_id", "open"),
        ),
        (
            "Verstuurde aanbiedingen per recruiter",
            count_sent_by_recruiter(recruiters, aanbiedingen),
        ),
        (
            "Intro's per recruiter",
            count_by_recruiter(recruiters, aanbiedingen, "sent_by_recruiter_id", "intro"),
        ),
    ]

    for title, counts in sections:
        st.subheader(title)
        st.table([{"Recruiter": name, "Aantal": count} for name, count in counts.items()])


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

    menu_items = [
        "Mijn Kandidaten",
        "Alle Kandidaten",
        "Kandidaat toevoegen",
        "Kandidaatdetail",
        "Mijn te versturen aanbiedingen",
        "Dashboard",
    ]

    if "view" not in st.session_state:
        st.session_state.view = "Mijn Kandidaten"

    st.sidebar.divider()
    st.session_state.view = st.sidebar.radio(
        "Menu",
        menu_items,
        index=menu_items.index(st.session_state.view),
    )

    if st.session_state.view == "Mijn Kandidaten":
        st.header("Mijn Kandidaten")
        show_candidates_list(fetch_candidates(only_active=False, owner_id=current_recruiter["id"]))
    elif st.session_state.view == "Alle Kandidaten":
        st.header("Alle actieve kandidaten")
        show_candidates_list(fetch_candidates(only_active=True))
    elif st.session_state.view == "Kandidaat toevoegen":
        show_add_candidate(current_recruiter)
    elif st.session_state.view == "Kandidaatdetail":
        show_candidate_page(current_recruiter, recruiters)
    elif st.session_state.view == "Mijn te versturen aanbiedingen":
        show_mijn_open_aanbiedingen(current_recruiter)
    elif st.session_state.view == "Dashboard":
        show_dashboard(recruiters)


if __name__ == "__main__":
    main()
