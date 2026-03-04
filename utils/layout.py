import streamlit as st
from auth.security import login

def aplicar_estilo_corporativo():
    # CSS focado em beleza e visibilidade, sem ocultar controles vitais
    st.markdown("""
        <style>
            /* 1. Esconde apenas a lista de arquivos nativa, mas mantém o container da sidebar */
            [data-testid="stSidebarNav"] {display: none;}
            
            /* 2. Mantém a barra de ferramentas (toolbar) invisível para estética */
            [data-testid="stToolbar"] {visibility: hidden !important;}
            footer {visibility: hidden !important;}
            
            /* 3. Garante que o botão de abrir/fechar sidebar esteja visível e clicável */
            [data-testid="collapsedControl"] {
                display: flex !important;
                color: #2563EB !important;
            }

            /* 4. Estilo de Cartões e Fundo */
            .stApp { background-color: #F8FAFC; }
            [data-testid="metric-container"] {
                background: white; border: 1px solid #E2E8F0; padding: 20px;
                border-radius: 12px; border-top: 5px solid #2563EB;
            }
        </style>
    """, unsafe_allow_html=True)

    # RENDERIZAÇÃO FORÇADA DO MENU
    # Se o usuário está logado, o menu PRECISA aparecer
    if st.session_state.get('logged_in'):
        with st.sidebar:
            st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário')}")
            st.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
            st.divider()
            
            # Links de Navegação
            st.page_link("pages/2_📋_Projetos.py", label="Workspace de Projetos", icon="🏢")
            st.page_link("pages/3_➕_Novo_Projeto.py", label="Iniciar Novo Projeto", icon="🚀")
            
            if st.session_state.get('role') == 'admin':
                st.markdown("<br>**👑 ESTRATÉGICO**", unsafe_allow_html=True)
                st.page_link("pages/1_📊_Dashboard.py", label="Dashboard Executivo", icon="📊")
                st.page_link("pages/4_⚙️_Configuracoes.py", label="Usuários e Acessos", icon="⚙️")
            
            st.divider()
            if st.button("🚪 Sair do Sistema", use_container_width=True):
                st.session_state.clear()
                st.rerun()
    else:
        # Se não logado, o formulário de login aparece na lateral para não travar o sistema
        with st.sidebar:
            st.info("🔒 Faça login para acessar")
            with st.form("login_sidebar_fix"):
                u = st.text_input("Usuário")
                p = st.text_input("Senha", type="password")
                if st.form_submit_button("Entrar"):
                    if login(u, p): st.rerun()
                    else: st.error("Incorreto")
