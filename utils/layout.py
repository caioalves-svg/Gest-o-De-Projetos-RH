import streamlit as st

def aplicar_estilo_corporativo():
    # CSS para esconder o menu padrão e fixar o visual SaaS
    st.markdown("""
        <style>
            /* 1. Esconde a lista de arquivos padrão do Streamlit */
            [data-testid="stSidebarNav"] {display: none;}
            
            /* 2. Resolve o bug do 'keyboard_double' mantendo o header transparente */
            header { background-color: transparent !important; }
            [data-testid="stToolbar"] { visibility: hidden !important; }
            footer { visibility: hidden !important; }

            /* 3. Design dos Cards e Botões */
            .stApp { background-color: #F8FAFC; }
            [data-testid="metric-container"] {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 12px !important;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important;
                border-top: 4px solid #2563EB !important;
            }
            .stButton>button { border-radius: 8px !important; font-weight: 600 !important; }
        </style>
    """, unsafe_allow_html=True)

    # RENDERIZAÇÃO DO MENU LATERAL (Idêntico para todas as páginas)
    if st.session_state.get('logged_in'):
        st.sidebar.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário')}")
        st.sidebar.caption(f"🛡️ Perfil: **{st.session_state.get('role', '').upper()}**")
        st.sidebar.divider()
        
        st.sidebar.markdown("**🌐 NAVEGAÇÃO**")
        st.sidebar.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
        st.sidebar.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
        
        if st.session_state.get('role') == 'admin':
            st.sidebar.markdown("<br>**👑 ADMINISTRAÇÃO**", unsafe_allow_html=True)
            st.sidebar.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
            st.sidebar.page_link("pages/4_⚙️_Configuracoes.py", label="Configurações & Acessos", icon="⚙️")
        
        st.sidebar.divider()
        if st.sidebar.button("🚪 Sair / Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()
