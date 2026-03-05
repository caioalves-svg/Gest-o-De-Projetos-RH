import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    if st.session_state.get('role') != 'admin':
        st.error("🔒 Acesso restrito a administradores.")
        return

    st.title("📊 Dashboard Executivo do Portfólio")
    st.markdown("---")

    # ==========================================
    # LEITURA DE DADOS
    # ==========================================
    conn = sqlite3.connect(DB_PATH)
    df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
    
    # Busca os chats para calcular o TMR (Tempo Médio de Resposta)
    df_chats = pd.read_sql_query("SELECT task_id, created_at FROM task_chats ORDER BY task_id, created_at", conn)
    conn.close()

    if df_projects.empty:
        st.info("Nenhum projeto cadastrado no momento.")
        return

    # ==========================================
    # CÁLCULOS DE PRAZOS E STATUS
    # ==========================================
    df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
    projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
    projetos_ativos = df_projects[df_projects['status'].isin(['Não Iniciado', 'Em Planejamento', 'Em Execução', 'Aguardando Aprovação'])]
    projetos_bloqueados = df_projects[df_projects['status'] == 'Pausado / Bloqueado']

    if 'real_end_date' in df_projects.columns and not projetos_concluidos.empty:
        df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
        no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
        kpi_prazo_pct = (len(no_prazo) / len(projetos_concluidos)) * 100
    else:
        kpi_prazo_pct = 0.0

    # ==========================================
    # CÁLCULO DO TMR (NOVO)
    # ==========================================
    tmr_text = "N/A"
    if not df_chats.empty and len(df_chats) > 1:
        # Converte a coluna de data/hora para o formato datetime do Pandas
        df_chats['created_at'] = pd.to_datetime(df_chats['created_at'], errors='coerce')
        
        # Calcula a diferença de tempo (em horas) entre mensagens DENTRO da mesma tarefa
        df_chats['diff_hours'] = df_chats.groupby('task_id')['created_at'].diff().dt.total_seconds() / 3600.0
        
        # Faz a média geral de todas as diferenças
        tmr_hours = df_chats['diff_hours'].mean()
        
        if pd.isna(tmr_hours):
            tmr_text = "Sem respostas"
        elif tmr_hours < 1: # Se for menor que 1 hora, mostra em minutos
            tmr_text = f"{int(tmr_hours * 60)} min"
        else: # Se for maior, mostra em horas
            tmr_text = f"{tmr_hours:.1f} horas"

    # ==========================================
    # RENDERIZAÇÃO DOS CARTÕES
    # ==========================================
    st.markdown("### 🎯 Visão Estratégica & Engajamento")
    
    # Dividi em 5 colunas para acomodar a nova métrica elegantemente
    col1, col2, col3, col4, col5 = st.columns(5)
    
    col1.metric("Projetos Totais", len(df_projects))
    col2.metric("🏆 Entregues no Prazo", f"{kpi_prazo_pct:.1f}%", help="Projetos concluídos que não ultrapassaram a data limite estipulada.")
    col3.metric("⏳ Ativos", len(projetos_ativos))
    col4.metric("🛑 Bloqueados", len(projetos_bloqueados))
    
    # O Novo Cartão de TMR
    col5.metric("⏱️ TMR (Chat)", tmr_text, help="Tempo Médio de Resposta: Média de tempo que a equipa demora para responder às mensagens nas tarefas.")

    st.divider()
    
    # ==========================================
    # GRÁFICO INTERATIVO
    # ==========================================
    with st.container(border=True):
        st.markdown("<h4 style='color: #0F172A;'>Distribuição do Portfólio por Status</h4>", unsafe_allow_html=True)
        fig_status = px.pie(
            df_projects, names='status', hole=0.45,
            color='status',
            color_discrete_map={
                'Não Iniciado': '#475569', 'Em Planejamento': '#7C3AED', 
                'Em Execução': '#2563EB', 'Aguardando Aprovação': '#D97706',
                'Pausado / Bloqueado': '#DC2626', 'Concluído': '#059669', 'Cancelado': '#1E293B'
            }
        )
        fig_status.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)
