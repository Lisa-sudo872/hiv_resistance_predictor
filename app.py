import streamlit as st
from auth.auth_utils import authenticate_user, register_user

def login_screen():
    st.image("assets/dna_animation.gif", use_column_width=True)
    st.title("🔐 HIV-1 Resistance Predictor Login")

    choice = st.radio("Login or Register", ["Login", "Register"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if choice == "Login":
        if st.button("Login"):
            if authenticate_user(username, password):
                st.success(f"Welcome back, {username}!")
                st.session_state["authenticated"] = True
                st.session_state["user"] = username
            else:
                st.error("Invalid username or password.")
    else:
        if st.button("Register"):
            if register_user(username, password):
                st.success("Account created. Please login.")
            else:
                st.warning("Username already exists.")

# Show login screen unless user is authenticated
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login_screen()
    st.stop()
