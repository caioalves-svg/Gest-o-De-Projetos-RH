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
    """
    Novo SLA: Tempo para a primeira resposta do Dono da Tarefa no Chat.
    Calcula a diferença em horas entre a 1ª mensagem de terceiros e a resposta do dono.
    """
    conn = _get_connection()
    
    # 1. Obter quem é o responsável (Assignee) da tarefa
    query_task = "SELECT assignee_id FROM tasks WHERE id = ?"
    df_task = pd.read_sql_query(query_task, conn, params=(task_id,))
    
    if df_task.empty or pd.isna(df_task['assignee_id'].iloc[0]):
        conn.close()
        return None # Se a tarefa não tem dono, não há SLA a medir
        
    assignee_id = df_task['assignee_id'].iloc[0]
    
    # 2. Obter todo o histórico do chat em ordem cronológica
    query_chat = "SELECT user_id, created_at FROM task_chats WHERE task_id = ? ORDER BY created_at ASC"
    df_chat = pd.read_sql_query(query_chat, conn, params=(task_id,))
    conn.close()

    if df_chat.empty:
        return None

    # Converter para o tipo datetime do Pandas para contas matemáticas
    df_chat['created_at'] = pd.to_datetime(df_chat['created_at'])

    # 3. Lógica de detecção de resposta
    for idx, row in df_chat.iterrows():
        # Encontra a primeira mensagem que NÃO é do dono da tarefa (uma cobrança/pergunta)
        if row['user_id'] != assignee_id:
            hora_pergunta = row['created_at']
            
            # Corta o dataframe para olhar apenas as mensagens DEPOIS dessa pergunta
            df_subsequente = df_chat.iloc[idx+1:]
            
            # Filtra para achar as mensagens que SÃO do dono da tarefa
            respostas_dono = df_subsequente[df_subsequente['user_id'] == assignee_id]
            
            if not respostas_dono.empty:
                # Pega a exata hora da primeira resposta que ele deu
                hora_resposta = respostas_dono.iloc[0]['created_at']
                
                # Calcula a diferença em horas
                diff_horas = (hora_resposta - hora_pergunta).total_seconds() / 3600.0
                return max(0, round(diff_horas, 1))
            else:
                return None # O terceiro mandou mensagem, mas o dono ainda não respondeu!
                
    return None # Só tem mensagens do próprio dono (ele falando sozinho)

def obter_metricas_gerais_sla():
    """
    Agrega as novas métricas de SLA e Lead Time para o Dashboard Principal.
    """
    conn = _get_connection()
    df_tasks = pd.read_sql_query("SELECT id FROM tasks", conn)
    df_projects = pd.read_sql_query("SELECT id, start_date, real_end_date, status FROM projects", conn)
    conn.close()

    # 1. Média do tempo de resposta do Chat (Todas as tarefas)
    slas_resposta = []
    for tid in df_tasks['id']:
        sla = calcular_sla_resposta_tarefa(tid)
        if sla is not None:
            slas_resposta.append(sla)
            
    avg_first_response = round(sum(slas_resposta) / len(slas_resposta), 1) if slas_resposta else 0.0

    # 2. Média do Lead Time Geral (Apenas projetos concluídos)
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
