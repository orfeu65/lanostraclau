"""Pàgina d'informació útil — dades llegides des de Supabase."""
import streamlit as st
from pathlib import Path


def mostrar(supabase) -> None:
    st.title("ℹ️ Informació útil")

    recursos    = _obtenir(supabase, "recursos",    "ordre")
    subministres = _obtenir(supabase, "subministres", "ordre")
    acords      = _obtenir(supabase, "acords",      "ordre")

    drive     = [r for r in recursos if r["categoria"] == "drive"]
    transport = [r for r in recursos if r["categoria"] == "transport"]

    # --- Drive ---
    if drive:
        st.subheader("📁 Google Drive")
        for r in drive:
            st.markdown(f"[{r['titol']}]({r['url']})")
        st.divider()

    # --- Subministres ---
    if subministres:
        st.subheader("📞 Subministres i telèfons d'interès")
        cap1, cap2, cap3 = st.columns([2, 2, 2])
        cap1.markdown("**Servei**")
        cap2.markdown("**Empresa**")
        cap3.markdown("**Telèfon**")
        for s in subministres:
            c1, c2, c3 = st.columns([2, 2, 2])
            nom = s["nom"]
            if s.get("notes"):
                nom += f"  \n_{s['notes']}_"
            c1.markdown(nom)
            empresa = s.get("empresa") or "—"
            if s.get("url"):
                c2.markdown(f"[{empresa}]({s['url']})")
            else:
                c2.markdown(empresa)
            c3.markdown(f"`{s.get('telefon') or '—'}`")
        st.divider()

    # --- Acords ---
    if acords:
        st.subheader("🤝 Acords entre famílies")
        for a in acords:
            st.markdown(f"**{a['titol']}** — {a['text']}")
        st.divider()

    # --- Transport ---
    if transport:
        st.subheader("🚌 Transport")
        for r in transport:
            st.markdown(f"[{r['titol']}]({r['url']})")

    pdf_path = Path(__file__).parent.parent / "static" / "sarfa.pdf"
    if pdf_path.exists():
        with open(pdf_path, "rb") as f:
            st.download_button(
                "⬇️ Descarrega horaris BCN–Palamós (PDF)",
                data=f.read(),
                file_name="sarfa_horaris.pdf",
                mime="application/pdf",
            )


def _obtenir(supabase, taula: str, ordre: str) -> list:
    try:
        return supabase.table(taula).select("*").order(ordre).execute().data or []
    except Exception as e:
        st.warning(f"No s'ha pogut carregar {taula}. ({e})")
        return []
