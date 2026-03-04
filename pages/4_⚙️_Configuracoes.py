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

# Configuração e Layout
st.set_page_config(page_title="Configurações", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito a administradores.")
    st.stop()

st.title("⚙️ Gestão de Usuários e Acessos")

tab_l, tab_n = st.tabs(["📋 Usuários Cadastrados", "➕ Criar Novo Usuário"])

with tab_l:
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name, username, role, can_edit_tasks FROM users", conn)
    conn.close()
    st.dataframe(df, use_container_width=True, hide_index=True)

with tab_n:
    with st.form("new_user", clear_on_submit=True):
        name = st.text_input("Nome Completo*")
        user = st.text_input("Login/Username*")
        passw = st.text_input("Senha*", type="password")
        role = st.selectbox("Perfil", ["colaborador", "admin"])
        p_edit = st.checkbox("Permitir que este usuário edite tarefas (Título/Prazo)?")
        
        if st.form_submit_button("Salvar Usuário"):
            if name and user and passw:
                try:
                    hashed = bcrypt.hashpw(passw.encode(), bcrypt.gensalt()).decode()
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("INSERT INTO users (username, password_hash, name, role, can_edit_tasks) VALUES (?,?,?,?,?)",
                                (user, hashed, name, role, 1 if p_edit or role == 'admin' else 0))
                    conn.commit(); conn.close()
                    st.success("Usuário criado com sucesso!")
                    time.sleep(1.5)
                    st.rerun()
                except:
                    st.error("Erro: Usuário já existe.")
            else:
                st.error("Preencha todos os campos.")
