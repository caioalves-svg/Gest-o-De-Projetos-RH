import streamlit as st

def aplicar_css_seguro():
    st.markdown("""
        <style>
            /* 1. OCULTA A POLUIÇÃO VISUAL COM SEGURANÇA */
            [data-testid="stSidebarNav"] { display: none !important; } /* Menu nativo */
            [data-testid="stToolbar"] { display: none !important; } /* Botão deploy e 3 pontinhos */
            footer { display: none !important; }
            
            /* 2. MANTÉM A BARRA SUPERIOR E O BOTÃO '>' INTACTOS */
            header[data-testid="stHeader"] {
                background-color: transparent !important;
                box-shadow: none !important;
            }
            
            /* 3. CORES E FUNDO SAAS */
            .stApp { background-color: #F8FAFC; }
            section[data-testid="stSidebar"] {
                background-color: #FFFFFF !important;
                border-right: 1px solid #E2E8F0 !important;
                min-width: 280px !important;
            }

            /* 4. BOTÕES DO MENU LATERAL (Navegação Instantânea) */
            .stButton > button {
                border-radius: 8px !important;
                border: 1px solid #E2E8F0 !important;
                background-color: #FFFFFF !important;
                color: #334155 !important;
                font-weight: 600 !important;
                padding: 10px !important;
                transition: all 0.2s ease;
            }
            .stButton > button:hover {
                background-color: #F1F5F9 !important;
                border-color: #CBD5E1 !important;
                color: #2563EB !important;
            }
            
            /* Botões Primários (Salvar/Entrar) */
            [data-testid="stFormSubmitButton"] > button {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                border: none !important;
            }
            [data-testid="stFormSubmitButton"] > button:hover {
                background-color: #1D4ED8 !important;
            }
        </style>
    """, unsafe_allow_html=True)

def renderizar_menu_lateral():
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário').split()[0]}")
        st.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
        st.divider()

        st.markdown("**📁 NAVEGAÇÃO**")
        
        # Botoes que alteram o estado (Instantâneo, sem delay de recarregamento de página)
        if st.button("🏢 Workspace de Projetos", use_container_width=True):
            st.session_state['tela_atual'] = 'projetos'
            st.rerun()
            
        if st.button("🚀 Iniciar Novo Projeto", use_container_width=True):
            st.session_state['tela_atual'] = 'novo_projeto'
            st.rerun()

        if st.session_state.get('role') == 'admin':
            st.markdown("<br>**👑 GESTÃO**", unsafe_allow_html=True)
            if st.button("📊 Dashboard Executivo", use_container_width=True):
                st.session_state['tela_atual'] = 'dashboard'
                st.rerun()
            if st.button("⚙️ Configurações", use_container_width=True):
                st.session_state['tela_atual'] = 'configuracoes'
                st.rerun()

        st.divider()
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            st.session_state.clear()
            st.rerun()
