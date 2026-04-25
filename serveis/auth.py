"""Gestió de l'autenticació amb Supabase (magic link per email)."""
import streamlit as st


def enviar_magic_link(supabase, email: str) -> bool:
    """
    Envia un magic link a l'email indicat.
    El control d'accés el fa Supabase Auth: amb "Allow new users to sign up"
    desactivat, només els emails registrats a auth.users rebran l'enllaç.
    """
    try:
        supabase.auth.sign_in_with_otp({"email": email})
        return True
    except Exception as e:
        st.error(f"Error enviant el magic link: {e}")
        return False


def verificar_token_url(supabase) -> bool:
    """
    Comprova si hi ha un token de magic link a la URL i inicia la sessió.
    Gestiona dos casos:
      - PKCE: ?token_hash=xxx&type=email
      - Implicit (hash convertit a query params per JS): ?access_token=xxx&refresh_token=xxx
    Retorna True si s'ha iniciat sessió correctament.
    """
    params = st.query_params

    # Cas 1: flux PKCE (token_hash)
    token_hash = params.get("token_hash")
    if token_hash:
        try:
            resposta = supabase.auth.verify_otp({
                "token_hash": token_hash,
                "type": params.get("type") or "email",
            })
            if resposta and resposta.session:
                st.session_state["sessio"] = resposta.session
                st.session_state["usuari"] = resposta.user
                st.query_params.clear()
                return True
        except Exception as e:
            st.error(f"Error verificant el magic link (token_hash): {e}")

    # Cas 2: flux implicit (access_token convertit des del hash per JS)
    access_token = params.get("access_token")
    if access_token:
        try:
            refresh_token = params.get("refresh_token") or ""
            resposta = supabase.auth.set_session(access_token, refresh_token)
            if resposta and resposta.session:
                st.session_state["sessio"] = resposta.session
                st.session_state["usuari"] = resposta.user
                st.query_params.clear()
                return True
        except Exception as e:
            st.error(f"Error verificant el magic link (access_token): {e}")

    return False


def obtenir_usuari_actual():
    """Retorna les dades de l'usuari de la sessió activa, o None."""
    return st.session_state.get("usuari")


def tancar_sessio(supabase) -> None:
    """Tanca la sessió activa."""
    try:
        supabase.auth.sign_out()
    except Exception:
        pass
    finally:
        st.session_state.pop("sessio", None)
        st.session_state.pop("usuari", None)
        st.rerun()


def mostrar_login(supabase) -> None:
    """Mostra el formulari de login amb magic link."""
    st.title("🔑 La Nostra Clau")
    st.caption("Pis de Palamós")
    st.divider()

    st.subheader("Entra a l'app")
    st.write("Introdueix el teu email i et enviarem un enllaç d'accés directe.")

    with st.form("login"):
        email = st.text_input("Email", placeholder="nom@exemple.com")
        enviat = st.form_submit_button("Envia'm l'enllaç", use_container_width=True)

    if enviat:
        if not email or "@" not in email:
            st.error("Introdueix un email vàlid.")
        elif enviar_magic_link(supabase, email):
            st.success(
                f"T'hem enviat un enllaç a **{email}**. "
                "Comprova el correu i fes clic a l'enllaç per entrar."
            )
