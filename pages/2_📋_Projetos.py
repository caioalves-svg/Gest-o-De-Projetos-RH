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

init_db()
check_auth()

st.set_page_config(page_title="Workspace de Projetos", page_icon="🏢", layout="wide")

st.markdown("""
<style>
    .kanban-card { background-color: #ffffff; border-left: 4px solid #3498DB; padding: 15px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 12px; }
    .kanban-card-done { border-left-color: #2ECC71; }
    .kanban-card-doing { border-left-color: #F39C12; }
    .kanban-col-header { font-weight: 600; font-size: 1.1em; padding: 10px; background-color: #f8f9fa; border-radius: 6px; text-align: center; margin-bottom: 15px; }
    .chat-bubble-me { background-color: #DCF8C6; padding: 10px; border-radius: 10px 10px 0px 10px; margin: 5px 0; text-align: right; }
    .chat-bubble-other { background-color: #F1F0F0; padding: 10px; border-radius: 10px 10px 10px 0px; margin: 5px 0; text-align: left; }
    .chat-meta { font-size: 0.8em; color: #666; }
</style>
""", unsafe_allow_html=True)

user_id = st.session_state['user_id']
user_role = st.session_state['role']
can_edit_tasks = st.session_state.get('can_edit_tasks', False)

if 'selected_project_id' not in st.session_state:
    st.session_state['selected_project_id'] = None

def go_back_to_portfolio():
    st.session_state['selected_project_id'] = None
    st.session_state['confirm_delete'] = False

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

def get_project_details(project_id, p_type):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(f"SELECT * FROM project_{p_type.lower().replace('ç', 'c').replace('ã', 'a')} WHERE project_id = ?", conn, params=(project_id,))
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else {}

def get_tasks(project_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.project_id = ?", conn, params=(project_id,))
    conn.close()
    return df

def get_users_dict():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT id, name FROM users", conn)
    conn.close()
    return dict(zip(df['id'], df['name']))

def update_task(task_id, title, desc, assignee_id, due_date):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("UPDATE tasks SET title=?, description=?, assignee_id=?, due_date=? WHERE id=?", (title, desc, assignee_id, due_date, task_id))
    conn.commit()
    conn.close()

if st.session_state['selected_project_id'] is None:
    st.title("🏢 Portfólio de Projetos")
    df_projects = get_projects()
    
    if df_projects.empty:
        st.info("Nenhum projeto encontrado.")
    else:
        cols = st.columns(3)
        for idx, row in df_projects.iterrows():
            with cols[idx % 3]:
                with st.container(border=True):
                    st.markdown(f"### {row['code']}")
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"Status: **{row['status']}**")
                    if st.button("Abrir Projeto ➔", key=f"open_{row['id']}", use_container_width=True):
                        st.session_state['selected_project_id'] = row['id']
                        st.session_state['selected_project_data'] = row.to_dict()
                        st.rerun()
else:
    p_data = st.session_state['selected_project_data']
    p_id = p_data['id']
    sla_proj = calcular_sla_projeto(p_id)
    sla_display = f"{sla_proj} horas" if sla_proj is not None else "Sem histórico"

    col_back, col_title, col_status = st.columns([1, 6, 3])
    with col_back:
        if st.button("⬅ Voltar"):
            go_back_to_portfolio()
            st.rerun()
            
    with col_title:
        st.title(f"[{p_data['code']}] {p_data['name']}")
        st.caption(f"Início: {p_data['start_date']} | Prazo: {p_data['due_date']} | ⏱️ **SLA de Resposta: {sla_display}**")

    with col_status:
        status_opts = ["Não Iniciado", "Em Planejamento", "Em Execução", "Aguardando Aprovação", "Pausado / Bloqueado", "Concluído", "Cancelado"]
        curr_status = p_data['status']
        if curr_status not in status_opts: status_opts.append(curr_status)
        new_status = st.selectbox("Status:", options=status_opts, index=status_opts.index(curr_status))
        
        if new_status != curr_status:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE projects SET status = ? WHERE id = ?", (new_status, p_id))
            if new_status == "Concluído":
                conn.execute("UPDATE projects SET real_end_date = ? WHERE id = ?", (datetime.now().strftime('%Y-%m-%d'), p_id))
            conn.commit()
            conn.close()
            st.session_state['selected_project_data']['status'] = new_status
            st.rerun()

    st.divider()

    tab_kanban, tab_overview = st.tabs(["🗂️ Kanban & Chat", "📊 Visão Geral"])

    with tab_kanban:
        df_tasks = get_tasks(p_id)
        users_dict = get_users_dict()
        
        if user_role == 'admin' or can_edit_tasks:
            with st.expander("➕ Adicionar Nova Tarefa"):
                with st.form("form_new_task"):
                    t_title = st.text_input("Título*")
                    t_desc = st.text_area("Descrição")
                    t_assignee = st.selectbox("Responsável*", options=list(users_dict.keys()), format_func=lambda x: users_dict[x])
                    t_due = st.date_input("Prazo")
                    if st.form_submit_button("Criar Tarefa") and t_title:
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("INSERT INTO tasks (project_id, title, description, assignee_id, due_date) VALUES (?, ?, ?, ?, ?)", (p_id, t_title, t_desc, t_assignee, t_due))
                        conn.commit()
                        conn.close()
                        st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        col_todo, col_doing, col_done = st.columns(3)
        with col_todo: st.markdown("<div class='kanban-col-header'>📝 A Fazer</div>", unsafe_allow_html=True)
        with col_doing: st.markdown("<div class='kanban-col-header'>⏳ Em Progresso</div>", unsafe_allow_html=True)
        with col_done: st.markdown("<div class='kanban-col-header'>✅ Concluído</div>", unsafe_allow_html=True)

        if not df_tasks.empty:
            for _, task in df_tasks.iterrows():
                t_id, t_status = task['id'], task['status']
                target_col = col_todo if t_status == 'To Do' else col_doing if t_status == 'Doing' else col_done
                css_class = "kanban-card" if t_status == 'To Do' else "kanban-card kanban-card-doing" if t_status == 'Doing' else "kanban-card kanban-card-done"
                
                with target_col:
                    st.markdown(f"<div class='{css_class}'><b>{task['title']}</b><br><small>👤 {task['assignee_name']} | 📅 {task['due_date']}</small></div>", unsafe_allow_html=True)
                    
                    # Botões de Interação
                    col_m, col_c, col_e = st.columns([1.2, 1, 1])
                    
                    # 1. Mover (Todos que veem a tarefa podem mover o status dela)
                    new_st = col_m.selectbox("Mover:", ["To Do", "Doing", "Done"], index=["To Do", "Doing", "Done"].index(t_status), key=f"mv_{t_id}", label_visibility="collapsed")
                    if new_st != t_status:
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_st, t_id))
                        conn.commit()
                        conn.close()
                        st.rerun()

                    # 2. Chat
                    if col_c.button("💬", key=f"ch_{t_id}", help="Abrir Chat"):
                        st.session_state[f'show_chat_{t_id}'] = not st.session_state.get(f'show_chat_{t_id}', False)
                        st.session_state[f'show_edit_{t_id}'] = False

                    # 3. Editar (Apenas com permissão)
                    if user_role == 'admin' or can_edit_tasks:
                        if col_e.button("✏️", key=f"ed_{t_id}", help="Editar Tarefa"):
                            st.session_state[f'show_edit_{t_id}'] = not st.session_state.get(f'show_edit_{t_id}', False)
                            st.session_state[f'show_chat_{t_id}'] = False

                    # PAINEL DE EDIÇÃO DA TAREFA
                    if st.session_state.get(f'show_edit_{t_id}', False):
                        with st.container(border=True):
                            st.markdown("##### Editar Tarefa")
                            e_title = st.text_input("Título", value=task['title'], key=f"et_{t_id}")
                            e_desc = st.text_area("Descrição", value=task['description'] if task['description'] else "", key=f"edesc_{t_id}")
                            e_assign = st.selectbox("Responsável", options=list(users_dict.keys()), format_func=lambda x: users_dict[x], index=list(users_dict.keys()).index(task['assignee_id']) if task['assignee_id'] in users_dict else 0, key=f"ea_{t_id}")
                            e_due = st.date_input("Prazo", value=pd.to_datetime(task['due_date']) if pd.notnull(task['due_date']) else datetime.today(), key=f"edue_{t_id}")
                            
                            if st.button("💾 Salvar Alterações", key=f"esv_{t_id}", type="primary"):
                                update_task(t_id, e_title, e_desc, e_assign, e_due)
                                st.session_state[f'show_edit_{t_id}'] = False
                                st.rerun()

                    # PAINEL DE CHAT
                    if st.session_state.get(f'show_chat_{t_id}', False):
                        with st.container(border=True):
                            conn = sqlite3.connect(DB_PATH)
                            df_chat = pd.read_sql_query("SELECT c.*, u.name as user_name FROM task_chats c JOIN users u ON c.user_id = u.id WHERE c.task_id = ? ORDER BY c.created_at ASC", conn, params=(t_id,))
                            conn.close()
                            
                            for _, msg in df_chat.iterrows():
                                is_me = msg['user_id'] == user_id
                                b_class = "chat-bubble-me" if is_me else "chat-bubble-other"
                                st.markdown(f"<div class='{b_class}'><span class='chat-meta'><b>{msg['user_name']}</b> • {msg['created_at']}</span><br>{msg['message']}</div>", unsafe_allow_html=True)
                            
                            with st.form(key=f"f_chat_{t_id}", clear_on_submit=True):
                                new_msg = st.text_area("Mensagem", height=60)
                                if st.form_submit_button("Enviar"):
                                    conn = sqlite3.connect(DB_PATH)
                                    conn.execute("INSERT INTO task_chats (task_id, user_id, message) VALUES (?, ?, ?)", (t_id, user_id, new_msg))
                                    conn.commit()
                                    conn.close()
                                    st.rerun()

    with tab_overview:
        st.info("Consulte aqui a documentação estratégica e escopo do projeto, preenchida durante a criação.")
