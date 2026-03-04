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

# Garante que as tabelas existem (resolve o problema do Streamlit Cloud)
init_db()
check_auth()

st.set_page_config(page_title="Workspace de Projetos", page_icon="🏢", layout="wide")

# ==========================================
# CSS CUSTOMIZADO PARA VISUAL ENTERPRISE
# ==========================================
st.markdown("""
<style>
    /* Estilo dos Cartões do Kanban */
    .kanban-card {
        background-color: #ffffff;
        border-left: 4px solid #3498DB;
        padding: 15px;
        border-radius: 6px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 12px;
        transition: transform 0.2s;
    }
    .kanban-card:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.15); }
    .kanban-card-done { border-left-color: #2ECC71; }
    .kanban-card-doing { border-left-color: #F39C12; }
    
    /* Headers das Colunas */
    .kanban-col-header {
        font-weight: 600;
        font-size: 1.1em;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 6px;
        text-align: center;
        margin-bottom: 15px;
    }
    
    /* Balões de Chat */
    .chat-bubble-me {
        background-color: #DCF8C6;
        padding: 10px;
        border-radius: 10px 10px 0px 10px;
        margin: 5px 0;
        text-align: right;
    }
    .chat-bubble-other {
        background-color: #F1F0F0;
        padding: 10px;
        border-radius: 10px 10px 10px 0px;
        margin: 5px 0;
        text-align: left;
    }
    .chat-meta { font-size: 0.8em; color: #666; }
</style>
""", unsafe_allow_html=True)


user_id = st.session_state['user_id']
user_role = st.session_state['role']

# Controle de Navegação Master-Detail
if 'selected_project_id' not in st.session_state:
    st.session_state['selected_project_id'] = None

def go_back_to_portfolio():
    st.session_state['selected_project_id'] = None

# ==========================================
# FUNÇÕES DE BANCO DE DADOS
# ==========================================
def get_projects():
    conn = sqlite3.connect(DB_PATH)
    if user_role == 'admin':
        query = "SELECT p.*, u.name as manager_name FROM projects p LEFT JOIN users u ON p.manager_id = u.id"
        df = pd.read_sql_query(query, conn)
    else:
        query = """
            SELECT DISTINCT p.*, u.name as manager_name FROM projects p
            LEFT JOIN users u ON p.manager_id = u.id
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.manager_id = ? OR t.assignee_id = ?
        """
        df = pd.read_sql_query(query, conn, params=(user_id, user_id))
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
    query = """
        SELECT t.*, u.name as assignee_name 
        FROM tasks t 
        LEFT JOIN users u ON t.assignee_id = u.id 
        WHERE t.project_id = ?
    """
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()
    return df

def get_chat_history(task_id):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT c.*, u.name as user_name 
        FROM task_chats c
        JOIN users u ON c.user_id = u.id
        WHERE c.task_id = ?
        ORDER BY c.created_at ASC
    """
    df = pd.read_sql_query(query, conn, params=(task_id,))
    conn.close()
    return df

def send_chat_message(task_id, message, file_path=None):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO task_chats (task_id, user_id, message, file_path)
        VALUES (?, ?, ?, ?)
    """, (task_id, user_id, message, file_path))
    conn.commit()
    conn.close()

# ==========================================
# VISÃO 1: PORTFÓLIO (MASTER)
# ==========================================
if st.session_state['selected_project_id'] is None:
    st.title("🏢 Portfólio de Projetos")
    st.markdown("Selecione um projeto abaixo para abrir a **Sala de Comando**.")
    
    df_projects = get_projects()
    
    if df_projects.empty:
        st.info("Nenhum projeto encontrado. Peça para o Admin cadastrar novos projetos.")
    else:
        # Layout de Cards para os Projetos
        cols = st.columns(3)
        for idx, row in df_projects.iterrows():
            with cols[idx % 3]:
                # Card visual do projeto
                with st.container(border=True):
                    status_color = "🟢" if row['status'] == 'Concluído' else "🟡" if row['status'] in ['Em Progresso', 'Backlog'] else "🔴"
                    st.markdown(f"### {status_color} {row['code']}")
                    st.markdown(f"**{row['name']}**")
                    st.caption(f"Tipo: {row['type']} | Gestor: {row['manager_name']}")
                    st.progress(100 if row['status'] == 'Concluído' else 50 if row['status'] == 'Em Progresso' else 10)
                    
                    if st.button("Abrir Workspace ➔", key=f"open_{row['id']}", use_container_width=True):
                        st.session_state['selected_project_id'] = row['id']
                        st.session_state['selected_project_data'] = row.to_dict()
                        st.rerun()

# ==========================================
# VISÃO 2: SALA DO PROJETO (DETAIL)
# ==========================================
else:
    p_data = st.session_state['selected_project_data']
    p_id = p_data['id']
    
    # Header da Sala
    col_back, col_title = st.columns([1, 10])
    with col_back:
        if st.button("⬅ Voltar"):
            go_back_to_portfolio()
            st.rerun()
            
    with col_title:
        st.title(f"[{p_data['code']}] {p_data['name']}")
        st.caption(f"Status: **{p_data['status']}** | Início: {p_data['start_date']} | Prazo: {p_data['due_date']}")

    st.divider()

    # ABAS DA SALA DE COMANDO
    tab_kanban, tab_overview = st.tabs(["🗂️ Quadro Kanban & Chat", "📊 Visão Geral do Escopo"])

    # ----------------------------------------
    # ABA 1: KANBAN & CHAT DA TAREFA
    # ----------------------------------------
    with tab_kanban:
        df_tasks = get_tasks(p_id)
        
        # Botão de Nova Tarefa (Apenas Admin pode criar)
        if user_role == 'admin':
            with st.expander("➕ Adicionar Nova Tarefa"):
                with st.form("form_new_task"):
                    t_title = st.text_input("Título da Tarefa*")
                    t_desc = st.text_area("Descrição")
                    
                    # Carregar usuários para atribuir
                    conn = sqlite3.connect(DB_PATH)
                    users_df = pd.read_sql_query("SELECT id, name FROM users", conn)
                    conn.close()
                    user_dict = dict(zip(users_df['id'], users_df['name']))
                    
                    t_assignee = st.selectbox("Responsável*", options=list(user_dict.keys()), format_func=lambda x: user_dict[x])
                    t_due = st.date_input("Prazo")
                    
                    if st.form_submit_button("Criar Tarefa"):
                        if t_title:
                            conn = sqlite3.connect(DB_PATH)
                            conn.execute("INSERT INTO tasks (project_id, title, description, assignee_id, due_date) VALUES (?, ?, ?, ?, ?)", 
                                         (p_id, t_title, t_desc, t_assignee, t_due))
                            conn.commit()
                            conn.close()
                            st.success("Tarefa criada!")
                            st.rerun()
                        else:
                            st.error("Título é obrigatório.")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Layout das Colunas do Kanban
        col_todo, col_doing, col_done = st.columns(3)
        
        with col_todo:
            st.markdown("<div class='kanban-col-header'>📝 A Fazer (To Do)</div>", unsafe_allow_html=True)
        with col_doing:
            st.markdown("<div class='kanban-col-header'>⏳ Em Progresso (Doing)</div>", unsafe_allow_html=True)
        with col_done:
            st.markdown("<div class='kanban-col-header'>✅ Concluído (Done)</div>", unsafe_allow_html=True)

        if not df_tasks.empty:
            for _, task in df_tasks.iterrows():
                t_id = task['id']
                t_status = task['status']
                
                # Determina o alvo
                target_col = col_todo if t_status == 'To Do' else col_doing if t_status == 'Doing' else col_done
                css_class = "kanban-card" if t_status == 'To Do' else "kanban-card kanban-card-doing" if t_status == 'Doing' else "kanban-card kanban-card-done"
                
                with target_col:
                    # O Cartão Visual
                    st.markdown(f"""
                        <div class="{css_class}">
                            <div style="font-weight:bold; font-size:1.1em;">{task['title']}</div>
                            <div style="color:#666; font-size:0.9em; margin-top:5px;">👤 {task['assignee_name']}</div>
                            <div style="color:#e74c3c; font-size:0.8em;">📅 {task['due_date']}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    # Interações do Cartão (Mover e Chat)
                    col_move, col_chat = st.columns([1, 1])
                    
                    # Mover Status
                    new_status = col_move.selectbox("Mover:", ["To Do", "Doing", "Done"], index=["To Do", "Doing", "Done"].index(t_status), key=f"move_{t_id}", label_visibility="collapsed")
                    if new_status != t_status:
                        conn = sqlite3.connect(DB_PATH)
                        conn.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, t_id))
                        conn.commit()
                        conn.close()
                        st.rerun()

                    # Abrir Chat / Detalhes da Tarefa
                    if col_chat.button("💬 Abrir Chat", key=f"btn_chat_{t_id}", use_container_width=True):
                        st.session_state[f'show_chat_{t_id}'] = not st.session_state.get(f'show_chat_{t_id}', False)

                    # Painel Expansível de Chat e Anexos
                    if st.session_state.get(f'show_chat_{t_id}', False):
                        with st.container(border=True):
                            st.markdown("#### Histórico e Comunicação")
                            st.caption(task['description'] if task['description'] else "Sem descrição adicional.")
                            st.divider()
                            
                            # Renderizar Mensagens
                            chat_history = get_chat_history(t_id)
                            for _, msg in chat_history.iterrows():
                                is_me = msg['user_id'] == user_id
                                bubble_class = "chat-bubble-me" if is_me else "chat-bubble-other"
                                st.markdown(f"""
                                    <div class="{bubble_class}">
                                        <span class="chat-meta"><b>{msg['user_name']}</b> • {msg['created_at']}</span><br>
                                        {msg['message']}
                                    </div>
                                """, unsafe_allow_html=True)
                                
                                # Renderizar anexo se existir
                                if msg['file_path'] and os.path.exists(msg['file_path']):
                                    # Se for imagem, renderiza. Se não, gera link de download
                                    if msg['file_path'].lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                                        st.image(msg['file_path'], width=250)
                                    else:
                                        with open(msg['file_path'], "rb") as file:
                                            st.download_button(label="📎 Baixar Anexo", data=file, file_name=os.path.basename(msg['file_path']), key=f"dl_{msg['id']}")
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            
                            # Formulário de Envio (Texto + Upload)
                            with st.form(key=f"form_chat_{t_id}", clear_on_submit=True):
                                new_msg = st.text_area("Sua mensagem...", height=80)
                                uploaded_file = st.file_uploader("Anexar arquivo/imagem (Opcional)")
                                submit_chat = st.form_submit_button("Enviar Mensagem ➔")
                                
                                if submit_chat and (new_msg or uploaded_file):
                                    file_path_saved = None
                                    if uploaded_file is not None:
                                        file_path_saved = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uploaded_file.name}")
                                        with open(file_path_saved, "wb") as f:
                                            f.write(uploaded_file.getbuffer())
                                            
                                    send_chat_message(t_id, new_msg if new_msg else "📎 Arquivo Anexado", file_path_saved)
                                    st.rerun()

    # ----------------------------------------
    # ABA 2: VISÃO GERAL (DETALHES DO ESCOPO)
    # ----------------------------------------
    with tab_overview:
        st.subheader("Documentação do Projeto")
        details = get_project_details(p_id, p_data['type'])
        
        if p_data['type'] == 'Melhoria':
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**Cenário Atual (As-Is):**\n> {details.get('as_is', 'N/A')}")
            col_a.markdown(f"**Problema Identificado:**\n> {details.get('problem', 'N/A')}")
            col_a.markdown(f"**Causa Raiz:**\n> {details.get('root_cause', 'N/A')}")
            col_b.markdown(f"**Cenário Futuro (To-Be):**\n> {details.get('to_be', 'N/A')}")
            col_b.markdown(f"**Indicador Impactado:** {details.get('impacted_kpi', 'N/A')}")
            col_b.markdown(f"Métrica Antes: `{details.get('metric_before', 'N/A')}` ➔ Depois: `{details.get('metric_after', 'N/A')}`")
        else:
            col_a, col_b = st.columns(2)
            col_a.markdown(f"**Justificativa Estratégica:**\n> {details.get('justification', 'N/A')}")
            col_a.markdown(f"**Risco da Não Implantação:**\n> {details.get('risk', 'N/A')}")
            col_b.markdown(f"**Impacto Estratégico:**\n> {details.get('strategic_impact', 'N/A')}")
            col_b.markdown(f"**Recursos Necessários:**\n> {details.get('resources', 'N/A')}")
