import streamlit as st
from database.setup import init_db
from utils.layout import aplicar_estilo_corporativo

# Força o estado expandido
st.set_page_config(page_title="Sistema RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

init_db()
aplicar_estilo_corporativo()

st.title("🚀 Central de Projetos RH")
st.write("---")
st.markdown("### Bem-vindo ao seu Workspace.")
st.write("Utilize o menu lateral para gerenciar suas demandas e visualizar indicadores.")
