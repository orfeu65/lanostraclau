"""Pàgina de calendari d'estades."""
import streamlit as st
import calendar as cal_mod
from streamlit_calendar import calendar
from datetime import date, datetime, timezone, timedelta
from typing import Optional
from serveis.auth import obtenir_usuari_actual


def mostrar(supabase) -> None:
    st.title("📅 Calendari d'estades")

    usuari = obtenir_usuari_actual()
    usuari_id, familia_id, es_admin = _obtenir_usuari_info(supabase, usuari)

    # Inicialitzem l'estat de sessió si cal
    for clau in ("cal_accio", "cal_inici", "cal_fi", "cal_estada_id"):
        if clau not in st.session_state:
            st.session_state[clau] = None

    estades = _obtenir_estades(supabase)
    events  = _estades_a_events(estades)

    tab_mensual, tab_anual = st.tabs(["Mensual", "Anual"])

    with tab_mensual:
        opcions = {
            "initialView": "dayGridMonth",
            "selectable": True,
            "selectMirror": True,
            "unselectAuto": False,
            "locale": "ca",
            "timeZone": "local",
            "firstDay": 1,
            "headerToolbar": {
                "left":   "prev,next today",
                "center": "title",
                "right":  "",
            },
            "buttonText": {"today": "avui"},
            "height": 480,
            "eventDisplay": "block",
            "displayEventTime": False,
        }
        resultat = calendar(events=events, options=opcions, key="calendari_principal")

    with tab_anual:
        if "cal_any" not in st.session_state:
            st.session_state.cal_any = date.today().year

        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("←", key="any_prev"):
                st.session_state.cal_any -= 1
                st.rerun()
        with c2:
            st.markdown(
                f"<p style='text-align:center;font-size:18px;font-weight:500;"
                f"margin:0;padding:4px 0'>{st.session_state.cal_any}</p>",
                unsafe_allow_html=True,
            )
        with c3:
            if st.button("→", key="any_next"):
                st.session_state.cal_any += 1
                st.rerun()

        st.markdown(
            _calendari_anual_html(estades, st.session_state.cal_any),
            unsafe_allow_html=True,
        )

        # Llegenda
        families_vistes = {}
        for e in estades:
            f = e.get("families") or {}
            if f.get("nom") and f["nom"] not in families_vistes:
                families_vistes[f["nom"]] = f.get("color", "#888")
        if families_vistes:
            llegenda = " &nbsp; ".join(
                f'<span style="display:inline-block;width:12px;height:12px;'
                f'background:{color};border-radius:2px;margin-right:4px;vertical-align:middle;"></span>{nom}'
                for nom, color in families_vistes.items()
            )
            st.markdown(f"<p style='margin-top:12px;font-size:13px'>{llegenda}</p>", unsafe_allow_html=True)

    # Processem el callback del calendari
    if resultat:
        callback = resultat.get("callback")

        if callback == "select":
            info  = resultat.get("select", {})
            inici = _parse_data(info.get("start", ""))
            fi_ex = _parse_data(info.get("end",   ""))
            # FullCalendar retorna end exclusiu en events all-day: restem 1 dia
            fi = (date.fromisoformat(fi_ex) - timedelta(days=1)).isoformat() if fi_ex else inici
            st.session_state.cal_accio    = "crear"
            st.session_state.cal_inici    = inici
            st.session_state.cal_fi       = fi
            st.session_state.cal_estada_id = None

        elif callback == "eventClick":
            event = resultat.get("eventClick", {}).get("event", {})
            st.session_state.cal_accio    = "editar"
            st.session_state.cal_estada_id = event.get("id")
            st.session_state.cal_inici    = None
            st.session_state.cal_fi       = None

    st.divider()

    accio = st.session_state.cal_accio

    if accio == "crear":
        _formulari_crear(supabase, usuari_id, familia_id, estades)

    elif accio == "editar" and st.session_state.cal_estada_id:
        estada = next((e for e in estades if e["id"] == st.session_state.cal_estada_id), None)
        if estada:
            _formulari_editar(supabase, estada, usuari_id, familia_id, es_admin, estades)
        else:
            st.session_state.cal_accio = None


# --- Formularis ---

def _formulari_crear(supabase, usuari_id, familia_id, estades) -> None:
    """Formulari per crear una nova estada."""
    st.subheader("Nova estada")

    inici_default = date.fromisoformat(st.session_state.cal_inici) if st.session_state.cal_inici else date.today()
    fi_default    = date.fromisoformat(st.session_state.cal_fi)    if st.session_state.cal_fi    else date.today()

    with st.form("crear_estada"):
        col1, col2 = st.columns(2)
        with col1:
            data_inici = st.date_input("Data d'inici", value=inici_default)
        with col2:
            data_fi = st.date_input("Data de fi", value=fi_default)
        comentari = st.text_input("Comentari (opcional)", placeholder="Qui hi va, convidats, notes...")

        col_desa, col_cancel = st.columns(2)
        with col_desa:
            enviat = st.form_submit_button("Crear estada", use_container_width=True)
        with col_cancel:
            cancel = st.form_submit_button("Cancel·lar", use_container_width=True)

    if cancel:
        st.session_state.cal_accio = None
        st.rerun()

    if enviat:
        if data_fi < data_inici:
            st.error("La data de fi no pot ser anterior a la d'inici.")
        elif not usuari_id or not familia_id:
            st.error("No s'ha pogut identificar l'usuari o la família.")
        else:
            solapament = _comprova_solapament(estades, data_inici, data_fi)
            if solapament:
                familia_sol = (solapament.get("families") or {}).get("nom", "una altra família")
                st.error(
                    f"Les dates se solapen amb una estada de {familia_sol} "
                    f"({_fmt(solapament['data_inici'])} — {_fmt(solapament['data_fi'])})."
                )
            else:
                _desar_estada_nova(supabase, usuari_id, familia_id, data_inici, data_fi, comentari)


def _formulari_editar(supabase, estada, usuari_id, familia_id, es_admin, estades) -> None:
    """Formulari per editar o eliminar una estada existent."""
    familia_nom = (estada.get("families") or {}).get("nom", "—")
    responsable = (estada.get("usuaris") or {}).get("nom", "—")

    # Comprovem si l'usuari pot editar aquesta estada
    pot_editar = es_admin or (estada.get("creada_per") == usuari_id)

    st.subheader(f"Estada de la {familia_nom}")
    st.caption(f"Responsable: {responsable}")

    if not pot_editar:
        st.info("Només pots editar les teves pròpies estades.")
        if st.button("Tancar"):
            st.session_state.cal_accio = None
            st.rerun()
        return

    with st.form("editar_estada"):
        col1, col2 = st.columns(2)
        with col1:
            data_inici = st.date_input("Data d'inici", value=date.fromisoformat(estada["data_inici"]))
        with col2:
            data_fi = st.date_input("Data de fi", value=date.fromisoformat(estada["data_fi"]))
        comentari = st.text_input("Comentari (opcional)", value=estada.get("comentari") or "")

        col_desa, col_elimina, col_cancel = st.columns(3)
        with col_desa:
            desa    = st.form_submit_button("Desar",    use_container_width=True)
        with col_elimina:
            elimina = st.form_submit_button("Eliminar", use_container_width=True)
        with col_cancel:
            cancel  = st.form_submit_button("Cancel·lar", use_container_width=True)

    if cancel:
        st.session_state.cal_accio = None
        st.rerun()

    if elimina:
        _eliminar_estada(supabase, estada["id"])

    if desa:
        if data_fi < data_inici:
            st.error("La data de fi no pot ser anterior a la d'inici.")
        else:
            altres = [e for e in estades if e["id"] != estada["id"]]
            solapament = _comprova_solapament(altres, data_inici, data_fi)
            if solapament:
                familia_sol = (solapament.get("families") or {}).get("nom", "una altra família")
                st.error(
                    f"Les dates se solapen amb una estada de {familia_sol} "
                    f"({_fmt(solapament['data_inici'])} — {_fmt(solapament['data_fi'])})."
                )
            else:
                _actualitzar_estada(supabase, estada["id"], data_inici, data_fi, comentari)


# --- Operacions de base de dades ---

def _desar_estada_nova(supabase, usuari_id, familia_id, data_inici, data_fi, comentari) -> None:
    try:
        res = supabase.table("estades").insert({
            "familia_id":      familia_id,
            "responsable_id":  usuari_id,
            "data_inici":      data_inici.isoformat(),
            "data_fi":         data_fi.isoformat(),
            "comentari":       comentari or None,
            "creada_per":      usuari_id,
            "creada_quan":     datetime.now(timezone.utc).isoformat(),
            "modificada_quan": datetime.now(timezone.utc).isoformat(),
        }).execute()
        nova_id = res.data[0]["id"] if res.data else None
        st.session_state.cal_accio     = "editar"
        st.session_state.cal_estada_id = nova_id
        st.rerun()
    except Exception as e:
        st.error(f"Error creant l'estada: {e}")


def _actualitzar_estada(supabase, estada_id, data_inici, data_fi, comentari) -> None:
    try:
        supabase.table("estades").update({
            "data_inici":      data_inici.isoformat(),
            "data_fi":         data_fi.isoformat(),
            "comentari":       comentari or None,
            "modificada_quan": datetime.now(timezone.utc).isoformat(),
        }).eq("id", estada_id).execute()
        st.success("Estada actualitzada.")
        st.session_state.cal_accio = None
        st.rerun()
    except Exception as e:
        st.error(f"Error actualitzant l'estada: {e}")


def _eliminar_estada(supabase, estada_id) -> None:
    try:
        supabase.table("estades").delete().eq("id", estada_id).execute()
        st.success("Estada eliminada.")
        st.session_state.cal_accio = None
        st.rerun()
    except Exception as e:
        st.error(f"Error eliminant l'estada: {e}")


# --- Consultes ---

def _obtenir_estades(supabase) -> list:
    try:
        res = (
            supabase.table("estades")
            .select("*, families(nom, color), usuaris!responsable_id(nom)")
            .order("data_inici")
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def _obtenir_usuari_info(supabase, usuari) -> tuple:
    if not usuari:
        return None, None, False
    try:
        email = usuari.email if hasattr(usuari, "email") else usuari.get("email")
        res = (
            supabase.table("usuaris")
            .select("id, familia_id, es_admin")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        if res and res.data:
            return res.data["id"], res.data["familia_id"], res.data.get("es_admin", False)
    except Exception:
        pass
    return None, None, False


# --- Utilitats ---

def _estades_a_events(estades: list) -> list:
    """Converteix estades de BD a events de FullCalendar."""
    events = []
    for e in estades:
        familia = e.get("families") or {}
        responsable = e.get("usuaris") or {}
        # FullCalendar end és exclusiu per a events all-day: sumem 1 dia
        fi_exclusiu = (
            date.fromisoformat(e["data_fi"]) + timedelta(days=1)
        ).isoformat()
        events.append({
            "id":    e["id"],
            "title": f"{familia.get('nom', '—')} · {responsable.get('nom', '—')}",
            "start": e["data_inici"],
            "end":   fi_exclusiu,
            "color": familia.get("color", "#888888"),
        })
    return events


def _comprova_solapament(estades: list, inici: date, fi: date) -> Optional[dict]:
    """Retorna la primera estada que se solapa amb el rang donat, o None."""
    for e in estades:
        e_inici = date.fromisoformat(e["data_inici"])
        e_fi    = date.fromisoformat(e["data_fi"])
        if inici <= e_fi and fi >= e_inici:
            return e
    return None


def _parse_data(data_str: str) -> str:
    """
    Converteix una data del calendari a format ISO (YYYY-MM-DD).
    FullCalendar retorna datetimes UTC (ex: '2026-04-24T22:00:00.000Z')
    que representen la mitjanit local. Afegim 12h per corregir qualsevol
    fus horari sense necessitar conèixer el TZ del client.
    """
    if not data_str:
        return ""
    if len(data_str) == 10:
        return data_str
    try:
        dt = datetime.fromisoformat(data_str.replace("Z", "+00:00"))
        return (dt + timedelta(hours=12)).date().isoformat()
    except Exception:
        return data_str[:10]


_NOMS_MESOS = [
    "", "Gener", "Febrer", "Març", "Abril", "Maig", "Juny",
    "Juliol", "Agost", "Setembre", "Octubre", "Novembre", "Desembre"
]

def _calendari_anual_html(estades: list, any_sel: int) -> str:
    """Genera un calendari anual HTML amb els dies d'estada acolorits."""
    # Mapa de dies ocupats → color
    dies_ocupats = {}
    for e in estades:
        color  = (e.get("families") or {}).get("color", "#888")
        cursor = date.fromisoformat(e["data_inici"])
        fi     = date.fromisoformat(e["data_fi"])
        while cursor <= fi:
            if cursor.year == any_sel:
                dies_ocupats[cursor] = color
            cursor += timedelta(days=1)

    cap = "<th style='text-align:center;padding:2px 4px;font-size:11px;color:var(--color-text-secondary);font-weight:400;'>"
    dies_cap = f"{cap}Dl</th>{cap}Dt</th>{cap}Dc</th>{cap}Dj</th>{cap}Dv</th>{cap}Ds</th>{cap}Dg</th>"

    mesos_html = []
    for mes in range(1, 13):
        files = cal_mod.monthcalendar(any_sel, mes)
        taula = f"<div style='margin-bottom:16px'>"
        taula += f"<p style='font-size:13px;font-weight:500;margin:0 0 4px'>{_NOMS_MESOS[mes]}</p>"
        taula += f"<table style='border-collapse:collapse;width:100%'><tr>{dies_cap}</tr>"
        for setmana in files:
            taula += "<tr>"
            for dia in setmana:
                if dia == 0:
                    taula += "<td></td>"
                else:
                    d = date(any_sel, mes, dia)
                    color = dies_ocupats.get(d)
                    if color:
                        s = (f"background:{color};color:white;border-radius:3px;"
                             f"text-align:center;padding:2px;font-size:11px;")
                    else:
                        s = "text-align:center;padding:2px;font-size:11px;"
                    taula += f"<td style='{s}'>{dia}</td>"
            taula += "</tr>"
        taula += "</table></div>"
        mesos_html.append(taula)

    grid = "<div style='display:grid;grid-template-columns:repeat(3,1fr);gap:8px 20px;'>"
    grid += "".join(mesos_html)
    grid += "</div>"
    return grid


def _fmt(data_iso: str) -> str:
    """Converteix data ISO a DD/MM/YYYY."""
    try:
        p = data_iso[:10].split("-")
        return f"{p[2]}/{p[1]}/{p[0]}"
    except Exception:
        return data_iso
