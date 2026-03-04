import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from utils.layout import aplicar_estilo_corporativo
from services.kpi_service import obter_metricas_gerais_sla
from database.setup import DB_PATH

st.set_page_config(page_title="Dashboard", layout="wide", initial_sidebar_state="expanded")
aplicar_estilo_corporativo()

if st.session_state.get('role') != 'admin':
    st.error("Acesso negado.")
    st.stop()

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM projects", conn)
conn.close()

st.title("📊 Dashboard Executivo")
slas = obter_metricas_gerais_sla()

c1, c2, c3 = st.columns(3)
c1.metric("Lead Time Médio", f"{slas['avg_lead_time']} dias")
c2.metric("SLA de Resposta", f"{slas['avg_first_response']} horas")
c3.metric("Total Projetos", len(df))

with st.container(border=True):
    fig = px.pie(df, names='status', hole=0.4, title="Status do Portfólio")
    st.plotly_chart(fig, use_container_width=True)
