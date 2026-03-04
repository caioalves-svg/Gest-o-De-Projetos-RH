import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

# Ajuste de paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH, UPLOAD_DIR, init_db
from auth.security import check_auth

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

if 'selected_project_id' not in st.session_state:
    st.session_state['selected_project_id'] = None

def go_back_to_portfolio():
    st.session_state['selected_project_id'] = None
    st.session_state['confirm_delete'] = False

# FUNÇÕES DE BANCO DE DADOS
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
    if p_type == 'Melhoria':
        df = pd.read_sql_query("SELECT * FROM project_melhoria WHERE project_id = ?", conn, params=(project_id,))
    else:
        df = pd.read_sql_query("SELECT * FROM project_implantacao WHERE project_id = ?", conn, params=(project_id,))
    conn.close()
    return df.iloc[0].to_dict() if not df.empty else {}

def get_tasks(project_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.project_id = ?", conn, params=(project_id,))
    conn.close()
    return df

def get_chat_history(task_id):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT c.*, u.name as user_name FROM task_chats c JOIN users u ON c.user_id = u.id WHERE c.task_id = ? ORDER BY c.created_at ASC", conn, params=(task_id,))
    conn.close()
    return df

def send_chat_message(task_id, message, file_path=None):
    conn = sqlite3.connect(DB_PATH)
    conn.execute("INSERT INTO task_chats (task_id, user_id, message, file_path) VALUES (?, ?, ?, ?)", (task_id, user_id, message, file_path))
    conn.commit()
    conn.close()

def delete_project_full(project_id):
    """Deleta o projeto e todo o seu histórico (Tarefas, Chats e Escopo)"""
    conn = sqlite3.connect(DB_PATH)
    # Deleta os chats das tarefas deste projeto
    conn.execute("DELETE FROM task_chats WHERE task_id IN (SELECT id FROM tasks WHERE project_id = ?)", (project_id,))
    # Deleta as tarefas
    conn.execute("DELETE FROM tasks WHERE project_id = ?", (project_id,))
    # Deleta o escopo
    conn.execute("DELETE FROM project_melhoria WHERE project_id = ?", (project_id,))
    conn.execute("DELETE FROM project_implantacao WHERE project_id = ?", (project_id,))
    # Deleta o projeto
    conn.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    conn.commit()
    conn.close()

# ==========================================
# VISÃO 1: PORTFÓLIO
# ==========================================
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

# ==========================================
# VISÃO 2: SALA DO PROJETO
# ==========================================
else:
    p_data = st.session_state['selected_project_data']
    p_id = p_data['id']
    
    col_back, col_title, col_status = st.columns([1, 6, 3])
    with col_back:
        if st.button("⬅ Voltar"):
            go_back_to_portfolio()
            st.rerun()
            
    with col_title:
        st.title(f"[{p_data['code']}] {p_data['name']}")
        st.caption(f"Início: {p_data['start_date']} | Prazo: {p_data['due_date']}")

    with col_status:
        # STATUS DE MERCADO APLICADOS AQUI
        status_options = [
            "Não Iniciado", 
            "Em Planejamento", 
            "Em Execução", 
            "Aguardando Aprovação", 
            "Pausado / Bloqueado", 
            "Concluído", 
            "Cancelado"
        ]
        
        current_status = p_data['status']
        if current_status not in status_options:
            status_options.append(current_status)
            
        new_proj_status = st.selectbox("Status do Projeto:", options=status_options, index=status_options.index(current_status))
        
        if new_proj_status != current_status:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE projects SET status = ? WHERE id = ?", (new_proj_status, p_id))
            if new_proj_status == "Concluído":
                hoje = datetime.now().strftime('%Y-%m-%d')
                conn.execute("UPDATE projects SET real_end_date = ? WHERE id = ?", (hoje, p_id))
            conn.commit()
            conn.close()
            st.session_state['selected_project_data']['status'] = new_proj_status
            st.success("Status atualizado!")
            st.rerun()

    # ZONA DE PERIGO: EXCLUSÃO DE PROJETO (Apenas Admin)
    if user_role == 'admin':
        if st.button("🗑️ Excluir Projeto", type="secondary"):
            st.session_state['confirm_delete'] = True
            
        if st.session_state.get('confirm_delete', False):
            st.warning("⚠️ Tem certeza que deseja excluir este projeto? Esta ação apagará todas as tarefas e conversas permanentemente.")
            col_y, col_n = st.columns(2)
            if col_y.button("✅ Sim, Excluir Definitivamente"):
                delete_project_full(p_id)
                st.success("Projeto excluído com sucesso!")
                go_back_to_portfolio()
                st.rerun()
            if col_n.button("❌ Cancelar"):
                st.session_state['confirm_delete'] = False
                st.rerun()

    st.divider()

    # ABAS
    tab_kanban, tab_overview = st.tabs(["🗂️ Kanban & Chat das Tarefas", "📊 Visão Geral do Escopo"])

    # ABA 1: KANBAN
    with tab_kanban:
        df_tasks = get_tasks(p_id)
        if user_role == 'admin':
            with st.expander("➕ Adicionar Nova Tarefa"):
                with st.form("form_new_task"):
                    t_title = st.text_input("Título da Tarefa*")
                    t_desc = st.text_area("Descrição")
                    conn = sqlite3.connect(DB_PATH)
                    users_df = pd.read_sql_query("SELECT id, name FROM users", conn)
                    conn.close()
                    user_dict = dict(zip(users_df['id'], users_df['name']))
                    t_assignee = st.selectbox("Responsável*", options=list(user_dict.keys()), format_func=lambda x: user_dict[x])
                    t_due = st.date_input("Prazo")
                    if st.form_submit_button("Criar Tarefa"):
                        if t_title:
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
                    st.markdown(f"<div class='{css_class}'><b>{task['title']}</b><br><small>👤 {task['assignee_name']}</small></div>", unsafe_allow_html=True)
                    
                    col_m, col_c = st.columns([1, 1])
                    new_st = col_m.selectbox("Mover:", ["To Do", "Doing", "Done"], index=["To Do", "Doing", "Done"].index(t_status), key=f"move_{t_id}", label_visibility="collapsed")
                    if new_st != t_status:
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_st, t_id))
                        conn.commit()
                        conn.close()
                        st.rerun()

                    if col_c.button("💬 Chat", key=f"chat_{t_id}", use_container_width=True):
                        st.session_state[f'show_chat_{t_id}'] = not st.session_state.get(f'show_chat_{t_id}', False)

                    if st.session_state.get(f'show_chat_{t_id}', False):
                        with st.container(border=True):
                            chat_history = get_chat_history(t_id)
                            for _, msg in chat_history.iterrows():
                                is_me = msg['user_id'] == user_id
                                b_class = "chat-bubble-me" if is_me else "chat-bubble-other"
                                st.markdown(f"<div class='{b_class}'><span class='chat-meta'><b>{msg['user_name']}</b> • {msg['created_at']}</span><br>{msg['message']}</div>", unsafe_allow_html=True)
                                if msg['file_path'] and os.path.exists(msg['file_path']):
                                    st.caption(f"📎 Anexo salvo: {os.path.basename(msg['file_path'])}")
                            
                            with st.form(key=f"f_chat_{t_id}", clear_on_submit=True):
                                new_msg = st.text_area("Sua mensagem...", height=60)
                                up_file = st.file_uploader("Anexo")
                                if st.form_submit_button("Enviar"):
                                    f_path = None
                                    if up_file:
                                        f_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{up_file.name}")
                                        with open(f_path, "wb") as f: f.write(up_file.getbuffer())
                                    send_chat_message(t_id, new_msg if new_msg else "📎 Arquivo", f_path)
                                    st.rerun()

    # ABA 2: VISÃO GERAL
    with tab_overview:
        st.subheader("Documentação do Projeto")
        details = get_project_details(p_id, p_data['type'])
        if p_data['type'] == 'Melhoria':
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**As-Is:** {details.get('as_is', 'N/A')}\n\n**Problema:** {details.get('problem', 'N/A')}\n\n**Causa Raiz:** {details.get('root_cause', 'N/A')}")
            col_b.markdown(f"**To-Be:** {details.get('to_be', 'N/A')}\n\n**KPI Impactado:** {details.get('impacted_kpi', 'N/A')}\n\n**Antes:** {details.get('metric_before', '')} ➔ **Depois:** {details.get('metric_after', '')}")
        else:
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**Justificativa:** {details.get('justification', 'N/A')}\n\n**Risco:** {details.get('risk', 'N/A')}")
            col_b.markdown(f"**Impacto Estratégico:** {details.get('strategic_impact', 'N/A')}\n\n**Recursos:** {details.get('resources', 'N/A')}")
