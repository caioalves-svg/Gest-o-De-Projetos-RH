import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys
import uuid # Para gerar nomes únicos para os ficheiros

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

# ==========================================
# FUNÇÃO PARA GUARDAR UPLOADS COM SEGURANÇA
# ==========================================
def salvar_arquivo(uploaded_file):
    if uploaded_file is None:
        return None
    
    upload_dir = "uploads"
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        
    # Limpa o nome do ficheiro e adiciona um código único para não haver ficheiros duplicados
    nome_seguro = uploaded_file.name.replace(" ", "_")
    nome_unico = f"{uuid.uuid4().hex[:8]}_{nome_seguro}"
    caminho_completo = os.path.join(upload_dir, nome_unico)
    
    # Guarda fisicamente no servidor
    with open(caminho_completo, "wb") as f:
        f.write(uploaded_file.getbuffer())
        
    return caminho_completo

def obter_badge_status(status):
    cores = {
        'Concluído': ('#059669', '#D1FAE5'), 'Em Execução': ('#2563EB', '#DBEAFE'),
        'Aguardando Aprovação': ('#D97706', '#FEF3C7'), 'Pausado / Bloqueado': ('#DC2626', '#FEE2E2'),
        'Não Iniciado': ('#475569', '#F1F5F9'), 'Em Planejamento': ('#7C3AED', '#EDE9FE')
    }
    cor_texto, cor_fundo = cores.get(status, ('#475569', '#F1F5F9'))
    return f"<span style='background-color: {cor_fundo}; color: {cor_texto}; padding: 4px 12px; border-radius: 999px; font-size: 0.75em; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;'>{status}</span>"

def formatar_data_pt(data_str):
    if not data_str or data_str == 'Aguardando Início':
        return 'Aguardando Início'
    try:
        return datetime.strptime(data_str, '%Y-%m-%d').strftime('%d/%m/%Y')
    except:
        return data_str

def render():
    user_id = st.session_state['user_id']
    user_role = st.session_state['role']
    can_edit = st.session_state.get('can_edit_tasks', False)

    # ==========================================
    # AUTOCURA DA BASE DE DADOS (Atualizado para suportar ficheiros)
    # ==========================================
    conn_init = sqlite3.connect(DB_PATH)
    # Cria tabela se não existir
    conn_init.execute('''CREATE TABLE IF NOT EXISTS project_updates (
                        id INTEGER PRIMARY KEY AUTOINCREMENT, 
                        project_id INTEGER NOT NULL, 
                        user_id INTEGER NOT NULL, 
                        update_text TEXT, 
                        created_at DATETIME)''')
    
    # Adiciona a coluna file_path na tabela de updates se ela ainda não existir
    cursor = conn_init.cursor()
    cursor.execute("PRAGMA table_info(project_updates)")
    colunas_updates = [col[1] for col in cursor.fetchall()]
    if 'file_path' not in colunas_updates:
        cursor.execute("ALTER TABLE project_updates ADD COLUMN file_path TEXT")
        
    conn_init.commit()
    conn_init.close()

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

        col_voltar, col_titulo, col_acoes = st.columns([1, 6, 3])
        if col_voltar.button("⬅ Voltar ao Hub"):
            st.session_state['selected_project_id'] = None
            st.rerun()
            
        data_inicio_pt = formatar_data_pt(p_data.get('start_date', 'Aguardando Início'))
        col_titulo.markdown(f"<h2 style='margin:0; color: #0F172A;'>{p_data['code']} - {p_data['name']}</h2>", unsafe_allow_html=True)
        col_titulo.markdown(f"<p style='color: #64748B; font-size: 0.9em; margin-top: -5px;'>🚀 Início Oficial: <b>{data_inicio_pt}</b></p>", unsafe_allow_html=True)
        
        with col_acoes:
            if user_role == 'admin':
                if st.button("🗑️ Excluir Projeto", type="secondary", use_container_width=True):
                    conn = sqlite3.connect(DB_PATH)
                    conn.execute("DELETE FROM project_updates WHERE project_id = ?", (pid,))
                    conn.execute("DELETE FROM task_chats WHERE task_id IN (SELECT id FROM tasks WHERE project_id = ?)", (pid,))
                    conn.execute("DELETE FROM tasks WHERE project_id = ?", (pid,))
                    conn.execute("DELETE FROM project_melhoria WHERE project_id = ?", (pid,))
                    conn.execute("DELETE FROM project_implantacao WHERE project_id = ?", (pid,))
                    conn.execute("DELETE FROM projects WHERE id = ?", (pid,))
                    conn.commit(); conn.close()
                    st.session_state['selected_project_id'] = None
                    st.rerun()

        st.divider()

        st_list = ["Não Iniciado", "Em Planejamento", "Em Execução", "Aguardando Aprovação", "Pausado / Bloqueado", "Concluído"]
        if p_data['status'] not in st_list: st_list.append(p_data['status'])
        
        col_st1, col_prazo, col_vazia = st.columns([4, 4, 2])
        
        novo_status_proj = col_st1.selectbox("Etapa Atual do Projeto:", st_list, index=st_list.index(p_data['status']))
        
        try:
            prazo_atual = datetime.strptime(p_data['due_date'], '%Y-%m-%d').date() if p_data.get('due_date') else datetime.today().date()
        except:
            prazo_atual = datetime.today().date()
            
        novo_prazo = col_prazo.date_input("📅 Prazo Desejado (Editável):", value=prazo_atual, format="DD/MM/YYYY")

        mudou_status = novo_status_proj != p_data['status']
        mudou_prazo = novo_prazo.strftime('%Y-%m-%d') != p_data.get('due_date', '')

        if mudou_status or mudou_prazo:
            conn = sqlite3.connect(DB_PATH)
            hoje_iso = datetime.now().strftime('%Y-%m-%d')
            prazo_str = novo_prazo.strftime('%Y-%m-%d')
            
            if mudou_status and novo_status_proj == "Em Planejamento":
                conn.execute("UPDATE projects SET status = ?, due_date = ?, start_date = ? WHERE id = ?", 
                             (novo_status_proj, prazo_str, hoje_iso, pid))
                st.session_state['selected_project_data']['start_date'] = hoje_iso
                hoje_pt = datetime.now().strftime('%d/%m/%Y')
                st.toast(f"🚀 Automação: Data de Início registrada como {hoje_pt}!", icon="✅")
            else:
                conn.execute("UPDATE projects SET status = ?, due_date = ? WHERE id = ?", 
                             (novo_status_proj, prazo_str, pid))
                
            conn.commit(); conn.close()
            st.session_state['selected_project_data']['status'] = novo_status_proj
            st.session_state['selected_project_data']['due_date'] = prazo_str
            st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        tab_kanban, tab_updates, tab_doc = st.tabs(["🗂️ Gestão Ágil (Kanban)", "📢 Atualizações (Log/Sprint)", "📄 Escopo e Documentação"])

        # ==========================================
        # ABA 1: KANBAN E CHAT (COM ANEXOS)
        # ==========================================
        with tab_kanban:
            conn = sqlite3.connect(DB_PATH)
            users_dict = dict(zip(pd.read_sql_query("SELECT id, name FROM users", conn)['id'], pd.read_sql_query("SELECT id, name FROM users", conn)['name']))
            
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
            
            c_todo, c_doing, c_done = st.columns(3)
            for st_label, col_obj in {"To Do": c_todo, "Doing": c_doing, "Done": c_done}.items():
                with col_obj:
                    st.markdown(f"<div style='background-color: #F1F5F9; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; color: #475569; margin-bottom: 15px;'>{st_label.upper()}</div>", unsafe_allow_html=True)
                    
                    for _, t in df_tasks[df_tasks['status'] == st_label].iterrows():
                        with st.container(border=True):
                            st.markdown(f"<p style='font-weight: 700; color: #0F172A; margin-bottom: 5px;'>{t['title']}</p>", unsafe_allow_html=True)
                            st.markdown(f"<p style='font-size: 0.8em; color: #64748B;'>👤 Resp: {t['assignee_name']}</p>", unsafe_allow_html=True)
                            
                            n_st = st.selectbox("Avançar para:", ["To Do", "Doing", "Done"], index=["To Do", "Doing", "Done"].index(t['status']), key=f"mv_{t['id']}", label_visibility="collapsed")
                            if n_st != t['status']:
                                conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (n_st, t['id']))
                                conn.commit(); st.rerun()
                                
                            if st.button("💬 Abrir Chat", key=f"chat_{t['id']}", use_container_width=True):
                                st.session_state[f"show_chat_{t['id']}"] = not st.session_state.get(f"show_chat_{t['id']}", False)
                                
                            # ÁREA DO CHAT COM UPLOAD DE FICHEIROS
                            if st.session_state.get(f"show_chat_{t['id']}", False):
                                st.markdown("---")
                                chats = pd.read_sql_query("SELECT c.message, c.file_path, u.name FROM task_chats c JOIN users u ON c.user_id = u.id WHERE task_id = ? ORDER BY created_at ASC", conn, params=(t['id'],))
                                
                                for chat_idx, msg in chats.iterrows(): 
                                    st.markdown(f"<div style='background-color: #EFF6FF; padding: 10px; border-radius: 10px; margin-bottom: 4px; border-left: 4px solid #2563EB;'><span style='font-size: 0.8em; font-weight: bold; color: #2563EB;'>{msg['name']}</span><br><span style='color: #334155; font-size: 0.9em;'>{msg['message']}</span></div>", unsafe_allow_html=True)
                                    
                                    # Se houver um anexo nesta mensagem, exibe o botão de download
                                    if msg['file_path'] and os.path.exists(msg['file_path']):
                                        nome_original = msg['file_path'].split('_', 1)[-1] if '_' in os.path.basename(msg['file_path']) else os.path.basename(msg['file_path'])
                                        with open(msg['file_path'], "rb") as file:
                                            st.download_button(label=f"📎 Descarregar: {nome_original}", data=file, file_name=nome_original, key=f"dl_chat_{t['id']}_{chat_idx}")
                                
                                with st.form(f"f_chat_{t['id']}", clear_on_submit=True):
                                    m = st.text_input("Escreva a sua mensagem...")
                                    arquivo_chat = st.file_uploader("📎 Anexar documento (Opcional)", key=f"up_chat_{t['id']}")
                                    
                                    if st.form_submit_button("Enviar Mensagem"):
                                        if m or arquivo_chat:
                                            caminho_salvo = salvar_arquivo(arquivo_chat)
                                            conn.execute("INSERT INTO task_chats (task_id, user_id, message, file_path) VALUES (?,?,?,?)", (t['id'], user_id, m, caminho_salvo))
                                            conn.commit(); st.rerun()
            conn.close()

        # ==========================================
        # ABA 2: MURAL DE ATUALIZAÇÕES (COM ANEXOS)
        # ==========================================
        with tab_updates:
            st.markdown("### 📢 Diário de Bordo do Projeto")
            st.markdown("<p style='color: #64748B;'>Registe conclusões de sprints, atas e anexe relatórios importantes.</p>", unsafe_allow_html=True)
            
            # Formulário com Upload
            with st.form(f"form_update_{pid}", clear_on_submit=True):
                novo_texto = st.text_area("Escreva a sua atualização aqui...")
                arquivo_update = st.file_uploader("📎 Anexar Ficheiro/Ata (Opcional)", key=f"up_update_{pid}")
                
                if st.form_submit_button("Publicar Atualização"):
                    if novo_texto.strip() or arquivo_update:
                        caminho_salvo = salvar_arquivo(arquivo_update)
                        conn = sqlite3.connect(DB_PATH)
                        agora_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        conn.execute("INSERT INTO project_updates (project_id, user_id, update_text, created_at, file_path) VALUES (?,?,?,?,?)", 
                                     (pid, user_id, novo_texto, agora_str, caminho_salvo))
                        conn.commit(); conn.close()
                        st.rerun()

            st.markdown("<br>", unsafe_allow_html=True)
            
            # Renderizar o feed de atualizações
            conn = sqlite3.connect(DB_PATH)
            df_updates = pd.read_sql_query("""
                SELECT p.update_text, p.created_at, p.file_path, u.name 
                FROM project_updates p 
                JOIN users u ON p.user_id = u.id 
                WHERE p.project_id = ? 
                ORDER BY p.created_at DESC
            """, conn, params=(pid,))
            conn.close()

            if df_updates.empty:
                st.info("Nenhuma atualização registada ainda.")
            else:
                for upd_idx, log in df_updates.iterrows():
                    data_log_pt = datetime.strptime(log['created_at'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m/%Y às %H:%M')
                    
                    with st.container(border=True):
                        st.markdown(f"<span style='color: #2563EB; font-weight: 700; font-size: 1.05em;'>{log['name']}</span> &nbsp;<span style='color: #94A3B8; font-size: 0.85em;'>• {data_log_pt}</span>", unsafe_allow_html=True)
                        if log['update_text']:
                            st.markdown(f"<div style='color: #334155; margin-top: 8px; line-height: 1.5;'>{log['update_text'].replace(chr(10), '<br>')}</div>", unsafe_allow_html=True)
                        
                        # Se houver anexo, mostra o botão de download
                        if log['file_path'] and os.path.exists(log['file_path']):
                            st.markdown("<br>", unsafe_allow_html=True)
                            nome_original = log['file_path'].split('_', 1)[-1] if '_' in os.path.basename(log['file_path']) else os.path.basename(log['file_path'])
                            with open(log['file_path'], "rb") as file:
                                st.download_button(label=f"📎 Descarregar Anexo: {nome_original}", data=file, file_name=nome_original, key=f"dl_upd_{pid}_{upd_idx}")

        # --- ABA 3: DOCUMENTAÇÃO ---
        with tab_doc:
            conn = sqlite3.connect(DB_PATH)
            if p_data['type'] == 'Melhoria':
                det = pd.read_sql_query("SELECT * FROM project_melhoria WHERE project_id = ?", conn, params=(pid,))
                if not det.empty: 
                    st.info(f"**Cenário Atual (As-Is):**\n\n{det.iloc[0]['as_is']}")
                    st.success(f"**Cenário Desejado (To-Be):**\n\n{det.iloc[0]['to_be']}")
            else:
                det = pd.read_sql_query("SELECT * FROM project_implantacao WHERE project_id = ?", conn, params=(pid,))
                if not det.empty:
                    st.info(f"**Justificativa:**\n\n{det.iloc[0]['justification']}")
                    st.warning(f"**Riscos:**\n\n{det.iloc[0]['risk']}")
            conn.close()
