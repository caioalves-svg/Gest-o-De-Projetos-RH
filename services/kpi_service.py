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

def calcular_lead_time_projeto(project_id):
    """
    SLA 3: Tempo total até resolução.
    Calcula a diferença em dias entre a start_date e a real_end_date.
    """
    conn = _get_connection()
    query = "SELECT start_date, real_end_date, status FROM projects WHERE id = ?"
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()

    if df.empty or df['status'].iloc[0] != 'Concluído' or pd.isna(df['real_end_date'].iloc[0]):
        return None # Apenas calculamos Lead Time de projetos concluídos

    start = pd.to_datetime(df['start_date'].iloc[0])
    end = pd.to_datetime(df['real_end_date'].iloc[0])
    
    lead_time_days = (end - start).days
    return max(0, lead_time_days) # Evita valores negativos se as datas estiverem invertidas por erro humano

def calcular_tempo_primeira_resposta(project_id):
    """
    SLA 1: Tempo para a primeira resposta.
    Diferença entre a data de início do projeto e o primeiro comentário registado.
    """
    conn = _get_connection()
    
    # Obter data de início do projeto
    query_proj = "SELECT start_date FROM projects WHERE id = ?"
    df_proj = pd.read_sql_query(query_proj, conn, params=(project_id,))
    
    # Obter o primeiro comentário
    query_com = "SELECT created_at FROM comments WHERE project_id = ? ORDER BY created_at ASC LIMIT 1"
    df_com = pd.read_sql_query(query_com, conn, params=(project_id,))
    conn.close()

    if df_proj.empty or df_com.empty or pd.isna(df_proj['start_date'].iloc[0]):
        return None # Sem resposta ainda ou sem data de início

    # Assumimos que o projeto começou às 08:00 da data de início para ter uma base de cálculo de horas
    start_date_str = f"{df_proj['start_date'].iloc[0]} 08:00:00"
    start_dt = pd.to_datetime(start_date_str)
    first_reply_dt = pd.to_datetime(df_com['created_at'].iloc[0])

    diff_hours = (first_reply_dt - start_dt).total_seconds() / 3600.0
    return max(0, round(diff_hours, 1))

def calcular_tempo_entre_interacoes(project_id):
    """
    SLA 2: Tempo médio entre interações.
    Calcula a média de tempo (em horas) entre comentários consecutivos num projeto.
    """
    conn = _get_connection()
    query = "SELECT created_at FROM comments WHERE project_id = ? ORDER BY created_at ASC"
    df = pd.read_sql_query(query, conn, params=(project_id,))
    conn.close()

    if len(df) < 2:
        return None # É preciso pelo menos 2 comentários para haver intervalo

    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # A magia do Pandas: .diff() calcula a diferença entre a linha atual e a anterior
    df['diff'] = df['created_at'].diff()
    
    # Calcular a média dessas diferenças em horas
    media_segundos = df['diff'].mean().total_seconds()
    media_horas = media_segundos / 3600.0
    
    return round(media_horas, 1)

def obter_metricas_gerais_sla():
    """
    Agrega os SLAs de todos os projetos para alimentar o Dashboard Executivo.
    """
    conn = _get_connection()
    df_projects = pd.read_sql_query("SELECT id FROM projects", conn)
    conn.close()

    if df_projects.empty:
        return {"avg_lead_time": 0, "avg_first_response": 0, "avg_interaction_time": 0}

    lead_times = []
    first_responses = []
    interaction_times = []

    for pid in df_projects['id']:
        lt = calcular_lead_time_projeto(pid)
        fr = calcular_tempo_primeira_resposta(pid)
        it = calcular_tempo_entre_interacoes(pid)

        if lt is not None: lead_times.append(lt)
        if fr is not None: first_responses.append(fr)
        if it is not None: interaction_times.append(it)

    return {
        "avg_lead_time": round(sum(lead_times) / len(lead_times), 1) if lead_times else 0,
        "avg_first_response": round(sum(first_responses) / len(first_responses), 1) if first_responses else 0,
        "avg_interaction_time": round(sum(interaction_times) / len(interaction_times), 1) if interaction_times else 0
    }
