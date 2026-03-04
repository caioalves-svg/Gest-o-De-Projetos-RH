import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os
import sys

# Ajuste de path para importar serviços e layout
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH, init_db
from auth.security import check_auth
from services.kpi_service import obter_metricas_gerais_sla
from utils.layout import aplicar_estilo_corporativo

# Configuração de Página e Estilo (Sempre no topo)
st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

# Verificação de segurança
if not st.session_state.get('logged_in'):
    st.error("⚠️ Por favor, faça login no menu lateral para acessar os dados.")
    st.stop()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito. Apenas administradores podem visualizar o Dashboard.")
    st.stop()

st.title("📊 Dashboard Executivo do Portfólio")

# Carregamento de Dados
conn = sqlite3.connect(DB_PATH)
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
conn.close()

if df_projects.empty:
    st.info("Nenhum projeto cadastrado no banco de dados.")
    st.stop()

# Tratamento de Datas
df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
df_projects['start_date'] = pd.to_datetime(df_projects['start_date'], errors='coerce')

# Segmentação de Status
projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
projetos_ativos = df_projects[df_projects['status'].isin(['Não Iniciado', 'Em Planejamento', 'Em Execução', 'Aguardando Aprovação'])]
projetos_bloqueados = df_projects[df_projects['status'] == 'Pausado / Bloqueado']

# KPI de Prazo
if not projetos_concluidos.empty:
    no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
    kpi_prazo_pct = (len(no_prazo) / len(projetos_concluidos)) * 100
else:
    kpi_prazo_pct = 0.0

slas = obter_metricas_gerais_sla()

# --- INTERFACE DE MÉTRICAS ---
st.markdown("### 🎯 Visão Estratégica")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Projetos Totais", len(df_projects))
col2.metric("🏆 % No Prazo", f"{kpi_prazo_pct:.1f}%")
col3.metric("⏳ Ativos / Em Execução", len(projetos_ativos))
col4.metric("🛑 Pausados / Bloqueados", len(projetos_bloqueados))

st.divider()

st.markdown("### ⏱️ SLAs de Operação (Médias)")
s1, s2, s3 = st.columns(3)
s1.metric("Lead Time Médio", f"{slas['avg_lead_time']} dias")
s2.metric("SLA de Resposta (Chat)", f"{slas['avg_first_response']} horas")

# Gráfico de Rosca (Status)
st.markdown("<br>", unsafe_allow_html=True)
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
    fig_status.update_layout(margin=dict(t=10, b=10, l=0, r=0))
    st.plotly_chart(fig_status, use_container_width=True)
