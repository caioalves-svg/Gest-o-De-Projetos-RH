import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    st.title("➕ Iniciar Novo Projeto")
    st.markdown("<p style='color: #64748B;'>Registe uma nova iniciativa estratégica no portfólio.</p>", unsafe_allow_html=True)
    st.markdown("---")
    
    if st.session_state.get('role') != 'admin':
        st.error("🔒 Acesso restrito a administradores.")
        return

    conn = sqlite3.connect(DB_PATH)
    users_df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    users_dict = dict(zip(users_df['id'], users_df['name']))

    with st.form("form_novo_proj", clear_on_submit=True):
        col1, col2 = st.columns(2)
        nome = col1.text_input("Nome do Projeto*")
        tipo = col2.selectbox("Tipo de Iniciativa", ["Melhoria", "Implantação"])
        
        col3, col4 = st.columns(2)
        req = col3.text_input("Área Solicitante*")
        sponsor = col4.text_input("Sponsor Executivo")
        
        col5, col6 = st.columns(2)
        manager = col5.selectbox("Gestor Responsável", list(users_dict.keys()), format_func=lambda x: users_dict[x])
        due_date = col6.date_input("Prazo Desejado")

        st.divider()
        st.markdown("### Escopo Específico")
        if tipo == "Melhoria":
            as_is = st.text_area("Cenário Atual (As-Is)")
            to_be = st.text_area("Cenário Desejado (To-Be)")
        else:
            just = st.text_area("Justificativa da Implantação")
            risk = st.text_area("Principais Riscos")

        st.markdown("<br>", unsafe_allow_html=True)
        if st.form_submit_button("🚀 Lançar Projeto no Portfólio"):
            if nome and req:
                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM projects")
                code = f"HR-{cur.fetchone()[0] + 1:03d}"
                
                cur.execute("""INSERT INTO projects (code, name, requester, sponsor, manager_id, type, due_date, status, start_date) 
                               VALUES (?,?,?,?,?,?,?,?,?)""", 
                            (code, nome, req, sponsor, manager, tipo, due_date, 'Não Iniciado', datetime.now().strftime('%Y-%m-%d')))
                proj_id = cur.lastrowid
                
                if tipo == "Melhoria":
                    cur.execute("INSERT INTO project_melhoria (project_id, as_is, to_be) VALUES (?,?,?)", (proj_id, as_is, to_be))
                else:
                    cur.execute("INSERT INTO project_implantacao (project_id, justification, risk) VALUES (?,?,?)", (proj_id, just, risk))
                
                conn.commit(); conn.close()
                st.success(f"✅ Projeto {code} criado com sucesso! Já está disponível no Workspace.")
            else:
                st.error("⚠️ Preencha os campos obrigatórios (*).")
