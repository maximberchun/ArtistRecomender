# src/auth.py
import os
import streamlit as st
import bcrypt

def login_guard() -> tuple[str, str]:
    """
    Bloquea la app hasta que el usuario se autentique.
    Usa APP_ADMIN_USER y APP_ADMIN_PASSWORD_HASH (bcrypt) del entorno.
    """
    user_env = os.getenv("APP_ADMIN_USER", "admin")
    hash_env = os.getenv("APP_ADMIN_PASSWORD_HASH", "").encode()

    if not hash_env:
        st.error("Falta APP_ADMIN_PASSWORD_HASH en el entorno (.env).")
        st.stop()

    if not st.session_state.get("auth_ok"):
        st.subheader("Acceso")
        u = st.text_input("Usuario", value="", autocomplete="username")
        p = st.text_input("Contraseña", value="", type="password", autocomplete="current-password")
        if st.button("Entrar", type="primary"):
            ok_user = (u == user_env)
            ok_pw = False
            try:
                ok_pw = bcrypt.checkpw(p.encode(), hash_env)
            except Exception:
                ok_pw = False

            if ok_user and ok_pw:
                st.session_state.auth_ok = True
                st.session_state.username = u
                st.success("Autenticado ✓")
                st.rerun()
            else:
                st.error("Credenciales inválidas")

        st.stop()

    # Logout en la sidebar
    with st.sidebar:
        if st.button("Cerrar sesión"):
            st.session_state.clear()
            st.rerun()

    return user_env, st.session_state.get("username", user_env)
