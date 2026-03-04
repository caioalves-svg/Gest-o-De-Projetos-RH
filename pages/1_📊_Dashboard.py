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

# Ajuste de Datas
df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
df_projects['start_date'] = pd.to_datetime(df_projects['start_date'], errors='coerce')

# Cálculos Base
projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
projetos_parados = df_projects[df_projects['status'].isin(['Parado', 'Aguardando Aprovação Orçamentária'])]
projetos_andamento = df_projects[df_projects['status'] == 'Em Andamento']

# KPI Principal
if not projetos_concluidos.empty:
    no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
    kpi_prazo_pct = (len(no_prazo) / len(projetos_concluidos)) * 100
else:
    kpi_prazo_pct = 0.0

slas = obter_metricas_gerais_sla()

# ==========================================
# MÉTRICAS
# ==========================================
st.markdown("### 🎯 Visão do Portfólio")
col1, col2, col3, col4 = st.columns(4)

col1.metric("Projetos Totais", len(df_projects))
col2.metric("🏆 % Entregue no Prazo", f"{kpi_prazo_pct:.1f}%")
col3.metric("⏳ Em Andamento", len(projetos_andamento))
col4.metric("🛑 Parados / Aguardando", len(projetos_parados))

st.divider()

st.markdown("### ⏱️ SLAs de Operação")
col_sla1, col_sla2, col_sla3 = st.columns(3)

col_sla1.metric("Lead Time Médio (Projetos)", f"{slas['avg_lead_time']} dias")
col_sla2.metric("SLA 1ª Resposta (Chat)", f"{slas['avg_first_response']} horas")

if not projetos_concluidos.empty:
    df_concluidos_copy = projetos_concluidos.copy()
    df_concluidos_copy['dias_exec'] = (df_concluidos_copy['real_end_date'] - df_concluidos_copy['start_date']).dt.days
    media_tipo = df_concluidos_copy.groupby('type')['dias_exec'].mean().round(1)
    col_sla3.metric("Lead Time (Melhoria | Implant.)", f"{media_tipo.get('Melhoria', 0)}d | {media_tipo.get('Implantação', 0)}d")
else:
    col_sla3.metric("Lead Time (Melhoria | Implant.)", "0d | 0d")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# ÚNICO GRÁFICO: STATUS DO PROJETO
# ==========================================
st.markdown("### 📈 Status Atual dos Projetos")
with st.container(border=True):
    fig_status = px.pie(
        df_projects, 
        names='status', 
        hole=0.45,
        color='status',
        color_discrete_map={
            'Concluído': '#2ECC71',
            'Em Andamento': '#3498DB',
            'Aguardando Início': '#BDC3C7',
            'Parado': '#E74C3C',
            'Aguardando Aprovação Orçamentária': '#F39C12',
            'Cancelado': '#000000'
        }
    )
    fig_status.update_layout(margin=dict(t=20, b=20, l=0, r=0))
    st.plotly_chart(fig_status, use_container_width=True)
