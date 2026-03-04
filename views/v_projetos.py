import streamlit as st
import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def obter_badge_status(status):
    cores = {
        'Concluído': ('#059669', '#D1FAE5'), 'Em Execução': ('#2563EB', '#DBEAFE'),
        'Aguardando Aprovação': ('#D97706', '#FEF3C7'), 'Pausado / Bloqueado': ('#DC2626', '#FEE2E2'),
        'Não Iniciado': ('#475569', '#F1F5F9'), 'Em Planejamento': ('#7C3AED', '#EDE9FE')
    }
    cor_texto, cor_fundo = cores.get(status, ('#475569', '#F1F5F9'))
    return f"<span style='background-color: {cor_fundo}; color: {cor_texto}; padding: 4px 12px; border-radius: 999px; font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;'>{status}</span>"

def render():
    user_id = st.session_state['user_id']
    user_role = st.session_state['role']
    can_edit = st.session_state.get('can_edit_tasks', False)

    # ==========================================
    # VISÃO 1: PORTFÓLIO
    # ==========================================
    if st.session_state.get('selected_project_id') is None:
        st.title("🏢 Workspace de Projetos")
        st.markdown("<p style='color: #64748B;'>Acompanhe e gira as entregas estratégicas de RH.</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        conn = sqlite3.connect(DB_PATH)
        if user_role == 'admin':
            df_p = pd.read_sql_query("SELECT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id", conn)
        else:
            df_p = pd.read_sql_query(f"SELECT DISTINCT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id LEFT JOIN tasks t ON p.id = t.project_id WHERE p.manager_id = {user_id} OR t.assignee_id = {user_id}", conn)
        conn.close()

        if df_p.empty:
            st.warning("📭 Nenhum projeto atribuído a si no momento.")
        else:
            cols = st.columns(3)
            for idx, row in df_p.iterrows():
                with cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"<p style='color: #3B82F6; font-weight: 800; margin-bottom: 0;'>{row['code']}</p>", unsafe_allow_html=True)
                        st.markdown(f"<h4 style='color: #0F172A; margin-top: 0;'>{row['name']}</h4>", unsafe_allow_html=True)
                        
                        st.markdown(f"{obter_badge_status(row['status'])}", unsafe_allow_html=True)
                        st.markdown(f"<p style='color: #64748B; font-size: 0.85em; margin-top: 10px;'>👤 Gestor: <b>{row['manager_name']}</b></p>", unsafe_allow_html=True)
                        
                        if st.button("Abrir Sala do Projeto ➔", key=f"abrir_{row['id']}", use_container_width=True):
                            st.session_state['selected_project_id'] = row['id']
                            st.session_state['selected_project_data'] = row.to_dict()
                            st.rerun()

    # ==========================================
    # VISÃO 2: SALA DO PROJETO & KANBAN
    # ==========================================
    else:
        p_data = st.session_state['selected_project_data']
        pid = p_data['id']

        # CABEÇALHO DA SALA E EXCLUSÃO
        col_voltar, col_titulo, col_acoes = st.columns([1, 6, 3])
        if col_voltar.button("⬅ Voltar ao Hub"):
            st.session_state['selected_project_id'] = None
            st.rerun()
            
        col_titulo.markdown(f"<h2 style='margin:0; color: #0F172A;'>{p_data['code']} - {p_data['name']}</h2>", unsafe_allow_html=True)
        
        with col_acoes:
            # BOTÃO DE EXCLUIR PROJETO (Apenas Admin)
            if user_role == 'admin':
                if st.button("🗑️ Excluir Projeto", type="secondary", use_container_width=True):
                    conn = sqlite3.connect(DB_PATH)
                    # Exclusão em Cascata para não corromper a BD
                    conn.execute("DELETE FROM task_chats WHERE task_id IN (SELECT id FROM tasks WHERE project_id = ?)", (pid,))
                    conn.execute("DELETE FROM tasks WHERE project_id = ?", (pid,))
                    conn.execute("DELETE FROM project_melhoria WHERE project_id = ?", (pid,))
                    conn.execute("DELETE FROM project_implantacao WHERE project_id = ?", (pid,))
                    conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
                    conn.commit()
                    conn.close()
                    st.session_state['selected_project_id'] = None
                    st.rerun()

        st.divider()

        # GESTÃO DE STATUS
        st_list = ["Não Iniciado", "Em Planejamento", "Em Execução", "Aguardando Aprovação", "Pausado / Bloqueado", "Concluído"]
        if p_data['status'] not in st_list: st_list.append(p_data['status'])
        
        col_st1, col_st2 = st.columns([3, 7])
        novo_status_proj = col_st1.selectbox("Etapa Atual do Projeto:", st_list, index=st_list.index(p_data['status']))
        if novo_status_proj != p_data['status']:
            conn = sqlite3.connect(DB_PATH)
            conn.execute("UPDATE projects SET status = ? WHERE id = ?", (novo_status_proj, pid))
            conn.commit(); conn.close()
            st.session_state['selected_project_data']['status'] = novo_status_proj
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        tab_kanban, tab_doc = st.tabs(["🗂️ Gestão Ágil (Kanban)", "📄 Escopo e Documentação"])

        # --- TAB KANBAN ---
        with tab_kanban:
            conn = sqlite3.connect(DB_PATH)
            users_dict = dict(zip(pd.read_sql_query("SELECT id, name FROM users", conn)['id'], pd.read_sql_query("SELECT id, name FROM users", conn)['name']))
            
            # Adicionar Tarefa
            if user_role == 'admin' or can_edit:
                with st.expander("➕ Criar Nova Tarefa para a Equipa"):
                    with st.form(f"add_task_{pid}", clear_on_submit=True):
                        t_tit = st.text_input("Título da Demanda*")
                        t_desc = st.text_area("Contexto / Descrição")
                        t_resp = st.selectbox("Atribuir a:", list(users_dict.keys()), format_func=lambda x: users_dict[x])
                        if st.form_submit_button("Lançar no Quadro (To Do)"):
                            if t_tit:
                                conn.execute("INSERT INTO tasks (project_id, title, description, assignee_id, status) VALUES (?,?,?,?,'To Do')", (pid, t_tit, t_desc, t_resp))
                                conn.commit(); st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            df_tasks = pd.read_sql_query("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.project_id = ?", conn, params=(pid,))
            
            # QUADRO KANBAN
            c_todo, c_doing, c_done = st.columns(3)
            for st_label, col_obj in {"To Do": c_todo, "Doing": c_doing, "Done": c_done}.items():
                with col_obj:
                    st.markdown(f"<div style='background-color: #F1F5F9; padding: 10px; border-radius:
