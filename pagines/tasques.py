"""Pàgina de tasques pendents del pis."""
import streamlit as st
from datetime import datetime, timezone
from typing import Optional
from serveis.auth import obtenir_usuari_actual


def mostrar(supabase) -> None:
    st.title("🔧 Tasques del pis")

    usuari = obtenir_usuari_actual()
    usuari_id = _obtenir_usuari_id(supabase, usuari)

    _formulari_nova_tasca(supabase, usuari_id)
    st.divider()
    _llista_tasques_pendents(supabase, usuari_id)
    st.divider()
    _historial_tasques_completades(supabase)


# --- Seccions ---

def _formulari_nova_tasca(supabase, usuari_id: Optional[str]) -> None:
    """Formulari per afegir una tasca nova."""
    with st.form("nova_tasca", clear_on_submit=True):
        descripcio = st.text_input(
            "Nova tasca",
            placeholder="Descriu la tasca o millora pendent...",
        )
        enviat = st.form_submit_button("Afegir tasca", use_container_width=True)

    if enviat:
        if not descripcio.strip():
            st.error("La descripció no pot estar buida.")
        elif not usuari_id:
            st.error("No s'ha pogut identificar l'usuari.")
        else:
            try:
                supabase.table("tasques").insert({
                    "descripcio":   descripcio.strip(),
                    "afegida_per":  usuari_id,
                    "afegida_quan": datetime.now(timezone.utc).isoformat(),
                    "completada":   False,
                }).execute()
                st.success("Tasca afegida.")
                st.rerun()
            except Exception as e:
                st.error(f"Error afegint la tasca: {e}")


def _llista_tasques_pendents(supabase, usuari_id: Optional[str]) -> None:
    """Mostra les tasques pendents."""
    st.subheader("⚒️ Pendents")
    try:
        res = (
            supabase.table("tasques")
            .select("*, usuaris!afegida_per(nom)")
            .eq("completada", False)
            .order("afegida_quan")
            .execute()
        )
        tasques = res.data or []

        if not tasques:
            st.info("No hi ha tasques pendents. Ben fet! 🎉")
            return

        for tasca in tasques:
            col1, col2 = st.columns([5, 1])
            with col1:
                afegida_per = (tasca.get("usuaris") or {}).get("nom", "—")
                st.markdown(f"**{tasca['descripcio']}**")
                st.caption(f"Afegida per {afegida_per} · {_formata_data(tasca['afegida_quan'])}")
            with col2:
                if st.button("✓ Feta", key=f"feta_{tasca['id']}", use_container_width=True):
                    _marcar_completada(supabase, tasca["id"], usuari_id)

    except Exception as e:
        st.warning(f"No s'han pogut carregar les tasques. ({e})")


def _historial_tasques_completades(supabase) -> None:
    """Mostra l'historial de tasques completades."""
    with st.expander("🎉 Fetes"):
        try:
            res = (
                supabase.table("tasques")
                .select("*, qui_afegeix:usuaris!afegida_per(nom), qui_completa:usuaris!completada_per(nom)")
                .eq("completada", True)
                .order("completada_quan", desc=True)
                .execute()
            )
            tasques = res.data or []

            if not tasques:
                st.write("Encara no hi ha tasques completades.")
                return

            for tasca in tasques:
                afegida_per    = (tasca.get("qui_afegeix") or {}).get("nom", "—")
                completada_per = (tasca.get("qui_completa") or {}).get("nom", "—")

                st.markdown(f"✅ {tasca['descripcio']}")
                st.caption(
                    f"Afegida per {afegida_per} · "
                    f"Completada per {completada_per} el {_formata_data(tasca['completada_quan'])}"
                )

        except Exception as e:
            st.warning(f"No s'ha pogut carregar l'historial. ({e})")


# --- Utilitats ---

def _marcar_completada(supabase, tasca_id: str, usuari_id: Optional[str]) -> None:
    """Marca una tasca com a completada."""
    try:
        supabase.table("tasques").update({
            "completada":      True,
            "completada_per":  usuari_id,
            "completada_quan": datetime.now(timezone.utc).isoformat(),
        }).eq("id", tasca_id).execute()
        st.rerun()
    except Exception as e:
        st.error(f"Error marcant la tasca: {e}")


def _obtenir_usuari_id(supabase, usuari) -> Optional[str]:
    """Obté l'UUID de l'usuari de la taula 'usuaris' a partir del seu email."""
    if not usuari:
        return None
    try:
        email = usuari.email if hasattr(usuari, "email") else usuari.get("email")
        res = (
            supabase.table("usuaris")
            .select("id")
            .eq("email", email)
            .maybe_single()
            .execute()
        )
        return res.data["id"] if res and res.data else None
    except Exception:
        return None


def _formata_data(data_iso: Optional[str]) -> str:
    """Converteix una data ISO a format llegible (DD/MM/YYYY)."""
    if not data_iso:
        return "—"
    try:
        parts = data_iso[:10].split("-")
        return f"{parts[2]}/{parts[1]}/{parts[0]}"
    except Exception:
        return data_iso
