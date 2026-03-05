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

    conn = sqlite3.connect(DB_PATH)
    df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
    conn.close()

    if df_projects.empty:
        st.info("Nenhum projeto cadastrado no momento.")
        return

    # Preparação das Datas
    df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
    
    # Filtros por Status
    projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
    projetos_ativos = df_projects[df_projects['status'].isin(['Não Iniciado', 'Em Planejamento', 'Em Execução', 'Aguardando Aprovação'])]
    projetos_bloqueados = df_projects[df_projects['status'] == 'Pausado / Bloqueado']

    # ========================================================
    # AQUI ESTÁ A CORREÇÃO DA MÉTRICA DE ENTREGA NO PRAZO
    # ========================================================
    if 'real_end_date' in df_projects.columns and not projetos_concluidos.empty:
        df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
        # Filtra apenas os concluídos que terminaram antes ou no dia do prazo
        no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
        kpi_prazo_pct = (len(no_prazo) / len(projetos_concluidos)) * 100
    else:
        # Se a lista de concluídos está vazia, o KPI é 0% (não 100%)
        kpi_prazo_pct = 0.0

    st.markdown("### 🎯 Visão Estratégica")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Projetos Totais", len(df_projects))
    
    # Adicionei uma dica (help) para explicar que só contabiliza os projetos já concluídos
    col2.metric("🏆 Entregues no Prazo", f"{kpi_prazo_pct:.1f}%", help="Porcentagem de projetos CONCLUÍDOS que não ultrapassaram a data limite estipulada.")
    
    col3.metric("⏳ Ativos / Em Execução", len(projetos_ativos))
    col4.metric("🛑 Pausados / Bloqueados", len(projetos_bloqueados))

    st.divider()
    
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
