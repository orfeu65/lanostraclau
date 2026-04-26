"""Pàgina d'informació útil — dades llegides des de Supabase."""
import streamlit as st
from pathlib import Path
from html import escape


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
        st.markdown(_html_subministres(subministres), unsafe_allow_html=True)
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


def _html_subministres(subministres: list) -> str:
    """Taula al web, expanders al mòbil (CSS media query, sense JS)."""

    # --- Taula (pantalla ampla) ---
    files = ""
    for s in subministres:
        nom     = escape(s["nom"])
        empresa = escape(s.get("empresa") or "—")
        telefon = escape(s.get("telefon") or "—")
        notes   = escape(s.get("notes") or "")
        url     = s.get("url") or ""
        empresa_html = f'<a href="{escape(url)}">{empresa}</a>' if url else empresa
        files += (
            f"<tr>"
            f"<td>{nom}</td>"
            f"<td>{empresa_html}</td>"
            f"<td><code>{telefon}</code></td>"
            f"<td>{notes}</td>"
            f"</tr>"
        )

    taula = f"""
    <table class="sub-taula">
      <thead>
        <tr>
          <th>Servei</th><th>Empresa</th><th>Telèfon</th><th>Notes</th>
        </tr>
      </thead>
      <tbody>{files}</tbody>
    </table>"""

    # --- Expanders (pantalla estreta) ---
    cards = '<div class="sub-cards">'
    for s in subministres:
        nom     = escape(s["nom"])
        empresa = escape(s.get("empresa") or "—")
        telefon = escape(s.get("telefon") or "—")
        notes   = escape(s.get("notes") or "")
        url     = s.get("url") or ""
        empresa_html = f'<a href="{escape(url)}">{empresa}</a>' if url else empresa
        notes_html   = f'<p><em>{notes}</em></p>' if notes else ""
        cards += f"""
        <details>
          <summary>{nom}</summary>
          <p>{empresa_html} · <code>{telefon}</code></p>
          {notes_html}
        </details>"""
    cards += "</div>"

    css = """
    <style>
      .sub-taula { width:100%; border-collapse:collapse; font-size:0.9em; }
      .sub-taula th { text-align:left; border-bottom:2px solid #555; padding:4px 8px; }
      .sub-taula td { padding:4px 8px; border-bottom:1px solid #333; vertical-align:top; }
      .sub-cards { display:none; }
      .sub-cards details { border:1px solid #444; border-radius:6px;
                           margin-bottom:6px; padding:6px 10px; }
      .sub-cards summary { font-weight:600; cursor:pointer; }
      .sub-cards p { margin:4px 0; font-size:0.9em; }
      @media (max-width: 600px) {
        .sub-taula { display:none; }
        .sub-cards { display:block; }
      }
    </style>"""

    return css + taula + cards


def _obtenir(supabase, taula: str, ordre: str) -> list:
    try:
        return supabase.table(taula).select("*").order(ordre).execute().data or []
    except Exception as e:
        st.warning(f"No s'ha pogut carregar {taula}. ({e})")
        return []
