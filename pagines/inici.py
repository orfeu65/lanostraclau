"""Pàgina d'inici — estat del pis, propera estada, tauler d'avisos i accessos ràpids."""
import streamlit as st
from datetime import date, datetime, timezone
from typing import Optional
from serveis.auth import obtenir_usuari_actual, tancar_sessio


def mostrar(supabase) -> None:
    avui = date.today().isoformat()
    usuari = obtenir_usuari_actual()

    # Capçalera
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title("⚓🔑 La Nostra Clau")
    with col2:
        if st.button("Sortir", use_container_width=True):
            tancar_sessio(supabase)

    st.divider()

    _mostrar_estat_pis(supabase, avui)
    _mostrar_propera_estada(supabase, avui, usuari)
    _mostrar_darrera_sortida(supabase, avui)
    _mostrar_tauler_avisos(supabase, usuari)
    _mostrar_accessos_rapids(supabase)


# --- Seccions ---

def _mostrar_estat_pis(supabase, avui: str) -> None:
    """Mostra si el pis és buit o qui hi és ara."""
    try:
        res = (
            supabase.table("estades")
            .select("*, families(nom, color), usuaris!responsable_id(nom)")
            .lte("data_inici", avui)
            .gte("data_fi", avui)
            .execute()
        )
        if res.data:
            estada = res.data[0]
            familia = estada.get("families") or {}
            responsable = estada.get("usuaris") or {}
            color = familia.get("color", "#666666")
            st.markdown(
                f"""
                <div style="background:{color}22; border-left:4px solid {color};
                            padding:12px 16px; border-radius:6px; margin-bottom:8px;">
                    <strong>🏠 El pis està ocupat</strong><br>
                    <strong>{familia.get('nom', '—')}</strong>
                    · Responsable: {responsable.get('nom', '—')}<br>
                    <small>Fins al {_formata_data(estada.get('data_fi', ''))}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("🏠 El pis és buit")
    except Exception as e:
        st.warning(f"No s'ha pogut carregar l'estat del pis. ({e})")


def _mostrar_propera_estada(supabase, avui: str, usuari) -> None:
    """Mostra la propera estada de la família de l'usuari actual."""
    if not usuari:
        return
    try:
        email = usuari.email if hasattr(usuari, "email") else usuari.get("email")
        res_usuari = (
            supabase.table("usuaris")
            .select("familia_id")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        if not res_usuari or not res_usuari.data:
            return

        familia_id = res_usuari.data["familia_id"]
        res = (
            supabase.table("estades")
            .select("*, usuaris!responsable_id(nom)")
            .eq("familia_id", familia_id)
            .gt("data_inici", avui)
            .order("data_inici")
            .limit(1)
            .execute()
        )

        st.subheader("La teva propera estada")
        if res.data:
            estada = res.data[0]
            responsable = estada.get("usuaris") or {}
            st.markdown(
                f"📅 **{_formata_data(estada['data_inici'])}** — "
                f"**{_formata_data(estada['data_fi'])}**  \n"
                f"Responsable: {responsable.get('nom', '—')}"
            )
            if estada.get("comentari"):
                st.caption(estada["comentari"])
        else:
            st.write("No tens cap estada programada.")
    except Exception as e:
        st.warning(f"No s'ha pogut carregar la propera estada. ({e})")


def _mostrar_darrera_sortida(supabase, avui: str) -> None:
    """Mostra el comentari de la darrera llista de sortida completada."""
    try:
        res = (
            supabase.table("estades")
            .select("data_fi, comentari_sortida, families(nom, color)")
            .lt("data_fi", avui)
            .not_.is_("comentari_sortida", "null")
            .order("data_fi", desc=True)
            .limit(1)
            .execute()
        )
        darrera = None
        for estada in res.data or []:
            if estada.get("comentari_sortida"):
                darrera = {"estada": estada, "comentari": estada["comentari_sortida"]}
                break

        if darrera:
            est = darrera["estada"]
            familia = est.get("families") or {}
            st.subheader("Darrera sortida")
            st.markdown(
                f"**{familia.get('nom', '—')}** · {_formata_data(est['data_fi'])}  \n"
                f"_{darrera['comentari']}_"
            )
    except Exception as e:
        st.warning(f"No s'ha pogut carregar la darrera sortida. ({e})")


def _mostrar_tauler_avisos(supabase, usuari) -> None:
    """Mostra i permet editar el tauler d'avisos."""
    st.subheader("📌 Suro de missatges")
    try:
        res = supabase.table("avisos").select("*").execute()
        avis = res.data[0] if res.data else {"text": ""}
        text_actual = avis.get("text", "")

        with st.container():
            nou_text = st.text_area(
                "Avís",
                value=text_actual,
                height=100,
                label_visibility="collapsed",
                placeholder="Escriu aquí un avís per a totes les famílies...",
            )
            if st.button("Desar avís", use_container_width=True):
                _desar_avis(supabase, usuari, avis, nou_text)
    except Exception as e:
        st.warning(f"No s'ha pogut carregar el tauler d'avisos. ({e})")


def _desar_avis(supabase, usuari, avis_actual: dict, nou_text: str) -> None:
    """Desa el tauler d'avisos a Supabase."""
    try:
        email = usuari.email if hasattr(usuari, "email") else usuari.get("email")
        res_usuari = (
            supabase.table("usuaris")
            .select("id")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        usuari_id = res_usuari.data["id"] if res_usuari.data else None
        ara = datetime.now(timezone.utc).isoformat()

        if avis_actual.get("id"):
            supabase.table("avisos").update({
                "text": nou_text,
                "modificat_per": usuari_id,
                "modificat_quan": ara,
            }).eq("id", avis_actual["id"]).execute()
        else:
            supabase.table("avisos").insert({
                "text": nou_text,
                "modificat_per": usuari_id,
                "modificat_quan": ara,
            }).execute()

        st.success("Avís desat.")
        st.rerun()
    except Exception as e:
        st.error(f"Error desant l'avís: {e}")


def _mostrar_accessos_rapids(supabase) -> None:
    """Mostra els accessos ràpids a recursos externs."""
    try:
        res = supabase.table("recursos").select("*").order("ordre").execute()
        if not res.data:
            return

        st.subheader("🔗 Accessos ràpids")
        categories: dict[str, list] = {}
        for rec in res.data:
            cat = rec.get("categoria", "Altres")
            categories.setdefault(cat, []).append(rec)

        for categoria, recursos in categories.items():
            st.caption(categoria)
            for rec in recursos:
                st.markdown(f"[{rec['titol']}]({rec['url']})")
    except Exception as e:
        st.warning(f"No s'ha pogut carregar els accessos ràpids. ({e})")


# --- Utilitats ---

def _formata_data(data_iso: str) -> str:
    """Converteix una data ISO (YYYY-MM-DD) a format llegible (DD/MM/YYYY)."""
    if not data_iso:
        return "—"
    try:
        parts = data_iso[:10].split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except Exception:
        return data_iso
