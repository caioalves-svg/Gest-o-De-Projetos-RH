import streamlit as st

# 1. CONFIGURAÇÃO (Sempre a primeira linha)
st.set_page_config(page_title="Gestão de Projetos RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

import sqlite3
import pandas as pd
from datetime import datetime
from database.setup import init_db, DB_PATH
from auth.security import login
from utils.layout import aplicar_css_seguro, renderizar_menu_lateral

# Inicializa Banco e Estado
init_db()
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'tela_atual' not in st.session_state: st.session_state['tela_atual'] = 'home'
if 'selected_project_id' not in st.session_state: st.session_state['selected_project_id'] = None

aplicar_css_seguro()

# ==========================================
# GATEWAY DE LOGIN
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center;'>⚡ Projetos RH</h2>", unsafe_allow_html=True)
        with st.form("form_login"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Workspace", use_container_width=True):
                if login(username, password): st.rerun()
                else: st.error("❌ Credenciais incorretas.")

# ==========================================
# SISTEMA OPERACIONAL (SPA)
# ==========================================
else:
    renderizar_menu_lateral()
    tela = st.session_state['tela_atual']

    # --- TELA: HOME ---
    if tela == 'home':
        st.title("🏠 Bem-vindo ao seu Workspace")
        st.success("✅ O sistema está online. Utilize o menu à esquerda para navegar.")

    # --- TELA: WORKSPACE DE PROJETOS E KANBAN ---
    elif tela == 'projetos':
        user_id = st.session_state['user_id']
        user_role = st.session_state['role']
        
        # VISÃO 1: PORTFÓLIO
        if st.session_state['selected_project_id'] is None:
            st.title("🏢 Portfólio de Projetos")
            conn = sqlite3.connect(DB_PATH)
            if user_role == 'admin':
                df_p = pd.read_sql_query("SELECT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id", conn)
            else:
                df_p = pd.read_sql_query(f"SELECT DISTINCT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id LEFT JOIN tasks t ON p.id = t.project_id WHERE p.manager_id = {user_id} OR t.assignee_id = {user_id}", conn)
            conn.close()

            if df_p.empty:
                st.info("Nenhum projeto encontrado para o seu perfil.")
            else:
                cols = st.columns(3)
                for idx, row in df_p.iterrows():
                    with cols[idx % 3]:
                        with st.container(border=True):
                            st.markdown(f"### {row['code']}")
                            st.write(f"**{row['name']}**")
                            st.caption(f"Status: {row['status']} | Gestor: {row['manager_name']}")
                            if st.button("Abrir Kanban ➔", key=f"abrir_{row['id']}", use_container_width=True):
                                st.session_state['selected_project_id'] = row['id']
                                st.session_state['selected_project_data'] = row.to_dict()
                                st.rerun()

        # VISÃO 2: SALA DO PROJETO (KANBAN REAL)
        else:
            p_data = st.session_state['selected_project_data']
            pid = p_data['id']

            c1, c2 = st.columns([1, 8])
            if c1.button("⬅ Voltar"):
                st.session_state['selected_project_id'] = None
                st.rerun()
            c2.title(f"{p_data['code']} - {p_data['name']}")
            st.divider()

            # Formulário Rápido de Tarefa
            if user_role == 'admin' or st.session_state.get('can_edit_tasks'):
                with st.expander("➕ Nova Tarefa"):
                    with st.form("nova_tarefa", clear_on_submit=True):
                        t_titulo = st.text_input("Título da Tarefa*")
                        if st.form_submit_button("Adicionar ao To Do"):
                            if t_titulo:
                                conn = sqlite3.connect(DB_PATH)
                                conn.execute("INSERT INTO tasks (project_id, title, assignee_id, status) VALUES (?, ?, ?, 'To Do')", (pid, t_titulo, user_id))
                                conn.commit(); conn.close(); st.rerun()

            # Renderização das Colunas do Kanban
            conn = sqlite3.connect(DB_PATH)
            df_tasks = pd.read_sql_query("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.project_id = ?", conn, params=(pid,))
            conn.close()

            col_todo, col_doing, col_done = st.columns(3)
            colunas_map = {"To Do": col_todo, "Doing": col_doing, "Done": col_done}

            for status_col, col_obj in colunas_map.items():
                with col_obj:
                    st.markdown(f"<h4 style='text-align: center; color: #475569;'>{status_col}</h4>", unsafe_allow_html=True)
                    tasks_status = df_tasks[df_tasks['status'] == status_col]
                    for _, t in tasks_status.iterrows():
                        with st.container(border=True):
                            st.write(f"**{t['title']}**")
                            # Mover Tarefa
                            novo_st = st.selectbox("Mover para:", ["To Do", "Doing", "Done"], index=["To Do", "Doing", "Done"].index(t['status']), key=f"move_{t['id']}", label_visibility="collapsed")
                            if novo_st != t['status']:
                                conn = sqlite3.connect(DB_PATH)
                                conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (novo_st, t['id']))
                                conn.commit(); conn.close(); st.rerun()

    # --- TELA: NOVO PROJETO ---
    elif tela == 'novo_projeto':
        st.title("🚀 Iniciar Novo Projeto")
        if st.session_state.get('role') != 'admin':
            st.error("🔒 Acesso restrito a administradores.")
        else:
            with st.form("form_novo_proj", clear_on_submit=True):
                nome = st.text_input("Nome do Projeto*")
                tipo = st.selectbox("Tipo", ["Melhoria", "Implantação"])
                req = st.text_input("Área Solicitante*")
                if st.form_submit_button("Lançar no Portfólio"):
                    if nome and req:
                        conn = sqlite3.connect(DB_PATH)
                        cur = conn.cursor()
                        cur.execute("SELECT COUNT(*) FROM projects")
                        code = f"HR-{cur.fetchone()[0] + 1:03d}"
                        cur.execute("INSERT INTO projects (code, name, requester, type, status, manager_id) VALUES (?,?,?,?,?,?)", (code, nome, req, tipo, 'Não Iniciado', st.session_state['user_id']))
                        conn.commit(); conn.close()
                        st.success(f"Projeto {code} criado com sucesso!")
                    else:
                        st.error("Preencha os campos obrigatórios.")

    # --- TELA: DASHBOARD E CONFIG ---
    elif tela == 'dashboard':
        st.title("📊 Dashboard Executivo")
        st.info("Métricas gerais operantes.")
    elif tela == 'configuracoes':
        st.title("⚙️ Configurações")
        st.info("Gestão de acessos operante.")
