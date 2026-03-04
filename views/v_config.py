import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import os
import sys

# Garante que ele encontra os ficheiros da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    if st.session_state.get('role') != 'admin':
        st.error("🔒 Acesso restrito a administradores.")
        return

    st.title("⚙️ Gestão de Usuários e Acessos")

    # Separador de Abas para Organização
    tab_lista, tab_novo = st.tabs(["📋 Usuários Cadastrados", "➕ Criar Novo Usuário"])

    # ABA 1: LISTAGEM DE USUÁRIOS
    with tab_lista:
        conn = sqlite3.connect(DB_PATH)
        df_users = pd.read_sql_query("SELECT id, name, username, role, can_edit_tasks FROM users", conn)
        conn.close()
        
        # Formatação para ficar mais elegante na tabela
        df_users['can_edit_tasks'] = df_users['can_edit_tasks'].apply(lambda x: "Sim" if x else "Não")
        df_users['role'] = df_users['role'].str.upper()
        df_users.columns = ["ID", "Nome Completo", "Login", "Perfil", "Pode Editar Tarefas?"]
        
        st.dataframe(df_users, use_container_width=True, hide_index=True)

    # ABA 2: CRIAÇÃO DE USUÁRIOS
    with tab_novo:
        with st.form("form_new_user", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("Nome Completo*")
            user = col2.text_input("Login/Username*")
            
            col3, col4 = st.columns(2)
            passw = col3.text_input("Senha*", type="password")
            role = col4.selectbox("Perfil de Acesso", ["colaborador", "admin"])
            
            # Permissão extra para colaboradores normais poderem editar títulos e prazos
            p_edit = st.checkbox("Permitir que este usuário edite tarefas de outros (Título/Prazo)?")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.form_submit_button("Salvar Novo Usuário"):
                if name and user and passw:
                    try:
                        # Encriptação da senha por segurança
                        hashed = bcrypt.hashpw(passw.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        
                        # Administradores têm sempre permissão de edição
                        can_edit = 1 if p_edit or role == 'admin' else 0 
                        
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("INSERT INTO users (username, password_hash, name, role, can_edit_tasks) VALUES (?,?,?,?,?)",
                                    (user, hashed, name, role, can_edit))
                        conn.commit()
                        conn.close()
                        st.success(f"✅ Usuário '{name}' criado com sucesso! Ele já pode aceder ao sistema.")
                    except sqlite3.IntegrityError:
                        st.error("❌ Erro: Este Login/Username já existe na base de dados.")
                    except Exception as e:
                        st.error(f"❌ Erro crítico ao criar utilizador: {e}")
                else:
                    st.error("⚠️ Por favor, preencha todos os campos obrigatórios (*).")
