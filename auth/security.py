import bcrypt
import sqlite3
import streamlit as st
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def verify_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def login(username, password):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # Puxa também a coluna can_edit_tasks
    cursor.execute("SELECT id, username, password_hash, name, role, can_edit_tasks FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()

    if user and verify_password(password, user[2]):
        st.session_state['logged_in'] = True
        st.session_state['user_id'] = user[0]
        st.session_state['username'] = user[1]
        st.session_state['name'] = user[3]
        st.session_state['role'] = user[4]
        st.session_state['can_edit_tasks'] = bool(user[5]) # Salva a permissão na sessão
        return True
    return False

def check_auth():
    if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
        st.warning("Por favor, faça login para acessar o sistema.")
        st.stop()
