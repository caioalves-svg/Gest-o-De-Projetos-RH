import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from auth.security import check_auth

check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito. Apenas administradores podem gerenciar usuários.")
    st.stop()

st.set_page_config(page_title="Configurações - HR", page_icon="⚙️", layout="wide")
st.title("⚙️ Configurações e Acessos")

st.subheader("👥 Gestão de Usuários (Admin / Colaboradores)")

tab_list, tab_create = st.tabs(["📋 Lista de Usuários", "➕ Cadastrar Novo Usuário"])

with tab_list:
    conn = sqlite3.connect(DB_PATH)
    # Mostra a coluna de permissão na tabela
    df_users = pd.read_sql_query("SELECT id, name, username, role, can_edit_tasks FROM users", conn)
    conn.close()
    
    df_users['can_edit_tasks'] = df_users['can_edit_tasks'].apply(lambda x: "Sim" if x else "Não")
    
    st.dataframe(
        df_users, 
        column_config={"id": "ID", "name": "Nome", "username": "Login", "role": "Perfil", "can_edit_tasks": "Pode Editar Tarefas?"},
        hide_index=True, use_container_width=True
    )

with tab_create:
    with st.container(border=True):
        with st.form("new_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Nome Completo*")
            new_username = col2.text_input("Nome de Usuário (Login)*")
            
            col3, col4 = st.columns(2)
            new_password = col3.text_input("Senha*", type="password")
            new_role = col4.selectbox("Perfil de Acesso*", ["colaborador", "admin"])
            
            # A NOVA PERMISSÃO AQUI
            can_edit = st.checkbox("🔑 Conceder permissão para Editar Tarefas (Título, Prazo, Responsável)")
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_user = st.form_submit_button("Criar Usuário", type="primary")
            
            if submit_user:
                if not new_name or not new_username or not new_password:
                    st.error("Preencha todos os campos obrigatórios.")
                else:
                    try:
                        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        is_admin_edit = 1 if new_role == 'admin' else (1 if can_edit else 0)
                        
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute(
                            "INSERT INTO users (username, password_hash, name, role, can_edit_tasks) VALUES (?, ?, ?, ?, ?)",
                            (new_username, hashed_pw, new_name, new_role, is_admin_edit)
                        )
                        conn.commit()
                        conn.close()
                        
                        st.success("Usuário criado com sucesso!")
                        time.sleep(1.5)
                        st.rerun()
                        
                    except sqlite3.IntegrityError:
                        st.error("Erro: Este Login já existe.")
