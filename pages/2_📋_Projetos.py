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

# Configuração de Página e Estilo
st.set_page_config(page_title="Projetos", page_icon="🏢", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

if not st.session_state.get('logged_in'):
    st.error("⚠️ Faça login na barra lateral para acessar o workspace.")
    st.stop()

user_id = st.session_state['user_id']
user_role = st.session_state['role']
can_edit = st.session_state.get('can_edit_tasks', False)

# --- FUNÇÕES DE BANCO ---
def get_projects():
    conn = sqlite3.connect(DB_PATH)
    if user_role == 'admin':
        df = pd.read_sql_query("SELECT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id", conn)
    else:
        df = pd.read_sql_query("""
            SELECT DISTINCT p.*, u.name as manager_name FROM projects p
            LEFT JOIN users u ON p.manager_id = u.id
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.manager_id = ? OR t.assignee_id = ?
        """, conn, params=(user_id, user_id))
    conn.close()
    return df

def get_tasks(pid):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.project_id = ?", conn, params=(pid,))
    conn.close()
    return df

def get_users_list():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    return dict(zip(df['id'], df['name']))

# --- NAVEGAÇÃO INTERNA ---
if 'selected_project_id' not in st.session_state:
    st.session_state['selected_project_id'] = None

# VISÃO 1: PORTFÓLIO (CARDS)
if st.session_state['selected_project_id'] is None:
    st.title("🏢 Portfólio de Projetos")
    df_p = get_projects()
    
    if df_p.empty:
        st.info("Nenhum projeto encontrado para o seu perfil.")
    else:
        cols = st.columns(3)
        for idx, row in df_p.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {row['code']}")
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"Status: {row['status']} | Gestor: {row['manager_name']}")
                    if st.button("Abrir Workspace ➔", key=f"btn_{row['id']}", use_container_width=True):
                        st.session_state['selected_project_id'] = row['id']
                        st.session_state['selected_project_data'] = row.to_dict()
                        st.rerun()

# VISÃO 2: SALA DO PROJETO
else:
    p_data = st.session_state['selected_project_data']
    pid = p_data['id']
    sla = calcular_sla_projeto(pid)

    col_back, col_title, col_st = st.columns([1, 6, 3])
    col_back.button("⬅ Voltar", on_click=lambda: st.session_state.update({'selected_project_id': None}))
    
    with col_title:
        st.title(f"{p_data['code']} - {p_data['name']}")
        st.caption(f"Prazo: {p_data['due_date']} | ⏱️ SLA Resposta: **{sla if sla else '0.0'}h**")

    with col_st:
        # SELETOR DE STATUS DO PROJETO
        status_opts = ["Não Iniciado", "Em Planejamento", "Em Execução", "Aguardando Aprovação", "Pausado / Bloqueado", "Concluído", "Cancelado"]
        curr_st = p_data['status']
        if curr_st not in status_opts: status_opts.append(curr_st)
        
        new_st = st.selectbox("Status Atual do Projeto:", status_opts, index=status_opts.index(curr_st))
        if new_st != curr_st:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE projects SET status = ? WHERE id = ?", (new_st, pid))
            if new_st == "Concluído":
                conn.execute("UPDATE projects SET real_end_date = ? WHERE id = ?", (datetime.now().strftime('%Y-%m-%d'), pid))
            conn.commit(); conn.close()
            st.session_state['selected_project_data']['status'] = new_st
            st.rerun()

    # BOTÃO EXCLUIR (ADMIN APENAS)
    if user_role == 'admin':
        if st.button("🗑️ Excluir Projeto Permanentemente", type="secondary"):
            conn = sqlite3.connect(DB_PATH)
            conn.execute("DELETE FROM tasks WHERE project_id = ?", (pid,))
            conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
            conn.commit(); conn.close()
            st.session_state['selected_project_id'] = None
            st.rerun()

    st.divider()

    tab_k, tab_d = st.tabs(["🗂️ Kanban & Chat", "📊 Documentação do Escopo"])

    with tab_k:
        df_tasks = get_tasks(pid)
        users = get_users_list()

        # Criar Nova Tarefa (Admin ou Permissão)
        if user_role == 'admin' or can_edit:
            with st.expander("➕ Nova Tarefa"):
                with st.form("f_task", clear_on_submit=True):
                    t_title = st.text_input("Título*")
                    t_desc = st.text_area("Descrição")
                    t_assign = st.selectbox("Responsável", list(users.keys()), format_func=lambda x: users[x])
                    t_due = st.date_input("Prazo")
                    if st.form_submit_button("Salvar Tarefa") and t_title:
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("INSERT INTO tasks (project_id, title, description, assignee_id, due_date) VALUES (?,?,?,?,?)",
                                    (pid, t_title, t_desc, t_assign, t_due))
                        conn.commit(); conn.close(); st.rerun()

        # COLUNAS KANBAN
        c_todo, c_doing, c_done = st.columns(3)
        cols_map = {"To Do": c_todo, "Doing": c_doing, "Done": c_done}
        
        for status_label, col_obj in cols_map.items():
            with col_obj:
                st.markdown(f"#### {status_label}")
                tasks_subset = df_tasks[df_tasks['status'] == status_label]
                for _, t in tasks_subset.iterrows():
                    with st.container(border=True):
                        st.write(f"**{t['title']}**")
                        st.caption(f"👤 {t['assignee_name']} | 📅 {t['due_date']}")
                        
                        # AÇÕES DA TAREFA
                        c_move, c_chat, c_edit = st.columns(3)
                        
                        # 1. Mover
                        m_val = c_move.selectbox("Ir:", ["To Do", "Doing", "Done"], index=["To Do", "Doing", "Done"].index(t['status']), key=f"m_{t['id']}", label_visibility="collapsed")
                        if m_val != t['status']:
                            conn = sqlite3.connect(DB_PATH); conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (m_val, t['id'])); conn.commit(); conn.close(); st.rerun()
                        
                        # 2. Abrir Chat
                        if c_chat.button("💬", key=f"chat_b_{t['id']}"):
                            st.session_state[f"show_chat_{t['id']}"] = not st.session_state.get(f"show_chat_{t['id']}", False)
                            st.session_state[f"show_edit_{t['id']}"] = False

                        # 3. Editar (Permissão)
                        if user_role == 'admin' or can_edit:
                            if c_edit.button("✏️", key=f"edit_b_{t['id']}"):
                                st.session_state[f"show_edit_{t['id']}"] = not st.session_state.get(f"show_edit_{t['id']}", False)
                                st.session_state[f"show_chat_{t['id']}"] = False

                        # ÁREAS EXPANSÍVEIS
                        if st.session_state.get(f"show_edit_{t['id']}", False):
                            with st.form(f"edit_f_{t['id']}"):
                                new_tt = st.text_input("Título", value=t['title'])
                                new_ds = st.text_area("Descrição", value=t['description'] if t['description'] else "")
                                new_as = st.selectbox("Responsável", list(users.keys()), index=list(users.keys()).index(t['assignee_id']) if t['assignee_id'] in users else 0, format_func=lambda x: users[x])
                                if st.form_submit_button("Salvar Alterações"):
                                    conn = sqlite3.connect(DB_PATH)
                                    conn.execute("UPDATE tasks SET title=?, description=?, assignee_id=? WHERE id=?", (new_tt, new_ds, new_as, t['id']))
                                    conn.commit(); conn.close(); st.rerun()

                        if st.session_state.get(f"show_chat_{t['id']}", False):
                            conn = sqlite3.connect(DB_PATH)
                            chats = pd.read_sql_query("SELECT c.*, u.name FROM task_chats c JOIN users u ON c.user_id = u.id WHERE task_id = ? ORDER BY created_at ASC", conn, params=(t['id'],))
                            conn.close()
                            for _, msg in chats.iterrows():
                                st.markdown(f"**{msg['name']}**: {msg['message']}")
                            with st.form(f"chat_f_{t['id']}", clear_on_submit=True):
                                m_txt = st.text_area("Mensagem")
                                if st.form_submit_button("Enviar"):
                                    conn = sqlite3.connect(DB_PATH); conn.execute("INSERT INTO task_chats (task_id, user_id, message) VALUES (?,?,?)", (t['id'], user_id, m_txt)); conn.commit(); conn.close(); st.rerun()

    with tab_d:
        st.info("Aqui você visualiza os detalhes estratégicos preenchidos na criação do projeto.")
        conn = sqlite3.connect(DB_PATH)
        if p_data['type'] == 'Melhoria':
            det = pd.read_sql_query("SELECT * FROM project_melhoria WHERE project_id = ?", conn, params=(pid,))
            if not det.empty: st.write(det.iloc[0].to_dict())
        else:
            det = pd.read_sql_query("SELECT * FROM project_implantacao WHERE project_id = ?", conn, params=(pid,))
            if not det.empty: st.write(det.iloc[0].to_dict())
        conn.close()
