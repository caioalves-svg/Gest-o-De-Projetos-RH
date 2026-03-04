import streamlit as st

# DEVE SER A PRIMEIRA LINHA - Força o menu a ficar expandido
st.set_page_config(page_title="Novo Projeto", layout="wide", initial_sidebar_state="expanded")

import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

# Ajuste de paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from utils.layout import aplicar_estilo_corporativo

# Aplica o layout e o menu lateral (faz a verificação de login automaticamente)
aplicar_estilo_corporativo()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito a administradores.")
    st.stop()

st.title("🚀 Iniciar Novo Projeto")
st.markdown("---")

def get_users():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    return dict(zip(df['id'], df['name']))

users_dict = get_users()

with st.form("form_new_project", clear_on_submit=True):
    col1, col2 = st.columns(2)
    p_name = col1.text_input("Nome do Projeto*")
    p_type = col2.selectbox("Tipo de Projeto", ["Melhoria", "Implantação"])
    
    col3, col4 = st.columns(2)
    p_req = col3.text_input("Área Solicitante*")
    p_sponsor = col4.text_input("Sponsor Executivo*")
    
    col5, col6 = st.columns(2)
    p_manager = col5.selectbox("Gestor Responsável", list(users_dict.keys()), format_func=lambda x: users_dict[x])
    p_due = col6.date_input("Prazo Final Estimado")
    
    st.divider()
    
    if p_type == "Melhoria":
        as_is = st.text_area("Cenário Atual (As-Is)")
        to_be = st.text_area("Cenário Desejado (To-Be)")
    else:
        just = st.text_area("Justificativa")
        risk = st.text_area("Risco")

    if st.form_submit_button("Lançar Projeto"):
        if p_name and p_req:
            conn = sqlite3.connect(DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM projects")
            code = f"HR-{cur.fetchone()[0] + 1:03d}"
            
            cur.execute("""INSERT INTO projects (code, name, requester, sponsor, manager_id, type, due_date, status, start_date) 
                           VALUES (?,?,?,?,?,?,?,?,?)""", 
                        (code, p_name, p_req, p_sponsor, p_manager, p_type, p_due, 'Não Iniciado', datetime.now().strftime('%Y-%m-%d')))
            
            conn.commit()
            conn.close()
            st.success(f"Projeto {code} criado!")
