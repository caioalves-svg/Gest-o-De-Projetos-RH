import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from database.setup import DB_PATH
from auth.security import check_auth

# Garante que só quem está logado entra
check_auth()

if st.session_state['role'] != 'admin':
    st.error("Acesso restrito. Apenas administradores podem ver o Dashboard Executivo.")
    st.stop()

st.title("📊 Dashboard Executivo de Inovação")

# Coleta de Dados
conn = sqlite3.connect(DB_PATH)
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
conn.close()

if df_projects.empty:
    st.info("Nenhum projeto cadastrado para gerar métricas.")
    st.stop()

# Cálculos Estratégicos
total_projetos = len(df_projects)
projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']

# KPI Principal: % Entregues no Prazo
if len(projetos_concluidos) > 0:
    no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
    kpi_prazo = (len(no_prazo) / len(projetos_concluidos)) * 100
else:
    kpi_prazo = 0.0

economia_total = df_projects['saved_value'].sum()

# Layout de Cards
col1, col2, col3, col4 = st.columns(4)
col1.metric("Projetos Totais", total_projetos)
col2.metric("🎯 % Entregue no Prazo", f"{kpi_prazo:.1f}%", help="Métrica inegociável de eficiência")
col3.metric("Projetos Concluídos", len(projetos_concluidos))
col4.metric("💰 Valor Economizado", f"R$ {economia_total:,.2f}")

st.divider()

# Gráficos
col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    st.subheader("Status dos Projetos")
    fig_status = px.pie(df_projects, names='status', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig_status, use_container_width=True)

with col_chart2:
    st.subheader("Tipos de Projetos")
    fig_type = px.bar(df_projects, x='type', color='type', title="Melhoria vs Implantação")
    st.plotly_chart(fig_type, use_container_width=True)
