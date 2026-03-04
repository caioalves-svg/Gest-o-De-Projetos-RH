import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH, init_db
from auth.security import check_auth
from services.kpi_service import obter_metricas_gerais_sla

init_db()
check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito. Apenas administradores.")
    st.stop()

st.set_page_config(page_title="Dashboard Executivo", page_icon="📊", layout="wide")

st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #ffffff; border: 1px solid #e0e0e0;
        padding: 15px; border-radius: 8px; border-top: 4px solid #2C3E50;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Executivo do Portfólio")

conn = sqlite3.connect(DB_PATH)
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
conn.close()

if df_projects.empty:
    st.info("Nenhum projeto cadastrado.")
    st.stop()

df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
df_projects['start_date'] = pd.to_datetime(df_projects['start_date'], errors='coerce')

projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
projetos_pendentes = df_projects[df_projects['status'].isin(['Não Iniciado', 'Em Planejamento', 'Em Execução', 'Aguardando Aprovação'])]
projetos_parados = df_projects[df_projects['status'] == 'Pausado / Bloqueado']

kpi_prazo_pct = (len(projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]) / len(projetos_concluidos)) * 100 if not projetos_concluidos.empty else 0.0

slas = obter_metricas_gerais_sla()

# QUADROS DE MÉTRICAS (VISÃO EXECUTIVA)
st.markdown("### 🎯 Visão Executiva do Portfólio")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Projetos Totais (Cadastrados)", len(df_projects))
col2.metric("🏆 % Entregue no Prazo", f"{kpi_prazo_pct:.1f}%")
col3.metric("⏳ Ativos / Em Andamento", len(projetos_pendentes))
col4.metric("🛑 Pausados / Bloqueados", len(projetos_parados))

st.divider()

# QUADROS DE SLA
st.markdown("### ⏱️ Acordos de Nível de Serviço (SLA)")
col_sla1, col_sla2, col_sla3 = st.columns(3)
col_sla1.metric("Lead Time Médio (Projetos)", f"{slas['avg_lead_time']} dias")
col_sla2.metric("SLA 1ª Resposta (Chat das Tarefas)", f"{slas['avg_first_response']} horas")

if not projetos_concluidos.empty:
    df_concluidos_copy = projetos_concluidos.copy()
    df_concluidos_copy['dias_exec'] = (df_concluidos_copy['real_end_date'] - df_concluidos_copy['start_date']).dt.days
    media_tipo = df_concluidos_copy.groupby('type')['dias_exec'].mean().round(1)
    col_sla3.metric("Lead Time (Melhoria | Implant.)", f"{media_tipo.get('Melhoria', 0)}d | {media_tipo.get('Implantação', 0)}d")
else:
    col_sla3.metric("Lead Time (Melhoria | Implant.)", "0d | 0d")

st.markdown("<br>", unsafe_allow_html=True)

# ÚNICO GRÁFICO (STATUS)
st.markdown("### 📈 Status Atual da Operação")
with st.container(border=True):
    fig_status = px.pie(
        df_projects, 
        names='status', 
        hole=0.45,
        color='status',
        color_discrete_map={
            'Não Iniciado': '#BDC3C7',
            'Em Planejamento': '#9B59B6',
            'Em Execução': '#3498DB',
            'Aguardando Aprovação': '#F1C40F',
            'Pausado / Bloqueado': '#E74C3C',
            'Concluído': '#2ECC71',
            'Cancelado': '#34495E'
        }
    )
    fig_status.update_layout(margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig_status, use_container_width=True)
