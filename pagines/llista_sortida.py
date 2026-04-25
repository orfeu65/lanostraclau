"""Pàgina de llista de sortida — checklist per estada."""
import streamlit as st
from datetime import date, datetime, timezone, timedelta
from typing import Optional
from serveis.auth import obtenir_usuari_actual


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

    st.caption(
        f"Estada: {_formata_data(estada['data_inici'])} — {_formata_data(estada['data_fi'])}"
    )
    st.info("Segons com estigui el pis, et pot portar tot el dia (si has de rentar roba), 30 minuts (si has de netejar) o 10 minuts (si tot està ja net).")
    st.divider()

    items = _obtenir_items(supabase)
    if not items:
        st.warning("La llista de comprovació no té ítems. Contacta amb l'administradora.")
        return

    respostes = _obtenir_respostes(supabase, estada["id"])
    respostes_per_item = {r["item_id"]: r for r in respostes}

    _mostrar_formulari(supabase, estada, items, respostes_per_item, usuari_id)


# --- Seccions ---

def _mostrar_formulari(supabase, estada, items, respostes_per_item, usuari_id) -> None:
    """Mostra el formulari de checklist amb seccions i comentari."""
    with st.form("llista_sortida"):
        marcats = {}

        # Agrupem els ítems per secció mantenint l'ordre
        seccions = {}
        for item in items:
            seccions.setdefault(item["seccio"], []).append(item)

        for seccio, items_seccio in seccions.items():
            st.subheader(seccio)
            for item in items_seccio:
                valor_actual = respostes_per_item.get(item["id"], {}).get("fet", False)
                label = item["descripcio"]
                if item.get("es_opcional"):
                    label += " *(opcional)*"
                marcats[item["id"]] = st.checkbox(
                    label,
                    value=valor_actual,
                    key=f"item_{item['id']}",
                )

        st.divider()
        comentari = st.text_area(
            "Comentari (opcional)",
            value=estada.get("comentari_sortida") or "",
            placeholder="Notes o incidències d'aquesta estada...",
            height=80,
        )

        desat = st.form_submit_button("Desar llista", use_container_width=True)

    if desat:
        _desar_respostes(supabase, estada, items, marcats, comentari, usuari_id)


# --- Lògica de dades ---

def _desar_respostes(supabase, estada, items, marcats, comentari, usuari_id) -> None:
    """Desa les respostes del checklist i el comentari de l'estada."""
    try:
        ara = datetime.now(timezone.utc).isoformat()

        # Upsert de cada ítem
        registres = [
            {
                "estada_id":      estada["id"],
                "item_id":        item["id"],
                "fet":            marcats.get(item["id"], False),
                "completada_per": usuari_id,
                "completada_quan": ara,
            }
            for item in items
        ]
        supabase.table("checklist_respostes").upsert(
            registres, on_conflict="estada_id,item_id"
        ).execute()

        # Desar el comentari a l'estada
        supabase.table("estades").update({
            "comentari_sortida": comentari or None,
            "modificada_quan":   ara,
        }).eq("id", estada["id"]).execute()

        # Comprovem si queden obligatoris sense marcar
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

        st.rerun()

    except Exception as e:
        st.error(f"Error desant la llista: {e}")


def _obtenir_estada_rellevant(supabase, familia_id: str) -> Optional[dict]:
    """
    Retorna l'estada que finalitza avui, o la que ha finalitzat
    en els últims 3 dies (per si no s'ha omplert a temps).
    No es pot omplir la llista abans del dia de sortida.
    """
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
    """Retorna tots els ítems de la llista ordenats."""
    try:
        res = supabase.table("checklist_items").select("*").order("ordre").execute()
        return res.data or []
    except Exception:
        return []


def _obtenir_respostes(supabase, estada_id: str) -> list:
    """Retorna les respostes ja desades per a una estada."""
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
    """Retorna (usuari_id, familia_id) de l'usuari actual."""
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


# --- Utilitats ---

def _formata_data(data_iso: Optional[str]) -> str:
    """Converteix una data ISO (YYYY-MM-DD) a format llegible (DD/MM/YYYY)."""
    if not data_iso:
        return "—"
    try:
        parts = data_iso[:10].split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except Exception:
        return data_iso
