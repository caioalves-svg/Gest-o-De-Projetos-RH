import streamlit as st

# DEVE SER A PRIMEIRA LINHA
st.set_page_config(page_title="Sistema RH", layout="wide", initial_sidebar_state="expanded")

from database.setup import init_db
from utils.layout import aplicar_estilo_corporativo

# Inicializa o banco
init_db()

# Aplica layout e menu lateral
aplicar_estilo_corporativo()

# Conteúdo Principal
st.title("🚀 Central de Projetos RH")
st.markdown("---")
st.write("Bem-vindo ao sistema. Utilize o menu lateral para navegar.")
