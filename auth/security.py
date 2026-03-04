import bcrypt
import sqlite3
import streamlit as st

DB_PATH = "rh_projects.db"

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, password_hash, name, role, can_edit_tasks FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[2]):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user[0]
        st.session_state['name'] = user[3]
        st.session_state['role'] = user[4]
        st.session_state['can_edit_tasks'] = bool(user[5])
        return True
    return False

def check_auth():
    if not st.session_state.get('logged_in'):
        st.stop()
