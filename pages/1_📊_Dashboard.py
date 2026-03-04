import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys

# Ajuste de path e imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH, init_db
from auth.security import check_auth
from services.kpi_service import obter_metricas_gerais_sla
from utils.layout import aplicar_estilo_corporativo

# Configuração e Layout Permanente
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito. Apenas administradores.")
    st.stop()

st.title("📊 Dashboard Executivo do Portfólio")

conn = sqlite3.connect(DB_PATH)
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
conn.close()

if df_projects.empty:
    st.info("Nenhum projeto cadastrado.")
    st.stop()

# Cálculos de KPI
df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
df_projects['start_date'] = pd.to_datetime(df_projects['start_date'], errors='coerce')

projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
projetos_ativos = df_projects[df_projects['status'].isin(['Não Iniciado', 'Em Planejamento', 'Em Execução', 'Aguardando Aprovação'])]
projetos_bloqueados = df_projects[df_projects['status'] == 'Pausado / Bloqueado']

kpi_prazo = (len(projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]) / len(projetos_concluidos)) * 100 if not projetos_concluidos.empty else 0.0
slas = obter_metricas_gerais_sla()

# Renderização de Métricas
st.markdown("### 🎯 Visão Executiva")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Projetos Totais", len(df_projects))
c2.metric("🏆 % No Prazo", f"{kpi_prazo:.1f}%")
c3.metric("⏳ Projetos Ativos", len(projetos_ativos))
c4.metric("🛑 Bloqueados", len(projetos_bloqueados))

st.divider()

st.markdown("### ⏱️ SLAs de Operação")
s1, s2, s3 = st.columns(3)
s1.metric("Lead Time Médio", f"{slas['avg_lead_time']} dias")
s2.metric("SLA Resposta Chat", f"{slas['avg_first_response']} h")
s3.metric("Performance (M|I)", f"{slas.get('avg_lead_time',0)}d")

# Gráfico de Status
with st.container(border=True):
    st.markdown("**Status Atual da Operação**")
    fig = px.pie(df_projects, names='status', hole=0.4, color='status',
                 color_discrete_map={'Não Iniciado':'#BDC3C7','Em Planejamento':'#9B59B6','Em Execução':'#3498DB',
                                    'Aguardando Aprovação':'#F1C40F','Pausado / Bloqueado':'#E74C3C','Concluído':'#2ECC71'})
    st.plotly_chart(fig, use_container_width=True)
