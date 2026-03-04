import streamlit as st
from auth.security import login

def aplicar_estilo_corporativo():
    # 1. CSS Profissional (Resolve o bug do ícone e esconde o menu padrão)
    st.markdown("""
        <style>
            [data-testid="stSidebarNav"] {display: none;}
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {background-color: transparent !important;}
            
            /* Ajuste da setinha do menu lateral */
            [data-testid="collapsedControl"] {
                color: #2563EB !important;
            }
            
            .stApp { background-color: #F8FAFC; }
            
            /* Estilo dos Cards */
            [data-testid="metric-container"] {
                background: white; border: 1px solid #E2E8F0; padding: 20px;
                border-radius: 12px; border-top: 5px solid #2563EB;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            }
            
            .stButton>button { border-radius: 8px !important; font-weight: 600 !important; }
        </style>
    """, unsafe_allow_html=True)

    # 2. Lógica de Navegação Permanente
    with st.sidebar:
        if st.session_state.get('logged_in'):
            st.markdown(f"### 👋 Olá, {st.session_state['name'].split()[0]}")
            st.caption(f"Perfil: **{st.session_state['role'].upper()}**")
            st.divider()
            
            st.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
            st.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
            
            if st.session_state['role'] == 'admin':
                st.markdown("<br>**👑 ESTRATÉGICO**", unsafe_allow_html=True)
                st.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
                st.page_link("pages/4_⚙️_Configuracoes.py", label="Usuários e Acessos", icon="⚙️")
            
            st.divider()
            if st.button("🚪 Sair"):
                st.session_state.clear()
                st.rerun()
        else:
            # Se não estiver logado, força o formulário de login na lateral
            st.warning("🔐 Acesso Restrito")
            with st.form("login_universal"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar no Sistema", use_container_width=True):
                    if login(u, p):
                        st.rerun()
                    else:
                        st.error("Credenciais inválidas")
            st.stop() # Interrompe o carregamento da página se não logar
