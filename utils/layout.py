import streamlit as st

def aplicar_css_seguro():
    st.markdown("""
        <style>
            /* 1. Limpeza de Interface (Remove menu nativo e rodapé) */
            [data-testid="stSidebarNav"] { display: none !important; }
            footer { display: none !important; }
            [data-testid="stToolbar"] { display: none !important; }
            
            /* 2. O CABEÇALHO E A SETINHA (Correção Definitiva) */
            header[data-testid="stHeader"] { 
                background-color: transparent !important; 
            }
            /* Força o botão de menu (setinha) a ser visível e azul */
            button[kind="header"] {
                color: #2563EB !important;
                background-color: #EFF6FF !important;
                border-radius: 8px !important;
                margin-top: 5px !important;
                margin-left: 5px !important;
            }
            button[kind="header"] svg {
                fill: #2563EB !important;
            }

            /* 3. Fundo e Cartões */
            .stApp { background-color: #F8FAFC; }
            section[data-testid="stSidebar"] {
                background-color: #FFFFFF !important;
                border-right: 1px solid #E2E8F0 !important;
                min-width: 280px !important;
            }
            [data-testid="metric-container"], .stForm {
                background-color: #FFFFFF !important;
                border: 1px solid #E2E8F0 !important;
                border-radius: 12px !important;
                box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
            }

            /* 4. Botões de Navegação SPA */
            .stButton > button {
                border-radius: 8px !important;
                font-weight: 600 !important;
                text-align: left !important;
                width: 100% !important;
                background-color: transparent !important;
                color: #334155 !important;
                border: 1px solid transparent !important;
                transition: all 0.2s ease !important;
            }
            .stButton > button:hover {
                background-color: #EFF6FF !important;
                color: #2563EB !important;
            }
            [data-testid="stFormSubmitButton"] > button {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                text-align: center !important;
            }
        </style>
    """, unsafe_allow_html=True)

def renderizar_menu_lateral():
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário').split()[0]}")
        st.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
        st.divider()

        st.markdown("**📁 NAVEGAÇÃO**")
        if st.button("🏢 Workspace de Projetos"):
            st.session_state['tela_atual'] = 'projetos'
            st.rerun()
            
        if st.button("🚀 Iniciar Novo Projeto"):
            st.session_state['tela_atual'] = 'novo_projeto'
            st.rerun()

        if st.session_state.get('role') == 'admin':
            st.markdown("<br>**👑 GESTÃO**", unsafe_allow_html=True)
            if st.button("📊 Dashboard Executivo"):
                st.session_state['tela_atual'] = 'dashboard'
                st.rerun()
            if st.button("⚙️ Configurações"):
                st.session_state['tela_atual'] = 'configuracoes'
                st.rerun()

        st.divider()
        if st.button("🚪 Sair do Sistema"):
            st.session_state.clear()
            st.rerun()
