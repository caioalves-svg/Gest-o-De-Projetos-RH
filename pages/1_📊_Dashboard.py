import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Ajuste de path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH, init_db
from auth.security import check_auth
from services.kpi_service import obter_metricas_gerais_sla

# 1. Inicialização e Segurança
init_db()
check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito. Apenas administradores podem aceder ao Dashboard Executivo.")
    st.stop()

st.set_page_config(page_title="Dashboard Executivo", page_icon="📊", layout="wide")

# CSS Corporativo
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border-top: 4px solid #2C3E50;
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Dashboard Executivo e Analytics")
st.markdown("Visão estratégica do Portfólio de Projetos do RH e SLAs de Operação.")

# 2. Extração de Dados
conn = sqlite3.connect(DB_PATH)
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
df_users = pd.read_sql_query("SELECT id, name FROM users", conn)
conn.close()

if df_projects.empty:
    st.info("Nenhum projeto cadastrado no momento. Vá até a página 'Novo Projeto' para começar.")
    st.stop()

# Tratamento de Datas
df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
df_projects['start_date'] = pd.to_datetime(df_projects['start_date'], errors='coerce')

# 3. Cálculos Estratégicos Base
projetos_concluidos = df_projects[df_projects['status'] == 'Concluído'].copy()
projetos_pendentes = df_projects[df_projects['status'].isin(['Backlog', 'Em Progresso'])]
projetos_atrasados = df_projects[df_projects['status'] == 'Atrasado']

# KPI Principal (Inegociável): % Entregues no Prazo
if not projetos_concluidos.empty:
    no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
    kpi_prazo_pct = (len(no_prazo) / len(projetos_concluidos)) * 100
else:
    kpi_prazo_pct = 0.0

economia_total = df_projects['saved_value'].sum()

# Consumindo o novo motor de SLA
slas = obter_metricas_gerais_sla()

# 4. Renderização: Primeira Linha (Métricas de Execução)
st.markdown("### 🎯 Indicadores de Execução (KPIs)")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Projetos no Portfólio", len(df_projects))
col2.metric("🏆 % Entregue no Prazo", f"{kpi_prazo_pct:.1f}%", help="Calculado sobre projetos já concluídos.")
col3.metric("⏳ Em Andamento", len(projetos_pendentes))
col4.metric("🚨 Atrasados", len(projetos_atrasados))
col5.metric("💰 Economia Gerada", f"R$ {economia_total:,.2f}")

st.divider()

# 5. Renderização: Segunda Linha (Acordos de Nível de Serviço)
st.markdown("### ⏱️ SLAs de Operação e Capacidade")
col_sla1, col_sla2, col_sla3, col_sla4 = st.columns(4)

col_sla1.metric("Lead Time Geral", f"{slas['avg_lead_time']} dias", help="Tempo médio entre o início e a conclusão do projeto.")
col_sla2.metric("SLA 1ª Resposta (Tarefas)", f"{slas['avg_first_response']} horas", help="Tempo médio que o dono da tarefa demora a responder no Chat.")

# Tempo médio por tipo de projeto
if not projetos_concluidos.empty:
    projetos_concluidos['dias_execucao'] = (projetos_concluidos['real_end_date'] - projetos_concluidos['start_date']).dt.days
    media_tipo = projetos_concluidos.groupby('type')['dias_execucao'].mean().round(1)
    melhoria_avg = media_tipo.get('Melhoria', 0)
    implanta_avg = media_tipo.get('Implantação', 0)
    col_sla3.metric("Lead Time: Melhoria", f"{melhoria_avg} dias")
    col_sla4.metric("Lead Time: Implantação", f"{implanta_avg} dias")
else:
    col_sla3.metric("Lead Time: Melhoria", "0 dias")
    col_sla4.metric("Lead Time: Implantação", "0 dias")

st.markdown("<br>", unsafe_allow_html=True)

# 6. Gráficos Analíticos (Plotly)
st.markdown("### 📈 Análise Visual")
col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.container(border=True):
        st.markdown("**Status do Portfólio**")
        fig_status = px.pie(
            df_projects, 
            names='status', 
            hole=0.45,
            color='status',
            color_discrete_map={
                'Concluído': '#2ECC71',
                'Em Progresso': '#F39C12',
                'Backlog': '#3498DB',
                'Atrasado': '#E74C3C'
            }
        )
        fig_status.update_layout(margin=dict(t=20, b=20, l=0, r=0), showlegend=True)
        st.plotly_chart(fig_status, use_container_width=True)

with col_g2:
    with st.container(border=True):
        st.markdown("**Carga de Trabalho (Projetos por Gestor)**")
        user_mapping = dict(zip(df_users['id'], df_users['name']))
        df_projects['manager_name'] = df_projects['manager_id'].map(user_mapping)
        
        workload = df_projects['manager_name'].value_counts().reset_index()
        workload.columns = ['Gestor', 'Qtd Projetos']
        
        fig_workload = px.bar(
            workload, 
            x='Qtd Projetos', 
            y='Gestor', 
            orientation='h',
            color='Qtd Projetos',
            color_continuous_scale='Teal'
        )
        fig_workload.update_layout(margin=dict(t=20, b=20, l=0, r=0), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_workload, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Gráfico de Linha: Economia por Período
with st.container(border=True):
    st.markdown("**Evolução da Economia Gerada (R$)**")
    if not projetos_concluidos.empty and projetos_concluidos['saved_value'].sum() > 0:
        projetos_concluidos['month_year'] = projetos_concluidos['real_end_date'].dt.to_period('M').astype(str)
        economia_periodo = projetos_concluidos.groupby('month_year')['saved_value'].sum().reset_index()
        economia_periodo = economia_periodo.sort_values('month_year')
        
        fig_econ = px.line(
            economia_periodo, 
            x='month_year', 
            y='saved_value', 
            markers=True,
            line_shape='spline',
            labels={'month_year': 'Mês/Ano de Conclusão', 'saved_value': 'Valor Economizado (R$)'}
        )
        fig_econ.update_traces(line=dict(color='#2C3E50', width=3), marker=dict(size=8, color='#E67E22'))
        fig_econ.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig_econ, use_container_width=True)
    else:
        st.info("Ainda não há dados de economia de projetos concluídos para gerar a curva de evolução.")
