"""Pàgina de llista de sortida — checklist per estada."""
import streamlit as st
from datetime import date, datetime, timezone, timedelta
from typing import Optional
from serveis.auth import obtenir_usuari_actual

_ICONES_SECCIO = {
    "El mateix dia de la sortida": "🧹",
    "Just abans de sortir":        "👋",
}


def mostrar(supabase) -> None:
    st.title("✅ Llista de sortida")

    usuari = obtenir_usuari_actual()
    usuari_id, familia_id = _obtenir_usuari_info(supabase, usuari)

    if not familia_id:
        st.warning("No s'ha pogut identificar la teva família.")
        return

    estada = _obtenir_estada_rellevant(supabase, familia_id)

    if not estada:
        st.info("La llista de sortida s'omple el dia que marxes. No tens cap estada que finalitzi avui o en els darrers 3 dies.")
        return

    st.caption(f"Estada: {_formata_data(estada['data_inici'])} — {_formata_data(estada['data_fi'])}")
    st.info("Segons com estigui el pis, et pot portar tot el dia (si has de rentar roba), 30 minuts (si has de netejar) o 10 minuts (si tot està ja net).")

    items = _obtenir_items(supabase)
    if not items:
        st.warning("La llista de comprovació no té ítems. Contacta amb l'administradora.")
        return

    respostes = _obtenir_respostes(supabase, estada["id"])
    respostes_per_item = {r["item_id"]: r for r in respostes}

    # Inicialitzem l'estat dels checkboxes a session_state
    clau_estada = f"checklist_{estada['id']}"
    if clau_estada not in st.session_state:
        st.session_state[clau_estada] = {
            item["id"]: respostes_per_item.get(item["id"], {}).get("fet", False)
            for item in items
        }

    marcats = st.session_state[clau_estada]

    # --- Seccions del checklist ---
    seccions = {}
    for item in items:
        seccions.setdefault(item["seccio"], []).append(item)

    for seccio, items_seccio in seccions.items():
        icona = _ICONES_SECCIO.get(seccio, "📋")
        st.subheader(f"{icona} {seccio}")
        for item in items_seccio:
            label = item["descripcio"]
            if item.get("es_opcional"):
                label += " *(opcional)*"
            marcats[item["id"]] = st.checkbox(
                label,
                value=marcats[item["id"]],
                key=f"cb_{estada['id']}_{item['id']}",
            )

    # --- Comentari ---
    st.divider()
    st.subheader("💬 Comentari")
    comentari = st.text_area(
        "Comentari",
        value=estada.get("comentari_sortida") or "",
        placeholder="Notes o incidències d'aquesta estada...",
        height=80,
        label_visibility="collapsed",
    )

    if st.button("Desar llista", use_container_width=True):
        _desar_respostes(supabase, estada, items, marcats, comentari, usuari_id)


# --- Lògica de dades ---

def _desar_respostes(supabase, estada, items, marcats, comentari, usuari_id) -> None:
    """Desa les respostes del checklist i el comentari de l'estada."""
    try:
        ara = datetime.now(timezone.utc).isoformat()

        registres = [
            {
                "estada_id":       estada["id"],
                "item_id":         item["id"],
                "fet":             marcats.get(item["id"], False),
                "completada_per":  usuari_id,
                "completada_quan": ara,
            }
            for item in items
        ]
        supabase.table("checklist_respostes").upsert(
            registres, on_conflict="estada_id,item_id"
        ).execute()

        supabase.table("estades").update({
            "comentari_sortida": comentari or None,
            "modificada_quan":   ara,
        }).eq("id", estada["id"]).execute()

        obligatoris_pendents = [
            item["descripcio"]
            for item in items
            if not item.get("es_opcional") and not marcats.get(item["id"], False)
        ]
        if obligatoris_pendents:
            st.warning(
                f"Llista desada, però queden **{len(obligatoris_pendents)}** "
                f"ítem(s) obligatori(s) sense marcar."
            )
        else:
            st.success("Llista de sortida completada. Bon viatge! 🏖️")

        clau_estada = f"checklist_{estada['id']}"
        st.session_state.pop(clau_estada, None)
        st.rerun()

    except Exception as e:
        st.error(f"Error desant la llista: {e}")


def _obtenir_estada_rellevant(supabase, familia_id: str) -> Optional[dict]:
    avui = date.today().isoformat()
    tres_dies = (date.today() - timedelta(days=3)).isoformat()
    try:
        res = (
            supabase.table("estades")
            .select("*")
            .eq("familia_id", familia_id)
            .gte("data_fi", tres_dies)
            .lte("data_fi", avui)
            .order("data_fi", desc=True)
            .limit(1)
            .execute()
        )
        if res and res.data:
            return res.data[0]
    except Exception as e:
        st.warning(f"Error carregant l'estada: {e}")
    return None


def _obtenir_items(supabase) -> list:
    try:
        res = supabase.table("checklist_items").select("*").order("ordre").execute()
        return res.data or []
    except Exception:
        return []


def _obtenir_respostes(supabase, estada_id: str) -> list:
    try:
        res = (
            supabase.table("checklist_respostes")
            .select("*")
            .eq("estada_id", estada_id)
            .execute()
        )
        return res.data or []
    except Exception:
        return []


def _obtenir_usuari_info(supabase, usuari) -> tuple:
    if not usuari:
        return None, None
    try:
        email = usuari.email if hasattr(usuari, "email") else usuari.get("email")
        res = (
            supabase.table("usuaris")
            .select("id, familia_id")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        if res and res.data:
            return res.data["id"], res.data["familia_id"]
    except Exception:
        pass
    return None, None


def _formata_data(data_iso: Optional[str]) -> str:
    if not data_iso:
        return "—"
    try:
        parts = data_iso[:10].split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except Exception:
        return data_iso
