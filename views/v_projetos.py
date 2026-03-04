import streamlit as st
import sqlite3
import pandas as pd
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    user_id = st.session_state['user_id']
    user_role = st.session_state['role']
    can_edit = st.session_state.get('can_edit_tasks', False)

    # ==========================================
    # VISÃO 1: PORTFÓLIO DE PROJETOS
    # ==========================================
    if st.session_state.get('selected_project_id') is None:
        st.title("🏢 Portfólio de Projetos")
        conn = sqlite3.connect(DB_PATH)
        if user_role == 'admin':
            df_p = pd.read_sql_query("SELECT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id", conn)
        else:
            df_p = pd.read_sql_query(f"""
                SELECT DISTINCT p.*, u.name as manager_name FROM projects p 
                LEFT JOIN users u ON p.manager_id = u.id 
                LEFT JOIN tasks t ON p.id = t.project_id 
                WHERE p.manager_id = {user_id} OR t.assignee_id = {user_id}
            """, conn)
        conn.close()

        if df_p.empty:
            st.info("Nenhum projeto associado ao seu perfil.")
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

    # ==========================================
    # VISÃO 2: SALA DO PROJETO (KANBAN E DETALHES)
    # ==========================================
    else:
        p_data = st.session_state['selected_project_data']
        pid = p_data['id']

        # Cabeçalho da Sala
        c1, c2, c3 = st.columns([1, 6, 3])
        if c1.button("⬅ Voltar"):
            st.session_state['selected_project_id'] = None
            st.rerun()
        c2.title(f"{p_data['code']} - {p_data['name']}")
        
        # Gestão de Status do Projeto
        with c3:
            st_list = ["Não Iniciado", "Em Planejamento", "Em Execução", "Aguardando Aprovação", "Pausado / Bloqueado", "Concluído"]
            curr_st = p_data['status']
            if curr_st not in st_list: st_list.append(curr_st)
            
            novo_status_proj = st.selectbox("Status do Projeto", st_list, index=st_list.index(curr_st))
            if novo_status_proj != curr_st:
                conn = sqlite3.connect(DB_PATH)
                conn.execute("UPDATE projects SET status = ? WHERE id = ?", (novo_status_proj, pid))
                conn.commit(); conn.close()
                st.session_state['selected_project_data']['status'] = novo_status_proj
                st.rerun()

        st.divider()
        tab_kanban, tab_doc = st.tabs(["🗂️ Kanban de Tarefas", "📄 Documentação do Escopo"])

        # --- TAB: KANBAN E CHAT ---
        with tab_kanban:
            conn = sqlite3.connect(DB_PATH)
            users_dict = dict(zip(pd.read_sql_query("SELECT id, name FROM users", conn)['id'], pd.read_sql_query("SELECT id, name FROM users", conn)['name']))
            
            # Adicionar Tarefa
            if user_role == 'admin' or can_edit:
                with st.expander("➕ Adicionar Nova Tarefa"):
                    with st.form(f"add_task_{pid}", clear_on_submit=True):
                        t_tit = st.text_input("Título")
                        t_desc = st.text_area("Descrição")
                        t_resp = st.selectbox("Responsável", list(users_dict.keys()), format_func=lambda x: users_dict[x])
                        if st.form_submit_button("Salvar no To Do"):
                            conn.execute("INSERT INTO tasks (project_id, title, description, assignee_id, status) VALUES (?,?,?,?,'To Do')", (pid, t_tit, t_desc, t_resp))
                            conn.commit(); st.rerun()

            # Desenhar Kanban
            df_tasks = pd.read_sql_query("SELECT t.*, u.name as assignee_name FROM tasks t LEFT JOIN users u ON t.assignee_id = u.id WHERE t.project_id = ?", conn, params=(pid,))
            col_todo, col_doing, col_done = st.columns(3)
            
            for st_label, col_obj in {"To Do": col_todo, "Doing": col_doing, "Done": col_done}.items():
                with col_obj:
                    st.markdown(f"<h4 style='text-align: center;'>{st_label}</h4>", unsafe_allow_html=True)
                    for _, t in df_tasks[df_tasks['status'] == st_label].iterrows():
                        with st.container(border=True):
                            st.write(f"**{t['title']}**")
                            st.caption(f"👤 {t['assignee_name']}")
                            
                            # Mover
                            n_st = st.selectbox("Mover:", ["To Do", "Doing", "Done"], index=["To Do", "Doing", "Done"].index(t['status']), key=f"mv_{t['id']}", label_visibility="collapsed")
                            if n_st != t['status']:
                                conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (n_st, t['id']))
                                conn.commit(); st.rerun()
                                
                            # Chat e Edição
                            btn1, btn2 = st.columns(2)
                            if btn1.button("💬 Chat", key=f"chat_{t['id']}"):
                                st.session_state[f"show_chat_{t['id']}"] = not st.session_state.get(f"show_chat_{t['id']}", False)
                                
                            if st.session_state.get(f"show_chat_{t['id']}", False):
                                chats = pd.read_sql_query("SELECT c.message, u.name FROM task_chats c JOIN users u ON c.user_id = u.id WHERE task_id = ? ORDER BY created_at ASC", conn, params=(t['id'],))
                                for _, msg in chats.iterrows(): st.write(f"**{msg['name']}**: {msg['message']}")
                                with st.form(f"f_chat_{t['id']}", clear_on_submit=True):
                                    m = st.text_input("Mensagem")
                                    if st.form_submit_button("Enviar"):
                                        conn.execute("INSERT INTO task_chats (task_id, user_id, message) VALUES (?,?,?)", (t['id'], user_id, m))
                                        conn.commit(); st.rerun()

        # --- TAB: DOCUMENTAÇÃO ---
        with tab_doc:
            if p_data['type'] == 'Melhoria':
                det = pd.read_sql_query("SELECT * FROM project_melhoria WHERE project_id = ?", conn, params=(pid,))
                if not det.empty: 
                    st.markdown("**Cenário Atual (As-Is):**")
                    st.info(det.iloc[0]['as_is'])
                    st.markdown("**Cenário Desejado (To-Be):**")
                    st.success(det.iloc[0]['to_be'])
            else:
                det = pd.read_sql_query("SELECT * FROM project_implantacao WHERE project_id = ?", conn, params=(pid,))
                if not det.empty:
                    st.markdown("**Justificativa:**")
                    st.info(det.iloc[0]['justification'])
                    st.markdown("**Riscos:**")
                    st.warning(det.iloc[0]['risk'])
        conn.close()
