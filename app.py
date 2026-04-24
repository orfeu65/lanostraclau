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
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_KEY")
    if not url or not key:
        st.error("Falten les credencials de Supabase. Comprova les variables d'entorn.")
        st.stop()
    return create_client(url, key)

supabase = init_supabase()

# Navegació principal
st.sidebar.title("🔑 La Nostra Clau")
st.sidebar.caption("Pis de Palamós")

pagines = {
    "Inici":            "pagines.inici",
    "Calendari":        "pagines.calendari",
    "Llista de sortida":"pagines.llista_sortida",
    "Tasques":          "pagines.tasques",
    "Informació útil":  "pagines.informacio",
    "Administració":    "pagines.administracio",
}

seleccio = st.sidebar.radio("Navegació", list(pagines.keys()))

# Carreguem la pàgina seleccionada
import importlib
modul = importlib.import_module(pagines[seleccio])
modul.mostrar(supabase)
