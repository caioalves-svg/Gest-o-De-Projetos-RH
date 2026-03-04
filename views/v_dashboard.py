import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys

# Garante que ele encontra os ficheiros da raiz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH

def render():
    if st.session_state.get('role') != 'admin':
        st.error("🔒 Acesso restrito. Apenas administradores podem visualizar o Dashboard.")
        return

    st.title("📊 Dashboard Executivo do Portfólio")

    # Ligação ao Banco e Leitura de Dados
    conn = sqlite3.connect(DB_PATH)
    df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()

    if df_projects.empty:
        st.info("Nenhum projeto cadastrado no momento.")
        return

    # Preparação de Datas para Cálculo de KPIs
    df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
    
    # Separação por Status
    projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
    projetos_ativos = df_projects[df_projects['status'].isin(['Não Iniciado', 'Em Planejamento', 'Em Execução', 'Aguardando Aprovação'])]
    projetos_bloqueados = df_projects[df_projects['status'] == 'Pausado / Bloqueado']

    # Cálculo do KPI de Prazo (Se houver a coluna real_end_date e projetos concluídos)
    if 'real_end_date' in df_projects.columns and not projetos_concluidos.empty:
        df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
        no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
        kpi_prazo_pct = (len(no_prazo) / len(projetos_concluidos)) * 100
    else:
        kpi_prazo_pct = 100.0

    # Tenta puxar os SLAs se o serviço existir (Fallback para 0 se não existir)
    try:
        from services.kpi_service import obter_metricas_gerais_sla
        slas = obter_metricas_gerais_sla()
    except ImportError:
        slas = {'avg_lead_time': 0, 'avg_first_response': 0}

    # --- RENDERIZAÇÃO DOS CARTÕES ---
    st.markdown("### 🎯 Visão Estratégica")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projetos Totais", len(df_projects))
    col2.metric("🏆 % Entregue no Prazo", f"{kpi_prazo_pct:.1f}%")
    col3.metric("⏳ Ativos / Em Execução", len(projetos_ativos))
    col4.metric("🛑 Pausados / Bloqueados", len(projetos_bloqueados))

    st.divider()

    st.markdown("### ⏱️ Acordos de Nível de Serviço (SLA)")
    s1, s2, s3 = st.columns(3)
    s1.metric("Lead Time Médio", f"{slas.get('avg_lead_time', 0)} dias")
    s2.metric("SLA de Resposta (Chat)", f"{slas.get('avg_first_response', 0)} horas")

    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- GRÁFICO INTERATIVO ---
    with st.container(border=True):
        st.markdown("#### Distribuição do Portfólio por Status")
        fig_status = px.pie(
            df_projects, names='status', hole=0.45,
            color='status',
            color_discrete_map={
                'Não Iniciado': '#BDC3C7', 'Em Planejamento': '#9B59B6', 
                'Em Execução': '#3498DB', 'Aguardando Aprovação': '#F1C40F',
                'Pausado / Bloqueado': '#E74C3C', 'Concluído': '#2ECC71', 'Cancelado': '#34495E'
            }
        )
        fig_status.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)
