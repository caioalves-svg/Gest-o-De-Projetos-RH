import streamlit as st
from database.setup import init_db
from utils.layout import aplicar_estilo_corporativo

# ESSENCIAL: Menu inicia aberto para evitar confusão
st.set_page_config(
    page_title="Sistema RH", 
    page_icon="⚡", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

init_db()
aplicar_estilo_corporativo()

if not st.session_state.get('logged_in'):
    st.title("🚀 Bem-vindo ao Sistema de Projetos")
    st.info("Efetue o login no formulário à esquerda para acessar o painel.")
    st.markdown("---")
    st.write("Caso o menu esteja oculto, clique na setinha **`>`** no topo esquerdo da tela.")
else:
    st.title("🏠 Página Inicial")
    st.success(f"Logado como {st.session_state['name']}. Use o menu para navegar.")
