import streamlit as st
import sqlite3
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from auth.security import check_auth
from utils.layout import aplicar_estilo_corporativo

# Configuração e Layout Permanente
st.set_page_config(page_title="Novo Projeto", page_icon="➕", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito.")
    st.stop()

st.title("🚀 Lançar Novo Projeto")

with st.form("new_project"):
    c1, c2 = st.columns(2)
    name = c1.text_input("Nome do Projeto*")
    tipo = c2.selectbox("Tipo", ["Melhoria", "Implantação"])
    
    req = st.text_input("Área Solicitante*")
    
    if st.form_submit_button("Criar Projeto"):
        if name and req:
            conn = sqlite3.connect(DB_PATH)
            # Código HR-XXX automático
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM projects")
            code = f"HR-{cur.fetchone()[0]+1:03d}"
            
            cur.execute("INSERT INTO projects (code, name, requester, type, status) VALUES (?,?,?,?,?)",
                       (code, name, req, tipo, "Não Iniciado"))
            conn.commit(); conn.close()
            st.success(f"Projeto {code} criado com sucesso!")
        else:
            st.error("Preencha os campos obrigatórios.")
