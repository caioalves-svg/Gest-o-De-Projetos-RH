import streamlit as st
import sqlite3
import pandas as pd
import bcrypt
import os
import sys
import time  # Importante para a pausa da mensagem de sucesso

# Ajuste de path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from auth.security import check_auth

# Verificação de Segurança
check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito. Apenas administradores podem gerenciar usuários.")
    st.stop()

st.set_page_config(page_title="Configurações - HR", page_icon="⚙️", layout="wide")
st.title("⚙️ Configurações e Acessos")

st.subheader("👥 Gestão de Usuários (Admin / Colaboradores)")

tab_list, tab_create = st.tabs(["📋 Lista de Usuários", "➕ Cadastrar Novo Usuário"])

# ABA 1: LISTAGEM
with tab_list:
    conn = sqlite3.connect(DB_PATH)
    df_users = pd.read_sql_query("SELECT id, name, username, role FROM users", conn)
    conn.close()
    
    st.dataframe(
        df_users, 
        column_config={
            "id": "ID",
            "name": "Nome Completo",
            "username": "Login",
            "role": "Perfil de Acesso"
        },
        hide_index=True,
        use_container_width=True
    )

# ABA 2: CRIAÇÃO
with tab_create:
    with st.container(border=True):
        with st.form("new_user_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            new_name = col1.text_input("Nome Completo*")
            new_username = col2.text_input("Nome de Usuário (Login)*")
            
            col3, col4 = st.columns(2)
            new_password = col3.text_input("Senha*", type="password")
            new_role = col4.selectbox("Perfil de Acesso*", ["colaborador", "admin"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            submit_user = st.form_submit_button("Criar Usuário", type="primary")
            
            if submit_user:
                if not new_name or not new_username or not new_password:
                    st.error("Preencha todos os campos obrigatórios.")
                else:
                    try:
                        # Gerar Hash da nova senha
                        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                        
                        conn = sqlite3.connect(DB_PATH)
                        cursor = conn.cursor()
                        cursor.execute(
                            "INSERT INTO users (username, password_hash, name, role) VALUES (?, ?, ?, ?)",
                            (new_username, hashed_pw, new_name, new_role)
                        )
                        conn.commit()
                        conn.close()
                        
                        # Mensagem exata solicitada e pausa para leitura
                        st.success("Usuário criado com sucesso!")
                        time.sleep(1.5)  # Congela a tela por 1.5 segundos para o usuário ler a mensagem
                        st.rerun()       # Recarrega para limpar o form e atualizar a lista
                        
                    except sqlite3.IntegrityError:
                        st.error("Erro: Este Nome de Usuário (Login) já existe. Escolha outro.")
