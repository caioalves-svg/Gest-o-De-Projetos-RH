import streamlit as st
from auth.security import login

def aplicar_estilo_corporativo():
    # CSS Ultra-Simples (Para evitar tela branca)
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            header {background: transparent !important;}
            footer {visibility: hidden;}
            .stApp { background-color: #F8FAFC; }
            [data-testid="metric-container"] {
                background: white; border: 1px solid #E2E8F0; padding: 15px; border-radius: 10px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Lógica de Login e Menu na Sidebar
    with st.sidebar:
        if st.session_state.get('logged_in'):
            st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário')}")
            st.caption(f"Perfil: {st.session_state.get('role', '').upper()}")
            st.divider()
            
            # Links Fixos
            st.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
            st.page_link("pages/3_➕_Novo_Projeto.py", label="Novo Projeto", icon="🚀")
            
            if st.session_state.get('role') == 'admin':
                st.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
                st.page_link("pages/4_⚙️_Configuracoes.py", label="Configurações", icon="⚙️")
            
            st.divider()
            if st.button("🚪 Sair"):
                st.session_state.clear()
                st.rerun()
        else:
            st.warning("🔐 Login Necessário")
            with st.form("login_sidebar"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    if login(u, p): st.rerun()
                    else: st.error("Erro")
            # Se não logado, para a execução do corpo da página
            st.stop()
