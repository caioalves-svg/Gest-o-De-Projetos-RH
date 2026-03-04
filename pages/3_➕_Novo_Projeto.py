import streamlit as st
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from auth.security import check_auth
from utils.layout import aplicar_estilo_corporativo

# Configuração e Layout
st.set_page_config(page_title="Novo Projeto", page_icon="➕", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Apenas administradores podem cadastrar novos projetos.")
    st.stop()

st.title("🚀 Iniciar Novo Projeto")
st.markdown("Preencha os dados abaixo para registrar a nova iniciativa.")

def get_users():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    return dict(zip(df['id'], df['name']))

import pandas as pd

users = get_users()

with st.form("form_new_project", clear_on_submit=True):
    col1, col2 = st.columns(2)
    p_name = col1.text_input("Nome do Projeto*")
    p_type = col2.selectbox("Tipo de Projeto", ["Melhoria", "Implantação"])
    
    col3, col4 = st.columns(2)
    p_req = col3.text_input("Área Solicitante*")
    p_sponsor = col4.text_input("Sponsor Executivo*")
    
    col5, col6 = st.columns(2)
    p_manager = col5.selectbox("Gestor Responsável", list(users.keys()), format_func=lambda x: users[x])
    p_due = col6.date_input("Prazo Final Estimado")
    
    st.divider()
    st.markdown("### Escopo Específico")
    
    if p_type == "Melhoria":
        as_is = st.text_area("Cenário Atual (As-Is)")
        to_be = st.text_area("Cenário Desejado (To-Be)")
    else:
        just = st.text_area("Justificativa do Projeto")
        risk = st.text_area("Principais Riscos")

    if st.form_submit_button("🚀 Lançar Projeto no Portfólio"):
        if not p_name or not p_req:
            st.error("Campos obrigatórios faltando.")
        else:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            # Gerar Código Automático
            cur.execute("SELECT COUNT(*) FROM projects")
            code = f"HR-{cur.fetchone()[0] + 1:03d}"
            
            # Inserir Base
            cur.execute("""INSERT INTO projects (code, name, requester, sponsor, manager_id, type, due_date, status, start_date) 
                           VALUES (?,?,?,?,?,?,?,?,?)""", 
                        (code, p_name, p_req, p_sponsor, p_manager, p_type, p_due, 'Não Iniciado', datetime.now().strftime('%Y-%m-%d')))
            
            last_id = cur.lastrowid
            # Inserir Detalhes
            if p_type == "Melhoria":
                cur.execute("INSERT INTO project_melhoria (project_id, as_is, to_be) VALUES (?,?,?)", (last_id, as_is, to_be))
            else:
                cur.execute("INSERT INTO project_implantacao (project_id, justification, risk) VALUES (?,?,?)", (last_id, just, risk))
                
            conn.commit(); conn.close()
            st.success(f"Projeto {code} criado com sucesso!")
