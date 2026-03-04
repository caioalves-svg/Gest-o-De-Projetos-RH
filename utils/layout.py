import streamlit as st

def aplicar_css_seguro():
    st.markdown("""
        <style>
            /* 1. Remove a navegação antiga de páginas (que não usamos mais) */
            [data-testid="stSidebarNav"] { display: none !important; }
            footer { display: none !important; }
            
            /* 2. Deixa o topo limpo, MAS mantém os botões de ação visíveis */
            header { background-color: transparent !important; }
            
            /* 3. A MÁGICA DA SETINHA: Força a cor azul e um fundo para ela NUNCA sumir */
            [data-testid="collapsedControl"] {
                color: #2563EB !important;
                background-color: #EFF6FF !important;
                border-radius: 50% !important;
                margin: 10px !important;
            }
            [data-testid="collapsedControl"] svg {
                fill: #2563EB !important;
            }

            /* 4. Fundo do App e da Sidebar */
            .stApp { background-color: #F8FAFC; }
            section[data-testid="stSidebar"] {
                background-color: #FFFFFF !important;
                border-right: 1px solid #E2E8F0 !important;
            }

            /* 5. Estilo dos botões de navegação no menu (Sem bordas feias) */
            .stButton > button {
                border-radius: 8px !important;
                font-weight: 600 !important;
                text-align: left !important;
                padding: 0.5rem 1rem !important;
                width: 100% !important;
                background-color: transparent !important;
                border: 1px solid transparent !important;
                color: #334155 !important;
                transition: all 0.2s ease !important;
            }
            
            /* Efeito ao passar o mouse nos botões do menu */
            .stButton > button:hover {
                background-color: #EFF6FF !important;
                color: #2563EB !important;
                border: 1px solid #BFDBFE !important;
            }
            
            /* Botão de Form (Login, Salvar) continua azul e destacado */
            [data-testid="stFormSubmitButton"] > button {
                background-color: #2563EB !important;
                color: #FFFFFF !important;
                text-align: center !important;
            }
            [data-testid="stFormSubmitButton"] > button:hover {
                background-color: #1D4ED8 !important;
            }
        </style>
    """, unsafe_allow_html=True)

def renderizar_menu_lateral():
    # O Streamlit desenha isso dentro da barra lateral
    with st.sidebar:
        st.markdown(f"### 👋 Olá, {st.session_state.get('name', 'Usuário').split()[0]}")
        st.caption(f"Perfil: **{st.session_state.get('role', '').upper()}**")
        st.divider()

        st.markdown("**📁 NAVEGAÇÃO**")
        
        # Botões do tipo SPA: Mudam a tela sem recarregar o navegador
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
