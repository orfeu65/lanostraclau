import streamlit as st
from supabase import create_client
import os
from dotenv import load_dotenv

# Carreguem les variables d'entorn (desenvolupament local)
load_dotenv()

# Configuració de la pàgina
st.set_page_config(
    page_title="La Nostra Clau",
    page_icon="🔑",
    layout="centered",
    initial_sidebar_state="expanded",
)

# Connexió a Supabase
@st.cache_resource
def init_supabase():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
    except Exception:
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("Falten les credencials de Supabase. Comprova les variables d'entorn.")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

from serveis.auth import verificar_token_url, obtenir_usuari_actual, mostrar_login

# Supabase envia el token com a fragment hash (#access_token=...) que Python no pot llegir.
# Aquest snippet JS el converteix a query params (?access_token=...) i recarrega la pàgina.
import streamlit.components.v1 as components
components.html("""
<script>
    const hash = window.parent.location.hash;
    if (hash && hash.includes('access_token')) {
        const params = new URLSearchParams(hash.substring(1));
        const access_token = params.get('access_token');
        const refresh_token = params.get('refresh_token') || '';
        const type = params.get('type') || '';
        if (access_token) {
            window.parent.location.replace(
                window.parent.location.pathname +
                '?access_token=' + encodeURIComponent(access_token) +
                '&refresh_token=' + encodeURIComponent(refresh_token) +
                '&type=' + encodeURIComponent(type)
            );
        }
    }
</script>
""", height=0)

# Comprovem si venim d'un magic link (token a la URL)
if not obtenir_usuari_actual():
    verificar_token_url(supabase)

# Si no hi ha sessió, mostrem el login i parem
if not obtenir_usuari_actual():
    mostrar_login(supabase)
    st.stop()

# Restaurem la sessió al client Supabase a cada rerun (necessari per a RLS)
sessio = st.session_state.get("sessio")
if sessio:
    supabase.auth.set_session(sessio.access_token, sessio.refresh_token)

# --- App principal (usuari autenticat) ---
st.sidebar.title("🔑 La Nostra Clau")
st.sidebar.caption("Del pis de Palamós")

pagines = {
    "Inici":             "pagines.inici",
    "Calendari":         "pagines.calendari",
    "Llista de sortida": "pagines.llista_sortida",
    "Tasques":           "pagines.tasques",
    "Informació útil":   "pagines.informacio",
    "Administració":     "pagines.administracio",
}

seleccio = st.sidebar.radio("Navegació", list(pagines.keys()))

import importlib
modul = importlib.import_module(pagines[seleccio])
modul.mostrar(supabase)
