import sqlite3
import pandas as pd
from datetime import datetime
import os
import sys

# Ajuste de path para importações a partir da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def _get_connection():
    return sqlite3.connect(DB_PATH)

def calcular_sla_resposta_tarefa(task_id):
    """Calcula o SLA (em horas) de uma única tarefa."""
    conn = _get_connection()
    query_task = "SELECT assignee_id FROM tasks WHERE id = ?"
    df_task = pd.read_sql_query(query_task, conn, params=(task_id,))
    
    if df_task.empty or pd.isna(df_task['assignee_id'].iloc[0]):
        conn.close()
        return None 
        
    assignee_id = df_task['assignee_id'].iloc[0]
    
    query_chat = "SELECT user_id, created_at FROM task_chats WHERE task_id = ? ORDER BY created_at ASC"
    df_chat = pd.read_sql_query(query_chat, conn, params=(task_id,))
    conn.close()

    if df_chat.empty:
        return None # Tarefa sem chat: Retorna None para ser ignorada na média

    df_chat['created_at'] = pd.to_datetime(df_chat['created_at'])

    for idx, row in df_chat.iterrows():
        # Acha a 1ª mensagem de cobrança (não é do dono)
        if row['user_id'] != assignee_id:
            hora_pergunta = row['created_at']
            df_subsequente = df_chat.iloc[idx+1:]
            respostas_dono = df_subsequente[df_subsequente['user_id'] == assignee_id]
            
            if not respostas_dono.empty:
                hora_resposta = respostas_dono.iloc[0]['created_at']
                diff_horas = (hora_resposta - hora_pergunta).total_seconds() / 3600.0
                return max(0, round(diff_horas, 1))
            else:
                return None # Cobraram, mas ele não respondeu ainda
                
    return None

def calcular_sla_projeto(project_id):
    """
    Calcula o SLA do Projeto (Média do SLA das suas tarefas).
    Ignora totalmente tarefas que não tiveram chat (retorno None).
    """
    conn = _get_connection()
    df_tasks = pd.read_sql_query("SELECT id FROM tasks WHERE project_id = ?", conn, params=(project_id,))
    conn.close()
    
    if df_tasks.empty:
        return None
        
    slas_tarefas = []
    
    # Varre todas as tarefas do projeto
    for tid in df_tasks['id']:
        sla = calcular_sla_resposta_tarefa(tid)
        if sla is not None:
            slas_tarefas.append(sla) # Só adiciona na conta se tiver SLA válido
            
    if not slas_tarefas:
        return None # Nenhuma tarefa deste projeto tem interações válidas para medir
        
    # Retorna a média exata das tarefas que tiveram interação
    return round(sum(slas_tarefas) / len(slas_tarefas), 1)

def obter_metricas_gerais_sla():
    """Para o Dashboard: Média Global baseada nas médias dos projetos."""
    conn = _get_connection()
    df_projects = pd.read_sql_query("SELECT id, start_date, real_end_date, status FROM projects", conn)
    conn.close()

    slas_projetos = []
    for pid in df_projects['id']:
        sla_proj = calcular_sla_projeto(pid)
        if sla_proj is not None:
            slas_projetos.append(sla_proj)
            
    avg_first_response = round(sum(slas_projetos) / len(slas_projetos), 1) if slas_projetos else 0.0

    df_concluidos = df_projects[df_projects['status'] == 'Concluído'].copy()
    if not df_concluidos.empty:
        df_concluidos['start_date'] = pd.to_datetime(df_concluidos['start_date'], errors='coerce')
        df_concluidos['real_end_date'] = pd.to_datetime(df_concluidos['real_end_date'], errors='coerce')
        df_concluidos['lead_time'] = (df_concluidos['real_end_date'] - df_concluidos['start_date']).dt.days
        avg_lead_time = round(df_concluidos['lead_time'].mean(), 1)
    else:
        avg_lead_time = 0.0

    return {
        "avg_lead_time": max(0, avg_lead_time),
        "avg_first_response": avg_first_response
    }
