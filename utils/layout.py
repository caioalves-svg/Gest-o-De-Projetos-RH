import streamlit as st
from auth.security import login

def aplicar_estilo_corporativo():
    # CSS de Elite
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;} /* Remove menu nativo */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {background-color: transparent !important;} /* Fix do ícone fantasma */
            
            .stApp { background-color: #F8FAFC; }
            [data-testid="metric-container"] {
                background: white; border: 1px solid #E2E8F0; padding: 20px;
                border-radius: 12px; border-top: 5px solid #2563EB;
            }
            .stButton>button { border-radius: 8px !important; font-weight: 600 !important; width: 100%; }
        </style>
    """, unsafe_allow_html=True)

    # Renderização do Menu Lateral Fixo
    if st.session_state.get('logged_in'):
        with st.sidebar:
            st.markdown(f"### 👋 Olá, {st.session_state['name']}")
            st.caption(f"Perfil: {st.session_state['role'].upper()}")
            st.divider()
            st.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
            st.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
            
            if st.session_state['role'] == 'admin':
                st.markdown("<br>**ESTRATÉGICO**", unsafe_allow_html=True)
                st.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
                st.page_link("pages/4_⚙️_Configuracoes.py", label="Usuários e Acessos", icon="⚙️")
            
            st.divider()
            if st.button("🚪 Sair"):
                st.session_state.clear()
                st.rerun()
    else:
        # Se não logado, o login aparece na lateral para evitar travas
        with st.sidebar:
            st.warning("🔐 Acesso Restrito")
            with st.form("login_side"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    if login(u, p): st.rerun()
                    else: st.error("Erro")
