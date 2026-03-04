import streamlit as st

def aplicar_estilo_corporativo():
    # 1. CSS para esconder o menu padrão e estilizar a interface
    st.markdown("""
        <style>
            /* Esconde o menu de arquivos padrão do Streamlit */
            [data-testid="stSidebarNav"] {display: none;}
            
            /* Limpa o topo (Deploy e 3 pontos), mas mantém a seta de expandir */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            header {background-color: transparent !important;}

            /* Fundo e Tipografia SaaS */
            .stApp {background-color: #F8FAFC;}
            
            /* Estilização da Sidebar */
            [data-testid="stSidebar"] {
                background-color: #FFFFFF !important;
                border-right: 1px solid #E2E8F0;
            }
            
            /* Estilo dos Botões e Inputs */
            .stButton>button { border-radius: 10px !important; font-weight: 600 !important; }
            [data-testid="stFormSubmitButton"]>button { background: #2563EB !important; color: white !important; width: 100% !important; }
        </style>
    """, unsafe_allow_html=True)

    # 2. Renderização do Menu Lateral Customizado
    # Só mostra o menu se o usuário estiver logado
    if st.session_state.get('logged_in'):
        st.sidebar.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário')}")
        st.sidebar.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
        st.sidebar.divider()
        
        st.sidebar.markdown("**📁 GESTÃO**")
        st.sidebar.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
        st.sidebar.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
        
        if st.session_state.get('role') == 'admin':
            st.sidebar.markdown("<br>**👑 ESTRATÉGICO**", unsafe_allow_html=True)
            st.sidebar.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
            st.sidebar.page_link("pages/4_⚙️_Configuracoes.py", label="Usuários e Acessos", icon="⚙️")
        
        st.sidebar.divider()
        if st.sidebar.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.clear()
            st.rerun()
