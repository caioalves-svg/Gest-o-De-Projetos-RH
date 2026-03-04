import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    if st.session_state.get('role') != 'admin':
        st.error("🔒 Acesso restrito a administradores.")
        return

    st.title("⚙️ Gestão de Usuários e Acessos")
    st.markdown("---")

    tab_lista, tab_novo = st.tabs(["📋 Usuários Cadastrados", "➕ Criar Novo Usuário"])

    with tab_lista:
        conn = sqlite3.connect(DB_PATH)
        df_users = pd.read_sql_query("SELECT id, name, username, role, can_edit_tasks FROM users", conn)
        conn.close()
        
        df_users['can_edit_tasks'] = df_users['can_edit_tasks'].apply(lambda x: "Sim" if x else "Não")
        df_users['role'] = df_users['role'].str.upper()
        df_users.columns = ["ID", "Nome Completo", "Login", "Perfil", "Pode Editar Tarefas?"]
        
        st.dataframe(df_users, use_container_width=True, hide_index=True)

    with tab_novo:
        with st.form("form_new_user", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Nome Completo*")
            user = col2.text_input("Login/Username*")
            
            col3, col4 = st.columns(2)
            passw = col3.text_input("Senha*", type="password")
            role = col4.selectbox("Perfil de Acesso", ["colaborador", "admin"])
            
            p_edit = st.checkbox("Permitir que este usuário edite tarefas (Título/Prazo)?")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Salvar Novo Usuário"):
                if name and user and passw:
                    try:
                        hashed = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        can_edit = 1 if p_edit or role == 'admin' else 0 
                        
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("INSERT INTO users (username, password_hash, name, role, can_edit_tasks) VALUES (?,?,?,?,?)",
                                    (user, hashed, name, role, can_edit))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Usuário '{name}' criado com sucesso!")
                    except sqlite3.IntegrityError:
                        st.error("❌ Erro: Este Login já existe.")
                    except Exception as e:
                        st.error(f"❌ Erro: {e}")
                else:
                    st.error("⚠️ Preencha todos os campos obrigatórios (*).")
