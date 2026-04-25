"""Pàgina d'informació útil."""
import streamlit as st
from pathlib import Path


_SARFA_PALAMOS_URL = "https://www.moventis.es/ca/consulta-els-horaris-la-nova-estacio-dautobusos-de-palamos"
_SARFA_URL = "https://www.moventis.es/es/lineas-horarios/linea-autobus-1-aeroport-bcn-barcelona-costa-brava-centre"
_SARFA_L44_URL = "https://www.moventis.es/ca/linies-horaris/linia-autobus-44-e3-girona-palamos-palafrugell"

_SUBMINISTRES = [
    ("Aigua",           "Palamós",     "972 061 056", None),
    ("Gas",             "Naturgy",     "912 100 100", "https://clientes.naturgy.es/"),
    ("Llum",            "Energia XXI", "800 760 333", "https://www.energiaxxi.com/"),
    ("Wi-Fi",           "Vinga",       "872 200 700", "https://www.vingafibra.com/ca"),
    ("Assegurança",     "AXA",         "91 807 00 55", "https://www.axa.es"),
    ("Avaries caldera", "Junker",      "972 902 582", None),
    ("Manteniment A/C", "—",           "—",           None),
]

_ACORDS = [
    ("Família Elisa",    "Ús preferent del llit sota la finestra de l'habitació de l'entrada (i els armaris)"),
    ("Família Cristina", "Ús preferent del llit de l'habitació del fons (i armaris)"),
]


def mostrar(supabase) -> None:
    st.title("ℹ️ Informació útil")

    # --- Subministres ---
    st.subheader("📞 Subministres i telèfons d'interès")

    cap1, cap2, cap3 = st.columns([2, 2, 2])
    cap1.markdown("**Servei**")
    cap2.markdown("**Empresa**")
    cap3.markdown("**Telèfon**")

    for servei, empresa, telefon, url in _SUBMINISTRES:
        c1, c2, c3 = st.columns([2, 2, 2])
        c1.markdown(servei)
        if url:
            c2.markdown(f"[{empresa}]({url})")
        else:
            c2.markdown(empresa)
        c3.markdown(f"`{telefon}`")

    st.divider()

    # --- Acords ---
    st.subheader("🤝 Acords entre famílies")
    for familia, text in _ACORDS:
        st.markdown(f"**{familia}** — {text}")

    st.divider()

    # --- SARFA ---
    st.subheader("🚌 SARFA")
    st.markdown(f"[Línies de l'estació de Palamós]({_SARFA_PALAMOS_URL})")
    st.markdown(f"[Línia 1 · Aeroport BCN – Barcelona – Costa Brava Centre]({_SARFA_URL})")
    st.markdown(f"[Línia 44 · Girona – Palamós – Palafrugell]({_SARFA_L44_URL})")

    pdf_path = Path(__file__).parent.parent / "static" / "sarfa.pdf"
    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇️ Descarrega horaris BCN–Palamós (PDF)",
                data=f.read(),
                file_name="sarfa_horaris.pdf",
                mime="application/pdf",
            )
