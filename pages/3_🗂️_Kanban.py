import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

# Ajuste de path para importar os módulos da raiz (caso execute de dentro da pasta pages)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

# Verificação de Autenticação (deve existir em todas as páginas)
if 'logged_in' not in st.session_state or not st.session_state['logged_in']:
    st.warning("Por favor, inicie sessão para aceder ao sistema.")
    st.stop()

st.set_page_config(page_title="Kanban - HR Projects", page_icon="🗂️", layout="wide")
st.title("🗂️ Gestão Visual (Kanban)")

user_id = st.session_state['user_id']
user_role = st.session_state['role']

# 1. Função para carregar projetos autorizados
def load_projects():
    conn = sqlite3.connect(DB_PATH)
    if user_role == 'admin':
        # Admin vê todos os projetos
        query = "SELECT id, name FROM projects"
        df = pd.read_sql_query(query, conn)
    else:
        # Colaborador vê projetos onde é o gestor OU tem tarefas atribuídas
        query = """
            SELECT DISTINCT p.id, p.name 
            FROM projects p
            LEFT JOIN tasks t ON p.id = t.project_id
            WHERE p.manager_id = ? OR t.assignee_id = ?
        """
        df = pd.read_sql_query(query, conn, params=(user_id, user_id))
    conn.close()
    return df

# 2. Funções de manipulação da base de dados (Tarefas e Comentários)
def update_task_status(task_id, new_status):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, task_id))
    conn.commit()
    conn.close()

def add_comment(project_id, task_id, comment_text):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("""
        INSERT INTO comments (project_id, task_id, user_id, content, created_at)
        VALUES (?, ?, ?, ?, ?)
    """, (project_id, task_id, user_id, comment_text, now))
    conn.commit()
    conn.close()

def load_comments(task_id):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT c.content, c.created_at, u.name 
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.task_id = ?
        ORDER BY c.created_at DESC
    """
    df_comments = pd.read_sql_query(query, conn, params=(task_id,))
    conn.close()
    return df_comments

# 3. Interface Principal do Kanban
df_projects = load_projects()

if df_projects.empty:
    st.info("Não tem projetos atribuídos no momento.")
    st.stop()

# Filtro de Seleção de Projeto
project_dict = dict(zip(df_projects['id'], df_projects['name']))
selected_project_id = st.selectbox("Selecione o Projeto para visualizar o Quadro:", options=list(project_dict.keys()), format_func=lambda x: project_dict[x])

st.divider()

# Carregar tarefas do projeto selecionado
conn = sqlite3.connect(DB_PATH)
query_tasks = """
    SELECT t.id, t.title, t.status, t.due_date, u.name as assignee
    FROM tasks t
    LEFT JOIN users u ON t.assignee_id = u.id
    WHERE t.project_id = ?
"""
df_tasks = pd.read_sql_query(query_tasks, conn, params=(selected_project_id,))
conn.close()

# Estrutura das Colunas do Kanban
col_todo, col_doing, col_done = st.columns(3)

STATUS_OPTIONS = ["To Do", "Doing", "Done"]

with col_todo:
    st.subheader("📝 A Fazer (To Do)")
    st.markdown("---")
with col_doing:
    st.subheader("⏳ Em Progresso (Doing)")
    st.markdown("---")
with col_done:
    st.subheader("✅ Concluído (Done)")
    st.markdown("---")

# Renderizar os cartões (cards) nas respetivas colunas
if not df_tasks.empty:
    for _, row in df_tasks.iterrows():
        t_id = row['id']
        t_title = row['title']
        t_status = row['status']
        t_due = row['due_date']
        t_assignee = row['assignee'] or "Não atribuído"

        # Determinar em que coluna renderizar
        if t_status == "To Do":
            target_col = col_todo
        elif t_status == "Doing":
            target_col = col_doing
        else:
            target_col = col_done

        # Renderização do Cartão da Tarefa
        with target_col:
            with st.container(border=True):
                st.markdown(f"**{t_title}**")
                st.caption(f"👤 {t_assignee} | 📅 Prazo: {t_due}")
                
                # Atualização de Estado (Mover no Kanban)
                new_status = st.selectbox(
                    "Mover para:", 
                    options=STATUS_OPTIONS, 
                    index=STATUS_OPTIONS.index(t_status) if t_status in STATUS_OPTIONS else 0,
                    key=f"status_{t_id}",
                    label_visibility="collapsed"
                )
                
                if new_status != t_status:
                    update_task_status(t_id, new_status)
                    st.rerun() # Atualiza a página imediatamente para refletir a mudança visual
                
                # Expansor para Comentários e Histórico (Comunicação Interna)
                with st.expander("Comentários / Detalhes"):
                    # Carregar comentários existentes
                    df_comments = load_comments(t_id)
                    if not df_comments.empty:
                        for _, c_row in df_comments.iterrows():
                            st.markdown(f"**{c_row['name']}** *({c_row['created_at']})*")
                            st.write(c_row['content'])
                            st.markdown("---")
                    else:
                        st.write("Sem interações ainda.")
                    
                    # Formulário para novo comentário
                    new_comment = st.text_input("Adicionar comentário...", key=f"comment_input_{t_id}")
                    if st.button("Enviar", key=f"btn_comment_{t_id}"):
                        if new_comment.strip():
                            add_comment(selected_project_id, t_id, new_comment)
                            st.success("Comentário adicionado!")
                            st.rerun()
                        else:
                            st.warning("O comentário não pode estar vazio.")
else:
    st.info("Nenhuma tarefa registada neste projeto. Crie tarefas na página de Projetos.")
