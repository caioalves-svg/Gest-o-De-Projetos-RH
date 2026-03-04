import streamlit as st

st.set_page_config(page_title="Gestão de Projetos RH", page_icon="⚡", layout="wide", initial_sidebar_state="expanded")

import sqlite3
from database.setup import init_db
from auth.security import login
from utils.layout import aplicar_css_seguro, renderizar_menu_lateral
from views import v_projetos, v_novo, v_dashboard, v_config

init_db()
if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
if 'tela_atual' not in st.session_state: st.session_state['tela_atual'] = 'home'
if 'selected_project_id' not in st.session_state: st.session_state['selected_project_id'] = None

aplicar_css_seguro()

# ==========================================
# GATEWAY DE LOGIN LUXUOSO
# ==========================================
if not st.session_state['logged_in']:
    col_vazia1, col_login, col_vazia2 = st.columns([1, 1.2, 1])
    with col_login:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<h1 style='text-align: center; color: #0F172A; font-size: 2.5em; margin-bottom: 0;'>⚡ Hub de Projetos</h1>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748B; font-size: 1.1em;'>Acesso exclusivo para colaboradores RH</p><br>", unsafe_allow_html=True)
            
            with st.form("form_login", clear_on_submit=True):
                username = st.text_input("🔑 Nome de Usuário", placeholder="Insira o seu login...")
                password = st.text_input("🔒 Palavra-passe", type="password", placeholder="••••••••")
                
                st.markdown("<br>", unsafe_allow_html=True)
                if st.form_submit_button("Aceder ao Workspace", use_container_width=True):
                    if login(username, password): st.rerun()
                    else: st.error("❌ Credenciais incorretas ou acesso negado.")

# ==========================================
# ROTEADOR DE TELAS (SPA)
# ==========================================
else:
    renderizar_menu_lateral()
    tela = st.session_state['tela_atual']

    if tela == 'home':
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.title(f"Bem-vindo de volta, {st.session_state['name'].split()[0]}! 👋")
        st.markdown("### O seu painel de controlo está pronto.")
        st.info("👈 Navegue pelo menu lateral para gerir projetos, aprovar tarefas ou visualizar métricas.")
        
    elif tela == 'projetos': v_projetos.render()
    elif tela == 'novo_projeto': v_novo.render()
    elif tela == 'dashboard': v_dashboard.render()
    elif tela == 'configuracoes': v_config.render()
