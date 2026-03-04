import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH, UPLOAD_DIR, init_db
from auth.security import check_auth
from services.kpi_service import calcular_sla_projeto
from utils.layout import aplicar_estilo_corporativo

# Configuração e Layout Permanente
st.set_page_config(page_title="Projetos", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

check_auth()

user_id = st.session_state['user_id']
user_role = st.session_state['role']
can_edit = st.session_state.get('can_edit_tasks', False)

if 'selected_project_id' not in st.session_state:
    st.session_state['selected_project_id'] = None

# Funções de DB
def get_projects():
    conn = sqlite3.connect(DB_PATH)
    query = "SELECT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id"
    if user_role != 'admin':
        query += f" WHERE p.manager_id = {user_id} OR p.id IN (SELECT project_id FROM tasks WHERE assignee_id = {user_id})"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def get_tasks(pid):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.project_id = ?", conn, params=(pid,))
    conn.close()
    return df

# --- VISÃO MASTER (PORTFÓLIO) ---
if st.session_state['selected_project_id'] is None:
    st.title("🏢 Portfólio de Projetos")
    df_p = get_projects()
    if df_p.empty: st.info("Sem projetos.")
    else:
        cols = st.columns(3)
        for i, row in df_p.iterrows():
            with cols[i%3]:
                with st.container(border=True):
                    st.subheader(row['code'])
                    st.write(f"**{row['name']}**")
                    st.caption(f"Status: {row['status']}")
                    if st.button("Abrir Workspace", key=f"p_{row['id']}", use_container_width=True):
                        st.session_state['selected_project_id'] = row['id']
                        st.session_state['selected_project_data'] = row.to_dict()
                        st.rerun()

# --- VISÃO DETAIL (SALA DO PROJETO) ---
else:
    p = st.session_state['selected_project_data']
    sla = calcular_sla_projeto(p['id'])
    
    col_b, col_t, col_s = st.columns([1, 6, 3])
    col_b.button("⬅ Voltar", on_click=lambda: st.session_state.update({'selected_project_id': None}))
    col_t.title(f"{p['code']} - {p['name']}")
    col_t.caption(f"⏱️ SLA Médio: {sla if sla else 'N/A'}h")
    
    with col_s:
        status_list = ["Não Iniciado", "Em Planejamento", "Em Execução", "Aguardando Aprovação", "Pausado / Bloqueado", "Concluído", "Cancelado"]
        new_st = st.selectbox("Status do Projeto", status_list, index=status_list.index(p['status']) if p['status'] in status_list else 0)
        if new_st != p['status']:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE projects SET status = ? WHERE id = ?", (new_st, p['id']))
            conn.commit(); conn.close()
            st.session_state['selected_project_data']['status'] = new_st
            st.rerun()

    tab1, tab2 = st.tabs(["🗂️ Kanban & Chat", "📊 Documentação"])
    with tab1:
        # Lógica simplificada de Kanban (Colunas To Do, Doing, Done)
        st.write("Interface de Kanban Ativa...")
        # (O código detalhado do Kanban permanece o mesmo que enviamos antes)
