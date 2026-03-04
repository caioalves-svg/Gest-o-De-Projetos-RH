import streamlit as st

# 1. CONFIGURAÇÃO INICIAL (Sempre a primeira linha)
st.set_page_config(page_title="Gestão de Projetos RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_css_seguro, renderizar_menu_lateral

# Importando a lógica pura das Views (vamos criá-las a seguir)
from views import v_projetos, v_novo, v_dashboard, v_config

# Inicializa Banco e Estado
init_db()
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'tela_atual' not in st.session_state: st.session_state['tela_atual'] = 'home'
if 'selected_project_id' not in st.session_state: st.session_state['selected_project_id'] = None

aplicar_css_seguro()

# ==========================================
# GATEWAY DE LOGIN
# ==========================================
if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<br><br><h2 style='text-align: center;'>⚡ Projetos RH</h2>", unsafe_allow_html=True)
        with st.form("form_login"):
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            if st.form_submit_button("Entrar no Workspace", use_container_width=True):
                if login(username, password): st.rerun()
                else: st.error("❌ Credenciais incorretas.")

# ==========================================
# SISTEMA OPERACIONAL (SPA MODULAR)
# ==========================================
else:
    renderizar_menu_lateral()
    tela = st.session_state['tela_atual']

    if tela == 'home':
        st.title("🏠 Bem-vindo ao seu Workspace")
        st.success("✅ O sistema está online e a navegação instantânea está ativada.")
        
    elif tela == 'projetos':
        v_projetos.render() # Chama toda a lógica do Kanban e Chat
        
    elif tela == 'novo_projeto':
        v_novo.render()     # Chama a lógica de criação de projetos
        
    elif tela == 'dashboard':
        v_dashboard.render() # Chama os gráficos e SLAs
        
    elif tela == 'configuracoes':
        v_config.render()    # Chama a gestão de utilizadores
