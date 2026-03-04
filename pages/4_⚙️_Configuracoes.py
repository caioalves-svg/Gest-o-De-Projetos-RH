import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import time
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from auth.security import check_auth
from utils.layout import aplicar_estilo_corporativo

# Configuração e Layout Permanente
st.set_page_config(page_title="Configurações", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito.")
    st.stop()

st.title("⚙️ Gestão de Acessos")

t1, t2 = st.tabs(["Lista", "Novo"])

with t1:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name, username, role, can_edit_tasks FROM users", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

with t2:
    with st.form("user"):
        n = st.text_input("Nome")
        u = st.text_input("Login")
        p = st.text_input("Senha", type="password")
        r = st.selectbox("Perfil", ["colaborador", "admin"])
        edit = st.checkbox("Pode editar tarefas?")
        
        if st.form_submit_button("Criar"):
            hashed = bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
            conn = sqlite3.connect(DB_PATH)
            conn.execute("INSERT INTO users (name, username, password_hash, role, can_edit_tasks) VALUES (?,?,?,?,?)",
                        (n, u, hashed, r, 1 if edit else 0))
            conn.commit(); conn.close()
            st.success("Usuário criado com sucesso!")
            time.sleep(1)
            st.rerun()
