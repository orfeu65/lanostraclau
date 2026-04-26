"""Pàgina d'administració — només per a l'administradora."""
import streamlit as st
from serveis.auth import obtenir_usuari_actual


def mostrar(supabase) -> None:
    st.title("⚙️ Administració")

    usuari = obtenir_usuari_actual()
    if not _es_admin(supabase, usuari):
        st.error("Accés restringit a l'administradora.")
        return

    tab_sub, tab_acords, tab_rec = st.tabs(["Subministres", "Acords", "Recursos"])

    with tab_sub:
        _gestionar_subministres(supabase)

    with tab_acords:
        _gestionar_acords(supabase)

    with tab_rec:
        _gestionar_recursos(supabase)


# --- Subministres ---

def _gestionar_subministres(supabase) -> None:
    st.subheader("Subministres")
    items = _obtenir(supabase, "subministres", "ordre")

    for s in items:
        with st.expander(s["nom"]):
            with st.form(f"edit_sub_{s['id']}"):
                nom      = st.text_input("Nom",     value=s["nom"])
                empresa  = st.text_input("Empresa", value=s.get("empresa") or "")
                telefon  = st.text_input("Telèfon", value=s.get("telefon") or "")
                url      = st.text_input("Web",     value=s.get("url") or "")
                notes    = st.text_area("Notes",    value=s.get("notes") or "", height=80)
                ordre    = st.number_input("Ordre", value=s.get("ordre") or 0, step=1)
                c1, c2   = st.columns(2)
                desar    = c1.form_submit_button("Desar",    use_container_width=True)
                eliminar = c2.form_submit_button("Eliminar", use_container_width=True)

            if desar:
                supabase.table("subministres").update({
                    "nom": nom, "empresa": empresa or None, "telefon": telefon or None,
                    "url": url or None, "notes": notes or None, "ordre": ordre,
                }).eq("id", s["id"]).execute()
                st.rerun()
            if eliminar:
                supabase.table("subministres").delete().eq("id", s["id"]).execute()
                st.rerun()

    st.divider()
    with st.expander("➕ Nou subministre"):
        with st.form("nou_sub"):
            nom     = st.text_input("Nom")
            empresa = st.text_input("Empresa")
            telefon = st.text_input("Telèfon")
            url     = st.text_input("Web")
            notes   = st.text_area("Notes", height=80)
            ordre   = st.number_input("Ordre", value=len(items), step=1)
            if st.form_submit_button("Afegir", use_container_width=True):
                if nom.strip():
                    supabase.table("subministres").insert({
                        "nom": nom.strip(), "empresa": empresa or None,
                        "telefon": telefon or None, "url": url or None,
                        "notes": notes or None, "ordre": ordre,
                    }).execute()
                    st.rerun()
                else:
                    st.error("El nom és obligatori.")


# --- Acords ---

def _gestionar_acords(supabase) -> None:
    st.subheader("Acords entre famílies")
    items = _obtenir(supabase, "acords", "ordre")

    for a in items:
        with st.expander(a["titol"]):
            with st.form(f"edit_acord_{a['id']}"):
                titol    = st.text_input("Títol", value=a["titol"])
                text     = st.text_area("Text",  value=a["text"], height=100)
                ordre    = st.number_input("Ordre", value=a.get("ordre") or 0, step=1)
                c1, c2   = st.columns(2)
                desar    = c1.form_submit_button("Desar",    use_container_width=True)
                eliminar = c2.form_submit_button("Eliminar", use_container_width=True)

            if desar:
                supabase.table("acords").update({
                    "titol": titol, "text": text, "ordre": ordre,
                }).eq("id", a["id"]).execute()
                st.rerun()
            if eliminar:
                supabase.table("acords").delete().eq("id", a["id"]).execute()
                st.rerun()

    st.divider()
    with st.expander("➕ Nou acord"):
        with st.form("nou_acord"):
            titol = st.text_input("Títol")
            text  = st.text_area("Text", height=100)
            ordre = st.number_input("Ordre", value=len(items), step=1)
            if st.form_submit_button("Afegir", use_container_width=True):
                if titol.strip() and text.strip():
                    supabase.table("acords").insert({
                        "titol": titol.strip(), "text": text.strip(), "ordre": ordre,
                    }).execute()
                    st.rerun()
                else:
                    st.error("El títol i el text són obligatoris.")


# --- Recursos ---

def _gestionar_recursos(supabase) -> None:
    st.subheader("Recursos i enllaços")
    items = _obtenir(supabase, "recursos", "ordre")

    CATEGORIES = ["drive", "transport"]

    for r in items:
        with st.expander(r["titol"]):
            with st.form(f"edit_rec_{r['id']}"):
                titol     = st.text_input("Títol",    value=r["titol"])
                url       = st.text_input("URL",      value=r["url"])
                categoria = st.selectbox("Categoria", CATEGORIES,
                                         index=CATEGORIES.index(r["categoria"])
                                         if r["categoria"] in CATEGORIES else 0)
                ordre     = st.number_input("Ordre",  value=r.get("ordre") or 0, step=1)
                c1, c2    = st.columns(2)
                desar     = c1.form_submit_button("Desar",    use_container_width=True)
                eliminar  = c2.form_submit_button("Eliminar", use_container_width=True)

            if desar:
                supabase.table("recursos").update({
                    "titol": titol, "url": url, "categoria": categoria, "ordre": ordre,
                }).eq("id", r["id"]).execute()
                st.rerun()
            if eliminar:
                supabase.table("recursos").delete().eq("id", r["id"]).execute()
                st.rerun()

    st.divider()
    with st.expander("➕ Nou recurs"):
        with st.form("nou_rec"):
            titol     = st.text_input("Títol")
            url       = st.text_input("URL")
            categoria = st.selectbox("Categoria", CATEGORIES)
            ordre     = st.number_input("Ordre", value=len(items), step=1)
            if st.form_submit_button("Afegir", use_container_width=True):
                if titol.strip() and url.strip():
                    supabase.table("recursos").insert({
                        "titol": titol.strip(), "url": url.strip(),
                        "categoria": categoria, "ordre": ordre,
                    }).execute()
                    st.rerun()
                else:
                    st.error("El títol i la URL són obligatoris.")


# --- Utilitats ---

def _obtenir(supabase, taula: str, ordre: str) -> list:
    try:
        return supabase.table(taula).select("*").order(ordre).execute().data or []
    except Exception as e:
        st.warning(f"No s'ha pogut carregar {taula}. ({e})")
        return []


def _es_admin(supabase, usuari) -> bool:
    if not usuari:
        return False
    try:
        email = usuari.email if hasattr(usuari, "email") else usuari.get("email")
        res = supabase.table("usuaris").select("es_admin").eq("email", email).maybe_single().execute()
        return bool(res.data and res.data.get("es_admin"))
    except Exception:
        return False
