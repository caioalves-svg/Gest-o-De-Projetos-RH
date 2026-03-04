import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
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
    st.error("🔒 Acesso restrito. Apenas administradores podem acessar o Dashboard Executivo.")
    st.stop()

st.set_page_config(page_title="Dashboard Executivo", page_icon="📊", layout="wide")

# CSS Corporativo para os Cards
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

st.title("📊 Dashboard Executivo do Portfólio")
st.markdown("Visão estratégica e status global dos Projetos de RH.")

# 2. Extração de Dados
conn = sqlite3.connect(DB_PATH)
df_projects = pd.read_sql_query("SELECT * FROM projects", conn)
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

# Consumindo o motor de SLA
slas = obter_metricas_gerais_sla()

# ==========================================
# BLOCO 1: KPIs DE EXECUÇÃO
# ==========================================
st.markdown("### 🎯 Indicadores de Eficiência (Projetos)")
col1, col2, col3, col4, col5 = st.columns(5)

col1.metric("Projetos no Portfólio", len(df_projects))
col2.metric("🏆 % Entregue no Prazo", f"{kpi_prazo_pct:.1f}%", help="O Indicador Inegociável.")
col3.metric("⏳ Em Andamento", len(projetos_pendentes))
col4.metric("🚨 Atrasados", len(projetos_atrasados))
col5.metric("💰 Economia Gerada", f"R$ {economia_total:,.2f}")

st.divider()

# ==========================================
# BLOCO 2: SLAs DE OPERAÇÃO
# ==========================================
st.markdown("### ⏱️ SLAs de Operação e Capacidade")
col_sla1, col_sla2, col_sla3, col_sla4 = st.columns(4)

col_sla1.metric("Lead Time Médio (Projetos)", f"{slas['avg_lead_time']} dias")
col_sla2.metric("SLA 1ª Resposta (Chat das Tarefas)", f"{slas['avg_first_response']} horas")

if not projetos_concluidos.empty:
    projetos_concluidos['dias_execucao'] = (projetos_concluidos['real_end_date'] - projetos_concluidos['start_date']).dt.days
    media_tipo = projetos_concluidos.groupby('type')['dias_execucao'].mean().round(1)
    col_sla3.metric("Lead Time: Melhoria", f"{media_tipo.get('Melhoria', 0)} dias")
    col_sla4.metric("Lead Time: Implantação", f"{media_tipo.get('Implantação', 0)} dias")
else:
    col_sla3.metric("Lead Time: Melhoria", "0 dias")
    col_sla4.metric("Lead Time: Implantação", "0 dias")

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# BLOCO 3: GRÁFICOS DO PORTFÓLIO (PROJETOS)
# ==========================================
st.markdown("### 📈 Análise do Portfólio de Projetos")

# Primeira Linha de Gráficos
col_g1, col_g2 = st.columns(2)

with col_g1:
    with st.container(border=True):
        st.markdown("**1. Status Geral dos Projetos**")
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
        fig_status.update_layout(margin=dict(t=20, b=20, l=0, r=0))
        st.plotly_chart(fig_status, use_container_width=True)

with col_g2:
    with st.container(border=True):
        st.markdown("**2. Volume de Demandas por Área Solicitante**")
        demandas = df_projects['requester'].value_counts().reset_index()
        demandas.columns = ['Área Solicitante', 'Qtd de Projetos']
        
        fig_area = px.bar(
            demandas, 
            x='Qtd de Projetos', 
            y='Área Solicitante', 
            orientation='h',
            color='Qtd de Projetos',
            color_continuous_scale='Blues'
        )
        fig_area.update_layout(margin=dict(t=20, b=20, l=0, r=0), yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_area, use_container_width=True)

# Segunda Linha de Gráficos
col_g3, col_g4 = st.columns(2)

with col_g3:
    with st.container(border=True):
        st.markdown("**3. Composição: Tipo vs Prioridade**")
        # Garante a ordem correta das prioridades
        category_orders = {"priority": ["Baixa", "Média", "Alta"]}
        
        fig_tipo = px.histogram(
            df_projects, 
            x='type', 
            color='priority', 
            barmode='group',
            color_discrete_map={'Baixa': '#95A5A6', 'Média': '#F39C12', 'Alta': '#E74C3C'},
            category_orders=category_orders,
            labels={'type': 'Tipo de Projeto', 'count': 'Quantidade'}
        )
        fig_tipo.update_layout(margin=dict(t=20, b=20, l=0, r=0), yaxis_title="Qtd de Projetos", xaxis_title="")
        st.plotly_chart(fig_tipo, use_container_width=True)

with col_g4:
    with st.container(border=True):
        st.markdown("**4. Curva de Valor Economizado (ROI)**")
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
                labels={'month_year': 'Mês de Conclusão', 'saved_value': 'Valor Economizado (R$)'}
            )
            fig_econ.update_traces(line=dict(color='#2C3E50', width=3), marker=dict(size=8, color='#E67E22'))
            fig_econ.update_layout(margin=dict(t=20, b=20, l=0, r=0))
            st.plotly_chart(fig_econ, use_container_width=True)
        else:
            st.info("Conclua projetos com 'Valor Economizado' para visualizar a curva de ROI.")
