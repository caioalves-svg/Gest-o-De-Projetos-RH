import streamlit as st
from database.setup import init_db
from utils.layout import aplicar_estilo_corporativo

# Força o menu a iniciar aberto (EXPANDED)
st.set_page_config(
    page_title="Sistema RH", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

init_db()
aplicar_estilo_corporativo()

if not st.session_state.get('logged_in'):
    st.title("🚀 Central de Projetos RH")
    st.info("Efetue o login na barra lateral para acessar o workspace.")
else:
    st.title("🏠 Bem-vindo")
    st.write("Seu acesso foi liberado. Utilize o menu à esquerda.")
