import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from datetime import datetime
import os
import sys

# Ajuste de path para importações
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from database.setup import DB_PATH
from auth.security import check_auth
from services.kpi_service import obter_metricas_gerais_sla

# 1. Verificação de Segurança
check_auth()

if st.session_state.get('role') != 'admin':
    st.error("🔒 Acesso restrito. Apenas administradores podem aceder ao Dashboard Executivo.")
    st.stop()

st.set_page_config(page_title="Dashboard Executivo - HR", page_icon="📊", layout="wide")
st.title("📊 Dashboard Executivo de Projetos e Inovação")

# 2. Extração de Dados
conn = sqlite3.connect(DB_PATH)
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
df_users = pd.read_sql_query("SELECT id, name FROM users", conn)
conn.close()

if df_projects.empty:
    st.info("Nenhum projeto cadastrado no momento. Vá até a página de Projetos para começar.")
    st.stop()

# Conversão de datas para cálculos precisos
df_projects['due_date'] = pd.to_datetime(df_projects['due_date'], errors='coerce')
df_projects['real_end_date'] = pd.to_datetime(df_projects['real_end_date'], errors='coerce')
df_projects['start_date'] = pd.to_datetime(df_projects['start_date'], errors='coerce')

# 3. Cálculos Estratégicos Base
projetos_concluidos = df_projects[df_projects['status'] == 'Concluído']
projetos_pendentes = df_projects[df_projects['status'].isin(['Backlog', 'Em Progresso'])]
projetos_atrasados = df_projects[df_projects['status'] == 'Atrasado']

# INDICADOR PRINCIPAL (INEGOCIÁVEL): % Entregues no Prazo
if not projetos_concluidos.empty:
    # Considera no prazo se a data real for menor ou igual à data prevista
    no_prazo = projetos_concluidos[projetos_concluidos['real_end_date'] <= projetos_concluidos['due_date']]
    kpi_prazo_pct = (len(no_prazo) / len(projetos_concluidos)) * 100
else:
    kpi_prazo_pct = 0.0

economia_total = df_projects['saved_value'].sum()

# 4. Renderização: KPIs Principais
st.markdown("### 🎯 Indicadores Chave de Desempenho (KPIs)")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Projetos Totais", len(df_projects))
col2.metric("🏆 Entregues no Prazo", f"{kpi_prazo_pct:.1f}%", help="Calculado sobre projetos já concluídos.")
col3.metric("⏳ Pendentes", len(projetos_pendentes))
col4.metric("🚨 Atrasados", len(projetos_atrasados))
col5.metric("💰 Economia Total", f"R$ {economia_total:,.2f}")

st.divider()

# 5. Renderização: SLAs e Métricas de Eficiência (Consumindo o kpi_service)
st.markdown("### ⏱️ Acordos de Nível de Serviço (SLA) e Operação")
slas = obter_metricas_gerais_sla()

col_sla1, col_sla2, col_sla3, col_sla4 = st.columns(4)

col_sla1.metric("Lead Time Médio", f"{slas['avg_lead_time']} dias", help="Tempo médio entre o início e a conclusão.")
col_sla2.metric("SLA - 1ª Resposta", f"{slas['avg_first_response']} horas", help="Tempo médio até o primeiro comentário.")
col_sla3.metric("Tempo Médio entre Interações", f"{slas['avg_interaction_time']} horas")

# Cálculo de tempo médio por tipo de projeto
if not projetos_concluidos.empty:
    projetos_concluidos['dias_execucao'] = (projetos_concluidos['real_end_date'] - projetos_concluidos['start_date']).dt.days
    media_tipo = projetos_concluidos.groupby('type')['dias_execucao'].mean().round(1)
    melhoria_avg = media_tipo.get('Melhoria', 0)
    implanta_avg = media_tipo.get('Implantação', 0)
    col_sla4.metric("Tempo Médio (Melhoria | Implant.)", f"{melhoria_avg}d | {implanta_avg}d")
else:
    col_sla4.metric("Tempo Médio (Melhoria | Implant.)", "0d | 0d")

st.divider()

# 6. Visualizações Gráficas (Plotly)
st.markdown("### 📈 Análise Visual")
col_graf1, col_graf2, col_graf3 = st.columns(3)

with col_graf1:
    st.markdown("**Distribuição de Status**")
    fig_status = px.pie(
        df_projects, 
        names='status', 
        hole=0.4, 
        color='status',
        color_discrete_map={
            'Concluído': '#2ECC71',
            'Em Progresso': '#F39C12',
            'Backlog': '#3498DB',
            'Atrasado': '#E74C3C'
        }
    )
    fig_status.update_layout(margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_status, use_container_width=True)

with col_graf2:
    st.markdown("**Projetos por Tipo e Complexidade**")
    fig_type = px.histogram(
        df_projects, 
        x='type', 
        color='complexity', 
        barmode='group',
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    fig_type.update_layout(margin=dict(t=0, b=0, l=0, r=0), xaxis_title="Tipo", yaxis_title="Quantidade")
    st.plotly_chart(fig_type, use_container_width=True)

with col_graf3:
    st.markdown("**Carga de Trabalho (Projetos por Gestor)**")
    # Mapear IDs para Nomes
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
        color_continuous_scale='Blues'
    )
    fig_workload.update_layout(margin=dict(t=0, b=0, l=0, r=0), yaxis={'categoryorder':'total ascending'})
    st.plotly_chart(fig_workload, use_container_width=True)
