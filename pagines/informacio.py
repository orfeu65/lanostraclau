"""Pàgina d'informació útil — dades llegides des de Supabase."""
import streamlit as st
from pathlib import Path


def mostrar(supabase) -> None:
    st.title("ℹ️ Informació útil")

    recursos     = _obtenir(supabase, "recursos",     "ordre")
    subministres = _obtenir(supabase, "subministres", "ordre")
    acords       = _obtenir(supabase, "acords",       "ordre")

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
        for s in subministres:
            empresa = s.get("empresa") or "—"
            telefon = s.get("telefon") or "—"
            notes   = s.get("notes") or ""
            url     = s.get("url") or ""
            empresa_md = f"[{empresa}]({url})" if url else empresa
            with st.expander(s["nom"]):
                st.markdown(f"**Empresa:** {empresa_md}")
                st.markdown(f"**Telèfon:** `{telefon}`")
                if notes:
                    st.markdown(f"_{notes}_")
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
