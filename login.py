import streamlit as st

USERS = {
    "dr_schmidt": {"password": "1234", "role": "arzt"},
    "maria": {"password": "abcd", "role": "patient"}
}

def login():
    st.title("Login für Ärzt:in/ Patient:in")

    role_choice = st.selectbox("Rolle wählen", ["arzt", "patient"])
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")

    if st.button("Einloggen"):
        user = USERS.get(username)
        if user and user["password"] == password and user["role"] == role_choice:
            st.session_state["logged_in"] = True
            st.session_state["role"] = user["role"]
            st.session_state["username"] = username
            st.success(f"Eingeloggt als {user['role']}")
            st.rerun()
        else:
            st.error("Login fehlgeschlagen – prüfe Benutzername, Passwort und Rolle.")