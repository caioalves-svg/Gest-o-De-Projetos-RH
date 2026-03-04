import streamlit as st
import sqlite3
import pandas as pd
from utils.layout import aplicar_estilo_corporativo
from services.kpi_service import calcular_sla_projeto
from database.setup import DB_PATH

st.set_page_config(page_title="Projetos", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

if not st.session_state.get('logged_in'):
    st.error("Por favor, faça login na lateral.")
    st.stop()

# ... (Lógica de carregar projetos e tarefas aqui)
# No loop do Kanban, adicione a trava de edição:
if st.session_state.get('can_edit_tasks') or st.session_state['role'] == 'admin':
    if st.button("✏️ Editar", key=f"ed_{task_id}"):
        # Abre formulário de edição
        pass
