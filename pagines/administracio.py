"""Pàgina d'administració — només per a l'administradora."""
import streamlit as st
from serveis.auth import obtenir_usuari_actual


def mostrar(supabase) -> None:
    st.title("⚙️ Administració")

    usuari = obtenir_usuari_actual()
    if not _es_admin(supabase, usuari):
        st.error("Accés restringit a l'administradora.")
        return

    tabs = st.tabs(["Usuaris", "Famílies", "Seccions", "Checklist", "Subministres", "Acords", "Recursos"])

    with tabs[0]:
        _gestionar_usuaris(supabase)
    with tabs[1]:
        _gestionar_families(supabase)
    with tabs[2]:
        _gestionar_seccions_checklist(supabase)
    with tabs[3]:
        _gestionar_checklist(supabase)
    with tabs[4]:
        _gestionar_subministres(supabase)
    with tabs[5]:
        _gestionar_acords(supabase)
    with tabs[6]:
        _gestionar_recursos(supabase)


# --- Usuaris ---

def _gestionar_usuaris(supabase) -> None:
    st.subheader("Usuaris")
    families = _obtenir(supabase, "families", "nom")
    familia_noms = {f["id"]: f["nom"] for f in families}
    familia_opcions = {f["nom"]: f["id"] for f in families}

    usuaris = supabase.table("usuaris").select("*").order("nom").execute().data or []

    for u in usuaris:
        etiqueta = u["nom"] + ("" if u.get("actiu", True) else " ⚠️ desactivat")
        with st.expander(etiqueta):
            with st.form(f"edit_usr_{u['id']}"):
                nom      = st.text_input("Nom",   value=u["nom"])
                email    = st.text_input("Email", value=u["email"], disabled=True)
                familia_actual = familia_noms.get(u.get("familia_id"), "")
                familia_idx = list(familia_opcions.keys()).index(familia_actual) if familia_actual in familia_opcions else 0
                familia_sel = st.selectbox("Família", list(familia_opcions.keys()), index=familia_idx)
                es_admin = st.checkbox("Administradora", value=bool(u.get("es_admin")))
                actiu    = st.checkbox("Actiu",          value=bool(u.get("actiu", True)))
                desar    = st.form_submit_button("Desar", use_container_width=True)

            if desar:
                supabase.table("usuaris").update({
                    "nom":       nom,
                    "familia_id": familia_opcions[familia_sel],
                    "es_admin":  es_admin,
                    "actiu":     actiu,
                }).eq("id", u["id"]).execute()
                st.rerun()

    st.divider()
    with st.expander("➕ Nou usuari"):
        st.caption("Cal crear l'usuari primer a Supabase Auth (Authentication → Users) abans d'afegir-lo aquí.")
        with st.form("nou_usr"):
            nom      = st.text_input("Nom")
            email    = st.text_input("Email")
            familia_sel = st.selectbox("Família", list(familia_opcions.keys()))
            es_admin = st.checkbox("Administradora", value=False)
            if st.form_submit_button("Afegir", use_container_width=True):
                if nom.strip() and email.strip():
                    try:
                        res_auth = supabase.table("usuaris").select("id").eq("email", email.strip()).maybe_single().execute()
                        if res_auth.data:
                            st.error("Aquest email ja existeix.")
                        else:
                            # Obtenim l'id de auth.users
                            auth_res = supabase.auth.admin.get_user_by_email(email.strip())
                            supabase.table("usuaris").insert({
                                "id":        auth_res.user.id,
                                "nom":       nom.strip(),
                                "email":     email.strip(),
                                "familia_id": familia_opcions[familia_sel],
                                "es_admin":  es_admin,
                                "actiu":     True,
                            }).execute()
                            st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
                else:
                    st.error("El nom i l'email són obligatoris.")


# --- Famílies ---

def _gestionar_families(supabase) -> None:
    st.subheader("Famílies")
    items = _obtenir(supabase, "families", "nom")

    for f in items:
        with st.expander(f["nom"]):
            with st.form(f"edit_fam_{f['id']}"):
                nom   = st.text_input("Nom",   value=f["nom"])
                color = st.color_picker("Color", value=f.get("color") or "#cccccc")
                c1, c2 = st.columns(2)
                desar    = c1.form_submit_button("Desar",    use_container_width=True)
                eliminar = c2.form_submit_button("Eliminar", use_container_width=True)

            if desar:
                supabase.table("families").update({"nom": nom, "color": color}).eq("id", f["id"]).execute()
                st.rerun()
            if eliminar:
                supabase.table("families").delete().eq("id", f["id"]).execute()
                st.rerun()

    st.divider()
    with st.expander("➕ Nova família"):
        with st.form("nova_fam"):
            nom   = st.text_input("Nom")
            color = st.color_picker("Color", value="#cccccc")
            if st.form_submit_button("Afegir", use_container_width=True):
                if nom.strip():
                    supabase.table("families").insert({"nom": nom.strip(), "color": color}).execute()
                    st.rerun()
                else:
                    st.error("El nom és obligatori.")


# --- Seccions del checklist ---

def _gestionar_seccions_checklist(supabase) -> None:
    st.subheader("Seccions de la llista de sortida")
    seccions = _obtenir(supabase, "seccions_checklist", "ordre")

    for s in seccions:
        etiqueta = f"{s.get('icona', '📋')} {s['nom']}"
        with st.expander(etiqueta):
            with st.form(f"edit_sec_{s['id']}"):
                nom   = st.text_input("Nom",   value=s["nom"])
                icona = st.text_input("Icona", value=s.get("icona") or "📋")
                ordre = st.number_input("Ordre", value=s.get("ordre") or 0, step=1)
                c1, c2 = st.columns(2)
                desar    = c1.form_submit_button("Desar",    use_container_width=True)
                eliminar = c2.form_submit_button("Eliminar", use_container_width=True)

            if desar:
                supabase.table("seccions_checklist").update({
                    "nom": nom, "icona": icona or "📋", "ordre": ordre,
                }).eq("id", s["id"]).execute()
                st.rerun()
            if eliminar:
                supabase.table("seccions_checklist").delete().eq("id", s["id"]).execute()
                st.rerun()

    st.divider()
    with st.expander("➕ Nova secció"):
        with st.form("nova_seccio"):
            nom   = st.text_input("Nom")
            icona = st.text_input("Icona (emoji)", value="📋")
            ordre = st.number_input("Ordre", value=len(seccions), step=1)
            if st.form_submit_button("Afegir", use_container_width=True):
                if nom.strip():
                    supabase.table("seccions_checklist").insert({
                        "nom": nom.strip(), "icona": icona.strip() or "📋", "ordre": ordre,
                    }).execute()
                    st.rerun()
                else:
                    st.error("El nom és obligatori.")


# --- Checklist ---

def _gestionar_checklist(supabase) -> None:
    st.subheader("Llista de sortida")
    seccions = _obtenir(supabase, "seccions_checklist", "ordre")
    seccio_opcions = {s["nom"]: s["id"] for s in seccions}
    seccio_noms    = {s["id"]: s["nom"] for s in seccions}
    items = _obtenir(supabase, "checklist_items", "ordre")

    for item in items:
        seccio_nom = seccio_noms.get(item.get("seccio_id"), item.get("seccio", "—"))
        etiqueta = f"{seccio_nom} — {item['descripcio'][:40]}{'…' if len(item['descripcio']) > 40 else ''}"
        with st.expander(etiqueta):
            with st.form(f"edit_chk_{item['id']}"):
                noms_seccio = list(seccio_opcions.keys())
                idx = noms_seccio.index(seccio_nom) if seccio_nom in seccio_opcions else 0
                seccio_sel  = st.selectbox("Secció", noms_seccio, index=idx)
                descripcio  = st.text_area("Descripció", value=item["descripcio"], height=80)
                es_opcional = st.checkbox("Opcional",    value=bool(item.get("es_opcional")))
                ordre       = st.number_input("Ordre",   value=item.get("ordre") or 0, step=10)
                c1, c2      = st.columns(2)
                desar       = c1.form_submit_button("Desar",    use_container_width=True)
                eliminar    = c2.form_submit_button("Eliminar", use_container_width=True)

            if desar:
                supabase.table("checklist_items").update({
                    "seccio_id":  seccio_opcions[seccio_sel],
                    "seccio":     seccio_sel,
                    "descripcio": descripcio,
                    "es_opcional": es_opcional,
                    "ordre":      ordre,
                }).eq("id", item["id"]).execute()
                st.rerun()
            if eliminar:
                supabase.table("checklist_items").delete().eq("id", item["id"]).execute()
                st.rerun()

    st.divider()
    with st.expander("➕ Nou ítem"):
        with st.form("nou_chk"):
            noms_seccio = list(seccio_opcions.keys())
            seccio_sel  = st.selectbox("Secció", noms_seccio) if noms_seccio else None
            descripcio  = st.text_area("Descripció", height=80)
            es_opcional = st.checkbox("Opcional", value=False)
            ordre       = st.number_input("Ordre", value=(max(i.get("ordre", 0) for i in items) + 10) if items else 10, step=10)
            if st.form_submit_button("Afegir", use_container_width=True):
                if seccio_sel and descripcio.strip():
                    supabase.table("checklist_items").insert({
                        "seccio_id":  seccio_opcions[seccio_sel],
                        "seccio":     seccio_sel,
                        "descripcio": descripcio.strip(),
                        "es_opcional": es_opcional,
                        "ordre":      ordre,
                    }).execute()
                    st.rerun()
                else:
                    st.error("La secció i la descripció són obligatòries.")


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
